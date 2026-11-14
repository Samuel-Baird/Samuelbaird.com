"""HW 6 hand calculations (N, mm, MPa). Imported by solve.py; `python hand.py` prints them.

Bracket geometry follows cad.py: origin at the top-left corner, top edge y = 0, wall x = 0.
"""
import math

import numpy as np

P = 2.5                 # MPa (250 N/cm^2)
T = 2.0                 # mm
E = 200e3               # MPa
NU = 0.3
G = E / (2 * (1 + NU))
SY = 250.0              # MPa, ANSYS Structural Steel tensile yield (for a factor of safety only)
L_TOP = 200.0           # loaded length of the top edge, mm
H_ARM = 40.0            # arm depth, mm
X_TIP = 220.0           # free end of the arm (right end of the R20 semicircle)
X_SEC = 140.0           # section for the beam-theory stress check
X_FIL = 90.0            # where the R50 fillet meets the arm's lower edge

w = P * T               # N/mm, line load on the 2 mm plate
W = w * L_TOP           # N, resultant
x_W = L_TOP / 2         # mm, line of action
Ry = W                  # N, wall reaction (up)
Rx = 0.0
M_wall = W * x_W        # N mm, wall reaction moment (same about any point on the wall: only vertical loads)

I_arm = T * H_ARM ** 3 / 12
c_arm = H_ARM / 2


def M(x):
    """Bending moment (hogging, N mm) at section x from the load to the right (load ends at x = 200)."""
    return w * max(L_TOP - x, 0.0) ** 2 / 2


def V(x):
    return w * max(L_TOP - x, 0.0)


def sigma_beam(x):
    return M(x) * c_arm / I_arm


def depth(x):
    """Section depth (mm) through the solid at x, holes ignored."""
    if x <= 40:
        return 120 + math.sqrt(max(400 - (x - 20) ** 2, 0.0))
    if x < 90:
        return 90 - math.sqrt(max(2500 - (x - 90) ** 2, 0.0))
    if x <= 200:
        return H_ARM
    return 2 * math.sqrt(max(400 - (x - 200) ** 2, 0.0))


def tip_deflection(n=20001):
    """Unit-load method on a variable-depth cantilever clamped at the wall:
    delta = int M m / (E I) dx + int V v / (kappa G A) dx, m = (x_tip - x), v = 1."""
    xs = np.linspace(0.0, L_TOP, n)          # M = V = 0 beyond x = 200
    h = np.array([depth(x) for x in xs])
    I = T * h ** 3 / 12
    A = T * h
    Mx = np.array([M(x) for x in xs])
    Vx = np.array([V(x) for x in xs])
    bend = np.trapezoid(Mx * (X_TIP - xs) / (E * I), xs)
    shear = np.trapezoid(Vx / ((5 / 6) * G * A), xs)
    return bend, shear


def fillet_peak(n=5001):
    """Largest beam-theory edge stress 6M/(t h^2) through the fillet (40 <= x <= 90), section depth h(x)."""
    xs = np.linspace(40.0, 90.0, n)
    s = np.array([6 * M(x) / (T * depth(x) ** 2) for x in xs])
    i = int(s.argmax())
    return float(xs[i]), float(s[i]), depth(xs[i])


def cantilever_bounds():
    """Uniform 40 mm arm clamped at x = 90 (fillet end, stiff) or at x = 40 (vertical arm face)."""
    out = {}
    for x0 in (X_FIL, 40.0):
        Lc = L_TOP - x0
        out[x0] = w * Lc ** 4 / (8 * E * I_arm) + w * Lc ** 3 / (6 * E * I_arm) * (X_TIP - L_TOP)
    return out


def vm_plane(sx, sy, txy=0.0):
    return math.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2)


SIG_SEC = sigma_beam(X_SEC)
SIG_FIL = sigma_beam(X_FIL)
VM_TOP_FIL = vm_plane(SIG_FIL, -P)      # top edge above the fillet end: bending + edge pressure
TAU_SEC = 1.5 * V(X_SEC) / (T * H_ARM)
DELTA_B, DELTA_S = tip_deflection()
DELTA = DELTA_B + DELTA_S
BOUNDS = cantilever_bounds()
X_PK, SIG_PK, H_PK = fillet_peak()
DEEP_CORR = P / 5                        # elasticity correction to My/I for a uniformly loaded beam (order p/5)

if __name__ == "__main__":
    for k, v in dict(w=w, W=W, M_wall=M_wall, I_arm=I_arm, M140=M(X_SEC), sig140=SIG_SEC, tau140=TAU_SEC,
                     M90=M(X_FIL), sig90=SIG_FIL, vm_top90=VM_TOP_FIL, d_bend=DELTA_B, d_shear=DELTA_S, delta=DELTA,
                     x_pk=X_PK, sig_pk=SIG_PK, h_pk=H_PK, M_pk=M(X_PK), bound90=BOUNDS[X_FIL], bound40=BOUNDS[40.0], FoS=SY / VM_TOP_FIL).items():
        print(f"{k:10s} {v:.5g}")
