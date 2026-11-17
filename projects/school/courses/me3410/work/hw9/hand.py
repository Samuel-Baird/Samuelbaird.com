"""HW 9 hand calculations (SI for Q1, N-mm-MPa for Q2). Every number the report shows comes from here."""
import math

# ------------------------------------------------------------------ Q1: rotating part, 100 rpm
RPM = 100.0
OMEGA = RPM * 2 * math.pi / 60                    # rad/s
RHO, E, NU = 7850.0, 200e9, 0.3                   # kg/m^3, Pa, -
RHO_W2 = RHO * OMEGA ** 2                         # N/m^3 (body force per unit volume = rho w^2 r)
A_IN, B_OUT = 0.030, 0.046                        # rim inner / outer radius, m
R_MID = 0.5 * (A_IN + B_OUT)
R_BORE = 0.005
K_DISK = (3 + NU) / 8

# thin-ring estimate for the rim (mid radius)
SIG_RING = RHO_W2 * R_MID ** 2                    # Pa
U_RING = SIG_RING * R_MID / E                     # m


def lame_rim(r):
    """Rotating annulus a..b, plane stress, free surfaces: (sigma_r, sigma_theta, u) at radius r (Pa, Pa, m)."""
    a, b = A_IN, B_OUT
    sr = K_DISK * RHO_W2 * (a * a + b * b - a * a * b * b / r ** 2 - r * r)
    st = K_DISK * RHO_W2 * (a * a + b * b + a * a * b * b / r ** 2 - (1 + 3 * NU) / (3 + NU) * r * r)
    return sr, st, r * (st - NU * sr) / E


RIM_OUT = lame_rim(B_OUT)
RIM_IN = lame_rim(A_IN)
U_RIM_OUT = RIM_OUT[2]
SIG_TH_RIM_IN = RIM_IN[1]

# whole part idealised as one thin disk with a central hole (order of magnitude for the bore)
SIG_BORE_DISK = (3 + NU) / 4 * RHO_W2 * (B_OUT ** 2 + (1 - NU) / (3 + NU) * R_BORE ** 2)

# volume and mass of the half-section revolved (Pappus), mm
PTS = [(5, -15), (13, -15), (13, -6), (30, -6), (30, -25), (46, -25), (46, 25), (30, 25), (30, 6), (13, 6), (13, 15), (5, 15)]


def pappus():
    """Area, centroid radius, volume (mm) of the profile polygon."""
    A = 0.0
    Cx = 0.0
    n = len(PTS)
    for i in range(n):
        x0, y0 = PTS[i]
        x1, y1 = PTS[(i + 1) % n]
        c = x0 * y1 - x1 * y0
        A += c
        Cx += (x0 + x1) * c
    A /= 2
    Cx /= 6 * A
    return abs(A), Cx, 2 * math.pi * Cx * abs(A)


Q1_AREA, Q1_XBAR, Q1_VOL = pappus()
Q1_MASS = Q1_VOL * 1e-9 * RHO

# ------------------------------------------------------------------ Q2: lifting bracket
P = 20000.0                                       # N, +Y
E2, NU2, SY = 200e3, 0.3, 250.0                   # MPa (structural steel; Sy from the ANSYS material)
T = 30.0                                          # lug / upright thickness, mm
W0, W1 = 120.0, 60.0                              # upright width at y = 0 and at the hole centre
Y_HOLE = 80.0
D_HOLE, R_LUG = 30.0, 30.0

A_BASE_SEC = W0 * T                               # upright section at its root
SIG_ROOT = P / A_BASE_SEC
A_HOLE_GROSS = W1 * T
A_HOLE_NET = (W1 - D_HOLE) * T
SIG_GROSS = P / A_HOLE_GROSS
SIG_NET = P / A_HOLE_NET
SIG_BEAR = P / (D_HOLE * T)
P0_COS = 4 * P / (math.pi * D_HOLE * T)           # peak of a cosine bearing-pressure distribution
SLOPE = (W0 - W1) / 2 / Y_HOLE                    # tan of the side-face angle
TAU_EDGE_ROOT = SIG_ROOT * SLOPE


def w_at(y):
    return W0 - (W0 - W1) / Y_HOLE * y


def axial_stretch(n=4000):
    """Elongation of the tapered upright, y = 0..80 mm, as an axial bar: integral of P dy / (E t w(y))."""
    s = 0.0
    for i in range(n):
        y = (i + 0.5) * Y_HOLE / n
        s += P / (E2 * T * w_at(y)) * (Y_HOLE / n)
    return s


DELTA_AX = axial_stretch()
DELTA_AX_CLOSED = P / (E2 * T) * math.log(W0 / W1) / ((W0 - W1) / Y_HOLE)

if __name__ == "__main__":
    print("omega", OMEGA, "rho w2", RHO_W2)
    print("ring sigma", SIG_RING, "u", U_RING * 1e3, "mm")
    print("rim out", RIM_OUT, "rim in", RIM_IN)
    print("bore disk", SIG_BORE_DISK)
    print("pappus", Q1_AREA, Q1_XBAR, Q1_VOL, Q1_MASS)
    print("Q2", SIG_ROOT, SIG_GROSS, SIG_NET, SIG_BEAR, P0_COS, SLOPE, TAU_EDGE_ROOT, DELTA_AX, DELTA_AX_CLOSED)
