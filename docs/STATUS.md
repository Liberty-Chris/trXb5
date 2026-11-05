# Current status

**November 5, 2026. Rev A1 is ready for electrical review.** The next physical milestone is an identified 2.9-inch label on a direct reader, with its factory configuration preserved. Start with the [commissioning sequence and design limits](validation/REV_A1.md).

| Area | Current evidence | Next gate |
| --- | --- | --- |
| Vendor writer | Static extraction found PC/SC, LZO and three command literals in the NFC payload. The 1.2.6 archive uses a serial application. [Evidence and hashes](research/VENDOR-PAYLOAD.md) | Capture an actual transaction on this unit |
| Reader and host | PN5180A0HN/C4E and 3.3 V host harness. A Linux SPI probe reads product, firmware and EEPROM version words. | Run on a Pi and an actual reader |
| Controller | Ten KiCad sheets, BOM and 162 placed footprints. KiCad ERC passes. Preliminary board has 441 unrouted connections. | Prove isolation sequencing and usable RX level before routing |
| Antenna | Routed 150 × 150 mm PCB. ERC, DRC and board-to-schematic parity pass. | Measure loop impedance and retune with actual coax, ferrite and metalwork |
| Label bench | PC/SC commands enforce physical ID, geometry and raster size before transfer. The journal distinguishes transfer, refresh and camera evidence. | Capture identity, completion and a camera image on the same label |
| Supply and integration | Raspberry Pi likely, ESP32 possible. Supply is adaptable. Panel size confirmed. | Measure installed cable, clearance, orientation, dwell and power |
| Release | Electrical review files only | Controller routing, procurement and land-pattern review, component stress measurements, cavity coverage and build approval remain open |

An actual label refresh, maximum range, transferable operating power and an approved fabrication package remain outstanding.
