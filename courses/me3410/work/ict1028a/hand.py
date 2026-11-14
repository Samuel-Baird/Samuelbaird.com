"""In-class tutorial 10-28, problem 1: hand calculations (N, mm, MPa). Imported by solve.py; `python hand.py` prints them.

Geometry follows cad.py: origin at the bottom-left corner, wall at x = 0, load at the free end x = 250 mm.
"""
import math

import numpy as np

F = 1000.0              # N, downward at the free end
L = 250.0               # mm, wall to free end
L1 = 120.0              # mm, length of the deep block
D = 100.0               # mm, deep block depth
d = 40.0                # mm, arm depth
r = 25.0                # mm, fillet radius
T = 5.0                 # mm, plate thickness
E = 200e3               # MPa, Structural Steel
NU = 0.3
G = E / (2 * (1 + NU))
SY = 250.0              # MPa, Structural Steel tensile yield
SU = 460.0              # MPa, Structural Steel tensile ultimate
X_FIL_END = L1 + r      # 145 mm, where the fillet meets the arm
X_SEC = 200.0           # mm, beam-theory check section on the arm

# ANSYS Structural Steel S-N curve (zero mean stress, log-log interpolation), from General_Materials.xml.
SN_N = [10, 20, 50, 100, 200, 2000, 10000, 20000, 100000, 200000, 1000000]
SN_S = [3999, 2827, 1896, 1413, 1069, 441, 262, 214, 138, 114, 86.2]

# --- statics
Ry = F
Rx = 0.0
M_wall = F * L                      # N mm

# --- arm section
I_arm = T * d ** 3 / 12             # mm^4
c_arm = d / 2


def M(x):
    """Bending moment (N mm) at section x (hogging: tension on top)."""
    return F * (L - x)


def sigma_nom(arm):
    """Nominal bending stress in the 40 mm arm for a moment arm `arm` (mm)."""
    return F * arm * c_arm / I_arm


# Nominal stress used in class: moment arm 112.5 mm, i.e. a short way up the fillet from where it meets the arm.
ARM_CLASS = 112.5
SIG0 = sigma_nom(ARM_CLASS)
R_D = r / d                         # 0.625
D_D = D / d                         # 2.5
KT = 1.4                            # read in class from the stepped-flat-bar bending chart (extrapolated, see solve.py)
SIG_MAX = KT * SIG0
# Bounds on the nominal stress: moment arm at the fillet's end on the arm (x = 145) and at its start (x = 120).
SIG0_END = sigma_nom(L - X_FIL_END)     # 78.75 MPa
SIG0_START = sigma_nom(L - L1)          # 97.5 MPa (40 mm section assumed, as the chart does)

# --- check sections
SIG_SEC = M(X_SEC) * c_arm / I_arm      # x = 200 mm on the arm
SIG_WALL = 6 * M_wall / (T * D ** 2)    # deep block at the wall (beam theory; the block is short and deep)

# --- DET (von Mises) safety factor against yield at the fillet
N_YIELD = SY / SIG_MAX


def depth(x):
    """Section depth (mm) at x: 100 in the block, the R25 fillet (centre (145, 65)), then 40."""
    if x <= L1:
        return D
    if x < X_FIL_END:
        return 65.0 - math.sqrt(max(r ** 2 - (x - X_FIL_END) ** 2, 0.0))
    return d


def _deflection(hfun, n=25001):
    """Unit-load method for the tip: delta = int M m/(E I) + int V v/(k G A), m = L - x, v = 1."""
    x = np.linspace(0.0, L, n)
    h = np.array([hfun(xi) for xi in x])
    I = T * h ** 3 / 12
    A = T * h
    kappa = 5 / 6
    db = np.trapezoid(F * (L - x) ** 2 / (E * I), x)
    ds = np.trapezoid(F * np.ones_like(x) / (kappa * G * A), x)
    return db, ds


DELTA_B, DELTA_S = _deflection(depth)
DELTA = DELTA_B + DELTA_S                           # best estimate, real depth through the fillet
DELTA_B2, DELTA_S2 = _deflection(lambda x: D if x <= L1 else d)
DELTA_STEP = DELTA_B2 + DELTA_S2                    # sharp step, fillet material ignored (more flexible)
DELTA_ARM = F * (L - L1) ** 3 / (3 * E * I_arm)     # arm alone clamped at x = 120 (block rigid)


# --- fatigue (stress-life, ANSYS S-N curve)
def sn_life(sa):
    """Cycles to failure at alternating stress sa (MPa), log-log interpolation of the S-N table."""
    ls, ln = np.log10(SN_S[::-1]), np.log10(SN_N[::-1])
    if sa <= SN_S[-1]:
        return float("inf")
    return float(10 ** np.interp(math.log10(sa), ls, ln))


def sn_strength(n_cycles):
    """Alternating strength (MPa) at n_cycles."""
    return float(10 ** np.interp(math.log10(n_cycles), np.log10(SN_N), np.log10(SN_S)))


DESIGN_LIFE = 1e6
SE = sn_strength(DESIGN_LIFE)                       # 86.2 MPa


def fatigue(sig_max, ratio):
    """Alternating/mean stress, Goodman-equivalent alternating stress, life, and the Goodman safety factor at 1e6
    cycles: the factor n on the load that puts (n sa, n sm) on the Goodman line, 1/n = sa/Se + sm/Su."""
    smin = ratio * sig_max
    sa = (sig_max - smin) / 2
    sm = (sig_max + smin) / 2
    sar = sa / (1 - sm / SU) if sm > 0 else sa      # Goodman (no correction for compressive mean)
    sf = 1 / (sa / SE + max(sm, 0.0) / SU)
    return {"sa": sa, "sm": sm, "sar": sar, "life": sn_life(sar), "sf": sf}


FAT_R1 = fatigue(SIG_MAX, -1.0)
FAT_R05 = fatigue(SIG_MAX, -0.5)


if __name__ == "__main__":
    for k in ("Ry", "M_wall", "I_arm", "SIG0", "SIG_MAX", "SIG0_END", "SIG0_START", "SIG_SEC", "SIG_WALL", "N_YIELD",
              "DELTA_B", "DELTA_S", "DELTA", "DELTA_STEP", "DELTA_ARM", "SE"):
        print(f"{k:10s} {globals()[k]:.5g}")
    print("R=-1  ", {k: round(v, 4) for k, v in FAT_R1.items()})
    print("R=-0.5", {k: round(v, 4) for k, v in FAT_R05.items()})
