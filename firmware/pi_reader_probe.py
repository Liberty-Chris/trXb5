"""Bring up the PN5180 over the A1 isolated SPI port. Only READ_EEPROM is sent."""
import argparse
from datetime import datetime, timezone
import json
import sys
import time
from contextlib import contextmanager, nullcontext


# GPIO line offsets on the chip serving the Pi's 40-pin header.
ADDRESS = (12, 13, 16)
SET, CLEAR, RUN = 17, 27, 22
FEEDBACK = (4, 18, 19, 20, 21)
ARM = 26


@contextmanager
def selected_port(port, drive, sense, sleep=time.sleep):
    """Commissioning only. Keep commands low at rest and release RUN on every exit."""
    def positions():
        return sum(int(sense(pin)) << index for index, pin in enumerate(FEEDBACK))

    def pulse(index, command):
        for bit, pin in enumerate(ADDRESS):
            drive(pin, bool(index & (1 << bit)))
        sleep(.005)
        if sense(ARM):
            raise RuntimeError("ARM rose before a relay pulse")
        drive(command, True)
        try:
            sleep(.020)
        finally:
            drive(command, False)
        sleep(.020)

    try:
        drive(RUN, False)
        drive(SET, False)
        drive(CLEAR, False)
        # Allow decay before requesting a pulse. Hardware TP301 gates the decoder.
        sleep(.5)
        if sense(ARM):
            raise RuntimeError("Reader remained armed with RUN low")
        seen = positions()
        wanted = 1 << port
        for index in range(len(FEEDBACK)):
            mask = 1 << index
            if seen & mask and mask != wanted:
                pulse(index, CLEAR)
                seen &= ~mask
                if positions() != seen:
                    raise RuntimeError("Port did not reset or another position changed")
        if seen != wanted:
            pulse(port, SET)
        if positions() != wanted:
            raise RuntimeError("Incorrect port feedback before RUN")
        drive(RUN, True)
        sleep(.15)
        if not sense(ARM) or positions() != wanted:
            raise RuntimeError("ARM or port feedback differs from the requested state")
        yield
    finally:
        drive(RUN, False)
        drive(SET, False)
        drive(CLEAR, False)


def version_bytes(transfer, chip_select, busy, timeout=.25):
    def wait(level):
        until = time.monotonic() + timeout
        while busy() != level:
            if time.monotonic() >= until:
                raise TimeoutError(f"Timed out waiting for BUSY={int(level)}")
            time.sleep(.0001)

    def frame(data):
        wait(False)
        chip_select(False)
        try:
            result = bytes(transfer(data))
            wait(True)
        finally:
            chip_select(True)
        wait(False)
        return result

    frame([0x07, 0x10, 6])
    versions = frame([0xff]*6)
    if len(versions) != 6 or any(versions[i:i+2] in (b"\x00\x00", b"\xff\xff") for i in (0, 2, 4)):
        raise ValueError("Unusable version words from reader")
    return versions


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gpiochip", required=True, help="Linux GPIO chip for the 40-pin header")
    p.add_argument("--fixture", required=True)
    p.add_argument("--port", type=int, choices=range(5),
                   help="Select and arm port 0–4 using the qualified J4/J5 harness")
    args = p.parse_args()
    import gpiod
    import spidev
    from gpiod.line import Direction, Value
    nss, reset, busy = 5, 6, 25  # GPIO line offsets on the header controller, not physical pin numbers
    config = {
            nss: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE),
            reset: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
            busy: gpiod.LineSettings(direction=Direction.INPUT)}
    if args.port is not None:
        config[(*ADDRESS, SET, CLEAR, RUN)] = gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE)
        config[(*FEEDBACK, ARM)] = gpiod.LineSettings(direction=Direction.INPUT)
    with gpiod.request_lines(args.gpiochip, consumer="trx-a1-bench", config=config) as lines:
        def drive(pin, high):
            lines.set_value(pin, Value.ACTIVE if high else Value.INACTIVE)
        def sense(pin):
            return lines.get_value(pin) == Value.ACTIVE
        spi = spidev.SpiDev()
        try:
            spi.open(0, 0)
            spi.mode = 0
            spi.max_speed_hz = 500_000
            # Hardware CE0 is unused on the bench harness. GPIO5 controls the chip itself.
            selection = selected_port(args.port, drive, sense) if args.port is not None else nullcontext()
            with selection:
                time.sleep(.020)
                drive(reset, True)
                try:
                    time.sleep(.020)
                    versions = version_bytes(spi.xfer2, lambda high: drive(nss, high), lambda: sense(busy))
                finally:
                    drive(reset, False)
        finally:
            lines.set_value(reset, Value.INACTIVE)
            spi.close()
    print(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), fixture=args.fixture, port=args.port,
                          product_le=versions[:2].hex(), firmware_le=versions[2:4].hex(),
                          eeprom_le=versions[4:].hex(), label_identity="unobserved",
                          transfer="not_started", refresh="not_started", camera="unverified")))


if __name__ == "__main__":
    try:
        main()
    except (ImportError, OSError, ValueError, RuntimeError) as error:
        print(f"Probe stopped: {error}", file=sys.stderr)
        sys.exit(1)
