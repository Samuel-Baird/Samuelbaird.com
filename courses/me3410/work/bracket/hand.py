"""In-class tutorial (3D bracket): hand calculations (N, mm, MPa). Imported by solve.py; `python hand.py` prints them.

Geometry and axes follow cad.py: X along the 60 mm edge, Y up, Z toward the front; the upright is the back plate
(z 0..10), its bearing hole centre is (30, 70, 5), and the base bottom face (y = 0) is fixed.
"""
import math

import numpy as np

FX, FY, FZ = 5500.0, 3500.0, 1700.0
W, T, H, D = 60.0, 10.0, 100.0, 50.0       # upright width, thickness, height; base depth
Y_LOAD = 70.0
D_BEAR = 30.0
E = 71e3                                    # MPa, ANSYS Aluminum Alloy
NU = 0.33
G = E / (2 * (1 + NU))
SY = 280.0                                  # MPa, tensile yield
Y_SEC = 35.0                                # check section on the upright

P_LOAD = np.array([W / 2, Y_LOAD, T / 2])   # resultant of the hole load acts through the hole centre
F = np.array([FX, FY, FZ])
F_RES = float(np.linalg.norm(F))

# --- reactions: equal and opposite to the load
R = -F
# fixed face: 60 x 50 rectangle minus two 10 mm holes at (15, 35) and (45, 35) (z measured from the back)
A_RECT, A_HOLE = W * D, math.pi * 5.0 ** 2
A_BASE = A_RECT - 2 * A_HOLE
ZC_BASE = (A_RECT * D / 2 - 2 * A_HOLE * 35.0) / A_BASE
C_BASE = np.array([W / 2, 0.0, ZC_BASE])
M_LOAD = np.cross(P_LOAD - C_BASE, F)       # moment of the load about the base centroid (N mm)
M_REACT = -M_LOAD

# --- upright section (60 wide in x, 10 thick in z)
A = W * T
I_STRONG = T * W ** 3 / 12                  # bending by Fx (about the z axis)
I_WEAK = W * T ** 3 / 12                    # bending by Fz (about the x axis)


def section(y):
    """Axial, strong- and weak-axis bending stresses (MPa) at height y; positive = tension."""
    arm = Y_LOAD - y
    s_ax = FY / A
    s_strong = FX * arm * (W / 2) / I_STRONG    # tension at x = 0, compression at x = 60
    s_weak = FZ * arm * (T / 2) / I_WEAK        # tension on the back face z = 0
    return {"arm": arm, "M_strong": FX * arm, "M_weak": FZ * arm, "ax": s_ax, "strong": s_strong, "weak": s_weak,
            "max_t": s_ax + s_strong + s_weak, "max_c": s_ax - s_strong - s_weak}


def sigma_y(x, z, y=Y_SEC):
    s = section(y)
    return s["ax"] + s["strong"] * (W / 2 - x) / (W / 2) + s["weak"] * (T / 2 - z) / (T / 2)


SEC = section(Y_SEC)
ROOT = section(T)                            # top of the base (fillet ignored)
N_YIELD_ROOT = SY / ROOT["max_t"]
TAU_X = 1.5 * FX / A                         # peak transverse shear from Fx (rectangular section)
TAU_Z = 1.5 * FZ / A

# --- bearing stress on the hole (projected area)
F_RADIAL = math.hypot(FX, FY)
SIG_BEAR = F_RADIAL / (D_BEAR * T)


# --- deflection of the hole centre: upright as a cantilever clamped at the top of the base (y = 10)
def cantilever(Fv, I, L):
    """Bending + shear deflection at the load, and the slope there."""
    kappa = 5 / 6
    return Fv * L ** 3 / (3 * E * I), Fv * L / (kappa * G * A), Fv * L ** 2 / (2 * E * I)


L_C = Y_LOAD - T                             # 60 mm
DZ_B, DZ_S, TH_Z = cantilever(FZ, I_WEAK, L_C)
DX_B, DX_S, TH_X = cantilever(FX, I_STRONG, L_C)
DZ = DZ_B + DZ_S
DX = DX_B + DX_S
DY = FY * L_C / (E * A)
# top of the upright (y = 100): the part above the load rotates rigidly with the slope at the load
DZ_TOP = DZ + TH_Z * (H - Y_LOAD)
DX_TOP = DX + TH_X * (H - Y_LOAD)
# lower bound: clamp at the top of the R10 fillet (y = 20)
DZ_LO = sum(cantilever(FZ, I_WEAK, Y_LOAD - 20.0)[:2])
DZ_TOP_LO = DZ_LO + cantilever(FZ, I_WEAK, Y_LOAD - 20.0)[2] * (H - Y_LOAD)


if __name__ == "__main__":
    print("R", R, "base centroid", C_BASE.round(3))
    print("M_load about base centroid", M_LOAD.round(1), "|M|", round(float(np.linalg.norm(M_LOAD)), 1))
    for nm, s in (("y=35", SEC), ("y=10", ROOT)):
        print(nm, {k: round(v, 3) for k, v in s.items()})
    print("n_yield root", round(N_YIELD_ROOT, 3), "tau", round(TAU_X, 2), round(TAU_Z, 2), "bearing", round(SIG_BEAR, 2))
    print("DZ", round(DZ_B, 4), round(DZ_S, 4), round(DZ, 4), "top", round(DZ_TOP, 4), "| clamp y=20", round(DZ_LO, 4), round(DZ_TOP_LO, 4))
    print("DX", round(DX_B, 4), round(DX_S, 4), round(DX, 4), "top", round(DX_TOP, 4), "DY", round(DY, 5))
