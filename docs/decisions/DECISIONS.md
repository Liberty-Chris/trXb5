# Decision log

| ID | Decision | State | Rationale |
| :--- | :--- | :--- | :--- |
| D01 | One primary loop plus four optional external loops | Accepted target | Variable product position inside cavity |
| D02 | Select one antenna at a time | Accepted target | Maintain a defined RF path during update |
| D03 | SMA connectors for prototype external panels | Accepted target | Repeatable bench connection |
| D04 | 150 × 150 mm PCB loop outline | Accepted for A1 | Owner specified the size for mounting flexibility |
| D05 | Coarse capacitor selection and RF trimmer adjustment | Accepted target | Bench tuning access |
| D06 | Manual tuning for coax baseline | Accepted baseline | ST AN5592 cable topology does not supply direct AAT |
| D07 | PN5180A0HN/C4E | Selected for A1 | [Reader comparison and protocol constraints](READER-A1.md) |
| D08 | THS3491 linear stage on separate ±15 V rails | Bench candidate | Begin with a dummy load and measure modulation, receive margin and heating |
| D09 | Five G6KU-2F-RF DC5 latching relays with 49.9 Ω damping | Selected for A1 | Second pole reports position. Separate normally open G6K relay disconnects both reader RF paths at rest |
| D10 | Raspberry Pi likely, ESP32 possible | 3.3 V harness chosen | J3, J4 and J5 carry SPI, commands and feedback. The owner permits a separate supply |
| D11 | Use existing metal cavity, do not add shielding by default | Baseline | Measure interference and metal loading first |
| D12 | License | Open | Owner has not selected a license |

Change a decision by recording the new evidence, affected hardware revision and consequences. Do not silently convert a provisional target into a verified fact.
