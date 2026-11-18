# trXb5

Custom 13.56 MHz NFC reader and writer with one primary loop and four optional external antenna panels for ROACH RXVault.

The system identifies a batteryless electronic paper label, transfers an image, maintains power through display refresh and reports verification evidence to the vending platform. Camera verification establishes the visible result.

Rev A3 provides a factory-populated [controller](hardware/controller/RevA3/Controller_A3.kicad_pro) and [150 mm panel](hardware/antenna/RevA3/Panel_A3.kicad_pro). The [JLCPCB submissions](releases/RevA3/) include the SMT and through-hole components. Start with the [sourcing and electrical review](docs/validation/REV_A3.md) and [physical commissioning procedure](docs/validation/COMMISSION_A3.md).

## Start here

| Resource | Purpose |
| :--- | :--- |
| [Current status](docs/STATUS.md) | What exists and what remains open |
| [Requirements](docs/REQUIREMENTS.md) | Agreed scope and acceptance targets |
| [Architecture](docs/ARCHITECTURE.md) | Reader, amplifier, selector and antenna boundaries |
| [Protocol evidence](docs/research/PROTOCOL.md) | Santek evidence and implementation leads |
| [Observed label](docs/research/LABEL.md) | Display identity and reported chip marking |
| [Evidence register](docs/research/EVIDENCE.csv) | Facts, inferences and missing validation |
| [KiCad handoff](docs/KICAD_HANDOFF.md) | Desktop implementation instructions |
| [Development plan](docs/ROADMAP.md) | Stages and release criteria |
| [Bench validation](docs/validation/PLAN.md) | Electrical and full refresh testing |
| [Decision log](docs/decisions/DECISIONS.md) | Accepted targets and pending decisions |
| [Original A0 package](hardware/reference/RevA0/START_HERE.md) | Historical schematic baseline with correction notice |
| [Original schematic PDF](hardware/reference/RevA0/ROACH_NFC_RevA0_Schematic.pdf) | Six preliminary review sheets |

The starting geometry is a roughly 457 mm cube metal cavity and 150 × 150 mm PCB loop panels. A maximum antenna to label distance of roughly 305 mm is a development goal, not a proven operating range. Antenna dimensions and RF output power remain subject to engineering and testing.

The A1 reader is PN5180A0HN/C4E. Raspberry Pi is the probable host and the controller exposes 3.3 V SPI and GPIO for either a Pi or an ESP32 implementation. [Reader selection](docs/decisions/READER-A1.md)

The current documents supersede outdated protocol uncertainty in the original A0 package. The package remains preserved as a historical target. Read its correction notice before implementation.

The owner has yet to select a project license. Bundled KiCad footprints retain their [library terms](hardware/LIBRARY-NOTICES.md). See [contribution guidance](CONTRIBUTING.md).

## Interactive antenna model

A separate wire loop mechanical prototype is available in the [Bluejacket RX antenna 3D viewer](web/nfc-viewer/). It shows the 1.7 mm groove pitch version with 1.02 mm wire, integrated housing and representative electronics. This is a mechanical visualization, not the Rev A3 PCB release or validated RF operation. [Hosting and model notes](docs/MECHANICAL_VIEWER.md)

