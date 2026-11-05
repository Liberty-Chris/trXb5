# Rev A3 JLCPCB prototype submission

| Job | Download and extract | Fabrication upload | Assembly uploads | Settings |
|---|---|---|---|---|
| Two controllers | [Controller package](controller/Controller_A3-JLC-submission.zip) | [Gerbers and drills](controller/Controller_A3-JLC-Gerbers.zip) | [BOM](controller/assembly/Controller_A3-JLC-BOM.csv) · [CPL](controller/assembly/Controller_A3-JLC-CPL.csv) | [Controller order](controller/ORDER.md) |
| Ten panels | [Panel package](panel/Panel_A3-JLC-submission.zip) | [Gerbers and drills](panel/Panel_A3-JLC-Gerbers.zip) | [BOM](panel/assembly/Panel_A3-JLC-BOM.csv) · [CPL](panel/assembly/Panel_A3-JLC-CPL.csv) | [Panel order](panel/ORDER.md) |

The outer archives also contain schematic and numbered assembly PDFs, the fabricated-feature list and SHA256SUMS.txt. Use the inner Gerber ZIP for PCB upload. Use the two CSVs for top-side Standard PCBA and retain the factory through-hole lines. Match every reference before releasing either job. Confirm current matching stock in the job when ordering. The package covers board-level population. External cabling, power, host, tuning and commissioning are installation steps. [Stock and attrition evidence](../../docs/validation/RevA3/sourcing.csv) · [Validation](../../docs/validation/REV_A3.md) · [Commissioning](../../docs/validation/COMMISSION_A3.md)

From a checkout or extracted Git archive, run `python tools/release_a3.py verify`. Verification uses the Python standard library and needs no network. For a fresh public stock and factory-process check before ordering, run `python tools/check_a3_stock.py` with network access. To plot again, use the source commit recorded in [manifest.json](manifest.json), KiCad 10.0.8, Python with gerbonara 1.6.3 and the dependencies pinned in [requirements-bench.txt](../../software/requirements-bench.txt). Run the following from the repository root on Windows.

```powershell
$source = (Get-Content releases/RevA3/manifest.json -Raw | ConvertFrom-Json).source_commit
python tools/release_a3.py build --source $source --cli 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' --pcb-python 'C:/Program Files/KiCad/10.0/bin/python.exe'
python tools/release_a3.py verify
```

KiCad embeds export timestamps. A fresh build produces new artifact hashes. The manifest records the delivered bytes alongside the native-source inventory. [Command log and raw ERC/DRC reports](../../docs/validation/RevA3/) · [Historical A2 release](../RevA2/)
