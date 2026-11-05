# trXb5

Custom 13.56 MHz NFC reader and writer with one primary loop and four optional external antenna panels for ROACH RXVault.

The system identifies a batteryless electronic paper label, transfers an image, maintains power through display refresh and reports verification evidence to the vending platform. Camera verification establishes the visible result.

Development baseline established November 4, 2026. The project currently contains requirements, protocol research, a preliminary electrical target and a plan for native KiCad implementation. No native KiCad design, completed amplifier circuit, manufactured prototype or demonstrated extended range is included yet.

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

PN5180 and ST25R3916B are reader candidates. The original A0 target uses ST25R3916B; an independent implementation specifically supports EZ Sign through PN5180. Reader selection has not been finalized.

The current documents supersede outdated protocol uncertainty in the original A0 package. The package remains preserved as a historical target. Read its correction notice before implementation.

No project license has been selected. External references retain their own licenses and are linked rather than copied. See [contribution guidance](CONTRIBUTING.md).
