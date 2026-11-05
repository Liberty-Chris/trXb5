# Santek evidence recovered from the desktop

The local ROACH development tree contains two distinct lines of work. These identifiers allow another engineer to inspect the same objects without redistributing vendor software.

| Source | Identifier | What it establishes |
| --- | --- | --- |
| ROACH eINK R&D checkout, `Roach Balto Development/eINK_Writing_Development` | `Roach-LLC/eINK_Writing_Development@73ec23dca9f1bdc39ccd311e4d0d336a6948f753` | The local refs point to the initial README. A local unreachable-object scan returned no further objects. The remote returned HTTP 404 with the available account. Later work could exist elsewhere. |
| Local Liberty-Chris/Balto history | [interoperability probe](https://github.com/Liberty-Chris/Balto/commit/aa08bab292f9072cba484c641836257921377136), [PN532 bench](https://github.com/Liberty-Chris/Balto/commit/28fa1acae3111ce264dc75eb0934cce54cbe071a) | The earlier team analyzed the installer imports and strings, wrote an enumeration probe and documented a discovery bench. The probe deliberately avoids transmitting. |
| Balto research objects | `research/imports-analysis.md` blob `3401666a41cccf3b321d681a1be7ac317f5cc11b`, `src/protocol_probe.py` blob `8a66273929a84fd9016a0e301ee0b4ff692d3d1b` at commit `94c197877ec7454a67075d04b825e05a405aff6a` | Recoverable source and analysis for the transport investigation. |
| Vendor download, `EZ Sign(TM) NFC-v1.0.2/NFC-writer.exe` | 22,795,128 bytes, SHA-256 `ab628d3b6b759dcf9dc576fa4a6774a56512f3a4f17c43cc5e34a0756ebb0e80` | Fingerprints the installer. No installation or execution was required. |
| Local Balto main, `src/writer.py` | SHA-256 `bea212671569b17b9accd5df7ac98bde3f9169a308125e8c161ffddf539c6270` | This revision simulates writes. The subsequently reported working writer and on-air traces remain unlocated. |

The owner subsequently identified the original vendor archives in Balto. [Payload hashes and command offsets](VENDOR-PAYLOAD.md) distinguish their NFC and serial transports. The next evidence needed is the later team writer commit or a trace of one known-good update. Record a physical unit ID, board and flex photos, reader, orientation, image hash and hardware/software revisions. Keep UID and image data in the controlled bench record. Preserve the factory display configuration.
