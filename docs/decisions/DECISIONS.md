# Decision log

| ID | Decision | State | Rationale |
| :--- | :--- | :--- | :--- |
| D01 | One primary loop plus four optional external loops | Accepted target | Variable product position inside cavity |
| D02 | Select one antenna at a time | Accepted target | Maintain a defined RF path during update |
| D03 | SMA connectors for prototype external panels | Accepted target | Repeatable bench connection |
| D04 | Initial 150 × 150 mm PCB loop outline | Provisional | Practical prototype geometry; range unproven |
| D05 | Coarse capacitor selection and RF trimmer adjustment | Accepted target | Bench tuning access |
| D06 | Manual tuning for coax baseline | Accepted baseline | ST AN5592 cable topology does not supply direct AAT |
| D07 | Reader selection | Open | Compare PN5180 and ST25R3916B against actual protocol and PA needs |
| D08 | PA topology, power and supply | Open | Modulation and receive validation required |
| D09 | Five SPDT RF relays and damping loads | Provisional | Needs part selection, lifetime and coupling tests |
| D10 | Host connection and MCU | Open | A0 header is a proposed interface, not a standard Pi header |
| D11 | Use existing metal cavity, do not add shielding by default | Baseline | Measure interference and metal loading first |
| D12 | License | Open | Owner has not selected a license |

Change a decision by recording the new evidence, affected hardware revision and consequences. Do not silently convert a provisional target into a verified fact.
