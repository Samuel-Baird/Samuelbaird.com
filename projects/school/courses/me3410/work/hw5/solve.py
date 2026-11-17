"""HW 5: beam element (W16x31). FE hand solution (two beam elements), statics + mechanics-of-materials
validation, ANSYS comparison -> Word.

    python solve.py            (reads ansys_out/results.json from ansys.py)
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "HW5_Beam_Element.docx"
HANDOUT_PAGE = HERE.parents[1] / "canvas" / "files" / "_extract" / "HW5_Beam_Element" / "img" / "page01.png"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

# ---------------------------------------------------------------- given (lb, in)
A, D, I = 9.12, 15.88, 375.0          # in^2, in, in^4
E = 29e6                              # psi
NU = 0.3                              # structural steel (ANSYS library), used only for the shear check
L1, L2 = 120.0, 60.0                  # in (10 ft, 5 ft)
W_FT = 1000.0
W = W_FT / 12.0                       # lb/in
P = 500.0                             # lb
A_P = L1 + L2 / 2                     # 150 in from the wall
LT = L1 + L2                          # 180 in
C = D / 2
EI = E * I

# ---------------------------------------------------------------- FE hand solution
def k_beam(L):
    return EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L],
                                   [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                   [-12, -6 * L, 12, -6 * L],
                                   [6 * L, 2 * L * L, -6 * L, 4 * L * L]])


k1, k2 = k_beam(L1), k_beam(L2)
K = np.zeros((6, 6))
K[:4, :4] += k1
K[2:, 2:] += k2
f1 = np.array([-W * L1 / 2, -W * L1 ** 2 / 12, -W * L1 / 2, W * L1 ** 2 / 12])   # UDL, element 1
f2 = np.array([-P / 2, -P * L2 / 8, -P / 2, P * L2 / 8])                         # P at mid-element 2
Feq = np.zeros(6)
Feq[:4] += f1
Feq[2:] += f2
FREE = [3, 4, 5]                      # theta_2, v_3, theta_3  (v1 = theta1 = v2 = 0)
Kr = K[np.ix_(FREE, FREE)]
dr = np.linalg.solve(Kr, Feq[FREE])
d = np.zeros(6)
d[FREE] = dr
Rfe = K @ d - Feq                     # reactions (nodal) = [K]{d} - {F_eq}
th2, v3, th3 = dr
R1_fe, M1_fe, R2_fe = Rfe[0], Rfe[1], Rfe[2]

# ---------------------------------------------------------------- statics + MoM (superposition)
# Release the roller: cantilever under w and P plus the redundant R2 (up) at x = L1; v(L1) = 0.
dw_L1 = -W * L1 ** 4 / (8 * EI)
dP_L1 = -P * L1 ** 2 * (3 * A_P - L1) / (6 * EI)
dR_L1 = L1 ** 3 / (3 * EI)            # per unit R2
R2 = -(dw_L1 + dP_L1) / dR_L1
R1 = W * L1 + P - R2
M1 = W * L1 ** 2 / 2 + P * A_P - R2 * L1   # wall moment (counter-clockwise on the beam), lb.in

x = np.linspace(0, LT, 18001)


def V_of(xx):
    return R1 - W * np.minimum(xx, L1) + R2 * (xx >= L1) - P * (xx >= A_P)


def M_of(xx):
    return (-M1 + R1 * xx - W * np.minimum(xx, L1) * (xx - np.minimum(xx, L1) / 2)
            + R2 * np.clip(xx - L1, 0, None) - P * np.clip(xx - A_P, 0, None))


Vx, Mx = V_of(x), M_of(x)
M_pos_x = R1 / W                                    # V = 0 in element 1
M_pos = float(M_of(np.array([M_pos_x]))[0])
M_roller = float(M_of(np.array([L1]))[0])
M_max = max(abs(M1), abs(M_pos), abs(M_roller))
sig_max = M_max * C / I
sig_pos = M_pos * C / I
# Elastic curve, element 1: EI v = -M1 x^2/2 + R1 x^3/6 - w x^4/24  (v(0) = v'(0) = 0)
# v' = 0 -> (w/6) x^2 - (R1/2) x + M1 = 0
qa, qb, qc = W / 6, -R1 / 2, M1
x_vmin = (-qb - np.sqrt(qb * qb - 4 * qa * qc)) / (2 * qa)
v_span = lambda xx: (-M1 * xx ** 2 / 2 + R1 * xx ** 3 / 6 - W * xx ** 4 / 24) / EI  # noqa: E731
v_min = v_span(x_vmin)
th2_mom = (-M1 * L1 + R1 * L1 ** 2 / 2 - W * L1 ** 3 / 6) / EI
# Tip by superposition on the cantilever (released roller)
tip_w = -(W * L1 ** 4 / (8 * EI) + W * L1 ** 3 / (6 * EI) * (LT - L1))
tip_P = -(P * A_P ** 3 / (3 * EI) + P * A_P ** 2 / (2 * EI) * (LT - A_P))
tip_R = R2 * (L1 ** 3 / (3 * EI) + L1 ** 2 / (2 * EI) * (LT - L1))
v_tip = tip_w + tip_P + tip_R
# Numerical elastic curve (checks the closed forms and gives v at any x)


def curve(Mfun_vals, extra_shear=None):
    th = np.concatenate([[0], np.cumsum((Mfun_vals[1:] + Mfun_vals[:-1]) / 2 * np.diff(x))]) / EI
    v = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(x))])
    if extra_shear is not None:
        v = v + extra_shear
    return th, v


th_x, v_x = curve(Mx)
v_150 = float(np.interp(A_P, x, v_x))
assert abs(v_x[-1] - v_tip) < 1e-6 and abs(v_x[-1] - v3) < 1e-6, (v_x[-1], v_tip, v3)
assert abs(R1 - R1_fe) < 1e-6 and abs(R2 - R2_fe) < 1e-6 and abs(M1 - M1_fe) < 1e-4
assert abs(np.interp(L1, x, v_x)) < 1e-9 and abs(th2_mom - th2) < 1e-10

# ---------------------------------------------------------------- Timoshenko (shear-deformation) check
G = E / (2 * (1 + NU))
RES_PATH = HERE / "ansys_out" / "results.json"
FE = json.loads(RES_PATH.read_text()) if RES_PATH.exists() else None
TF = FE["section"]["tf"] if FE else 0.4535
TW = FE["section"]["tw"] if FE else 0.2744
AS = (D - TF) * TW                    # shear area ~ web between flange centrelines


def timoshenko():
    """Same superposition with shear flexibility v_s' = -V/(G A_s) added (unit-load method)."""
    def defl(R2t):
        R1t, M1t = W * L1 + P - R2t, W * L1 ** 2 / 2 + P * A_P - R2t * L1
        Mt = (-M1t + R1t * x - W * np.minimum(x, L1) * (x - np.minimum(x, L1) / 2)
              + R2t * np.clip(x - L1, 0, None) - P * np.clip(x - A_P, 0, None))
        Vt = R1t - W * np.minimum(x, L1) + R2t * (x >= L1) - P * (x >= A_P)
        vs = -np.concatenate([[0], np.cumsum((Vt[1:] + Vt[:-1]) / 2 * np.diff(x))]) / (G * AS)
        return R1t, M1t, curve(Mt, vs)[1]
    i2 = np.searchsorted(x, L1)
    v0, v1 = defl(0.0)[2][i2], defl(1.0)[2][i2]
    R2t = -v0 / (v1 - v0)
    R1t, M1t, vt = defl(R2t)
    return dict(R1=R1t, R2=R2t, M1=M1t, tip=vt[-1], vmin=vt.min(), sig=M1t * C / I)


TIM = timoshenko()


# ---------------------------------------------------------------- figures
def fig_handout():
    from PIL import Image
    im = Image.open(HANDOUT_PAGE)
    w, h = im.size
    box = (int(0.34 * w), int(0.60 * h), int(0.66 * w), int(0.72 * h))
    p = FIG / "handout_beam.png"
    im.crop(box).save(p)
    return p


def fig_fbd():
    fig, ax = plt.subplots(figsize=(7.6, 2.6))
    ax.plot([0, LT], [0, 0], color="#1f2937", lw=6, solid_capstyle="butt")
    ax.add_patch(plt.Rectangle((-6, -22), 6, 44, color="#9ca3af", hatch="///", ec="#6b7280"))
    for xi in np.linspace(0, L1, 9):
        ax.annotate("", (xi, 3), (xi, 15), arrowprops=dict(arrowstyle="-|>", color="#16a34a", lw=1.2))
    ax.plot([0, L1], [15, 15], color="#16a34a", lw=1.2)
    ax.text(L1 / 2, 18, "w = 1000 lb/ft (83.33 lb/in)", ha="center", color="#16a34a", fontsize=9)
    ax.annotate("", (A_P, 3), (A_P, 22), arrowprops=dict(arrowstyle="-|>", color="#dc2626", lw=1.8))
    ax.text(A_P, 24, "P = 500 lb", ha="center", color="#dc2626", fontsize=9)
    ax.plot([L1], [-6], marker="o", ms=10, color="#2563eb")
    ax.annotate("", (L1, -4), (L1, -24), arrowprops=dict(arrowstyle="-|>", color="#2563eb", lw=1.8))
    ax.text(L1 + 3, -24, f"R₂ = {R2:,.1f} lb", color="#2563eb", fontsize=9)
    ax.annotate("", (0, -4), (0, -24), arrowprops=dict(arrowstyle="-|>", color="#2563eb", lw=1.8))
    ax.text(3, -24, f"R₁ = {R1:,.1f} lb", color="#2563eb", fontsize=9)
    ax.text(-4, 26, f"M₁ = {M1:,.0f} lb·in (CCW)", color="#2563eb", fontsize=9)
    for xi, lab in ((0, "1"), (L1, "2"), (LT, "3")):
        ax.text(xi, 6, lab, ha="center", fontsize=9, fontweight="bold")
    for xa, xb, lab in ((0, L1, "element (1): 10 ft"), (L1, LT, "element (2): 5 ft")):
        ax.annotate("", (xa, -34), (xb, -34), arrowprops=dict(arrowstyle="<->", color="#374151", lw=0.8))
        ax.text((xa + xb) / 2, -40, lab, ha="center", fontsize=8.5)
    ax.text(A_P, -14, "2.5 ft", ha="center", fontsize=8, color="#6b7280")
    ax.set_xlim(-25, LT + 15)
    ax.set_ylim(-45, 32)
    ax.axis("off")
    p = FIG / "fbd.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_vm():
    xf = x / 12
    fig, axs = plt.subplots(3, 1, figsize=(7.4, 6.4), sharex=True)
    axs[0].fill_between(xf, Vx, color="#93c5fd", step=None)
    axs[0].plot(xf, Vx, color="#1d4ed8")
    axs[0].set_ylabel("V (lb)")
    axs[1].fill_between(xf, Mx / 12, color="#fca5a5")
    axs[1].plot(xf, Mx / 12, color="#b91c1c")
    axs[1].set_ylabel("M (lb·ft)")
    axs[2].plot(xf, v_x, color="#047857")
    axs[2].axhline(0, color="k", lw=0.6)
    axs[2].set_ylabel("v (in)")
    axs[2].set_xlabel("x from the wall (ft)")
    for a in axs:
        a.grid(alpha=0.3)
        a.axvline(L1 / 12, color="#6b7280", lw=0.6, ls="--")
    axs[0].annotate(f"{R1:,.1f}", (0, R1), (0.5, R1 - 1500), fontsize=8)
    axs[1].annotate(f"{-M1 / 12:,.0f} (wall)", (0, -M1 / 12), (0.6, -M1 / 12), fontsize=8)
    axs[1].annotate(f"+{M_pos / 12:,.0f} at x = {M_pos_x / 12:.2f} ft", (M_pos_x / 12, M_pos / 12),
                    (M_pos_x / 12 - 2, M_pos / 12 + 2500), fontsize=8)
    axs[1].annotate(f"{M_roller / 12:,.0f} (roller)", (L1 / 12, M_roller / 12), (L1 / 12 + 0.3, M_roller / 12 - 3500), fontsize=8)
    axs[2].annotate(f"{v_min:.5f} in at x = {x_vmin / 12:.2f} ft", (x_vmin / 12, v_min), (x_vmin / 12 - 3, v_min + 0.004), fontsize=8)
    axs[2].annotate(f"+{v_tip:.5f} in (tip)", (LT / 12, v_tip), (LT / 12 - 3.3, v_tip - 0.002), fontsize=8)
    fig.tight_layout()
    p = FIG / "vm.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_section():
    fig, ax = plt.subplots(figsize=(3.6, 3.6))
    bf = FE["section"]["bf"] if FE else 5.525
    col = "#cbd5e1"
    ax.add_patch(plt.Rectangle((-bf / 2, D / 2 - TF), bf, TF, color=col, ec="k"))
    ax.add_patch(plt.Rectangle((-bf / 2, -D / 2), bf, TF, color=col, ec="k"))
    ax.add_patch(plt.Rectangle((-TW / 2, -D / 2 + TF), TW, D - 2 * TF, color=col, ec="k"))
    ax.annotate("", (bf / 2 + 0.8, -D / 2), (bf / 2 + 0.8, D / 2), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(bf / 2 + 1.1, 0, f"$d$ = {D}", rotation=90, va="center", fontsize=8)
    ax.annotate("", (-bf / 2, D / 2 + 0.7), (bf / 2, D / 2 + 0.7), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(0, D / 2 + 1.1, f"$b_f$ = {bf}", ha="center", fontsize=8)
    ax.annotate(f"$t_f$ = {TF:.4f}", (-bf / 2 + 0.3, D / 2 - TF / 2), (-bf / 2 - 4.4, D / 2 - 2.4), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate(f"$t_w$ = {TW:.4f}", (-TW / 2, 0), (-bf / 2 - 4.4, -1.0), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.text(0, -D / 2 - 1.4, "A = 9.12 in², I = 375 in⁴", ha="center", fontsize=8)
    ax.set_xlim(-bf / 2 - 4.6, bf / 2 + 2)
    ax.set_ylim(-D / 2 - 2.2, D / 2 + 2)
    ax.set_aspect("equal")
    ax.axis("off")
    p = FIG / "section.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


# ---------------------------------------------------------------- report helpers
def bm(M, scale, fmt_="{:.4g}"):
    rows = [" & ".join(("0" if abs(v) < 1e-12 else fmt_.format(v / scale)) for v in r) for r in M]
    return r"\begin{bmatrix}" + r" \\ ".join(rows) + r"\end{bmatrix}"


def pct(a, b):
    """Percent difference of magnitudes (ANSYS vs. reference)."""
    return "—" if abs(b) < 1e-12 else f"{(abs(a) - abs(b)) / abs(b) * 100:+.2f}"


def build():
    r = Report("HW 5: Beam Element", "W16x31 beam, fixed at the wall with a roller and a 5 ft overhang · "
               "ANSYS Workbench beam model · Statics and mechanics-of-materials validation",
               due="Sun Oct 11, 2026, 11:59 PM (submitted late)")
    r.h2("Problem")
    r.p("A W16x31 wide-flange beam ($A = 9.12\\ \\text{in}^2$, $d = 15.88$ in, $I = 375\\ \\text{in}^4$, "
        "$E = 29\\times10^6$ psi) is fixed at the wall (node 1) and rests on a roller at node 2. Element (1) "
        "is 10 ft long and carries 1000 lb/ft. Element (2) is a 5 ft overhang with a 500 lb load at its "
        "middle. Using ANSYS Workbench, find (1) the FE model with all BCs and loads, (2) the total "
        "deformation, (3) the Y deformation, (4) the maximum bending stress from the Beam Tool and (5) the "
        "reactions, then (6) validate them with statics and mechanics of materials.")
    if HANDOUT_PAGE.exists():
        r.img(fig_handout(), "Beam and loading (from the assignment handout).", width="45%", border=False)
    r.table(["Quantity", "Value", "In lb–in units"], [
        ["Area A", "9.12 in²", "9.12 in²"], ["Depth d (c = d/2)", "15.88 in", f"c = {C:.2f} in"],
        ["Second moment I", "375 in⁴", "375 in⁴"], ["Modulus E", "29×10⁶ psi", f"EI = {EI / 1e10:.4f}×10¹⁰ lb·in²"],
        ["Element (1) length, load", "10 ft, 1000 lb/ft", f"{L1:.0f} in, w = {W:.4f} lb/in"],
        ["Element (2) length", "5 ft", f"{L2:.0f} in"], ["Point load P", "500 lb at mid-element (2)", f"x = {A_P:.0f} in"],
    ], "Given data (handout). Sign convention: x from the wall, y and v up, CCW moments and rotations positive.")

    # ------------------------------------------------ FE hand solution
    r.h2("Finite element hand solution (two beam elements)")
    r.p("This is the hand version of what ANSYS does: two Euler–Bernoulli beam elements and three nodes, "
        "each node with deflection $v$ and rotation $\\theta$. It also checks the ANSYS model.")
    r.handcalc("Step 1: element stiffness matrices")
    r.eq(r"[k]^{(e)} = \frac{EI}{L^3}\begin{bmatrix} 12 & 6L & -12 & 6L \\ 6L & 4L^2 & -6L & 2L^2 \\ -12 & -6L & 12 & -6L \\ 6L & 2L^2 & -6L & 4L^2 \end{bmatrix}")
    r.step(r"\frac{EI}{L_1^3}", None, rf"\frac{{({fmt(E)})(375)}}{{120^3}}", EI / L1 ** 3, r"lb/in")
    r.step(r"\frac{EI}{L_2^3}", None, rf"\frac{{({fmt(E)})(375)}}{{60^3}}", EI / L2 ** 3, r"lb/in")
    r.eq(rf"[k]^{{(1)}} = 10^{{3}}\ {bm(k1, 1e3, '{:.7g}')}\quad (v_1, \theta_1, v_2, \theta_2)")
    r.eq(rf"[k]^{{(2)}} = 10^{{3}}\ {bm(k2, 1e3, '{:.7g}')}\quad (v_2, \theta_2, v_3, \theta_3)")
    r.p("Units: lb/in for force–deflection terms, lb for mixed terms, lb·in for moment–rotation terms.")
    r.end_handcalc()

    r.handcalc("Step 2: equivalent nodal loads")
    r.p("Uniform load on element (1) (work-equivalent): $f = \\{-\\tfrac{wL}{2}, -\\tfrac{wL^2}{12}, -\\tfrac{wL}{2}, +\\tfrac{wL^2}{12}\\}$. "
        "Point load at the middle of element (2): $f = \\{-\\tfrac{P}{2}, -\\tfrac{PL}{8}, -\\tfrac{P}{2}, +\\tfrac{PL}{8}\\}$.")
    r.step(r"\frac{wL_1}{2}", None, rf"\frac{{({W:.4f})(120)}}{{2}}", W * L1 / 2, "lb")
    r.step(r"\frac{wL_1^2}{12}", None, rf"\frac{{({W:.4f})(120)^2}}{{12}}", W * L1 ** 2 / 12, r"lb\cdot in")
    r.step(r"\frac{PL_2}{8}", None, r"\frac{(500)(60)}{8}", P * L2 / 8, r"lb\cdot in")
    r.eq(r"\{F\} = \begin{Bmatrix} F_1 \\ M_1 \\ F_2 \\ M_2 \\ F_3 \\ M_3 \end{Bmatrix} = "
         + r"\begin{Bmatrix}" + r" \\ ".join(f"{v:,.1f}".replace(",", r"\,") for v in Feq) + r"\end{Bmatrix}"
         + r"\ \begin{matrix} \text{lb} \\ \text{lb in} \\ \text{lb} \\ \text{lb in} \\ \text{lb} \\ \text{lb in} \end{matrix}")
    r.end_handcalc()

    r.handcalc("Step 3: assemble and apply the boundary conditions")
    r.eq(rf"[K] = 10^{{3}}\ {bm(K, 1e3, '{:.7g}')}")
    r.p("Wall: $v_1 = \\theta_1 = 0$. Roller: $v_2 = 0$. That strikes rows and columns 1, 2 and 3 and leaves "
        "three equations in $\\theta_2$, $v_3$ and $\\theta_3$:")
    r.eq(rf"10^{{3}}\ {bm(Kr, 1e3, '{:.7g}')} \begin{{Bmatrix}} \theta_2 \\ v_3 \\ \theta_3 \end{{Bmatrix}} = "
         rf"\begin{{Bmatrix}} {Feq[3]:,.1f} \\ {Feq[4]:,.1f} \\ {Feq[5]:,.1f} \end{{Bmatrix}}".replace(",", r"\,"))
    r.end_handcalc()

    r.handcalc("Step 4: solve for the nodal displacements")
    r.step(r"\theta_2", None, None, fmt(th2), "rad")
    r.step(r"v_3", None, None, f"{v3:.5f}", "in", "Positive: the tip moves up. The span load rotates the beam "
           "counter-clockwise over the roller, which lifts the overhang more than the 500 lb load pushes it down.")
    r.step(r"\theta_3", None, None, fmt(th3), "rad")
    r.end_handcalc()

    r.handcalc("Step 5: reactions")
    r.eq(r"\{R\} = [K]\{d\} - \{F\}")
    r.step(r"R_1", None, None, f"{R1_fe:,.1f}", "lb", "Up.")
    r.step(r"M_1", None, None, f"{M1_fe:,.0f}", r"lb\cdot in", f"= {M1_fe / 12:,.1f} lb·ft, counter-clockwise on the beam (hogging at the wall).")
    r.step(r"R_2", None, None, f"{R2_fe:,.1f}", "lb", "Up.")
    r.step(r"\sum F_y", r"R_1 + R_2 - wL_1 - P", f"{R1_fe:,.1f} + {R2_fe:,.1f} - {W * L1:,.0f} - 500".replace(",", r"\,"),
           "0" if abs(R1_fe + R2_fe - W * L1 - P) < 1e-6 else fmt(R1_fe + R2_fe - W * L1 - P), "lb", "Equilibrium holds.")
    r.end_handcalc()

    # ------------------------------------------------ statics + MoM
    r.pagebreak()
    r.h2("Validation by statics and mechanics of materials")
    r.img(fig_fbd(), "Free-body diagram with the reactions found below.", width="95%", border=False)
    r.handcalc("Statics: the beam is indeterminate to degree 1")
    r.p("Three unknowns ($R_1$, $M_1$, $R_2$) and two useful equilibrium equations ($\\sum F_y$, $\\sum M$), "
        "so one compatibility condition is needed: the roller does not move, $v(L_1) = 0$.")
    r.eq(r"\sum F_y = 0:\ R_1 + R_2 = wL_1 + P \qquad \sum M_{\text{wall}} = 0:\ M_1 = \frac{wL_1^2}{2} + P\,a - R_2 L_1,\quad a = 150\ \text{in}")
    r.end_handcalc()
    r.handcalc("Compatibility by superposition (release the roller: cantilever + redundant R₂)")
    r.step(r"v_w(L_1)", r"-\frac{wL_1^4}{8EI}", rf"-\frac{{({W:.4f})(120)^4}}{{8({fmt(EI)})}}", f"{dw_L1:.6f}", "in")
    r.step(r"v_P(L_1)", r"-\frac{P L_1^2 (3a - L_1)}{6EI}", rf"-\frac{{(500)(120)^2(450 - 120)}}{{6({fmt(EI)})}}", f"{dP_L1:.6f}", "in",
           "Cantilever point load at a = 150 in, deflection at x = 120 in < a.")
    r.step(r"v_R(L_1)", r"+\frac{R_2 L_1^3}{3EI}", None, rf"{fmt(dR_L1)}\,R_2", "in")
    r.step(r"R_2", r"\frac{-(v_w + v_P)}{L_1^3/3EI}", rf"\frac{{{-(dw_L1 + dP_L1):.6f}}}{{{fmt(dR_L1)}}}", f"{R2:,.2f}", "lb")
    r.step(r"R_1", r"wL_1 + P - R_2", rf"{W * L1:,.0f} + 500 - {R2:,.2f}".replace(",", r"\,"), f"{R1:,.2f}", "lb")
    r.step(r"M_1", r"\frac{wL_1^2}{2} + Pa - R_2L_1", rf"{W * L1 ** 2 / 2:,.0f} + {P * A_P:,.0f} - ({R2:,.2f})(120)".replace(",", r"\,"),
           f"{M1:,.0f}", r"lb\cdot in", f"= {M1 / 12:,.1f} lb·ft. Same as the FE hand solution.")
    r.end_handcalc()

    r.handcalc("Shear and moment, maximum bending stress")
    r.eq(r"M(x) = -M_1 + R_1 x - \frac{w x^2}{2}\quad (0 \le x \le 120\ \text{in})")
    r.step(r"x_{V=0}", r"\frac{R_1}{w}", rf"\frac{{{R1:,.2f}}}{{{W:.4f}}}".replace(",", r"\,"), f"{M_pos_x:.2f}", "in", f"= {M_pos_x / 12:.3f} ft")
    r.step(r"M_{+,\max}", r"-M_1 + \frac{R_1^2}{2w}", None, f"{M_pos:,.0f}", r"lb\cdot in", "Largest sagging moment in the span.")
    r.step(r"M(L_1)", r"-P\,(a - L_1)", r"-(500)(30)", f"{M_roller:,.0f}", r"lb\cdot in", "Hogging over the roller (from the overhang).")
    r.step(r"|M|_{\max}", r"M_1", None, f"{M_max:,.0f}", r"lb\cdot in", "At the wall.")
    r.step(r"\sigma_{\max}", r"\frac{M_{\max}\,c}{I}", rf"\frac{{({M_max:,.0f})(7.94)}}{{375}}".replace(",", r"\,"), f"{sig_max:,.0f}", "psi",
           "Tension on top, compression on the bottom flange at the wall.")
    r.step(r"\sigma_{+}", r"\frac{M_{+}\,c}{I}", None, f"{sig_pos:,.0f}", "psi", "Peak in the span (bottom in tension).")
    r.end_handcalc()

    r.handcalc("Deflections (double integration and superposition)")
    r.eq(r"EI\,v(x) = -\frac{M_1 x^2}{2} + \frac{R_1 x^3}{6} - \frac{w x^4}{24},\qquad v(0) = v'(0) = 0")
    r.eq(r"v'(x) = 0:\quad \frac{w}{6}x^2 - \frac{R_1}{2}x + M_1 = 0")
    r.step(r"x_{v,\min}", r"\frac{3R_1 - \sqrt{9R_1^2 - 24\,w\,M_1}}{2w}", None, f"{x_vmin:.2f}", "in",
           f"= {x_vmin / 12:.3f} ft (the other root lies outside the span).")
    r.step(r"v_{\min}", r"v(x_{v,\min})", None, f"{v_min:.5f}", "in", "Largest downward deflection (in the span).")
    r.step(r"\theta_2", r"\frac{1}{EI}\left(-M_1L_1 + \frac{R_1L_1^2}{2} - \frac{wL_1^3}{6}\right)", None, fmt(th2_mom), "rad", "Same as the FE value.")
    r.p("Tip deflection by superposition on the cantilever (deflection at the end of a loaded length plus its "
        "slope times the remaining length):")
    r.step(r"v_{\text{tip},w}", r"-\frac{wL_1^4}{8EI} - \frac{wL_1^3}{6EI}(60)", None, f"{tip_w:.5f}", "in")
    r.step(r"v_{\text{tip},P}", r"-\frac{Pa^3}{3EI} - \frac{Pa^2}{2EI}(30)", None, f"{tip_P:.5f}", "in")
    r.step(r"v_{\text{tip},R_2}", r"R_2\left(\frac{L_1^3}{3EI} + \frac{L_1^2}{2EI}(60)\right)", None, f"{tip_R:.5f}", "in")
    r.step(r"v_{\text{tip}}", r"v_{\text{tip},w} + v_{\text{tip},P} + v_{\text{tip},R_2}",
           f"{tip_w:.5f} {tip_P:+.5f} {tip_R:+.5f}", f"{v_tip:.5f}", "in", "Up. Same as $v_3$ from the FE hand solution.")
    r.step(r"v(150\ \text{in})", None, None, f"{v_150:.5f}", "in", "Under the 500 lb load (from the integrated curve).")
    r.end_handcalc()
    r.img(fig_vm(), "Shear force, bending moment and deflection from the hand solution.", width="90%", border=False)

    # ------------------------------------------------ ANSYS
    if FE:
        im = lambda k: HERE / "ansys_out" / f"{k}.png"  # noqa: E731
        sec = FE["section"]
        r.pagebreak()
        r.h2("ANSYS Workbench solution")
        r.bullets([
            "**Geometry:** a 15 ft line body along +X with vertices at the roller (10 ft) and at the 500 lb load "
            "(12.5 ft). Mechanical imports each edge as its own line body, so node merges join them at 10 ft and "
            "12.5 ft into one continuous beam.",
            "**Element:** BEAM188 (Timoshenko beam, quadratic), the Mechanical default for line bodies.",
            f"**Cross-section:** I-section with $d$ = 15.88 in and $b_f$ = 5.525 in (W16x31). The flange and web "
            f"thicknesses ($t_f$ = {sec['tf']:.4f} in, $t_w$ = {sec['tw']:.4f} in) are chosen so the section has "
            f"exactly the handout's $A$ = 9.12 in² and $I$ = 375 in⁴ (the AISC thicknesses give 367 in⁴ because "
            f"the fillets are left out). Mechanical reports A = {FE['cs_ansys']['A_in2']:.2f} in² and "
            f"I = {FE['cs_ansys']['IYY_in4']:.1f} in⁴, strong axis bending about Z.",
            "**Material:** Structural Steel with $E$ = 29×10⁶ psi as given (ν = 0.3).",
            "**Supports:** fixed support at node 1 (wall); displacement $u_y$ = 0 at node 2 (roller).",
            "**Loads:** line pressure 83.33 lb/in (1000 lb/ft) in −Y on element (1); 500 lb in −Y at x = 12.5 ft.",
            f"**Mesh:** {FE['mesh_study'][-1]['size_in']:.0f} in element size, {FE['elements']} elements, {FE['nodes']} nodes "
            "(converged; see the mesh study).",
        ])
        r.img(fig_section(), "Equivalent I-section used in ANSYS (in).", width="40%", border=False)
        r.img(im("model"), "Q1. FE model with all boundary conditions and loads (Static Structural selected): "
              "fixed support (A), roller (B), 1000 lb/ft line pressure (C), 500 lb force (D).")
        r.img(im("mesh"), f"Beam mesh ({FE['elements']} BEAM188 elements).")
        r.img(im("td"), f"Q2. Total deformation (in). Maximum {FE['td_max_in']:.5f} in at the free end.")
        r.img(im("td_iso"), "Q2. Total deformation, isometric view (deformation exaggerated).", width="80%")
        r.img(im("dy"), f"Q3. Directional deformation Y (in): {FE['dy_max_in']:+.5f} in at the tip, {FE['dy_min_in']:+.5f} in in the span.")
        bt = FE["beam_tool"]
        r.img(im("bt_maximum_bending_stress"), f"Q4. Beam Tool, maximum bending stress (psi): {bt['Maximum Bending Stress']['max_psi']:,.0f} psi at the wall.")
        r.img(im("bt_minimum_bending_stress"), f"Q4. Beam Tool, minimum bending stress (psi): {bt['Minimum Bending Stress']['min_psi']:,.0f} psi at the wall.")
        r.img(im("bt_direct_stress"), "Beam Tool, direct (axial) stress: zero, since no axial load acts.")
        r.img(im("bm"), f"Total bending moment (lb·in); maximum {FE['bm_max_lbfin']:,.0f} lb·in at the wall.")
        r.img(im("sf"), "Total shear force (lb).")
        rx = FE["reactions"]
        r.img(im("r1"), f"Q5. Force reaction at the wall: {rx['R1']['y']:,.1f} lb (+Y).")
        r.img(im("m1"), f"Q5. Moment reaction at the wall: {rx['M1']['z']:,.0f} lb·in (+Z, counter-clockwise).")
        r.img(im("r2"), f"Q5. Force reaction at the roller: {rx['R2']['y']:,.1f} lb (+Y).")

        r.h3("Mesh convergence")
        rows = [[f"{m['size_in']:.1f}", m["elements"], m["nodes"], f"{m['tip_in']:.6f}", f"{m['uy_min_in']:.6f}",
                 f"{m['R1_lbf']:,.1f}", f"{m['M1_lbfin']:,.0f}"] for m in FE["mesh_study"]]
        r.table(["Element size (in)", "Elements", "Nodes", "Tip v (in)", "Span v_min (in)", "R₁ (lb)", "M₁ (lb·in)"], rows,
                "ANSYS mesh study: the last two sizes agree to within 0.4%, so the 3 in mesh is converged.", cls="num")

        # ------------------------------------------------ comparison
        r.h2("Comparison and discussion")
        eb = FE["eb"]
        Rr = FE["reactions"]
        qty = [
            ("R₁, wall (lb)", R1, Rr["R1"]["y"], eb["R1_lbf"], TIM["R1"]),
            ("M₁, wall (lb·in)", M1, Rr["M1"]["z"], eb["M1_lbfin"], TIM["M1"]),
            ("R₂, roller (lb)", R2, Rr["R2"]["y"], eb["R2_lbf"], TIM["R2"]),
            ("Max bending stress (psi)", sig_max, bt["Maximum Bending Stress"]["max_psi"], eb["sb_max_psi"], TIM["sig"]),
            ("Tip deflection v₃ (in)", v_tip, FE["uy"]["180.0"], eb["tip_in"], TIM["tip"]),
            ("Max downward v, span (in)", v_min, FE["dy_min_in"], eb["dy_min_in"], TIM["vmin"]),
            ("v under the 500 lb load (in)", v_150, FE["uy"]["150.0"], eb["uy150_in"], None),
        ]

        def f_(v):
            return f"{v:.5f}" if abs(v) < 1 else f"{v:,.1f}" if abs(v) < 1e4 else f"{v:,.0f}"

        r.table(["Quantity", "Hand (statics + MoM = FE)", "ANSYS (BEAM188)", "% diff", "ANSYS, shear-rigid", "% diff"],
                [[q, f_(h), f_(a), pct(a, h), f_(e), pct(e, h)] for q, h, a, e, _ in qty],
                "Hand solution vs. ANSYS. The hand solution uses Euler–Bernoulli beam theory.", cls="num")
        force_err = max(abs(float(pct(Rr["R1"]["y"], R1))), abs(float(pct(Rr["R2"]["y"], R2))))
        mom_err = max(abs(float(pct(Rr["M1"]["z"], M1))), abs(float(pct(bt["Maximum Bending Stress"]["max_psi"], sig_max))))
        r.p(f"The force reactions agree to within {force_err:.1f}%, and the wall moment and peak bending stress to within {mom_err:.1f}%. The deflections differ more: the tip "
            f"deflection from ANSYS is {abs(float(pct(FE['uy']['180.0'], v_tip))):.1f}% larger than the hand value. The cause is shear "
            "deformation. BEAM188 is a Timoshenko element, so the web's shear strain adds deflection, while the hand "
            "solution (and the two-element FE hand model) is Euler–Bernoulli and ignores it. This beam is deep for its "
            f"length (span/depth = {L1 / D:.1f}, overhang/depth = {L2 / D:.1f}), so the shear term is not negligible. "
            "Extra shear flexibility in the span also lets the roller pick up a little more load, which lowers the "
            "wall reaction and wall moment, and with them the peak bending stress.")
        eb_err = max(abs((e - h) / h) * 100 for _, h, _a, e, _t in qty)
        tim_err = max(abs((a - t) / t) * 100 for _, _h, a, _e, t in qty if t is not None)
        r.p("Two checks confirm this explanation:")
        r.bullets([
            "**ANSYS with shear deformation removed.** A copy of the analysis re-declares the same I-section in APDL "
            "with `SECCONTROL` transverse shear stiffness of 10¹² lb (about 10⁵ times the real value), which turns "
            "BEAM188 into an Euler–Bernoulli beam. Its results (\"shear-rigid\" column) match the hand solution to "
            f"within {eb_err:.2f}%.",
            f"**Hand Timoshenko estimate.** Repeating the superposition with a shear term $v_s' = -V/(G A_s)$, "
            f"$G = E/2(1+\\nu)$ = {G / 1e6:.2f}×10⁶ psi and web shear area $A_s = (d - t_f)\\,t_w$ = {AS:.2f} in², gives "
            f"R₁ = {TIM['R1']:,.1f} lb, M₁ = {TIM['M1']:,.0f} lb·in, σ = {TIM['sig']:,.0f} psi and a tip deflection of "
            f"{TIM['tip']:.5f} in, all within {tim_err:.1f}% of the default ANSYS results.",
        ])
        r.table(["Quantity", "Hand, Timoshenko estimate", "ANSYS (BEAM188)", "% diff"],
                [[q, f_(t), f_(a), pct(a, t)] for q, h, a, e, t in qty if t is not None],
                "Hand estimate with shear deformation vs. default ANSYS.", cls="num")

        r.h2("Answers")
        r.table(["#", "Item", "ANSYS (BEAM188)", "Hand (Euler–Bernoulli)"], [
            ["1", "FE model, BCs and loads", "Figures above (fixed support, roller, 1000 lb/ft, 500 lb)", "Free-body diagram"],
            ["2", "Total deformation, max", f"{FE['td_max_in']:.5f} in (tip)", f"{abs(v_tip):.5f} in (tip)"],
            ["3", "Y deformation", f"{FE['dy_max_in']:+.5f} in tip; {FE['dy_min_in']:+.5f} in span",
             f"{v_tip:+.5f} in tip; {v_min:+.5f} in at x = {x_vmin / 12:.2f} ft"],
            ["4", "Max bending stress (Beam Tool)", f"{bt['Maximum Bending Stress']['max_psi']:,.0f} psi (wall)", f"{sig_max:,.0f} psi (wall)"],
            ["5", "Reactions", f"R₁ = {Rr['R1']['y']:,.1f} lb, M₁ = {Rr['M1']['z']:,.0f} lb·in, R₂ = {Rr['R2']['y']:,.1f} lb",
             f"R₁ = {R1:,.1f} lb, M₁ = {M1:,.0f} lb·in, R₂ = {R2:,.1f} lb"],
            ["6", "Validation", f"Shear-rigid ANSYS run matches the hand solution to {eb_err:.2f}%", "Statics + MoM = FE hand solution"],
        ], "Summary of the requested results.")
    out = r.docx(OUT_DOCX)
    print("wrote", out)


if __name__ == "__main__":
    print(f"FE: th2 {th2:.6e} v3 {v3:.6f} th3 {th3:.6e}  R1 {R1:.2f} M1 {M1:.1f} R2 {R2:.2f}")
    print(f"MoM: sig_max {sig_max:.1f} psi, M+ {M_pos:.0f} at {M_pos_x:.2f}, vmin {v_min:.6f} at {x_vmin:.2f}, v150 {v_150:.6f}")
    print("Timoshenko:", {k: round(v, 6) for k, v in TIM.items()})
    build()
