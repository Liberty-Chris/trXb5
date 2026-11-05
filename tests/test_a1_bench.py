"""Offline tests. The transcript here is synthetic, never a physical bench record."""
import hashlib
import math
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'software'), str(ROOT/'firmware')]
import ezsign_bench as bench
import panel_match as match
from pi_reader_probe import version_bytes
import pi_reader_probe as probe

INFO = bytes.fromhex("A00700070001000128 C10412345678")
RASTER = b"\x55"*9472


class LabelTests(unittest.TestCase):
    def test_identify_never_authenticates(self):
        exchange = Mock(side_effect=[b"", INFO])
        bench.run_job(exchange, Mock())
        self.assertEqual([x.args[0] for x in exchange.call_args_list], [bench.SELECT, bench.INFO])

    def test_bad_info_and_torn_tlvs(self):
        for data in [INFO[:-1], INFO+b"\xc0", INFO+INFO, INFO.replace(b"\x07\x00\x01", b"\x09\x00\x01")]:
            with self.subTest(data=data), self.assertRaises(bench.BenchError):
                bench.metadata(data)

    def test_authenticated_info_does_not_write_image(self):
        exchange = Mock(side_effect=[b"", b"", INFO])
        bench.run_job(exchange, Mock(), authenticate_for_info=True)
        self.assertEqual([x.args[0] for x in exchange.call_args_list],
                         [bench.SELECT, bench.AUTH, bench.INFO])

    def test_identity_gate_precedes_auth(self):
        exchange = Mock(side_effect=[b"", INFO])
        with self.assertRaises(bench.BenchError):
            bench.run_job(exchange, Mock(), [b"testing"], "00000000", (296, 128))
        self.assertEqual(exchange.call_count, 2)

    def test_image_block_offsets_and_lzo(self):
        import lzokay
        packets = bench.image_commands(RASTER)
        restored = bytearray()
        for i, packet in enumerate(packets):
            self.assertEqual(packet[:7], bytes([240,211,0,1,len(packet)-5,i,0]))
            size = min(2000, len(RASTER)-len(restored))
            restored.extend(lzokay.decompress(packet[7:], size))
        self.assertEqual(len(packets), 5)
        self.assertEqual(hashlib.sha256(restored).digest(), hashlib.sha256(RASTER).digest())
        with self.assertRaises(bench.BenchError):
            bench.image_commands(random.Random(39).randbytes(9472))

    def check_refresh(self, replies, expected, *, deadline=5, minimum_field_seconds=0):
        now = 0
        states = []
        polls = []

        def sleep(seconds):
            nonlocal now
            now += seconds

        remaining = iter(replies)

        def exchange(apdu):
            if apdu == bench.INFO:
                return INFO
            if apdu != bench.POLL:
                return b""
            polls.append(now)
            reply = next(remaining, replies[-1])
            if isinstance(reply, Exception):
                raise reply
            return reply

        def run():
            bench.run_job(exchange, lambda stage, state, **_: states.append((stage, state)),
                          [b"frame"], "12345678", (296, 128), sleep=sleep,
                          monotonic=lambda: now, refresh_seconds=deadline,
                          minimum_field_seconds=minimum_field_seconds)

        if expected == "complete":
            run()
        else:
            with self.assertRaises((bench.BenchError, OSError)):
                run()
            self.assertGreaterEqual(now, deadline)
            self.assertNotIn(("refresh", "complete"), states)
        self.assertIn(("transfer", "acknowledged"), states)
        self.assertIn(("refresh", "accepted"), states)
        self.assertEqual(states[-1], ("refresh", expected))
        return len(polls)

    def test_first_idle_and_never_busy(self):
        self.check_refresh([bytes([0])], "unknown")

    def test_observed_busy_then_stable_idle(self):
        self.assertEqual(self.check_refresh([bytes([x]) for x in (0, 1, 0, 0, 0)], "complete"), 5)

    def test_transient_idle_restarts_qualification(self):
        sequence = (1, 0, 0, 1, 0, 0, 0)
        self.assertEqual(self.check_refresh([bytes([x]) for x in sequence], "complete"), 7)

    def test_busy_or_premature_idle_at_timeout(self):
        self.check_refresh([bytes([1]), bytes([0])], "unknown", deadline=5,
                           minimum_field_seconds=30)
        for replies in ([bytes([1])], [bytes([1]), bytes([0])]):
            with self.subTest(replies=replies):
                self.check_refresh(replies, "unknown", deadline=1.4)

    def test_lost_or_invalid_poll_holds_field_window(self):
        for failure in (OSError("reader removed"), bytes([2]), b""):
            with self.subTest(failure=failure):
                self.check_refresh([bytes([1]), failure], "unknown")

    def test_lost_transfer_ack_does_not_repeat_block(self):
        exchange = Mock(side_effect=[b"", INFO, b"", OSError("link lost")])
        events = Mock()
        with self.assertRaises(OSError):
            bench.run_job(exchange, events, [b"frame"], "12345678", (296,128))
        self.assertEqual(exchange.call_count, 4)
        events.assert_any_call("transfer", "acknowledgement_unknown", block=0)


class ElectricalTests(unittest.TestCase):
    def test_selector_verifies_contacts_and_releases_run_on_probe_failure(self):
        lines = {}
        contacts = {0, 4}
        pulses = []

        def drive(pin, high):
            lines[pin] = high
            if high and pin in (probe.SET, probe.CLEAR):
                self.assertFalse(lines[probe.RUN])
                index = sum(int(lines[p]) << bit for bit,p in enumerate(probe.ADDRESS))
                pulses.append((pin, index))
                (contacts.add if pin == probe.SET else contacts.discard)(index)

        def sense(pin):
            if pin == probe.ARM:
                return lines[probe.RUN] and len(contacts) == 1
            return probe.FEEDBACK.index(pin) in contacts

        with self.assertRaises(TimeoutError):
            with probe.selected_port(2, drive, sense, sleep=lambda _: None):
                self.assertEqual(contacts, {2})
                raise TimeoutError()
        self.assertEqual(pulses, [(probe.CLEAR, 0), (probe.CLEAR, 4), (probe.SET, 2)])
        self.assertFalse(lines[probe.RUN])

    def test_selector_refuses_missing_feedback_before_run(self):
        drive = Mock()
        with self.assertRaises(RuntimeError):
            with probe.selected_port(0, drive, lambda _: False, sleep=lambda _: None):
                self.fail("Missing feedback permitted ARM")
        self.assertNotIn((probe.RUN, True), [call.args for call in drive.call_args_list])

    def test_network_and_reference_planes(self):
        w = 2*math.pi*13.56e6
        loop = 3.2+1j*w*.64e-6
        cs, cp = match.match(loop, w, 50)
        self.assertAlmostEqual(abs(match.panel_z(loop,w,cs,cp)-50), 0)
        self.assertAlmostEqual(abs(match.cable_z(50,13.56e6,1,.66,.2,50)-50),0)
        result = match.cable_z(25,13.56e6,.66*299792458/(4*13.56e6),.66,0,50)
        self.assertAlmostEqual(abs(result-100),0)
        z = match.reflected_impedance(w,.64e-6,[(.1,.4e-6,2+1j*w*.4e-6)])
        self.assertGreater(z.real,0)
        self.assertLess(z.imag,0)

    def test_spi_transaction_is_read_only(self):
        transfers = Mock(side_effect=[bytes(3),bytes.fromhex("010001040001")])
        cs = Mock()
        self.assertEqual(version_bytes(transfers, cs, Mock(side_effect=[False, True, False]*2)),
                         bytes.fromhex("010001040001"))
        self.assertEqual([x.args[0] for x in transfers.call_args_list],[[7,16,6],[255]*6])
        self.assertEqual([x.args[0] for x in cs.call_args_list],[False,True,False,True])
        with self.assertRaises(TimeoutError):
            version_bytes(transfers, cs, lambda: True, timeout=0)
