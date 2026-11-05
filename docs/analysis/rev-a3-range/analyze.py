"""Regenerate Rev A3 free-space analysis, or compare every generated result using --check."""
import argparse
import csv
from dataclasses import replace
from functools import lru_cache
import io
from itertools import product
import math
from pathlib import Path

from geometry import MU, contours, field, inductance, mutual, neumann_mutual, segments
from network import F, W, Setup, best_trim, dissipation, operating_point, panel_parts, reader, solve, source_planes, state
from plots import chart

HERE = Path(__file__).resolve().parent
DISTANCES = (10,25,50,75,100,150,225,305)
STRAIGHT, ROUTED = contours()
GEOM_L = inductance(ROUTED,[.002]*9+[.0011]*(len(ROUTED)-9))
BASE = best_trim(Setup(panel_l=GEOM_L))
MODES = ("direct","pa")


@lru_cache(maxsize=None)
def link(z, width=.050, depth=.025, turns=3, offset=0, tilt=0):
    return mutual(ROUTED,z/1000,width,depth,turns,offset,tilt)


def csv_text(header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf,lineterminator="\n")
    writer.writerow(header.split())
    for row in rows:
        writer.writerow([f"{v:.8g}" if isinstance(v,float) else v for v in row])
    return buf.getvalue()


def runs(values):
    intervals = []
    for v in values:
        if intervals and v == intervals[-1][1]+1:
            intervals[-1][1] = v
        else:
            intervals.append([v,v])
    return " / ".join(f"{a}-{b}" for a,b in intervals) or "none"


def calculate():
    outputs = {}
    cases = {"geometry":BASE, "release_L":best_trim(Setup())}
    curves = {}
    rows, stages, required = [], [], []
    for name,p in cases.items():
        for mode in MODES:
            points = []
            for z in range(5,306):
                m = link(z)
                r = operating_point(mode,m,p)
                i = abs(r["loop"])
                h = abs(field(ROUTED,0,0,z/1000)[2])*i
                sb = min(r["reply"])
                points.append((z,h,r["dc"]*1e6,sb*1e6))
                if z in DISTANCES:
                    rows.append([name,mode,z,p.panel_l*1e6,p.trim_series,p.trim_shunt,m*1e9,
                                 i*1000,h,h*MU*1e6,W*m*i, r["dc"]*1e6,
                                 abs(r["pin"]),*[(v*1e6) for v in r["reply"]],
                                 r["v210"],r["drive"],*[1000*v for pair in
                                 (r["j201"],r["output"],r["panel_waves"]) for v in pair],
                                 r["accepted"]*1000, r["zref"].real, abs(r["loop"])**2*2.2*1000])
                if z==305:
                    for uw in (10,100,1000,5000,15000):
                        ratio = math.sqrt(uw/(r["dc"]*1e6))
                        required.append([name,mode,uw,i*ratio,h*ratio,
                                         r["accepted"]*ratio**2,2.2*(i*ratio)**2,sb*1e9])
            curves[name,mode] = points
            for uw in (10,100,500,1000,5000,15000):
                for uv in (0,1,10,100):
                    passed = [z for z,_,dc,sb in points if dc>=uw and sb>=uv]
                    stages.append([name,mode,uw,uv,runs(passed)])
    outputs["distance.csv"] = csv_text(
        "panel path mm L_uH trim_series_pF trim_shunt_pF M_nH Iloop_mArms Haxis_Arms_m Baxis_uTrms "
        "tag_Voc_Vrms Pdc_uW RXcarrier_pin_Vrms RXlower_pin_uVrms RXupper_pin_uVrms "
        "J210_Vrms drive J201_fwd_mW J201_refl_mW output_fwd_mW output_refl_mW "
        "panel_fwd_mW panel_refl_mW panel_accepted_mW reflected_tag_R_ohm R401_mW",rows)
    outputs["thresholds.csv"] = csv_text("panel path required_DC_uW required_weaker_pin_sideband_uVrms pass_intervals_mm",stages)
    outputs["required-305.csv"] = csv_text("panel path needed_DC_uW required_loop_Arms required_Haxis_Arms_m "
                                          "required_panel_accepted_W required_R401_W available_weak_sideband_nVrms",required)
    plot_specs = [("field","Carrier field on the centerline","Axial H (A/m RMS)",1,[.001,.01,.1,1]),
                  ("power","Conditional rectified power at the label","DC power (µW)",2,[.1,1,10,100,1000,10000]),
                  ("reply","Weaker load-modulation sideband at one RX pin","Single-sideband voltage (µV RMS)",3,[.01,.1,1,10,100,1000])]
    for filename,title,ylabel,k,ticks in plot_specs:
        series = [(("PA" if m=="pa" else "Direct")+(" · etched L" if n=="geometry" else " · 0.64 µH"),
                   [(r[0],r[k]) for r in pts]) for (n,m),pts in curves.items()]
        outputs[filename+".svg"] = chart(title,ylabel,series,ticks)
    rows = []
    def sensitivity(name,p,width=.050,depth=.025,turns=3,offset=0,tilt=0):
        for z,mode in product((10,50,100,305),MODES):
            if z/1000 <= depth/2*abs(math.sin(math.radians(tilt))):
                continue
            m = link(z,width,depth,turns,offset,tilt)
            r = operating_point(mode,m,p)
            rows.append([name,mode,z,m*1e9,abs(r["loop"])*1000,r["dc"]*1e6,
                         min(r["reply"])*1e6,abs(r["pin"]),1000*r["accepted"],p.trim_series,p.trim_shunt])
    sensitivity("baseline",BASE)
    sensitivity("small_2turn_35x18",replace(BASE,tag_l=.6e-6,tag_q=15,eta=.2),.035,.018,2)
    sensitivity("large_5turn_65x32",replace(BASE,tag_l=3e-6,tag_q=50,eta=.6),.065,.032,5)
    alternatives = []
    for label,width,depth,turns,p in [
            ("Small coil",.035,.018,2,replace(BASE,tag_l=.6e-6,tag_q=15,eta=.2)),
            ("Reference coil",.050,.025,3,BASE),
            ("Large coil",.065,.032,5,replace(BASE,tag_l=3e-6,tag_q=50,eta=.6))]:
        points = []
        for z in range(5,306,2):
            result = operating_point("pa",link(z,width,depth,turns),p)
            points.append((z,result["dc"]*1e6))
        alternatives.append((label,points))
    outputs["label-sweep.svg"] = chart("How the unknown label changes harvested power",
        "PA path · DC power (µW)", alternatives, [.01,.1,1,10,100,1000,10000])
    for offset,tilt in ((.025,0),(.05,0),(0,45),(0,90),(.025,45)):
        sensitivity(f"offset_{offset*1000:g}mm_tilt_{tilt:g}deg",BASE,offset=offset,tilt=tilt)
    changes = {"half_drive":{"drive":.45}, "low_AGC":{"agc_r":200}, "detector_conducts":{"detector_r":1000},
               "coil_R_0.25":{"copper_r":.25}, "coil_R_2":{"copper_r":2}, "trimmer_Q20":{"trim_q":20},
               "trimmer_Q200":{"trim_q":200}, "fixed_banks_minus5pct":{"fixed_scale":.95},
               "fixed_banks_plus5pct":{"fixed_scale":1.05}, "opposite_cap_errors":{"series_scale":.95,"shunt_scale":1.05},
               "other_opposite_cap_errors":{"series_scale":1.05,"shunt_scale":.95},
               "chokes_plus5pct":{"choke_scale":1.05},"EMC_caps_minus5pct":{"match_c_scale":.95},
               "trimmers_midpoint":{"trim_series":24,"trim_shunt":24},
               "cable_3m":{"cable_m":3},"selector_excess_1dB":{"excess_db":1},
               "no_stub_C":{"bus_stub_c":0},"stub_C40pF":{"bus_stub_c":40e-12},
               "pin_C12pF":{"rx_c":12e-12},"pin_C15pF":{"rx_c":15e-12},
               "tag_detuned_5pct":{"tag_f0":1.05*F}, "tag_Q15":{"tag_q":15},
               "quarter_load":{"load_ratio":.25},"weak_reply":{"modulation":.03}}
    for name,changeset in changes.items():
        sensitivity(name,replace(BASE,**changeset))
    for k in (.02,.05,.10):
        zs,yp = panel_parts(F,BASE)
        inactive = 2.2+BASE.copper_r+1j*W*BASE.panel_l+zs+1/(yp+1/49.9)
        reflected = 4*(W*k*BASE.panel_l)**2/inactive
        sensitivity(f"four_inactive_k{k:g}",replace(BASE,other_z=reflected))
    outputs["sensitivity.csv"] = csv_text("case path mm M_nH loop_mArms Pdc_uW weaker_pin_uVrms "
                                          "carrier_pin_Vrms panel_accepted_mW trim_series_pF trim_shunt_pF",rows)
    rows = []
    for name,p in cases.items():
        for mode in MODES:
            for f in (F-F/16,F,F+F/16):
                s = state(mode,f,0,p)
                ref = state(mode,F,0,p)
                rows.append([name,mode,f/1e6,20*math.log10(abs(s["loop"]/ref["loop"])),
                             abs(s["loop"])*1000,s["panel_z"].real,s["panel_z"].imag])
    outputs["bandwidth.csv"] = csv_text("panel path MHz current_relative_dB loop_mArms panel_R panel_X",rows)
    rows = []
    for z,gap in product((10,50,100,305),(10,30,100)):
        nominal = link(z)
        scale = abs(1-link(z+2*gap)/nominal)
        rows.append([z,gap,scale,scale**2])
    outputs["wall-image.csv"] = csv_text("label_mm wall_behind_panel_mm mutual_ratio fixed_current_power_ratio",rows)
    rows = []
    for rail,rd,q,l,c in product((3.15,3.45),(0,12),(19,60),(.95,1.05),(.95,1.05)):
        p=replace(BASE,rail=rail,drive=1,driver_r=rd,choke_q=q,choke_scale=l,match_c_scale=c)
        v,z=reader(F,p)
        r=solve("pa",0,p)
        j201,out=source_planes("pa",r,p)
        rows.append([rail,rd,q,l,c,abs(v)**2/(4*z.real)*1000,r["v210"],j201[0]*1000,out[0]*1000])
    outputs["drive-corners.csv"] = csv_text("rail_V driver_diff_R choke_Q choke_scale EMC_C_scale "
        "J201_available_mW J210_Vrms J201_forward_mW J211_forward_mW_before_commissioning_backoff",rows)
    rows=[]
    for name,p in cases.items():
        for mode,z in product(MODES,(10,305)):
            result=operating_point(mode,link(z),p)
            losses=dissipation(mode,result,p)
            for part,value in losses.items():
                if abs(value)>1e-15:
                    rows.append([name,mode,z,part,1000*value])
            assert math.isclose(sum(losses[key] for key in
                ("panel_copper","R401","series_bank","shunt_bank","tag_RF_total")),result["accepted"])
    outputs["losses.csv"]=csv_text("panel path mm destination real_carrier_mW",rows)
    return outputs


def check_physics():
    a,z=.07,.305
    square=segments([(-a,-a),(a,-a),(a,a),(-a,a)])
    exact=2*a*a/(math.pi*(a*a+z*z)*math.sqrt(2*a*a+z*z))
    assert math.isclose(field(square,0,0,z)[2],exact,rel_tol=1e-12)
    assert math.isclose(link(305,.001,.001,1),MU*1e-6*field(ROUTED,0,0,z)[2],rel_tol=1e-5)
    for gap in DISTANCES:
        independent = neumann_mutual(ROUTED,gap/1000,.050,.025,3)
        assert math.isclose(independent,link(gap),rel_tol=1e-6)
    assert abs(link(305,tilt=90))/link(305)<.01
    for mode in MODES:
        empty=solve(mode,0.,BASE)
        assert empty["dc"]==0 and max(empty["reply"])==0
        x=solve(mode,link(100),BASE)
        half=solve(mode,link(100),replace(BASE,drive=BASE.drive/2))
        assert math.isclose(half["dc"],x["dc"]/4)
        assert math.isclose(half["reply"][0],x["reply"][0]/2)
    assert .5e-6 < GEOM_L < .65e-6


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args=parser.parse_args()
    check_physics()
    outputs=calculate()
    for name,data in outputs.items():
        path=HERE/name
        if args.check:
            if path.read_text(encoding="utf-8") != data:
                raise SystemExit(f"Generated values differ: {name}")
        else:
            path.write_text(data,encoding="utf-8",newline="\n")
    print(f"{len(outputs)} outputs {'verified' if args.check else 'generated'}; analytic and energy checks passed.")
