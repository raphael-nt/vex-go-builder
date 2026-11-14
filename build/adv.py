"""Competition Advanced (VEX 269-8115-040 Rev3), built on top of Competition Base.

Plain Python, no numpy. Reads docs/model-base.json (final coordinates, mm) and writes
docs/model-advanced.json. Every number below comes from the build instructions:

  * Green Connectors sit in the two top holes of the yellow end connectors next to the Brain
    (x = +-44.45, y = -6.35 and -19.05), pegs up.
  * Each tower foot is a Yellow Beam 1x4 with two Red Connectors. The connector holes drop on the
    green pegs, the connector pegs go outward into the yellow beam, and the Black Large Beam is pinned
    to the other two holes of the yellow beam (row 2 from the bottom, so the black beam stands on the base).
  * The tower with the Motor and the red gears is on the +X side (seen from the back in step 50).
  * Black Large Beam and Dark Gray Large Beam are joined by Blue Standoffs (12.7 mm apart).
  * The Motor rests on the Brain, the Plain Shaft spans from one black beam to the other.
  * Lift arms: black arm on the Plain Shaft through the blue gear, gray arm on the Plain Shaft
    through the yellow beam 25.4 mm above it, both ends on the Orange Connectors of the forks.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')

# ---------- small vector helpers ----------
def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def mul(a, k): return tuple(x * k for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def unit(a): l = math.sqrt(dot(a, a)); return mul(a, 1 / l)
X, Y, Z = (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)
def neg(a): return mul(a, -1)

def frame(x=None, y=None, z=None):
    """Rotation given the world direction of two local axes. Columns are the local axes."""
    if x is None: x = cross(y, z)
    if y is None: y = cross(z, x)
    if z is None: z = cross(x, y)
    x, y, z = unit(x), unit(y), unit(z)
    assert abs(dot(cross(x, y), z) - 1) < 1e-6, 'left-handed frame'
    return (x, y, z)

def rot(R, v): return add(add(mul(R[0], v[0]), mul(R[1], v[1])), mul(R[2], v[2]))

def quat(R):
    (m00, m10, m20), (m01, m11, m21), (m02, m12, m22) = R
    t = m00 + m11 + m22
    if t > 0:
        s = math.sqrt(t + 1) * 2; w = .25 * s; x = (m21 - m12) / s; y = (m02 - m20) / s; z = (m10 - m01) / s
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1 + m00 - m11 - m22) * 2; w = (m21 - m12) / s; x = .25 * s; y = (m01 + m10) / s; z = (m02 + m20) / s
    elif m11 > m22:
        s = math.sqrt(1 + m11 - m00 - m22) * 2; w = (m02 - m20) / s; x = (m01 + m10) / s; y = .25 * s; z = (m12 + m21) / s
    else:
        s = math.sqrt(1 + m22 - m00 - m11) * 2; w = (m10 - m01) / s; x = (m02 + m20) / s; y = (m12 + m21) / s; z = .25 * s
    return [round(v, 6) for v in (x, y, z, w)]

# ---------- model ----------
parts = []
for p in json.load(open(os.path.join(DOCS, 'model-base.json'), encoding='utf-8'))['parts']:
    q = dict(p); q['step'] = 1; parts.append(q)

def put(step, sid, col, R, local, world, come):
    """Place part so that its local point lands on the world point. come = direction it flies in from."""
    t = sub(world, rot(R, local))
    parts.append(dict(sid=sid, col=col, p=[round(v, 3) for v in t], q=quat(R), dir=[round(v, 4) for v in unit(come)], step=step))

def pin(step, sid, col, at, axis, local=(0, 0, 0)):
    """Pin, standoff or shaft along axis (local +z), local point on the world point."""
    a = unit(axis); ref = Z if abs(a[2]) < .9 else Y
    put(step, sid, col, frame(x=cross(ref, a), z=a), local, at, neg(a))

def collar(step, at, axis):
    """Shaft collar: its hole runs along local y."""
    put(step, '143', 'black', frame(y=axis, z=Z), (0, 0, 0), at, neg(axis))

def flat(step, sid, col, center_local, at, length_dir, normal, come=None):
    """Beam or plate: local x along length_dir, local z along normal."""
    put(step, sid, col, frame(x=length_dir, z=normal), center_local, at, come or normal)

# ---------- step 1: green connectors on the yellow end connectors next to the Brain ----------
Z_TOP = 50.5                        # top face of the base yellow connectors (holes are recessed below it)
for s in (1, -1):
    # local z up, local x along +Y so the two pegs (x = 0, -12.7) land on y = -6.35 and -19.05
    put(1, '2308', 'green', frame(x=Y, z=Z), (0, 0, -12.7), (s * 44.45, -6.35, Z_TOP), neg(Z))
G_PEG = Z_TOP + 12.7                # top pegs of the green connectors

# ---------- tower geometry (s = +1 motor tower, s = -1 plain tower) ----------
YT = -38.1                          # center line of both towers
Z_FOOT = G_PEG + 6.23               # red connector peg height = yellow foot beam center
Z_BLACK = Z_FOOT + 57.15            # foot beam pins in row 2 from the bottom, so the black beam stands on the base
Z_DG = Z_BLACK + 25.4               # dark gray top hole meets the black top hole
def X_BLACK(s): return s * 47.75    # black beam is pinned flat against the inner face of the foot beam
def X_DG(s): return s * 28.95       # 12.7 mm standoff gap inside the black beam
def dg(s, hx, hy, face):            # hole on the dark gray beam, face +1 outer (gears), -1 inner (motor)
    return (X_DG(s) + s * 3.05 * face, YT + hy, Z_DG + hx)
def bk(s, hx, hy, face):            # hole on the black large beam, face +1 outer, -1 inner
    return (X_BLACK(s) + s * 3.05 * face, YT + hy, Z_BLACK + hx)
P1 = (0, YT + 6.35, Z_DG + 6.35)    # Plain Shaft with the blue gear: black arm pivot
P2 = (0, YT + 6.35, Z_DG + 31.75)   # Plain Shaft through the yellow beam: gray arm pivot

def tower(s, st):
    out = (s, 0, 0)
    # dark gray large beam, long side vertical
    flat(st['dg'], '023', 'dgray', (0, 0, 0), (X_DG(s), YT, Z_DG), Z, out)
    if s > 0:   # pink idler pins stick out of the outer face, in the +Y column under the gear shaft
        for hx in (-31.75, -19.05): pin(st['dg'], '2258', 'pink', dg(s, hx, 6.35, 1), neg(out))
    for hx, hy in ((44.45, 6.35), (6.35, -6.35)):               # red pins out of the inner face
        pin(st['rp'], '2260', 'red', dg(s, hx, hy, -1), out)
    # yellow large beam 2x4 on the inner face over those pins
    flat(st['yl'], '019', 'yellow', (0, 0, 0), (X_DG(s) - s * 6.1, YT, Z_DG + 25.4), Z, neg(out))
    if s > 0:
        # motor on the inner face, output in the center column, cable up
        Rm = frame(x=neg(Z), y=out)                            # local y = face toward the beam
        mo = dg(s, -38.1, 0, -1)
        put(5, '269-6690', 'elec', Rm, (0, 31.63, 0), mo, neg(out))
        wm = lambda lp: add(mo, rot(Rm, sub(lp, (0, 31.63, 0))))
        for lp in ((-6.35, 31.63, 6.35), (-19.05, 31.63, 6.35), (-12.7, 31.63, 0)):
            pin(5, '2260', 'red', wm(lp), out)
        pin(6, '2260', 'red', wm((-25.4, 31.63, 0)), out)
        # red shaft: stop ring outside, 12.7 mm of it inside the motor
        pin(6, '2234', 'red', add(dg(s, -38.1, 0, 1), (s * 15.0, 0, 0)), neg(out))
        # red gears flat on the outer face: two on the pink pins, one on the motor shaft (as drawn in steps 8-10)
        pin(8, '2180', 'red', dg(s, -31.75, 6.35, 1), out, (0, 0, -3.17))
        pin(9, '2180', 'red', dg(s, -19.05, 6.35, 1), out, (0, 0, -3.17))
        pin(10, '2180', 'red', dg(s, -38.1, 0, 1), out, (0, 0, -3.17))
        # red pin in the back of the motor (step 19)
        pin(19, '2260', 'red', wm((-6.35, -18.98, 6.35)), neg(out))
    # blue standoffs from the outer face to the black beam
    for hx, hy in ((44.45, -6.35), (-44.45, 6.35), (-44.45, -6.35)):
        pin(st['so'], '2269', 'blue', dg(s, hx, hy, 1), neg(out))
    # black large beam with two pins on the inner face and two on the outer face
    flat(st['bk'], '026', 'black', (0, 0, 0), (X_BLACK(s), YT, Z_BLACK), Z, out)
    if s > 0:   # only the motor tower gets the two inner pins (step 14, not in step 38)
        for hx in (6.35, -6.35): pin(st['bk'], '2260', 'red', bk(s, hx, 6.35, -1), out)
    for hy in (6.35, -6.35): pin(st['bp'], '2260', 'red', bk(s, -57.15, hy, 1), neg(out))
    # foot: yellow beam 1x4 along Y, two red connectors in its front holes
    flat(st['ft'], '003', 'yellow', (0, 0, 0), (s * 53.85, -25.4, Z_FOOT), Y, out)
    for y in (-6.35, -19.05):
        # local z (peg) outward into the yellow beam, local y up, so the hole axis is vertical
        put(st['ft'], '2288', 'red', frame(y=Z, z=out), (0, 0, 0), (s * 50.8, y, Z_FOOT), neg(out))

tower(1, dict(dg=2, rp=3, yl=4, so=11, bk=14, bp=15, ft=16))
tower(-1, dict(dg=33, rp=33, yl=34, so=35, bk=38, bp=38, ft=39))

# Plain Shaft with collar and blue gear (step 12), between the dark gray and black beam of the motor tower
pin(12, '124', 'steel', P1, X)
pin(12, '2182', 'blue', (X_DG(1) + 3.05, P1[1], P1[2]), X, (0, 0, -3.05))
collar(12, (X_DG(1) + 3.05 + 9.525, P1[1], P1[2]), X)
# shaft collar on the other tower (step 37)
collar(37, (X_DG(-1) - 3.05 - 3.175, P1[1], P1[2]), neg(X))

# ---------- lift arms ----------
# Black arm: pivot in the end hole of each Black Beam 1x12, red pins in the other end hole, 139.7 mm.
# Gray arm: pivot in the second hole of each Gray Beam 1x14 (an orange standoff sits in the end hole
# behind it), red pins in the second hole from the far end, also 139.7 mm. Equal arms with pivots and
# end pins 25.4 mm apart make a parallelogram, so the orange connectors stay upright and the forks level.
# The arm angle is free (the motor drives it). 43 degrees is the lowest pose where the orange
# connectors still clear the front plate of the base.
L1 = L2 = 139.7
ALPHA = math.radians(43)
def ends(alpha):
    d = (0, math.cos(alpha), -math.sin(alpha))
    return add(P1, mul(d, L1)), add(P2, mul(d, L2))
E1, E2 = ends(ALPHA)
D1 = unit(sub(E1, P1)); D2 = unit(sub(E2, P2))
def at(P, Dv, x, s): return (x, P[1] + Dv[1] * s, P[2] + Dv[2] * s)

def arm_beam(step, sid, col, P, Dv, x, pivot_local):
    # local x points back toward the pivot, so local hole h sits at distance pivot_local - h
    put(step, sid, col, frame(x=neg(Dv), z=X), (pivot_local, 0, 0), at(P, Dv, x, 0), (1 if x > 0 else -1, 0, 0))

# black arm (steps 20-25). Thin beams: round holes stand 2.3 mm off the center on the pinned side
arm_beam(20, '011', 'black', P1, D1, -15.75, 69.85)
put(20, '1548', 'blue', frame(x=D1, z=X), (0, 0, -2.3), at(P1, D1, -12.7, 0), neg(X))   # square hole on the shaft
for s_ in (12.7, 38.1): pin(20, '2260', 'red', at(P1, D1, -12.7, s_), X)
put(21, '1548', 'blue', frame(x=D1, z=neg(X)), (0, 0, -2.3), at(P1, D1, 12.7, 0), X)
for s_ in (19.05, 31.75): pin(21, '2269', 'blue', at(P1, D1, -6.6, s_), neg(X))
for s_ in (12.7, 38.1): pin(22, '2260', 'red', at(P1, D1, 12.7, s_), neg(X))
pin(23, '2271', 'orange', at(P1, D1, -12.7, 101.6), neg(X))
arm_beam(24, '011', 'black', P1, D1, 15.75, 69.85)
for x in (-18.8, 18.8): pin(25, '2260', 'red', at(P1, D1, x, L1), (-1 if x < 0 else 1, 0, 0))

# gray arm (steps 27-31): standoffs in the end hole behind the pivot, the middle hole and hole 2 from the far end
arm_beam(27, '013', 'gray', P2, D2, -15.75, 69.85)
for s_ in (-12.7, 63.5, 127.0): pin(27, '2271', 'orange', at(P2, D2, -12.7, s_), neg(X))
pin(28, '124', 'steel', P2, X)
for x in (-9.525, 3.175): collar(28, (x, P2[1], P2[2]), X)        # one collar width apart (step 28)
arm_beam(30, '013', 'gray', P2, D2, 15.75, 69.85)
for x in (-18.8, 18.8): pin(31, '2260', 'red', at(P2, D2, x, L2), (-1 if x < 0 else 1, 0, 0))

# ---------- forks (steps 42-46) ----------
UPO = unit(sub(E2, E1))                     # orange connector peg axis (upright in the solved pose)
def fork(sign, st):
    out = (sign, 0, 0)
    # orange connector: holes on the two end pins, flat side outward, pegs along UPO
    Ro = frame(y=out, z=UPO)
    base = (sign * 18.8, E1[1], E1[2])
    put(st, '277', 'orange', Ro, (-6.35, -6.22, 6.35), base, out)
    wo = lambda lp: add(base, rot(Ro, sub(lp, (-6.35, -6.22, 6.35))))
    xl = rot(Ro, (1, 0, 0))                                  # direction of the peg row
    fwd = xl if dot(xl, Y) > 0 else neg(xl)
    back_peg = wo((0, 0, 0)) if dot(sub(wo((0, 0, 0)), wo((-12.7, 0, 0))), fwd) < 0 else wo((-12.7, 0, 0))
    # pink beam 1x7 under it, pointing forward, its two back holes on the bottom pegs
    centre = add(add(back_peg, mul(fwd, 38.1)), mul(UPO, -3.05))
    flat(st, '006', 'pink', (0, 0, 0), centre, fwd, UPO, neg(UPO))
    pin(st, '2268', 'yellow', add(add(centre, mul(fwd, 38.1)), mul(UPO, 3.05)), neg(UPO))
    return wo, fwd
(w1, fwd), (w2, _) = fork(-1, 42), fork(1, 44)
# red angle beam across the two forks on the front top pegs, straight part bent forward
pk = lambda w: max((w((0, 0, 38.1)), w((-12.7, 0, 38.1))), key=lambda v: dot(v, fwd))
a, b = pk(w1), pk(w2)
Ra = frame(x=neg(X), y=neg(fwd))
put(46, '1199', 'red', Ra, (-6.35, 11, -3.05), b, UPO)
print('arm angle', round(math.degrees(ALPHA), 2), 'E1', [round(v, 2) for v in E1], 'E2', [round(v, 2) for v in E2])

# ---------- steps 48-49: green pins through the side plates into the base ----------
for st, s in ((48, 1), (49, -1)):
    pin(st, '2261', 'green', (s * 56.9, -44.45, 57.0), (-s, 0, 0))

json.dump(dict(name='Competition Advanced', step=50, parts=parts, ref='269-8115-040'),
          open(os.path.join(DOCS, 'model-advanced.json'), 'w', encoding='utf-8'), ensure_ascii=False)
from collections import Counter
print(len(parts), 'parts', dict(Counter(p['sid'] for p in parts if p['step'] > 1)))
