"""Inspect the actual upload ZIPs with gerbonara==1.6.3. Optionally render SVG proofs."""
import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile
import zipfile
from gerbonara import ExcellonFile, GerberFile, LayerStack

DESIGNS = [("controller","Controller_A2",(20,-137,180,-25)), ("panel","Panel_A2",(25,-175,175,-25))]

def inspect(name, tag, bounds, preview):
    package = Path("releases/RevA2", name, f"{tag}-JLC-Gerbers.zip")
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(package) as zipped:
        folder=Path(tmp)
        for filename in zipped.namelist():
            if Path(filename).name != filename:raise ValueError(filename)
            (folder/filename).write_bytes(zipped.read(filename))
        layers={p.stem[len(tag)+1:]:GerberFile.open(p) for p in folder.glob("*.gbr")}
        copper=sorted(k for k in layers if k.endswith("_Cu"))
        assert len(copper)==(4 if name=="controller" else 2)
        outline=layers["Edge_Cuts"].objects
        assert len(outline)==4
        corners={(o.x1,o.y1) for o in outline}|{(o.x2,o.y2) for o in outline}
        x,y,xx,yy=bounds
        assert corners=={(x,y),(xx,y),(xx,yy),(x,yy)}
        for o in outline: assert o.x1==o.x2 or o.y1==o.y2
        holes={}
        for kind in ("PTH","NPTH"):
            drill=ExcellonFile.open(folder/f"{tag}-{kind}.drl")
            holes[kind]=dict(sorted(Counter(f"{h.aperture.diameter:.3f}" for h in drill.objects).items()))
            if kind=="NPTH":
                expected = {(a,-b) for a in ([25,175] if name=="controller" else [37,163])
                            for b in ([30,132] if name=="controller" else [37,163])}
                assert {(h.x,h.y) for h in drill.objects}==expected and holes[kind]=={"3.200":4}
        result={"outline_mm":[xx-x,yy-y],"copper_layers":copper,"drill_hits_by_diameter_mm":holes,
                "objects_by_layer":{k:len(v.objects) for k,v in sorted(layers.items())}}
        if name=="panel":
            points=[(94,-170),(35,-170),(30,-165),(30,-35),(35,-30),(165,-30),(170,-35),(170,-165),(165,-170),(106,-170)]
            bars=[o for o in layers["F_Cu"].objects if type(o).__name__=="Line" and o.attrs.get(".C")==("L401",)]
            segments={frozenset(((o.x1,o.y1),(o.x2,o.y2))) for o in bars}
            assert segments=={frozenset(pair) for pair in zip(points,points[1:])}
            assert all(o.polarity_dark and o.aperture.diameter==2.0 for o in bars)
            result["etched_loop"]={"segments":len(bars),"copper_width_mm":2.0,"feed_gap_center_to_center_mm":12.0}
        if preview:
            preview.mkdir(parents=True,exist_ok=True)
            stack=LayerStack.open_dir(folder)
            for side in ["top","bottom"]:
                (preview/f"{tag}-{side}.svg").write_text(str(stack.to_pretty_svg(side=side)),encoding="utf-8")
            for layer in copper:
                (preview/f"{tag}-{layer}.svg").write_text(str(layers[layer].to_svg()),encoding="utf-8")
        return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview",type=Path)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    results={name:inspect(name,tag,bounds,args.preview) for name,tag,bounds in DESIGNS}
    output=json.dumps(results,sort_keys=True,indent=2)+"\n"
    if args.report:args.report.write_text(output,encoding="utf-8")
    else:print(output)
