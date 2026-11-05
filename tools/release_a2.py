"""Build both Rev A2 prototype packages with KiCad 10.0.8. Run from the repo root."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("releases/RevA2")
CHECKS = Path("docs/validation/RevA2")
PARTS = Path("hardware/RevA2-sourcing.csv")
DESIGNS = [("controller", "controller", "Controller_A2"), ("panel", "antenna", "Panel_A2")]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

def write_rows(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)

def inputs():
    paths = [PARTS, Path("tools/release_a2.py"), Path("tools/check_a2_pinmap.py"),
             Path("tools/inspect_a2_cam.py"), Path("software/requirements-bench.txt")]
    paths.extend(Path("software").glob("*.py"))
    paths.extend(Path("firmware").rglob("*.py"))
    paths.extend(Path("tests").rglob("*.py"))
    for _, folder, _ in DESIGNS:
        base = Path("hardware", folder, "RevA2")
        paths.extend(p for p in base.rglob("*") if p.is_file()
                     and (p.suffix in {".kicad_pro", ".kicad_sch", ".kicad_pcb", ".kicad_mod", ".kicad_sym", ".csv"}
                          or p.name in {"fp-lib-table", "sym-lib-table"}))
    return {p.as_posix(): digest(p.read_bytes().replace(b"\r\n", b"\n")) for p in sorted(paths)}

def create_assembly(base, tag, folder, positions):
    placements = {r["Ref"]: r for r in read_rows(positions)}
    vendors = {r["MPN"]: r for r in read_rows(PARTS)}
    bom, cpl, hand, full = [], [], [], []
    for row in read_rows(base / "BOM.csv"):
        refs = row["References"].split()
        assert len(refs) == int(row["Qty"])
        mpn = row["MPN"]
        part = vendors.get(mpn, {})
        action = part["Assembly"] if row["Population"] == "Fit" else row["Population"]
        full.append([row["References"], len(refs), row["Value"], row["Footprint"], part.get("Manufacturer",""),
                     mpn, part.get("LCSC",""), action])
        if not action.startswith("JLC SMT"):
            hand.append([row["References"], len(refs), mpn, row["Value"], row["Footprint"], action])
            continue
        if not part["LCSC"] or not part["LCEDA footprint revision"]:
            raise ValueError(f"Unverified assembly part {mpn}")
        bom.append([mpn, ",".join(refs), row["Footprint"].split(":")[-1], part["LCSC"]])
        for ref in refs:
            pos = placements[ref]
            assert pos["Side"] == "top", ref
            angle = float(pos["Rot"])
            phi = math.radians(angle)
            # LCEDA's origin relative to the local KiCad footprint in X/right, Y/down.
            dx = float(part["Center offset X mm"])
            dy = -float(part["Center offset Y down mm"])
            x = float(pos["PosX"]) + dx*math.cos(phi) - dy*math.sin(phi)
            y = float(pos["PosY"]) + dx*math.sin(phi) + dy*math.cos(phi)
            rotation = (angle + float(part["Rotation correction deg CCW"])) % 360
            cpl.append([ref, f"{x:.4f}", f"{y:.4f}", "Top", f"{rotation:g}"])
    brefs = [r for line in bom for r in line[1].split(",")]
    assert sorted(brefs) == sorted(line[0] for line in cpl) and len(set(brefs)) == len(brefs)
    write_rows(folder / f"{tag}-JLC-BOM.csv", ["Comment", "Designator", "Footprint", "LCSC Part #"], bom)
    write_rows(folder / f"{tag}-JLC-CPL.csv", ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"], sorted(cpl))
    write_rows(folder / f"{tag}-full-BOM.csv", ["Designators","Qty","Value","Footprint","Manufacturer","MPN","LCSC","Population"], full)
    write_rows(folder / f"{tag}-manual-and-DNP.csv", ["Designators","Qty","MPN","Value","Footprint","Population"], hand)

def build(cli, revision):
    source = subprocess.check_output(["git","rev-parse",revision], text=True).strip()
    hashes = inputs()
    for name, expected in hashes.items():
        committed = subprocess.check_output(["git","show",f"{source}:{name}"])
        if digest(committed.replace(b"\r\n", b"\n")) != expected:
            raise SystemExit(f"Working input differs from {source}: {name}")
    version = subprocess.check_output([cli, "version"], text=True).strip()
    if version != "10.0.8":
        raise SystemExit(f"Release requires KiCad 10.0.8. Found {version}")
    CHECKS.mkdir(parents=True, exist_ok=True)
    runs = []
    def run(*args):
        cmd = [str(a) for a in args]
        result = subprocess.run([cli, *cmd], capture_output=True, text=True, errors="replace")
        runs.append({"command":["kicad-cli", *cmd], "exit":result.returncode})
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
    for board, folder, tag in DESIGNS:
        base = Path("hardware",folder,"RevA2")
        target = OUT / board
        fab, assembly = target / "fabrication", target / "assembly"
        fab.mkdir(parents=True, exist_ok=True)
        assembly.mkdir(exist_ok=True)
        pcb, sch = [base / (tag + ext) for ext in (".kicad_pcb", ".kicad_sch")]
        for check, cmd, flags, infile in [
            ("erc", ["sch","erc"], [], sch),
            ("drc", ["pcb","drc"], ["--schematic-parity","--all-track-errors"], pcb)
        ]:
            for fmt, ext in [("json","json"), ("report","rpt")]:
                run(*cmd, *flags, "--severity-all", "--exit-code-violations", "--format", fmt,
                    "-o", CHECKS / f"{tag}-{check}.{ext}", infile)
        top = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"] if board == "controller" else ["F.Cu","B.Cu"]
        layers = top + ["F.Mask","B.Mask","F.Paste","B.Paste","F.Silkscreen","B.Silkscreen","Edge.Cuts"]
        run("pcb","export","gerbers","--layers",",".join(layers),"--no-protel-ext","-o",fab,pcb)
        run("pcb","export","drill","--format","excellon","--excellon-separate-th","--excellon-units","mm","-o",fab,pcb)
        run("sch","export","pdf","-o",target / f"{tag}-schematic.pdf",sch)
        run("pcb","export","pdf","--mode-single","--layers","F.Fab,F.Silkscreen,Edge.Cuts","--exclude-value",
            "--black-and-white","--sketch-pads-on-fab-layers","--sketch-DNP-footprints-on-fab-layers",
            "--scale","0","-o",assembly / f"{tag}-assembly.pdf",pcb)
        with tempfile.TemporaryDirectory() as tmp:
            pos = Path(tmp) / "positions.csv"
            run("pcb","export","pos","--format","csv","--units","mm","--side","front","--exclude-dnp","-o",pos,pcb)
            runs[-1]["command"][-2] = "<temp>/positions.csv"
            create_assembly(base,tag,assembly,pos)
            if board == "controller":
                netlist = Path(tmp)/"controller.xml"
                run("sch","export","netlist","--format","kicadxml","-o",netlist,sch)
                runs[-1]["command"][-2] = "<temp>/controller.xml"
                audit=subprocess.run([sys.executable,"tools/check_a2_pinmap.py",netlist],
                                     text=True,capture_output=True,check=True)
                (CHECKS/"pin-audit.txt").write_text(audit.stdout,encoding="utf-8")
                runs.append({"command":["python","tools/check_a2_pinmap.py","<temp>/controller.xml"],"exit":audit.returncode})
        files = sorted(fab.iterdir())
        expected = {tag+"-"+layer.replace(".","_")+".gbr" for layer in layers}
        # Different KiCad layer aliases can be used for silk. Check by layer function in CAM too.
        if len(list(fab.glob("*.gbr"))) != len(expected) or len(list(fab.glob("*.drl"))) != 2:
            raise ValueError(f"Unexpected plot inventory in {fab}")
        with zipfile.ZipFile(target / f"{tag}-JLC-Gerbers.zip", "w") as archive:
            for p in files:
                if p.suffix not in {".gbr", ".drl", ".gbrjob"}:raise ValueError(p)
                entry = zipfile.ZipInfo(p.name,(2000,1,1,0,0,0))
                archive.writestr(entry,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
    result = subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"], capture_output=True,text=True)
    from importlib.metadata import version as package_version
    versions = {pkg:package_version(pkg) for pkg in ("lzokay","pyscard")}
    if versions != {"lzokay":"2.1.0","pyscard":"2.3.2"}: raise ValueError(versions)
    (CHECKS / "offline-tests.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
    runs.append({"command":["python","-m","unittest","discover","-s","tests","-v"],"exit":result.returncode})
    result.check_returncode()
    cam = subprocess.run([sys.executable,"tools/inspect_a2_cam.py","--report",str(CHECKS/"cam.json")],check=True)
    runs.append({"command":["python","tools/inspect_a2_cam.py","--report",(CHECKS/"cam.json").as_posix()],"exit":cam.returncode})
    write_json(CHECKS / "commands.json", {"source":source,"kicad":version,"bench_dependencies":versions,
                                         "gerbonara":package_version("gerbonara"),"runs":runs})
    if inputs()!=hashes:raise ValueError("Export changed source files")
    artifacts = {p.as_posix():digest(p.read_bytes()) for d in [OUT,CHECKS] for p in sorted(d.rglob("*"))
                 if p.is_file() and p != OUT/"manifest.json"}
    write_json(OUT/"manifest.json", {"source_commit":source,"source_sha256_lf":hashes,"artifact_sha256":artifacts})
    verify()

def verify():
    manifest=json.loads((OUT/"manifest.json").read_text())
    if inputs()!=manifest["source_sha256_lf"]:raise SystemExit("Source hash mismatch")
    for name, expected in manifest["artifact_sha256"].items():
        if digest(Path(name).read_bytes()) != expected:raise SystemExit(f"Artifact hash mismatch: {name}")
    for board, _, tag in DESIGNS:
        drc=json.loads((CHECKS/f"{tag}-drc.json").read_text())
        if any(drc[k] for k in ("violations","unconnected_items","schematic_parity")):raise ValueError(tag)
        with zipfile.ZipFile(OUT/board/f"{tag}-JLC-Gerbers.zip") as z:
            for member in z.namelist():
                if z.read(member)!=(OUT/board/"fabrication"/member).read_bytes():raise ValueError(member)
    print("Verified Rev A2 source, reports, artifacts and ZIP contents.")

if __name__ == "__main__":
    import os
    os.chdir(ROOT)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["build","verify"])
    parser.add_argument("--cli",default=shutil.which("kicad-cli") or "kicad-cli")
    parser.add_argument("--source",default="HEAD",help="Git revision containing the design and exporter")
    args=parser.parse_args()
    if args.action=="build":build(args.cli,args.source)
    else:verify()
