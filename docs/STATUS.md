# Current status

**Rev A3 is the current factory-assembly prototype.** Two controllers and ten panels fit the dated JLCPCB public inventory with an assembly reserve. The controller has 185 purchased placements and each panel has eight. Both designs pass ERC, DRC and schematic parity. [Upload packages](../releases/RevA3/) · [Raw reports and per-part sourcing](validation/RevA3/)

The controller supports one primary path, four optional SMA paths, and direct or 24 V PA commissioning. The host uses 3.3 V logic, with Raspberry Pi as the first integration target and ESP32 still an option. The PC/SC bench tool checks label identity, transfer acknowledgements and a qualified refresh status. The Pi tool reads PN5180 version registers. The recovered vendor software and its static evidence remain available for protocol comparison. [Vendor evidence](research/VENDOR-PAYLOAD.md)

The next milestone is one assembled controller and panel into a dummy load, followed by a factory-configuration-preserving, camera-confirmed close-range refresh. Supply-loss timing, RF output, receiver recovery, the custom SPI image transport, installed coax/cavity tuning and 305 mm coverage still require hardware. [Electrical decisions](validation/REV_A3.md) · [Acceptance sequence](validation/COMMISSION_A3.md)
