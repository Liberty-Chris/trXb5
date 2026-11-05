# Current status

**Rev A2 is ready for engineering prototype fabrication.** The routed controller and 150 mm panel each pass ERC and DRC with zero open connections and zero schematic mismatches. The two submission ZIPs, numbered assembly drawings, exact BOMs, CPLs and manual population lists are in the [release](../releases/RevA2/). [KiCad reports, commands and test evidence](validation/RevA2/)

The controller supports one primary path, four optional SMA paths, and direct or 24 V PA commissioning. The host uses 3.3 V logic, with Raspberry Pi as the first integration target and ESP32 still an option. The PC/SC bench tool checks label identity, transfer acknowledgements and a qualified refresh status. The Pi tool reads PN5180 version registers. The recovered vendor software and its static evidence remain available for protocol comparison. [Vendor evidence](research/VENDOR-PAYLOAD.md)

The next milestone is one assembled controller and panel into a dummy load, followed by a factory-configuration-preserving, camera-confirmed close-range refresh. Supply-loss timing, RF output, receiver recovery, the custom SPI image transport, installed coax/cavity tuning and 305 mm coverage still require hardware. [Electrical decisions](validation/REV_A2.md) · [Acceptance sequence](validation/COMMISSION_A2.md)
