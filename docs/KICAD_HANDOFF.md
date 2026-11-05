# Desktop implementation handoff

Develop trXb5 into a complete custom NFC reader and writer for ROACH RXVault using native KiCad projects. Read AGENTS.md, requirements, current status, protocol evidence, architecture and the historical A0 correction notice before editing.

Inspect the local environment and existing files. Preserve any new user work. Use this repository as the source of truth and commit coherent changes with validation notes. Make routine implementation choices autonomously. Ask only for information that materially blocks the circuit or mechanical design.

Recover our prior Santek reverse engineering artifacts when available and use the documented independent EZ Sign implementation as a concrete protocol reference. Do not dismiss prior work because the older Balto main contains a simulation. Confirm the physical label and preserve its factory display configuration.

Evaluate PN5180 and ST25R3916B using protocol support, raw exchange control, WTX and chaining behavior, RF control, receive feedback and amplifier integration. Record and justify the selected reader before fixing the native schematic. Verify every pin and package against official documentation.

Implement one primary disconnectable loop and four optional SMA panels, one active at a time. Use initial 150 × 150 mm panel outlines while retaining substitution capability. Provide coarse capacitor selection and fine rated RF trimmers. Model cable, ferrite and metal cavity loading. Do not claim the twelve inch goal is achieved from calculation alone.

Complete actual circuits for power protection, host interface, reader supply bypassing, crystal, RF matching, optional PA with direct bypass, protected receive sampling, antenna switching, coil drivers, hardware RF shutdown, fault handling and measurement access. Choose real components and calculate ratings. Do not leave generic PA or interlock boxes as a finished schematic.

The amplifier remains in scope even though direct drive is the commissioning baseline. Preserve NFC modulation and receive sensitivity. Define its supply and output envelope from electrical design and tests rather than assuming a wattage. Ensure direct and amplified links cannot drive the bus together.

Engineer true RF shutdown and no backpower behavior. Never switch antenna contacts while RF is active. Keep a selected path through transfer and refresh. Evaluate inactive loop coupling and relay lifetime. Do not infer panel control wiring through an SMA cable.

Create hierarchical schematics, verified footprints and self contained custom libraries. Complete circuit review before final routing. Design controller and antenna PCBs with appropriate RF geometry, return paths, mounting access and tuning access. Resolve ERC and DRC or document justified exceptions. Clearly distinguish calculated starting values from measured final RF values.

Provide firmware or bench tooling for the selected host architecture. Implement actual label writing only from supported protocol evidence. Expose separate identity, transfer, refresh and camera evidence states. Never report simulation output as real hardware success.

Deliver native sources, schematic PDFs, exact BOM, assembly data and prototype Gerbers and drills once electrical review permits fabrication. Follow the roadmap and bench plan. If physical hardware prevents completion, finish independent design work and state the exact missing test and acceptance criterion. Never describe an untested prototype as a validated production device.
