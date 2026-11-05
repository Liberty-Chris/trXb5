# Rev A1 controller

Open [Rev A2](RevA2/Controller_A2.kicad_pro) for the routed four-layer controller. [Fabrication and assembly](../../releases/RevA2/controller/ORDER.md) · [Electrical review](../../docs/validation/REV_A2.md)

Open [Controller_A1.kicad_pro](RevA1/Controller_A1.kicad_pro) in KiCad 10. The [schematic PDF](RevA1/Controller_A1.pdf) has ten pages. The [review BOM](RevA1/BOM.csv) lists fit quantities and MPNs. The 160 × 112 mm, four-layer board is a placement study with 441 unrouted connections. Its bottom and inner layers are available for the return planes and controlled-impedance layout after electrical review.

The PCB places each latching relay by its SMA and damping resistor. The crystal, bypass parts and differential network surround the reader. The PA has its own supply and patch ports. K200 breaks both reader RF paths at rest. The [engineering record](../../docs/validation/REV_A1.md) lists the shutdown and receiver measurements required before routing.
