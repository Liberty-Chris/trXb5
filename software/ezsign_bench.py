"""Direct, single-label PC/SC interoperability bench for the four-color 2.9 inch EZ Sign."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

SELECT = bytes.fromhex("00 A4 04 00 07 D2 76 00 00 85 01 01")
INFO = bytes.fromhex("00 D1 00 00 00")
AUTH = bytes.fromhex("00 20 00 01 04 20 09 12 10")
REFRESH = bytes.fromhex("F0 D4 85 80 00")
POLL = bytes.fromhex("F0 DE 00 00 01")


class BenchError(Exception):
    pass


def metadata(payload):
    fields = {}
    offset = 0
    while offset < len(payload):
        if len(payload) - offset < 2:
            raise BenchError("Truncated device-info TLV header")
        tag, length = payload[offset:offset + 2]
        offset += 2
        if offset + length > len(payload) or tag in fields:
            raise BenchError("Truncated or duplicate device-info TLV")
        fields[tag] = payload[offset:offset + length]
        offset += length
    panel = fields.get(0xA0, b"")
    ident = fields.get(0xC1, b"")
    if len(panel) != 7 or len(ident) != 4 or ident in (bytes(4), b"\xff"*4):
        raise BenchError("Missing or unusable A0 geometry or C1 device identifier")
    bits = {0x01: 1, 0x47: 1, 0x07: 2}.get(panel[1])
    height_bits = int.from_bytes(panel[3:5], "big")
    width = int.from_bytes(panel[5:7], "big")
    if bits is None or not width or not height_bits or height_bits % bits:
        raise BenchError("Unsupported or malformed geometry")
    return {"device_id": ident.hex(), "width": width, "height": height_bits // bits,
            "bpp": bits, "orientation_hex": fields.get(0xA1, b"").hex(), "raw_info": payload.hex()}


def image_commands(raw):
    """Single D3 APDU per 2000-byte block, reject oversized compressed blocks before any RF I/O."""
    import lzokay
    if len(raw) != 9472:
        raise BenchError("Expected 9472 bytes of device-order 2-bpp raster")
    result = []
    for index, offset in enumerate(range(0, len(raw), 2000)):
        block = raw[offset:offset + 2000]
        compressed = lzokay.compress(block)
        if len(compressed) > 250:
            raise BenchError(f"Block {index} exceeds the qualified single-fragment profile")
        result.append(bytes([0xF0, 0xD3, 0, 1, len(compressed) + 2, index, 0]) + compressed)
    return result


def run_job(exchange, record, frames=None, device_id=None, geometry=None, sleep=time.sleep,
            monotonic=time.monotonic, refresh_seconds=90, authenticate_for_info=False,
            minimum_field_seconds=30):
    exchange(SELECT)
    if authenticate_for_info:
        exchange(AUTH)
    unit = metadata(exchange(INFO))
    record("identity", "observed", **unit)
    if frames is None:
        return
    if unit["device_id"] != device_id or unit["bpp"] != 2 or (unit["width"], unit["height"]) != geometry:
        raise BenchError("Physical device ID or device-order geometry differs from the requested profile")
    if not authenticate_for_info:
        exchange(AUTH)
    for index, command in enumerate(frames):
        record("transfer", "issuing", block=index)
        try:
            exchange(command)
        except (Exception, KeyboardInterrupt):
            record("transfer", "acknowledgement_unknown", block=index)
            raise
        record("transfer", "block_acknowledged", block=index)
        sleep(.01)
    record("transfer", "acknowledged")
    # Any loss after this point is ambiguous. Avoid field reset or AUTH/replay.
    deadline = monotonic() + refresh_seconds
    record("refresh", "issuing")
    try:
        exchange(REFRESH)
        record("refresh", "accepted")
        earliest_idle = monotonic() + minimum_field_seconds
        observed_busy = False
        idle_polls = 0
        while monotonic() < deadline:
            sleep(min(.5, max(0, deadline - monotonic())))
            if monotonic() >= deadline:
                break
            status = exchange(POLL)
            if monotonic() >= deadline:
                break
            if status == b"\x01":
                if not observed_busy:
                    record("refresh", "busy_observed")
                observed_busy = True
                idle_polls = 0
            elif status == b"\x00":
                if observed_busy and monotonic() >= earliest_idle:
                    idle_polls += 1
                    if idle_polls == 3:
                        record("refresh", "complete")
                        return
            else:
                raise BenchError("Unknown refresh status "+status.hex())
        reason = "stable idle" if observed_busy else "busy transition"
        raise BenchError(f"Refresh timed out waiting for {reason}")
    except (Exception, KeyboardInterrupt):
        # Hold the same exclusive PC/SC session for the remainder of the observation window.
        # Only external field instrumentation can confirm physical RF continuity.
        try:
            record("refresh", "unknown")
        finally:
            sleep(max(0, deadline - monotonic()))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("readers")
    for cmd in ("identify", "write"):
        p = commands.add_parser(cmd)
        p.add_argument("--reader", required=True, help="Exact PC/SC reader name")
        p.add_argument("--record", required=True, type=Path, help="New JSONL evidence path")
        p.add_argument("--fixture", required=True, help="Hardware revision and physical bench identifier")
        p.add_argument("--authenticate-for-info", action="store_true",
                       help="Send EZ Sign session AUTH after SELECT, before reading device info")
        if cmd == "write":
            p.add_argument("--device-id", required=True, help="C1 hex from the physically identified unit")
            p.add_argument("--geometry", required=True, choices=["296x128","128x296"])
            p.add_argument("--raster", required=True, type=Path, help="Device-oriented, packed four-color raster")
    args = parser.parse_args()
    from smartcard.System import readers
    from smartcard.scard import SCARD_SHARE_EXCLUSIVE, SCARD_LEAVE_CARD
    if args.command == "readers":
        for reader in readers():
            print(reader)
        return
    frames = geometry = ident = image_hash = None
    if args.command == "write":
        ident = bytes.fromhex(args.device_id).hex()
        if len(ident) != 8:
            raise BenchError("C1 identifier must contain exactly four bytes")
        geometry = tuple(map(int, args.geometry.split("x")))
        raw = args.raster.read_bytes()
        frames = image_commands(raw)
        image_hash = hashlib.sha256(raw).hexdigest()
    with args.record.open("x", encoding="utf-8") as output:
        def record(stage, state, **details):
            event = dict(utc=datetime.now(timezone.utc).isoformat(), stage=stage, state=state, **details)
            output.write(json.dumps(event) + "\n")
            output.flush()
            os.fsync(output.fileno())
        record("job", "started", reader=args.reader, fixture=args.fixture, raster_sha256=image_hash,
               tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               transfer="not_started", refresh="not_started", camera="unverified")
        try:
            candidates = [r for r in readers() if str(r) == args.reader]
            if len(candidates) != 1:
                raise BenchError("Exact reader name must identify one device")
            connection = candidates[0].createConnection()
            connection.connect(mode=SCARD_SHARE_EXCLUSIVE, disposition=SCARD_LEAVE_CARD)
            try:
                def exchange(command):
                    data, sw1, sw2 = connection.transmit(list(command))
                    status = f"{sw1:02x}{sw2:02x}"
                    record("protocol", "response", ins=f"{command[1]:02x}", sw=status)
                    if status != "9000":
                        raise BenchError(f"INS {command[1]:02x} returned {status}")
                    return bytes(data)
                run_job(exchange, record, frames, ident, geometry,
                        authenticate_for_info=args.authenticate_for_info)
            finally:
                connection.disconnect()
        except (Exception, KeyboardInterrupt) as e:
            record("job", "interrupted", reason=str(e) or type(e).__name__)
            raise
        record("job", "session_ended", camera="unverified")


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as err:
        print(f"Bench session stopped: {err or type(err).__name__}", file=sys.stderr)
        sys.exit(1)
