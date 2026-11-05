"""RMS differential reader, bus sample, line and coupled resonators. No IC macromodel."""
import cmath
import math
from dataclasses import dataclass, replace

F = 13.56e6
Z0 = 50.
W = 2*math.pi*F


def series(z):
    return 1, z, 0, 1


def shunt(y):
    return 1, 0, y, 1


def cascade(*stages):
    a,b,c,d = 1,0,0,1
    for e,f,g,h in stages:
        a,b,c,d = a*e+b*g,a*f+b*h,c*e+d*g,c*f+d*h
    return a,b,c,d


def line(f, length=0, loss_db=0, loss_m=.2, vf=.66):
    gl = (loss_db+length*loss_m)*math.log(10)/20 + 2j*math.pi*f*length/(299792458*vf)
    return cmath.cosh(gl), Z0*cmath.sinh(gl), cmath.sinh(gl)/Z0, cmath.cosh(gl)


def drive(v, z, matrix):
    a,b,c,d = matrix
    return v/(a+z*c), (b+z*d)/(a+z*c)


def waves(v, i):
    return abs(v+Z0*i)**2/(4*Z0), abs(v-Z0*i)**2/(4*Z0)


@dataclass(frozen=True)
class Setup:
    # Full complementary square wave across TX1/TX2; drive scales the fundamental.
    rail: float = 3.3
    drive: float = .90
    driver_r: float = 4.   # both internal outputs combined
    choke_q: float = 35.
    choke_scale: float = 1.
    match_c_scale: float = 1.
    panel_l: float = .64e-6
    copper_r: float = 1.
    trim_q: float = 100.   # at the carrier, independently of the 1 MHz datasheet value
    fixed_q: float = 1500.
    trim_series: float = 24.
    trim_shunt: float = 24.
    fixed_scale: float = 1.
    series_scale: float = 1.
    shunt_scale: float = 1.
    cable_m: float = 1.
    cable_db_m: float = .2
    excess_db: float = .1  # trace/connector/relay parasitics at the selector
    bus_stub_c: float = 20e-12
    agc_r: float = 10000.
    rx_c: float = 14e-12  # 12 pF IC typical + assumed 1 pF per BAS316
    detector_r: float = math.inf
    balun_db: float = .3
    tag_l: float = 1.5e-6
    tag_q: float = 30.
    tag_f0: float = F
    load_ratio: float = 1.
    eta: float = .4
    modulation: float = .1
    other_z: complex = 0j


def reader_stages(f, p):
    w = 2*math.pi*f
    l = 470e-9*p.choke_scale
    c = p.match_c_scale
    # Odd-mode reduction of two identical arms. The 160 pF is across the full primary.
    coil = 2*(w*l/p.choke_q+1j*w*l)
    return [("chokes",series(coil)),("C111_C112",shunt(1j*w*34e-12*c)),
            ("C201_C202",series(1/(1j*w*150e-12*c))),("C203",shunt(1j*w*160e-12*c)),
            ("T201",line(f,loss_db=p.balun_db)),("drive_trace",line(f,.03128,vf=.55)),
            ("K200_TX",series(.1)),("output_trace",line(f,.01647,vf=.55))]


def reader(f, p):
    network = cascade(*(matrix for _,matrix in reader_stages(f,p)))
    source = 2*math.sqrt(2)/math.pi*p.rail*p.drive
    return drive(source, 66+p.driver_r, network)  # J201 open-circuit equivalent


def port_source(mode, f, p):
    v, z = reader(f,p)
    patch = line(f,.15,.03,p.cable_db_m)
    v, z = drive(v,z,patch)
    if mode == "direct":
        return v,z,0.
    xc = 1/(2j*math.pi*f*10e-9)
    vin,zin = drive(v,z,line(f,.01537,vf=.55))
    input_i = vin/(zin+xc+49.8)
    a,b,_,_ = line(f,.01537,vf=.55)
    v210 = (a*(49.8+xc)+b)*input_i
    feedback_gain = 1+(649+100)/187
    internal = feedback_gain*24.9*input_i
    vbus, zbus = drive(internal,49.9+xc,cascade(line(f,.00861,vf=.55),patch))
    return vbus,zbus,abs(v210)


def pickup(f, p):
    jw = 2j*math.pi*f
    pin = 1/(1/p.agc_r+jw*p.rx_c)
    leg = pin+4700+1/(jw*1e-9)
    # T202 is used into high impedance. A constant voltage efficiency is only a proxy.
    h = 10**(-p.balun_db/20)
    primary = 1/(1/4700+h*h/(2*leg))
    bus_load = .1+330+primary
    return 1/bus_load + 1/p.detector_r + jw*p.bus_stub_c, primary/bus_load*h*pin/(2*leg)


def bank(f, fixed_pf, trim_pf, p):
    # Two parallel series-RC branches; capacitance quoted in pF, ESR = |Xc|/Q.
    w = 2*math.pi*f
    return sum(w*c*1e-12/(1/q-1j) for c,q in ((fixed_pf,p.fixed_q),(trim_pf,p.trim_q)))


def panel_parts(f,p):
    ys = bank(f,259*p.fixed_scale*p.series_scale,p.trim_series,p)
    yp = bank(f,888*p.fixed_scale*p.shunt_scale,p.trim_shunt,p)
    return 1/ys, yp


def secondary(f, p):
    r = W*p.tag_l/p.tag_q
    rl = r*p.load_ratio
    w = 2*math.pi*f
    return complex(r+rl, p.tag_l*(w-(2*math.pi*p.tag_f0)**2/w)), rl


def state(mode, f, mutual, p):
    w = 2*math.pi*f
    vs,zs,v210 = port_source(mode,f,p)
    ybus,hpin = pickup(f,p)
    zcs,yp = panel_parts(f,p)
    z2,rl = secondary(f,p)
    zref = (w*mutual)**2/z2
    branch = p.copper_r+2.2+1j*w*p.panel_l+zcs+zref+p.other_z
    selector_line = cascade(line(f,.05856,vf=.55),series(.1),line(f,.02086,vf=.55),
                            line(f,p.cable_m,p.excess_db,p.cable_db_m))
    a,b,c,d = cascade(shunt(ybus),selector_line,shunt(yp))
    denominator = (a+zs*c)*branch+b+zs*d
    loop = vs/denominator
    vp = loop*branch
    ip = loop+yp*vp
    vb = (a*branch+b)*loop
    ib = (c*branch+d)*loop
    fw,rw = waves(vp,ip)
    tag_i = -1j*w*mutual*loop/z2
    dc = abs(tag_i)**2*rl*p.eta
    accepted = (vp*ip.conjugate()).real
    assert math.isclose(fw-rw,accepted,abs_tol=1e-12)
    assert math.isclose(accepted, abs(loop)**2*(p.copper_r+2.2+zcs.real+
                        zref.real+p.other_z.real)+abs(vp)**2*yp.real, abs_tol=1e-12)
    return dict(loop=loop, tag_i=tag_i, dc=dc, pin=abs(vb*hpin), bus_v=vb,
                bus_waves=waves(vb,ib), panel_waves=(fw,rw), accepted=accepted,
                v210=v210, rl=rl, reverse=zs*hpin/denominator/z2, zref=zref,
                panel_z=vp/ip, zcs=zcs, yp=yp)


def solve(mode, mutual, p):
    result = state(mode,F,mutual,p)
    # Each Fourier sideband of a symmetric +/-m*RL subcarrier square wave.
    ripple = result["tag_i"]*2*p.modulation*result["rl"]/math.pi
    result["reply"] = []
    for f in (F-F/16,F+F/16):
        rev = state(mode,f,mutual,p)["reverse"]
        result["reply"].append(abs(2*math.pi*f*mutual*ripple*rev))
    return result


def source_planes(mode, result, p):
    """Forward and reverse waves at J201, and at J211 for the PA patch."""
    a,b,c,d = line(F,.15,.03,p.cable_db_m)
    vb = result["bus_v"]
    vs,zs,_ = port_source(mode,F,p)
    ib = (vs-vb)/zs
    output = waves(a*vb+b*ib,c*vb+d*ib)
    if mode == "direct":
        return output, output
    a,b,c,d = cascade((a,b,c,d),line(F,.01537,vf=.55))
    vin,zin = drive(*reader(F,p),(a,b,c,d))
    load = 49.8+1/(1j*W*10e-9)
    i = vin/(zin+load)
    return waves((a*load+b)*i,(c*load+d)*i), output


def operating_point(mode, mutual, p):
    """Back off for the initial 25 mW forward setting at both patch reference planes."""
    result = solve(mode,mutual,p)
    j201, output = source_planes(mode,result,p)
    scale = min(1., math.sqrt(.025/max(j201[0],output[0])))
    if scale < 1:
        p = replace(p,drive=p.drive*scale)
        result = solve(mode,mutual,p)
        j201,output = source_planes(mode,result,p)
    assert result["v210"] <= 1.5 and output[0] <= .025000001
    result.update(j201=j201,output=output,drive=p.drive)
    return result


def dissipation(mode, result, p):
    """Back-propagate measured-plane phasors. Every value is real carrier power in watts."""
    p = replace(p,drive=result["drive"])
    def step(matrix,v,i):
        a,b,c,d = matrix
        return a*v+b*i,c*v+d*i
    losses = {}
    loop = result["loop"]
    vp = loop*result["panel_z"]/(1-result["yp"]*result["panel_z"])
    ip = loop+result["yp"]*vp
    losses["panel_copper"] = abs(loop)**2*p.copper_r
    losses["R401"] = abs(loop)**2*2.2
    losses["series_bank"] = abs(loop)**2*result["zcs"].real
    losses["shunt_bank"] = abs(vp)**2*result["yp"].real
    losses["tag_RF_total"] = abs(loop)**2*result["zref"].real
    def upstream(name,matrix,v,i):
        vu,iu = step(matrix,v,i)
        losses[name] = (vu*iu.conjugate()-v*i.conjugate()).real
        return vu,iu
    v,i = upstream("installed_coax",line(F,p.cable_m,loss_m=p.cable_db_m),vp,ip)
    v,i = upstream("selector_launch_excess",line(F,loss_db=p.excess_db),v,i)
    v,i = upstream("port_trace",line(F,.02086,vf=.55),v,i)
    v,i = upstream("selector_contact",series(.1),v,i)
    v,i = upstream("bus_trace",line(F,.05856,vf=.55),v,i)
    v,i = upstream("RX_and_detector_branches",shunt(pickup(F,p)[0]),v,i)
    v,i = upstream("output_patch",line(F,.15,.03,p.cable_db_m),v,i)
    if mode == "pa":
        v,i = upstream("PA_output_trace",line(F,.00861,vf=.55),v,i)
        losses["R214"] = abs(i)**2*49.9
        patch=line(F,.15,.03,p.cable_db_m)
        trace=line(F,.01537,vf=.55)
        voc,zs=drive(*reader(F,p),cascade(patch,trace))
        zin=49.8+1/(1j*W*10e-9)
        i=voc/(zs+zin)
        v=i*zin
        losses["R210_plus_R218"] = abs(i)**2*49.8
        losses["feedback_network"] = abs(24.9*i/187)**2*(749+187)
        v,i=upstream("PA_input_trace",trace,v,i)
        v,i=upstream("input_patch",patch,v,i)
    for name,matrix in reversed(reader_stages(F,p)):
        v,i=upstream(name,matrix,v,i)
    losses["R104_plus_R105"]=abs(i)**2*66
    losses["reader_internal_R"]=abs(i)**2*p.driver_r
    return losses


def best_trim(p):
    """Minimize reflected/incident ratio for the unloaded panel, on a 1 pF grid."""
    def reflection(pair):
        t = replace(p,trim_series=pair[0],trim_shunt=pair[1])
        zcs,y = panel_parts(F,t)
        z = 1/(y+1/(p.copper_r+2.2+1j*W*p.panel_l+zcs+p.other_z))
        return abs((z-Z0)/(z+Z0))
    pair = min(((cs,cp) for cs in range(8,41) for cp in range(8,41)),key=reflection)
    return replace(p,trim_series=pair[0],trim_shunt=pair[1])
