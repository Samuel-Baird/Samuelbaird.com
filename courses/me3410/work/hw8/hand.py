"""HW 8 hand calculations (N, mm, MPa, W, C). Imported by solve.py; `python hand.py` prints them.

Geometry and axes follow cad.py: flange 1 bolted face on z = 0, leg 1 along +Z (z = 0..100, flange z = 0..20),
R70 bend about the X axis through (y, z) = (70, 100), leg 2 along +Y in the plane z = 170 (y = 70..170),
flange 2 on y = 150..170 with its bolted face on y = 170. Both bolted faces are fixed.
Material: ANSYS "Aluminum Alloy" (values as read from Engineering Data by ansys.py).
"""
import math

import numpy as np

# ---------------------------------------------------------------- data
RI, RO = 25.0, 30.0                 # pipe bore and outside radii (mm)
T_WALL = RO - RI
R_FO, R_FI, T_F = 50.0, 25.0, 20.0  # flange outside / bore radius, thickness
D_BOLT = 10.0
L_LEG, R_BEND = 100.0, 70.0         # straight leg (from the bolted face), bend centreline radius
L_FREE = L_LEG - T_F                # straight pipe outside each flange: 80 mm
SPAN = L_LEG + R_BEND               # 170: bolted face to bolted face, in Y and in Z

T_BORE, T_AIR, H = 100.0, 30.0, 10.0      # C, C, W/m^2 C (tutorial loading)
T_REF = 22.0                               # structural reference (zero-thermal-strain) temperature, C
K = 165.0                                  # W/m C, Aluminum Alloy at 100 C (table: 114 @ -100, 144 @ 0, 165 @ 100, 175 @ 200)
E, NU = 71e3, 0.33                         # MPa
ALPHA = 2.3e-5                             # 1/C
SY, SU = 280.0, 310.0                      # MPa

# ---------------------------------------------------------------- Part I: thermal
# 1D radial conduction through the pipe wall in series with outside convection, per metre of pipe
ri, ro = RI / 1000, RO / 1000
R_WALL = math.log(ro / ri) / (2 * math.pi * K)          # m C / W
R_CONV = 1 / (2 * math.pi * ro * H)
Q_LINE = (T_BORE - T_AIR) / (R_WALL + R_CONV)           # W/m
T_OUT = T_BORE - Q_LINE * R_WALL                        # outside wall temperature
DT_WALL = T_BORE - T_OUT
Q_IN = Q_LINE / (2 * math.pi * ri)                      # heat flux at the bore, W/m^2
Q_OUT = Q_LINE / (2 * math.pi * ro)                     # at the outside surface (= h (T_out - T_air))
BI = H * (T_WALL / 1000) / K                            # Biot number of the wall


def q_wall(r_mm):
    """Radial heat flux (W/m^2) at radius r in the pipe wall."""
    return Q_LINE / (2 * math.pi * r_mm / 1000)


def t_wall(r_mm):
    return T_BORE - Q_LINE * math.log(r_mm / RI) / (2 * math.pi * K)


# convection areas (mm^2)
A_LEG = 2 * math.pi * RO * L_FREE                       # one leg, outside the flange
A_BEND = math.pi ** 2 * R_BEND * RO                     # 90 deg torus, outside
A_FOD = 2 * math.pi * R_FO * T_F                        # flange rim
A_FIN = math.pi * (R_FO ** 2 - RO ** 2) - 4 * math.pi * (D_BOLT / 2) ** 2   # flange pipe-side face
A_CONV = 2 * A_LEG + A_BEND + 2 * A_FOD + 2 * A_FIN
Q_TOTAL = H * A_CONV / 1e6 * (T_OUT - T_AIR)            # W, all convection faces at about T_out
Q_FLANGE = H * (A_FOD + A_FIN) / 1e6 * (T_BORE - T_AIR)  # W lost by one flange (upper bound: surface at 100 C)
# flange as a radial conductor from the bore (r = 25) to the rim (r = 50), all of its heat crossing r = 25..50
DT_FLANGE = Q_FLANGE * math.log(R_FO / R_FI) / (2 * math.pi * K * T_F / 1000)
# the four bolt holes (r = 35..45) remove 4 D / (2 pi 40) of the circumference in that ring
R_BOLT = 40.0
F_HOLES = 4 * D_BOLT / (2 * math.pi * R_BOLT)
LN_HOLES = (math.log((R_BOLT - D_BOLT / 2) / R_FI) + math.log((R_BOLT + D_BOLT / 2) / (R_BOLT - D_BOLT / 2)) / (1 - F_HOLES)
            + math.log(R_FO / (R_BOLT + D_BOLT / 2)))
DT_FLANGE_H = DT_FLANGE * LN_HOLES / math.log(R_FO / R_FI)

# ---------------------------------------------------------------- Part II: structural
DT = T_BORE - T_REF                                     # the body is at about 100 C (Part I)
EPS_TH = ALPHA * DT
SIG_1D = E * ALPHA * DT                                 # a straight bar held at both ends
SIG_2D = E * ALPHA * DT / (1 - NU)                      # a surface held in both in-plane directions
DELTA = ALPHA * DT * SPAN                               # free growth of face 2 relative to face 1, in Y and in Z
DELTA_TOT = math.hypot(DELTA, DELTA)

A_P = math.pi * (RO ** 2 - RI ** 2)                     # pipe section
I_P = math.pi / 4 * (RO ** 4 - RI ** 4)
R_M = (RO + RI) / 2
H_BEND = T_WALL * R_BEND / R_M ** 2                     # pipe-bend characteristic h = t R / r_m^2
K_BEND = 1.65 / H_BEND                                  # Karman / ASME B31.3 flexibility factor
I_SIF = 0.9 / H_BEND ** (2 / 3)                         # ASME B31.3 in-plane stress intensification factor
G = E / (2 * (1 + NU))
M_RATIO = RI / RO
KAPPA = (6 * (1 + NU) * (1 + M_RATIO ** 2) ** 2
         / ((7 + 6 * NU) * (1 + M_RATIO ** 2) ** 2 + (20 + 12 * NU) * M_RATIO ** 2))   # Cowper, hollow circle


def centreline(n=4001):
    """Flexible pipe between the flanges (flanges rigid): points (z, y), tangent, ds, and a bend flag."""
    pts, tan, ds, bend = [], [], [], []
    s_leg = np.linspace(T_F, L_LEG, n)                                  # leg 1: z = 20..100, y = 0
    for z in s_leg:
        pts.append((z, 0.0)); tan.append((1.0, 0.0)); bend.append(False)
    ds += [L_FREE / (n - 1)] * n
    for th in np.linspace(0, math.pi / 2, n):                           # bend
        pts.append((L_LEG + R_BEND * math.sin(th), R_BEND * (1 - math.cos(th))))
        tan.append((math.cos(th), math.sin(th))); bend.append(True)
    ds += [R_BEND * math.pi / 2 / (n - 1)] * n
    for y in np.linspace(R_BEND, R_BEND + L_FREE, n):                   # leg 2: y = 70..150, z = 170
        pts.append((SPAN, y)); tan.append((0.0, 1.0)); bend.append(False)
    ds += [L_FREE / (n - 1)] * n
    w = np.array(ds)
    # trapezoid weights per segment (ends of each segment get half)
    for k in range(3):
        w[k * n] *= 0.5
        w[k * n + n - 1] *= 0.5
    return np.array(pts), np.array(tan), w, np.array(bend)


def frame(k_bend=1.0, shear=True):
    """Flexibility (force) method for the pipe as an in-plane curved frame clamped at both flange faces.

    Cut at B (flange 2 face, z = 170, y = 150): redundants X = (Fz, Fy, M) on the pipe end. Moment and axial force at a
    point P from the end loads: m = M + (yB - yP) Fz - (zB - zP) Fy (moment about +X), n = (Fz, Fy) . t.
    f_ij = int m_i m_j k / EI ds + int n_i n_j / EA ds + int v_i v_j / (kappa G A) ds, and f X = -(free thermal growth
    of B relative to A), with the shear force v = (Fz, Fy) . (normal to the centreline).
    The flanges are rigid but grow with the rest: the gap between the two fixed faces is 170 mm in Y and in Z.
    """
    P, T, w, bend = centreline()
    zb, yb = SPAN, SPAN - T_F
    kk = np.where(bend, k_bend, 1.0)
    m_unit = [yb - P[:, 1], -(zb - P[:, 0]), np.ones(len(P))]      # Fz = 1, Fy = 1, M = 1
    n_unit = [T[:, 0], T[:, 1], np.zeros(len(P))]
    v_unit = [-T[:, 1], T[:, 0], np.zeros(len(P))]
    ks = 1.0 if shear else 0.0
    f = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            f[i, j] = np.sum(m_unit[i] * m_unit[j] * kk / (E * I_P) * w) + np.sum(n_unit[i] * n_unit[j] / (E * A_P) * w)                 + ks * np.sum(v_unit[i] * v_unit[j] / (KAPPA * G * A_P) * w)
    d_free = np.array([DELTA, DELTA, 0.0])                    # B would move +170 alpha dT in Z and in Y
    X = np.linalg.solve(f, -d_free)
    Fz, Fy, M = X
    m = M + (yb - P[:, 1]) * Fz - (zb - P[:, 0]) * Fy
    n = Fz * T[:, 0] + Fy * T[:, 1]
    out = {"Fz": Fz, "Fy": Fy, "M_B": M, "f": f, "P": P, "m": m, "n": n, "bend": bend,
           # moment about +X at each bolted-face centre (what Mechanical reports for the Fixed Supports)
           "M_face2": M + (yb - SPAN) * Fz - (zb - SPAN) * Fy,
           "M_face1": -(M + (yb - 0.0) * Fz - (zb - 0.0) * Fy)}
    i_mx = int(np.argmax(np.abs(m)))
    out["m_max"], out["m_max_at"] = float(m[i_mx]), tuple(P[i_mx])
    i_mid = len(P) // 2
    out["m_midbend"] = float(m[i_mid])
    out["n_midbend"] = float(n[i_mid])
    out["m_A"] = float(m[0])                                  # pipe end at flange 1 (z = 20)
    return out


def section(fr, z):
    """Leg 1 at z: N and M from the frame, sigma_z = N/A + M y / I."""
    zb, yb = SPAN, SPAN - T_F
    M = fr["M_B"] + (yb - 0.0) * fr["Fz"] - (zb - z) * fr["Fy"]
    N = fr["Fz"]
    return {"z": z, "N": N, "M": M, "ax": N / A_P, "b30": M * RO / I_P, "b25": M * RI / I_P,
            "top30": N / A_P + M * RO / I_P, "top25": N / A_P + M * RI / I_P,
            "bot30": N / A_P - M * RO / I_P, "bot25": N / A_P - M * RI / I_P}


def section_from_reactions(F1, M1x, z):
    """The same section stresses from ANSYS's reactions at fixed face 1 (statics only, no beam model).
    F1 = (Fy, Fz) force on the elbow at face 1, M1x its moment about +X at (y, z) = (0, 0)."""
    Fy, Fz = F1
    # free body from face 1 to the cut at z: moment about the cut centre (0, 0, z) of the face-1 loads
    M_cut = M1x + (0.0 * Fz - (0.0 - z) * Fy)          # r = (y, z) - (0, z) = (0, -z): Mx = r_y Fz - r_z Fy
    # the cut face of this free body has outward normal +z: sigma_z = N/A + Mint y / I with Mint = -M_cut
    N = -Fz
    Mint = -M_cut
    return {"N": N, "M": Mint, "top30": N / A_P + Mint * RO / I_P, "bot30": N / A_P - Mint * RO / I_P,
            "top25": N / A_P + Mint * RI / I_P, "bot25": N / A_P - Mint * RI / I_P}


FR0 = frame(1.0, shear=False)   # Euler-Bernoulli curved beam
FR1 = frame(1.0)                # + shear deformation (Timoshenko)
FRK = frame(K_BEND)             # + bend ovalization (Karman flexibility factor): the hand model used for comparison
Z_SEC = 60.0
SEC1 = section(FR1, Z_SEC)
SECK = section(FRK, Z_SEC)
SIG_BEND_K = I_SIF * abs(FRK["m_midbend"]) * RO / I_P + abs(FRK["n_midbend"]) / A_P   # B31.3-style bend estimate
SIG_BEND_1 = I_SIF * abs(FR1["m_midbend"]) * RO / I_P + abs(FR1["n_midbend"]) / A_P   # same, shear-only moment


def report():
    print(f"wall: R'={R_WALL:.3e} + {R_CONV:.3e} m C/W, q'={Q_LINE:.3f} W/m, T_out={T_OUT:.4f} C (drop {DT_WALL:.5f}),"
          f" q_in={Q_IN:.1f} q_out={Q_OUT:.1f} W/m2, Bi={BI:.2e}")
    print(f"areas: leg {A_LEG:.1f} bend {A_BEND:.1f} rim {A_FOD:.1f} face {A_FIN:.1f} total {A_CONV:.1f} mm2;"
          f" Q_total={Q_TOTAL:.2f} W, Q_flange={Q_FLANGE:.2f} W, flange drop {DT_FLANGE:.3f} C, with holes {DT_FLANGE_H:.3f} C")
    print(f"dT={DT}, eps={EPS_TH:.4e}, sigma 1D {SIG_1D:.1f}, 2D {SIG_2D:.1f} MPa, free growth {DELTA:.4f} mm each")
    print(f"A={A_P:.1f} I={I_P:.0f}, h={H_BEND:.4f}, k={K_BEND:.3f}, i={I_SIF:.3f}")
    print(f"kappa={KAPPA:.4f} G={G:.0f}")
    for nm, fr in (("EB", FR0), ("k=1", FR1), ("k=Karman", FRK)):
        print(f"{nm}: Fz={fr['Fz']:.0f} Fy={fr['Fy']:.0f} M_B={fr['M_B']:.0f} Mface1={fr['M_face1']:.0f} "
              f"Mface2={fr['M_face2']:.0f} m_max={fr['m_max']:.0f} at {fr['m_max_at']} m_mid={fr['m_midbend']:.0f} "
              f"n_mid={fr['n_midbend']:.0f} m_A={fr['m_A']:.0f}")
    for nm, s in (("k=1", SEC1), ("k=K", SECK)):
        print(nm, {k: round(v, 2) for k, v in s.items()})
    print(f"bend estimate (B31.3 SIF) {SIG_BEND_K:.1f} .. {SIG_BEND_1:.1f} MPa")


if __name__ == "__main__":
    report()
