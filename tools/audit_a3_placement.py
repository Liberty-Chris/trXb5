"""Compare every fitted Rev A3 footprint with its exact JLCPCB library part. Run with KiCad Python."""
import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "hardware/RevA3"

def phase(degrees):
    radians = math.radians(degrees)
    return complex(math.cos(radians), math.sin(radians))

def numbered_lands(footprint):
    """Normalize native F.Cu pad centers to footprint-local X-right / Y-down."""
    lands = defaultdict(list)
    for pad in footprint.Pads():
        if footprint.GetAttributes() & pcbnew.FP_SMD and pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            # A plated thermal connection inside an exposed land has no component lead.
            if pad.GetDrillSize().x > pcbnew.FromMM(.20):
                raise ValueError(f'Unexpected drilled pad in {footprint.GetReference()}')
            continue
        if pad.GetNumber() and pad.IsOnLayer(pcbnew.F_Cu):
            pos = pad.GetPosition() - footprint.GetPosition()
            lands[pad.GetNumber()].append(complex(pos.x, pos.y) / 1e6 * phase(footprint.GetOrientationDegrees()))
    return lands

def alignment(native, library, code):
    vendor = defaultdict(list)
    for pin, x, y, *dimensions in library["pads"]:
        if code == "C3174425":
            # Amphenol 132134 drawing: center signal, four electrically common shell legs.
            pin = "1" if pin == "5" else "2"
        vendor[pin].append(complex(x, y))
    if {p:len(v) for p,v in native.items()} != {p:len(v) for p,v in vendor.items()}:
        raise ValueError(f"Terminal inventory mismatch for {code}: {native.keys()} vs {vendor.keys()}")
    count = sum(map(len, native.values()))
    local_center = sum(sum(v) for v in native.values()) / count
    catalog_center = sum(sum(v) for v in vendor.values()) / count
    candidates = []
    for angle in (0, 90, 180, 270):
        rotation = phase(-angle)
        offset = local_center - catalog_center * rotation
        errors = []
        for pin, positions in native.items():
            fitted = [p * rotation + offset for p in vendor[pin]]
            errors.extend(min(abs(a-b) for b in fitted) for a in positions)
            errors.extend(min(abs(a-b) for a in positions) for b in fitted)
        candidates.append((round(max(errors), 4), angle, offset))
    error, angle, offset = min(candidates, key=lambda c: (c[0], c[1]))
    # Numeric thresholds reflect differences in toe length on the manufacturer-approved lands.
    limit = .45 if code in {"C2058649"} else .40
    if error > limit:
        raise ValueError(f"{code}: maximum numbered-pad center difference {error:.3f} mm")
    return angle, offset, error

def audit():
    catalog = json.loads((COMPONENTS / "catalog.json").read_text(encoding="utf-8"))["components"]
    patterns = json.loads((COMPONENTS / "lands.json").read_text())["patterns"]
    results = []
    for job, folder, tag in [("controller","controller","Controller"),("panel","antenna","Panel")]:
        base = ROOT / "hardware" / folder / "RevA3"
        board = pcbnew.LoadBoard(str(base / f"{tag}_A3.kicad_pcb"))
        footprints = {f.GetReference():f for f in board.GetFootprints()}
        omissions = {"H1","H2","H3","H4"} | ({"L401"} if job == "panel" else {"TP101","TP301","TP302"})
        audited = set()
        for code, part in catalog.items():
            for ref in part["jobs"].get(job, {}).get("designators", []):
                f = footprints[ref]
                wave = part["placement"] == "Wave Soldering"
                has_leads = bool(f.GetAttributes() & pcbnew.FP_THROUGH_HOLE)
                if (f.GetLayer() != pcbnew.F_Cu or wave != has_leads or ref in audited
                    or f.GetAttributes() & pcbnew.FP_DNP or f.GetFieldText("MPN") != part["mpn"]):
                    raise ValueError(f"{job} {ref}: assembly side, technology, population or part differs")
                angle, offset, error = alignment(numbered_lands(f), patterns[part["cad_revision"]], code)
                results.append([job,ref,part["mpn"],code,"Top",angle,round(offset.real,4),
                                round(offset.imag,4),error,part["cad_revision"]])
                audited.add(ref)
        if footprints.keys() - audited != omissions:
            raise ValueError(f"{job}: unexpected non-purchased features {footprints.keys() - audited}")
    return sorted(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = audit()
    with args.output.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(["Job","Ref","MPN","JLCPCB","Side","Correction CCW deg","Offset X mm",
                         "Offset Y down mm","Max center error mm","LCEDA revision"])
        writer.writerows(rows)
    print(f"Checked all {len(rows)} placements against numbered top-side lands.")
