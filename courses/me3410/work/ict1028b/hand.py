"""Hand calculations for the 10-28 tutorial, problem 2 (long pressurized concrete block with a hole).

Units: N, mm, MPa. Plane strain: every force is per mm of block length (ANSYS 2D plane strain uses unit
thickness); multiply by 500 mm for the whole block.
"""
import math

# ---- data (handout figure) ------------------------------------------------------------------------------
L, H_L, H_R = 400.0, 200.0, 100.0          # base length, left and right heights
B_L, B_R, X_R0 = 150.0, 150.0, 250.0       # left top length, loaded right top length, start of the right load
Q1, Q2, P = 50.0, 25.0, 10.0               # MPa: left top, right top, lateral (both sides)
HX, HY, D = 100.0, 50.0, 50.0              # hole centre and diameter
R_F = 20.0                                 # step fillet radius
T_LONG = 500.0                             # block length out of plane
E, NU, SC, ST = 30_000.0, 0.20, 40.0, 3.0  # MPa

# ---- statics (per mm of length) ------------------------------------------------------------------------
F1 = Q1 * B_L                              # 7 500 N/mm
F2 = Q2 * B_R                              # 3 750 N/mm
FY = F1 + F2                               # 11 250 N/mm down
X1, X2 = B_L / 2, X_R0 + B_R / 2           # load centroids: 75, 325
XBAR = (F1 * X1 + F2 * X2) / FY            # 158.33 mm
FL, FR = P * H_L, P * H_R                  # 2 000 (+x) and 1 000 (-x) N/mm
RY = FY                                    # base reaction, up
RX = -(FL - FR)                            # base reaction, -1 000 N/mm
# moment of the applied loads about the base centre (200, 0), CCW +
M_BASE = (XBAR - L / 2) * (-FY) - (H_L / 2) * FL - (H_R / 2) * (-FR)

# ---- "beam theory" on the horizontal section through the hole centre, y = 50 (gross section, no hole) ----
YS = HY
A_S = L * 1.0                              # per mm of length
I_S = L ** 3 / 12                          # 5.333e6 mm^4 per mm
FL_S, YL_S = P * (H_L - YS), (H_L + YS) / 2      # left pressure above the section: 1 500 N/mm at y = 125
FR_S, YR_S = P * (H_R - YS), (H_R + YS) / 2      # right: 500 N/mm at y = 75
# moment of the loads above the section about its centroid (200, 50), CCW +
M_S = (XBAR - L / 2) * (-FY) - (YL_S - YS) * FL_S - (YR_S - YS) * (-FR_S)
SIG_AVG = -FY / A_S                        # -28.125 MPa
SLOPE = M_S / I_S                          # MPa per mm: sigma_y(x) = SIG_AVG + SLOPE (x - 200)


def sig_y_beam(x):
    return SIG_AVG + SLOPE * (x - L / 2)


SY_NOM = sig_y_beam(HX)                    # nominal sigma_y at the hole centre
SX_NOM = -P                                # lateral pressure carried straight across (both sides loaded at y = 50)
SZ_NOM = NU * (SX_NOM + SY_NOM)            # plane strain


def kirsch(sx, sy):
    """Tangential stress on the edge of a circular hole in an infinite plate under remote sx, sy (no shear).
    A = sides of the hole (on the horizontal diameter), B = top/bottom (vertical diameter)."""
    return {"A": 3 * sy - sx, "B": 3 * sx - sy}


def sig_theta(sx, sy, th):
    """Kirsch tangential stress at angle th (rad, from +x) on the hole edge."""
    return (sx + sy) - 2 * (sx - sy) * math.cos(2 * th)


K = kirsch(SX_NOM, SY_NOM)
SZ_A, SZ_B = NU * K["A"], NU * K["B"]      # plane strain on the free hole edge (sigma_r = 0)


def mohr_coulomb(s1, s3):
    """Brittle Coulomb-Mohr safety factor for principal stresses s1 >= s3 (tension +)."""
    if s1 >= 0 >= s3:
        return 1.0 / (s1 / ST - s3 / SC)
    if s1 >= s3 >= 0:
        return ST / s1
    return SC / -s3                        # both compressive


def principals_on_edge(s_theta):
    """Free edge in plane strain: sigma_r = 0, sigma_theta, sigma_z = nu sigma_theta."""
    s = sorted([0.0, s_theta, NU * s_theta], reverse=True)
    return s[0], s[2]


N_A = mohr_coulomb(*principals_on_edge(K["A"]))
N_B = mohr_coulomb(*principals_on_edge(K["B"]))
N_FAR = mohr_coulomb(*sorted([SX_NOM, SY_NOM, SZ_NOM], reverse=True)[::2])
N_Q1 = SC / Q1                             # directly under the 50 MPa load: sigma_3 = -q1
N_Q2 = SC / Q2                             # under the 25 MPa load

# ---- vertical displacement of the left top (column estimates, plane strain) ----------------------------
def eps_y(sy, sx):
    return ((1 - NU ** 2) * sy - NU * (1 + NU) * sx) / E


DY_UPPER = eps_y(-Q1, -P) * H_L            # 50 MPa carried straight down the full 200 mm (no spreading)
DY_LOWER = eps_y(SIG_AVG, -P) * H_L        # load spread over the whole base at once


def col_width(y):
    """Width of the 150 mm left column at height y, less the hole chord."""
    dy = y - HY
    return B_L - (2 * math.sqrt((D / 2) ** 2 - dy ** 2) if abs(dy) < D / 2 else 0.0)


def dy_column_hole(n=4000):
    """The 50 MPa column load (7 500 N/mm) carried down a 150 mm column whose width drops around the hole."""
    h = H_L / n
    return sum(eps_y(-F1 / col_width((k + 0.5) * h), -P) * h for k in range(n))


DY_HOLE = dy_column_hole()                 # same column, with the hole taken out of its width
SIG_NET = -F1 / (B_L - D)                  # column stress at the hole's level, -75 MPa


if __name__ == "__main__":
    for k in ("FY", "XBAR", "RX", "RY", "M_BASE", "M_S", "SIG_AVG", "SLOPE", "SY_NOM", "SX_NOM", "SZ_NOM",
              "N_FAR", "N_A", "N_B", "DY_UPPER", "DY_LOWER"):
        print(f"{k:8s} {globals()[k]: .5g}")
    print("Kirsch", K, "sz", SZ_A, SZ_B)
    print("sigma_y beam at x = 0, 100, 400:", [round(sig_y_beam(x), 3) for x in (0, 100, 400)])
