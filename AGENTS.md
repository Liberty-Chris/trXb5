# Project instructions

Read README.md, docs/STATUS.md, docs/REQUIREMENTS.md, docs/research/PROTOCOL.md and docs/KICAD_HANDOFF.md before changing hardware or firmware.

This is the canonical repository for the trXb5 PCB initiative. Preserve user requirements and distinguish source documented behavior, user observations, calculations, simulations and measured results. Never present theoretical range or simulated operation as a successful label refresh.

Use official datasheets for pin mappings and electrical limits. Verify the exact orderable component and package. Do not infer display compatibility solely from generic NFC support. Keep native KiCad projects self contained with their libraries and relative paths. No native KiCad project exists at initialization.

The original RevA0 package is historical and must not be silently rewritten. Current documents and its correction notice take precedence. New electrical revisions belong under hardware/controller and hardware/antenna with explicit revision metadata.

Do not fabricate RF component values, amplifier performance, calibration, successful ERC or DRC, bench results or evidence. Record justified ERC and DRC exceptions. Resolve hardware shutdown and receive feedback before declaring the circuit complete. Preserve original label configuration during protocol investigation unless a deliberate documented test requires changing it.

Maintain a direct reader test path. External PA integration remains in scope. Never switch antennas while RF is active or interrupt field power during a display refresh. Validate inactive antenna coupling. Automatic tuning through the proposed coax topology is not assumed.

Make routine reversible changes without repeatedly asking for confirmation. Keep documentation and status current. Commit coherent changes with validation notes. Do not commit credentials, vendor installers, unrelated vending SDKs, caches or misleading production releases. Do not introduce a license without the owner's decision.

A fabrication package requires a reviewed complete circuit, verified footprints, an electrically justified BOM and recorded ERC and DRC outcomes. A validated operating release additionally requires real label and cavity measurements. Identify any physical test that cannot be completed in the current environment.
