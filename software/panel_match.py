"""Single-frequency installed-panel model. All impedances are referred to the panel input."""
import argparse
import cmath
import math


def reflected_impedance(omega, inductance, coupled_loops):
    """Series impedance reflected by independent, closed secondary loops (SI units)."""
    change = 0j
    for coupling, secondary_l, secondary_z in coupled_loops:
        if not 0 <= coupling < 1 or secondary_l <= 0 or secondary_z.real <= 0:
            raise ValueError("Each secondary needs 0 <= k < 1, positive L and positive loss")
        mutual = coupling * math.sqrt(inductance * secondary_l)
        change += (omega * mutual) ** 2 / secondary_z
    return change


def match(loop_z, omega, z0):
    """Feed shunt C across a branch containing series C, loop and damping R."""
    resistance = loop_z.real
    if not 0 < resistance < z0:
        raise ValueError("This capacitive topology requires 0 < effective series R < Z0")
    branch_x = math.sqrt(resistance * (z0 - resistance))
    if loop_z.imag <= branch_x:
        raise ValueError("The inductive branch has insufficient reactance for this match")
    series = 1 / (omega * (loop_z.imag - branch_x))
    shunt = branch_x / (omega * resistance * z0)
    return series, shunt


def panel_z(loop_z, omega, series, shunt):
    branch = loop_z + 1 / (1j * omega * series)
    return 1 / (1 / branch + 1j * omega * shunt)


def cable_z(load, frequency, length, vf, loss_db_m, z0):
    gamma = loss_db_m * math.log(10) / 20 + 2j * math.pi * frequency / (299792458 * vf)
    t = cmath.tanh(gamma * length)
    return z0 * (load + z0 * t) / (z0 + load * t)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--loop-uh", type=float, required=True, help="Effective L with ferrite installed")
    p.add_argument("--loop-ohm", type=float, required=True, help="Effective loss with ferrite installed")
    p.add_argument("--damping-ohm", type=float, default=2.2)
    p.add_argument("--length-m", type=float, required=True)
    p.add_argument("--vf", type=float, required=True)
    p.add_argument("--loss-db-m", type=float, required=True, help="Matched cable attenuation at 13.56 MHz")
    p.add_argument("--secondary", nargs=4, type=float, action="append", default=[],
                   metavar=("K", "L_UH", "R_OHM", "X_OHM"),
                   help="Coupled wall mode or inactive loop, including termination transformed to loop plane")
    p.add_argument("--series-pf", type=float)
    p.add_argument("--shunt-pf", type=float)
    p.add_argument("--accepted-w", type=float, default=.01, help="Assumed real power absorbed at panel")
    a = p.parse_args()
    numbers = [v for v in vars(a).values() if isinstance(v, float)]
    if not all(map(math.isfinite, numbers + [v for sec in a.secondary for v in sec])):
        p.error("Inputs must be finite")
    if min(a.loop_uh, a.loop_ohm, a.vf, a.accepted_w) <= 0 or a.vf > 1 or min(a.damping_ohm, a.length_m, a.loss_db_m) < 0:
        p.error("Invalid loss, geometry, cable or power input")
    if (a.series_pf is None) != (a.shunt_pf is None):
        p.error("Supply both capacitor totals or omit both")
    f = 13.56e6
    w = 2 * math.pi * f
    l = a.loop_uh * 1e-6
    try:
        reflected = reflected_impedance(w, l, [(k, ls * 1e-6, complex(r, x)) for k, ls, r, x in a.secondary])
        loop = complex(a.loop_ohm + a.damping_ohm, w * l) + reflected
        if a.series_pf is None:
            cs, cp = match(loop, w, 50)
        else:
            cs, cp = a.series_pf * 1e-12, a.shunt_pf * 1e-12
            if min(cs, cp) <= 0:
                raise ValueError("Capacitances must be positive")
        panel = panel_z(loop, w, cs, cp)
        controller = cable_z(panel, f, a.length_m, a.vf, a.loss_db_m, 50)
    except ValueError as e:
        p.error(str(e))
    reflection = abs((controller - 50) / (controller + 50))
    branch_i = math.sqrt(a.accepted_w / loop.real)
    vfeed = branch_i * abs(loop + 1 / (1j * w * cs))
    print("Calculated at 13.56 MHz using supplied assumptions")
    print(f"Cs {cs*1e12:.2f} pF   Cp {cp*1e12:.2f} pF")
    print(f"Panel {panel:.2f} ohm   controller {controller:.2f} ohm   |S11| {reflection:.4f}")
    print(f"Branch {branch_i:.3f} A rms   Cs {branch_i/(w*cs):.2f} V rms   Cp {vfeed:.2f} V rms")
    print(f"Damping resistor {branch_i**2*a.damping_ohm:.3f} W   Cp current {vfeed*w*cp:.3f} A rms")


if __name__ == "__main__":
    main()
