# Current status

Baseline date: November 4, 2026.

| Area | State | Evidence or next action |
| :--- | :--- | :--- |
| Requirements | Initial baseline recorded | Confirm label orientation, dwell time and supply constraints |
| Label identity | Santek EZ Sign 2.9 inch four color | Exact physical unit metadata still needed |
| Chip marking | User reports FMSC and 419J0G or 419JOG | Photo and exact silicon identification pending |
| Protocol | Independent EZ Sign implementation documents Type A, ISO 14443 part 4 and proprietary APDUs | Verify against our physical label and recover our own prior findings |
| Reader choice | PN5180 and ST25R3916B candidates | Compare software support, RF control and PA integration |
| Electrical target | Historical six sheet RevA0 concept available | Amplifier and selector are not completed circuits |
| KiCad | Not started in this repository | Implement native projects after circuit review |
| Firmware | Not implemented in this repository | Establish reader transport and label profile |
| Prototype and range | Not measured | Full refresh coverage mapping required |
| Manufacturing | Not released | Circuit, BOM, ERC and DRC gates pending |

Chris reports that Santek software was previously reverse engineered to develop our own writer. That work is project history, but the completed implementation and captures have not yet been located in the sources accessible during initialization. The older Liberty-Chris/Balto main code is a simulation scaffold and must not be used to deny the existence of later research.

The initial documentation package described the exact air protocol as unknown. Later research located an independent implementation for the actual EZ Sign product family. Current protocol documentation supersedes that broad uncertainty while preserving the distinction between external evidence and validation on our unit.
