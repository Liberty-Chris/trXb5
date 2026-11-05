# Requirements baseline

| ID | Requirement | Status |
| :--- | :--- | :--- |
| R01 | Read identity, write display image and check response for the same label | Required |
| R02 | Supply NFC field power for the entire required transfer and refresh interval | Required |
| R03 | Expose evidence for external camera verification of the visible image | Required |
| R04 | One primary antenna plus up to four external antennas | Required |
| R05 | Select one antenna at a time and retain selection throughout an update | Required |
| R06 | Flat 150 × 150 mm PCB loop panels for interchangeable mounting locations | Owner confirmed November 5, 2026 |
| R07 | SMA external connections and a disconnectable primary loop | Prototype target |
| R08 | Coarse capacitor selection and fine RF trimmer adjustments on each panel | Required |
| R09 | Adjustable RF drive and an external amplifier development path | Required development scope |
| R10 | Direct reader bypass for baseline testing | Required |
| R11 | Work inside a roughly 457 × 457 × 457 mm metal cavity | Working mechanical assumption |
| R12 | Seek operation up to roughly 305 mm from an antenna with variable product placement | Unproven range goal |
| R13 | Validate close positions as well as distant positions | Required |
| R14 | No antenna switching with RF active and a defined default off state | Required |
| R15 | Native KiCad controller and panel projects with self contained libraries | Required deliverable |

The current label is nominally SE0290C1, 296 × 128 pixels and four colors. Validate the exact physical unit before fixing firmware parameters.

The owner expects a Raspberry Pi host, with ESP32 as an option. Power can be adapted to the circuit. A1 uses a 5 V bench input and a separate split supply for PA characterization. Production supply capacity, cable runs, mounting clearance, product orientation, contents, motion and allowable pause duration remain open. Four-color refresh takes tens of seconds in referenced implementations, so motion and dwell time materially affect feasibility.

Readback means identity and protocol response verification unless true image memory readback is demonstrated. Do not promise pixel readback support. Camera verification is the separate visible image check.
