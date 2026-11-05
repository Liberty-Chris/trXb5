"""Build or verify the two Rev A3 factory assemblies. See releases/RevA3/README.md."""
import argparse
import csv
import hashlib
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("releases/RevA3")
REPORTS = Path("docs/validation/RevA3")
EVIDENCE = Path("hardware/RevA3")
DESIGNS = (("controller","controller","Controller_A3"), ("panel","antenna","Panel_A3"))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

def write_csv(path, headers, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)

def require(test, message):
    if not test:
        raise ValueError(message)

def source_hashes():
    paths = [*EVIDENCE.glob("*.json"), *Path("tools").glob("*a3*.py"), Path("software/requirements-bench.txt"),
             Path("docs/validation/REV_A3.md"), Path("docs/validation/COMMISSION_A3.md"), OUT/"README.md"]
    for job, folder, _ in DESIGNS:
        paths.append(OUT/job/"ORDER.md")
        paths.extend(p for p in Path("hardware",folder,"RevA3").rglob("*") if p.is_file() and
                     (p.suffix in {".kicad_sch",".kicad_pcb",".kicad_pro",".kicad_mod",".kicad_sym",".csv"}
                      or p.name in {"fp-lib-table","sym-lib-table"}))
    for top in ("firmware","software","tests"):
        paths.extend(Path(top).rglob("*.py"))
    return {p.as_posix():sha(p.read_bytes().replace(b"\r\n",b"\n")) for p in sorted(paths)}

def catalog():
    data=json.loads((EVIDENCE/"catalog.json").read_text(encoding="utf-8"))
    for code,p in data["components"].items():
        require("Standard" in p["service"] and p["route"]=="JLCPCB public stock", code)
        total=0
        for job,usage in p["jobs"].items():
            fit=len(usage["designators"])*data["build_quantity"][job]
            needed=max(p["least_patch_number"], fit+max(5,p["loss_number"],math.ceil(.03*fit)))
            require(usage["fit"]==fit and fit+usage["reserve"]==needed, code)
            total+=needed
        require(total<=p["available"]==max(0,min(p["catalog_stock"],p["can_presale"])),code)
    return data["components"]

def sourcing_report():
    rows=[]
    for code,p in sorted(catalog().items(),key=lambda row:row[1]["mpn"]):
        jobs=p["jobs"]
        controller=jobs.get("controller",{})
        panel=jobs.get("panel",{})
        rows.append([p["mpn"],p["manufacturer"],code,p["verified_utc"],p["route"],p["placement"],
                     p["service"],p["catalog_stock"],p["can_presale"],p["available"],p["least_patch_number"],
                     p["loss_number"],controller.get("fit",0),controller.get("reserve",0),
                     panel.get("fit",0),panel.get("reserve",0),
                     " ".join(controller.get("designators",[]))," ".join(panel.get("designators",[])),
                     p["part_url"],p["manufacturer_document"],
                     f"https://lceda.cn/api/products/{code}/components?version=6.5.51"])
    write_csv(REPORTS/"sourcing.csv",
              ["MPN","Manufacturer","JLCPCB part","Verified UTC","Procurement","Assembly","Service",
               "Catalog on hand","Available to presell","Conservative available","Minimum patch","Catalog loss",
               "Controller fit x2","Controller reserve","Panel fit x10","Panel reserve","Controller refs",
               "Panel refs","JLCPCB record","Manufacturer document","Numbered footprint"],rows)

def assembly(job, tag, dest, netlist, positions, base):
    components=catalog()
    native=ET.parse(netlist)
    byref={c.get("ref"):c for c in native.findall("components/comp")}
    source_bom={ref:row for row in read_csv(base/"BOM.csv") for ref in row["References"].split()}
    require(byref.keys()==source_bom.keys(),f"{job} native BOM differs")
    pos={r["Ref"]:r for r in read_csv(positions)}
    audit={r["Ref"]:r for r in read_csv(REPORTS/"placement.csv") if r["Job"]==job}
    bom, cpl, omissions, fitted=[],[],[],set()
    for code,p in sorted(components.items()):
        if job not in p["jobs"]:
            continue
        refs=p["jobs"][job]["designators"]
        packages=set()
        for ref in refs:
            c=byref[ref]
            row=source_bom[ref]
            require(c.findtext("fields/field[@name='MPN']")==row["MPN"]==p["mpn"] and
                    c.findtext("footprint")==row["Footprint"] and c.findtext("value")==row["Value"]
                    and row["Population"]=="Fit" and c.find("property[@name='dnp']") is None, ref)
            require(ref not in fitted and audit[ref]["JLCPCB"]==code and pos[ref]["Side"]=="top",ref)
            packages.add(row["Footprint"].split(":")[-1])
            angle=float(pos[ref]["Rot"])
            dx=float(audit[ref]["Offset X mm"])
            dy=-float(audit[ref]["Offset Y down mm"])
            rad=math.radians(angle)
            x=float(pos[ref]["PosX"])+dx*math.cos(rad)-dy*math.sin(rad)
            y=float(pos[ref]["PosY"])+dx*math.sin(rad)+dy*math.cos(rad)
            rot=(angle+float(audit[ref]["Correction CCW deg"]))%360
            cpl.append([ref,f"{x:.4f}",f"{y:.4f}","Top",f"{rot:g}"])
            fitted.add(ref)
        require(len(packages)==1,p["mpn"])
        bom.append([p["mpn"],",".join(refs),packages.pop(),code])
    require(fitted==audit.keys(),job+" CAD audit coverage")
    allowed={"L401"} if job=="panel" else {"TP101","TP301","TP302"}
    require(byref.keys()-fitted==allowed,job+" unassigned schematic part")
    for ref in sorted(allowed):
        require(source_bom[ref]["Population"]=="PCB feature" and not source_bom[ref]["MPN"],ref)
        omissions.append([ref,"Etched antenna conductor" if ref=="L401" else "Exposed copper probe pad"])
    omissions.extend([[f"H{i}","Unplated mounting hole"] for i in range(1,5)])
    write_csv(dest/(tag+"-JLC-BOM.csv"),["Comment","Designator","Footprint","LCSC Part #"],bom)
    write_csv(dest/(tag+"-JLC-CPL.csv"),["Designator","Mid X","Mid Y","Layer","Rotation"],sorted(cpl))
    write_csv(dest/(tag+"-PCB-features.csv"),["Designator","Fabricated feature"],omissions)

def zipped(path, members):
    with zipfile.ZipFile(path,"w") as archive:
        for name,data in sorted(members.items()):
            archive.writestr(zipfile.ZipInfo(name,(2000,1,1,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)

def submission(job, tag):
    folder=OUT/job
    paths=[folder/(tag+"-JLC-Gerbers.zip"),folder/"ORDER.md",folder/(tag+"-schematic.pdf"),
           *sorted((folder/"assembly").glob("*"))]
    require(len(paths)==7 and len({p.name for p in paths})==7, f"Unexpected upload inventory in {folder}")
    files={p.name:p.read_bytes() for p in paths}
    files["SHA256SUMS.txt"]="".join(f"{sha(data)}  {name}\n" for name,data in sorted(files.items())).encode()
    return files

def build(cli, pcb_python, revision):
    source=subprocess.check_output(["git","rev-parse",revision],text=True).strip()
    hashes=source_hashes()
    for name,h in hashes.items():
        data=subprocess.check_output(["git","show",f"{source}:{name}"])
        require(sha(data.replace(b"\r\n",b"\n"))==h, "Uncommitted source "+name)
    kver=subprocess.check_output([cli,"version"],text=True).strip()
    require(kver=="10.0.8","KiCad 10.0.8 required")
    deps={key:version(key) for key in ["gerbonara","lzokay","pyscard"]}
    require(deps=={"gerbonara":"1.6.3","lzokay":"2.1.0","pyscard":"2.3.2"},deps)
    REPORTS.mkdir(parents=True,exist_ok=True)
    runs=[]
    def run(exe,*args):
        result=subprocess.run([exe,*map(str,args)],capture_output=True,text=True,errors="replace")
        tool="kicad-cli" if exe==cli else ("KiCad-python" if exe==pcb_python else "python")
        runs.append({"command":[tool,*[str(a).replace(str(temp),"<temp>").replace("\\","/") for a in args]],
                     "exit":result.returncode})
        require(result.returncode==0,result.stdout+result.stderr)
        return result.stdout+result.stderr
    with tempfile.TemporaryDirectory() as temp_dir:
        temp=Path(temp_dir)
        sourcing_report()
        run(pcb_python,"tools/audit_a3_placement.py",REPORTS/"placement.csv")
        for job,folder,tag in DESIGNS:
            base=Path("hardware",folder,"RevA3")
            pcb=base/(tag+".kicad_pcb")
            sch=base/(tag+".kicad_sch")
            target=OUT/job
            fab=target/"fabrication"
            asm=target/"assembly"
            fab.mkdir(parents=True,exist_ok=True)
            asm.mkdir(exist_ok=True)
            for check,cmd,flags,src in [("erc","sch",[],sch),("drc","pcb",["--schematic-parity","--all-track-errors"],pcb)]:
                for fmt,ext in [("report","rpt"),("json","json")]:
                    run(cli,cmd,check,*flags,"--severity-all","--exit-code-violations","--format",fmt,
                        "-o",REPORTS/f"{tag}-{check}.{ext}",src)
            layers=["F.Cu"]+(["In1.Cu","In2.Cu"] if job=="controller" else [])+["B.Cu","F.Mask","B.Mask",
                    "F.Paste","B.Paste","F.Silkscreen","B.Silkscreen","Edge.Cuts"]
            run(cli,"pcb","export","gerbers","--layers",",".join(layers),"--no-protel-ext","-o",fab,pcb)
            run(cli,"pcb","export","drill","--format","excellon","--excellon-separate-th","--excellon-units","mm","-o",fab,pcb)
            gerbers={p.name:p.read_bytes() for p in fab.iterdir()}
            require(len(gerbers)==len(layers)+3 and all(p.endswith((".gbr",".gbrjob",".drl")) for p in gerbers),str(fab))
            zipped(target/(tag+"-JLC-Gerbers.zip"),gerbers)
            run(cli,"sch","export","pdf","-o",target/(tag+"-schematic.pdf"),sch)
            run(cli,"pcb","export","pdf","--mode-single","--layers","F.Fab,F.Silkscreen,Edge.Cuts","--exclude-value",
                "--black-and-white","--sketch-pads-on-fab-layers","--scale","0","-o",asm/(tag+"-assembly.pdf"),pcb)
            pos,net=temp/(tag+"-positions.csv"),temp/(tag+".xml")
            run(cli,"pcb","export","pos","--format","csv","--units","mm","--side","front","--exclude-dnp","-o",pos,pcb)
            run(cli,"sch","export","netlist","--format","kicadxml","-o",net,sch)
            assembly(job,tag,asm,net,pos,base)
            if job=="controller":
                (REPORTS/"pin-audit.txt").write_text(run(sys.executable,"tools/check_a3_pinmap.py",net),encoding="utf-8")
            zipped(target/(tag+"-JLC-submission.zip"),submission(job,tag))
        (REPORTS/"offline-tests.txt").write_text(run(sys.executable,"-m","unittest","discover","-s","tests","-v"),encoding="utf-8")
        run(sys.executable,"tools/inspect_a3_cam.py","--report",REPORTS/"cam.json")
        write_json(REPORTS/"commands.json",{"source":source,"kicad":kver,"python":sys.version.split()[0],"dependencies":deps,"runs":runs})
    require(hashes==source_hashes(),"Exporter changed its inputs")
    write_json(OUT/"manifest.json",{"source_commit":source,"source_sha256_lf":hashes,"artifact_sha256":artifact_hashes()})
    verify()

def artifact_hashes():
    return {p.as_posix():sha(p.read_bytes()) for base in (OUT,REPORTS) for p in sorted(base.rglob("*"))
            if p.is_file() and p!=OUT/"manifest.json"}

def verify():
    manifest=json.loads((OUT/"manifest.json").read_text())
    require(source_hashes()==manifest["source_sha256_lf"],"Source inventory or digest differs")
    require(artifact_hashes()==manifest["artifact_sha256"],"Artifact inventory or digest differs")
    components=catalog()
    for job,_,tag in DESIGNS:
        dest=OUT/job
        report=json.loads((REPORTS/(tag+"-drc.json")).read_text())
        require(all(not report[k] for k in ("violations","unconnected_items","schematic_parity")),tag+" DRC")
        erc=json.loads((REPORTS/(tag+"-erc.json")).read_text())
        require(all(not s["violations"] for s in erc["sheets"]),tag+" ERC")
        bom=read_csv(dest/"assembly"/(tag+"-JLC-BOM.csv"))
        cpl=read_csv(dest/"assembly"/(tag+"-JLC-CPL.csv"))
        expected={r:c for c,p in components.items() for r in p["jobs"].get(job,{}).get("designators",[])}
        pairs=[(r,b["LCSC Part #"]) for b in bom for r in b["Designator"].split(",")]
        require(len(pairs)==len(cpl)==len(expected) and dict(pairs)==expected and
                {p["Designator"] for p in cpl}==expected.keys(),tag+" BOM/CPL coverage")
        for suffix,members in [("Gerbers",{p.name:p.read_bytes() for p in (dest/"fabrication").iterdir()}),
                               ("submission",submission(job,tag))]:
            with zipfile.ZipFile(dest/(tag+"-JLC-"+suffix+".zip")) as z:
                require(sorted(z.namelist())==sorted(members) and all(z.read(n)==d for n,d in members.items()),tag+suffix)
    print("Verified Rev A3 native sources, exact stock and placement coverage, reports, CAM and both submissions.")

if __name__=="__main__":
    os.chdir(ROOT)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["build","verify"])
    parser.add_argument("--cli",default=shutil.which("kicad-cli") or "kicad-cli")
    parser.add_argument("--pcb-python",default=sys.executable,help="Interpreter with KiCad 10.0.8 pcbnew")
    parser.add_argument("--source",default="HEAD")
    args=parser.parse_args()
    if args.action=="build":
        build(args.cli,args.pcb_python,args.source)
    else:
        verify()
