# Rev A2 prototype submission

Order one controller design and one panel design as separate jobs. An identical panel can serve the primary port or any of the four external ports. Use the Gerber ZIP for board fabrication and the two CSV files for optional top-side assembly. Each ZIP contains the loose files from its adjacent fabrication directory. Keep the complete engineering BOM and the manual population list with the build.

| Job | Fabrication ZIP | Assembly BOM | Placement file | Order options |
| --- | --- | --- | --- | --- |
| Controller | [Gerbers and drills](controller/Controller_A2-JLC-Gerbers.zip) | [JLC BOM](controller/assembly/Controller_A2-JLC-BOM.csv) | [JLC CPL](controller/assembly/Controller_A2-JLC-CPL.csv) | [Controller order](controller/ORDER.md) |
| 150 mm panel | [Gerbers and drills](panel/Panel_A2-JLC-Gerbers.zip) | [JLC BOM](panel/assembly/Panel_A2-JLC-BOM.csv) | [JLC CPL](panel/assembly/Panel_A2-JLC-CPL.csv) | [Panel order](panel/ORDER.md) |

Each assembly directory includes a printable drawing, full BOM and separate manual/DNP list. Buy the listed exact MPNs for local placement. Some catalogued parts require preorder or consignment. Resolve availability in the quote before paying. Component references in the CPL match the factory-populated BOM. The positions use millimetres and the same absolute coordinate origin as the Gerbers and drills. Negative Y is expected.

The [manifest](manifest.json) identifies the source commit and SHA-256 digests. Native input hashes use LF line endings. Output hashes cover the delivered bytes, including timestamps supplied by KiCad. Archive members use fixed timestamps. Run the commands below from the repository root. A rebuild from the same source can have different document and plot timestamps.

```sh
python -m pip install -r software/requirements-bench.txt gerbonara==1.6.3
python tools/release_a2.py verify
python tools/release_a2.py build --source <source_commit_from_manifest> --cli kicad-cli
python tools/inspect_a2_cam.py --preview tmp/cam
```

[Electrical review](../../docs/validation/REV_A2.md) · [Raw ERC, DRC, parity and offline test records](../../docs/validation/RevA2/) · [Commissioning and acceptance](../../docs/validation/COMMISSION_A2.md)
