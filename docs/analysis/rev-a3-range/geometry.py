"""Free-space finite segments, geometric self inductance and label flux. SI throughout."""
import math
import re
from pathlib import Path

MU = 4e-7 * math.pi
# Eight-point Gauss-Legendre integration on [-1,1].
GAUSS = ((-.9602898565, .1012285363), (-.7966664774, .2223810345),
         (-.5255324099, .3137066459), (-.1834346425, .3626837834),
         (.1834346425, .3626837834), (.5255324099, .3137066459),
         (.7966664774, .2223810345), (.9602898565, .1012285363))
ROOT = Path(__file__).resolve().parents[3]


def native_loop():
    board = (ROOT / "hardware/antenna/RevA3/Panel_A3.kicad_pcb").read_text()
    fp = next(x for x in board.split('\n\t(footprint ') if '(property "Reference" "L401"' in x)
    edges = {}
    for line in fp.split('(fp_line')[1:]:
        data = line.split('(uuid')[0]
        if '(layer "F.Cu")' in data:
            def point(key):
                return tuple(float(v) for v in re.search(r'\('+key+r' ([^)]+)\)', data)[1].split())
            assert '(width 2)' in data
            edges[point('start')] = point('end')
    points = [(-6., 70.)]
    while points[-1] in edges:
        points.append(edges.pop(points[-1]))
    assert not edges and len(points) == 10 and points[-1] == (6., 70.)
    return [(x*.001, y*.001) for x,y in points]


def segments(points):
    return list(zip(points, points[1:] + points[:1]))


def field(edges, x, y, z):
    """Vector H per ampere from the finite straight wire Biot-Savart integral."""
    hx = hy = hz = 0.
    for (a,b),(c,d) in edges:
        length = math.hypot(c-a, d-b)
        ux, uy = (c-a)/length, (d-b)/length
        s = (x-a)*ux + (y-b)*uy
        perpendicular = ux*(y-b) - uy*(x-a)
        rho2 = perpendicular**2 + z*z
        if rho2 == 0 and (s < 0 or s > length):
            continue
        factor = (s/math.hypot(s, math.sqrt(rho2)) +
                  (length-s)/math.hypot(length-s, math.sqrt(rho2))) / (4*math.pi*rho2)
        hx += uy*z*factor
        hy -= ux*z*factor
        hz += perpendicular*factor
    return hx, hy, hz


def mutual(edges, height, width=.050, depth=.025, turns=3, offset=0., tilt=0.):
    """Flux through mean rectangular turns, rotated about their long x axis."""
    angle = math.radians(tilt)
    cosine, sine = math.cos(angle), math.sin(angle)
    flux = 0.
    for u, wu in GAUSS:
        for v, wv in GAUSS:
            t = depth*v/2
            _, hy, hz = field(edges, offset+width*u/2, t*cosine, height+t*sine)
            flux += wu*wv*(hz*cosine-hy*sine)
    return MU * turns * width * depth * flux / 4


def neumann_mutual(edges, height, width, depth, turns):
    """Independent centered-coil cross-check: integrate vector potential on its perimeter."""
    a,b = width/2,depth/2
    target = segments([(-a,-b),(a,-b),(a,b),(-a,b)])
    integral = 0.
    for (x,y),(xx,yy) in edges:
        length = math.hypot(xx-x,yy-y)
        ux,uy = (xx-x)/length,(yy-y)/length
        for (tx,ty),(ex,ey) in target:
            dx,dy = ex-tx,ey-ty
            dot = ux*dx+uy*dy
            for u,weight in GAUSS:
                px,py = tx+(1+u)*dx/2-x,ty+(1+u)*dy/2-y
                s = px*ux+py*uy
                rho = math.hypot(height,ux*py-uy*px)
                integral += dot*weight*(math.asinh(s/rho)+math.asinh((length-s)/rho))/2
    return MU*turns*integral/(4*math.pi)


def inductance(edges, widths):
    """Regularized self term on each strip; signed Neumann mutual terms."""
    partial = 0.
    for i, ((a,b),(c,d)) in enumerate(edges):
        dx, dy = c-a, d-b
        length = math.hypot(dx,dy)
        gmd = .22313 * widths[i]
        partial += 2*(length*math.asinh(length/gmd)-math.hypot(length,gmd)+gmd)
        for (x,y),(xx,yy) in edges[:i]:
            dot = dx*(xx-x)+dy*(yy-y)
            if dot:
                integral = sum(wu*wv / math.hypot(
                    a+dx*(u+1)/2 - x-(xx-x)*(v+1)/2,
                    b+dy*(u+1)/2 - y-(yy-y)*(v+1)/2)
                    for u,wu in GAUSS for v,wv in GAUSS)
                partial += dot*integral/2
    return MU*partial/(4*math.pi)


def contours():
    points = native_loop()
    # Closure via R401 and dominant C401/C404 bank positions. Currents split at the banks.
    feed = [(6.025,65), (8.975,65), (8.975,61), (-9.475,61), (-9.475,66.525)]
    routed = segments(points+[(x/1000,y/1000) for x,y in feed])
    return segments(points), routed
