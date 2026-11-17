"""In-class tutorial (1D element, truss, beam): hand FE / statics / MoM validation, ANSYS comparison -> Word.

    python solve.py            (reads ansys_out/q*_results.json from ansys_q1.py, ansys_q2.py, ansys_q3.py)
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "InClass_1D_Truss_Beam.docx"
HANDOUT = HERE.parents[1] / "canvas" / "files" / "_extract" / "In_Class_Tutorial_1D_Truss_Beam_V2" / "img"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
AO = HERE / "ansys_out"
PSI = 6894.757293168
LBF, LBFIN = 4.4482216152605, 0.1129848290276167


def load(name):
    p = AO / name
    return json.loads(p.read_text()) if p.exists() else None


FE1, FE2, FE3 = load("q1_results.json"), load("q2_results.json"), load("q3_results.json")


def pct(fe, hand):
    if abs(hand) < 1e-9:
        return "— (both ≈ 0)" if abs(fe) < 1e-3 else "—"
    return f"{abs(fe - hand) / abs(hand) * 100:.3f}"


def th(x, d=1):
    """Thousands separator that survives TeX (thin space)."""
    return f"{x:,.{d}f}".replace(",", r"\,")


def sci(x, d=4):
    """TeX scientific notation: 9.9197 x 10^-4."""
    m, e = f"{x:.{d}e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"


def crop(page, box, name):
    """Cut a figure out of a rendered handout page (local only; the Word file is gitignored)."""
    p = FIG / name
    Image.open(HANDOUT / page).crop(box).save(p)
    return p


# ===================================================================== Q1 stepped shaft (lb, in)
E1 = 29e6                      # psi, as in the handout's validation (ANSYS Structural Steel: 200 GPa)
E1_ANSYS = 200e9 / PSI
L1 = np.array([10.0, 12.0])
A1 = np.array([0.8, 0.5])
P1 = 3500.0
k1 = A1 * E1 / L1
K1 = np.zeros((3, 3))
for e in range(2):
    K1[e:e + 2, e:e + 2] += k1[e] * np.array([[1, -1], [-1, 1]])
F1v = np.array([0.0, P1, 0.0])
uB = P1 / (k1[0] + k1[1])
U1 = np.array([0.0, uB, 0.0])
R1v = K1 @ U1 - F1v
sig1 = E1 * np.diff(U1) / L1
force1 = sig1 * A1
uD, uF = uB * 4.0 / 10.0, uB * 5.0 / 12.0           # linear inside each element
uB_ansysE = P1 / ((A1 * E1_ANSYS / L1).sum())

# ===================================================================== Q2 two-bar truss (lb, in)
P2, A2, E2, L2 = 200.0, 2.3, 10e6, 36.0
th2 = math.radians(60)
F2 = -P2 / (2 * math.sin(th2))                       # both members, compression
sig2 = F2 / A2
R2x = -F2 * math.cos(th2)                            # support 1, +x (member pushes it down-left)
R2y = P2 / 2
kA = 2 * A2 * E2 / L2 * math.sin(th2) ** 2           # vertical stiffness at A (horizontal terms cancel)
uAy = -P2 / kA
u_axial = uAy * math.cos(math.radians(30))           # handout: u_3x' = u_3Y cos 30

# ===================================================================== Q3 overhanging beam (lb, in)
P3, L3, a3, I3, E3 = 50e3, 180.0, 48.0, 722.0, 29e6
D3 = 14.0
c3 = D3 / 2
G3 = E3 / (2 * 1.3)
RA3 = -P3 * a3 / L3                                  # + up: the pin pulls down
RB3 = P3 * (L3 + a3) / L3
MB3 = -P3 * a3                                       # hogging moment over the roller
sig3 = abs(MB3) * c3 / I3
xk = L3 / math.sqrt(3)
ymax_AB = P3 * a3 * L3 ** 2 / (9 * math.sqrt(3) * E3 * I3)       # upward
yC = -P3 * a3 ** 2 * (L3 + a3) / (3 * E3 * I3)
xs3 = np.linspace(0, L3 + a3, 2281)
V3 = np.where(xs3 < L3, RA3, RA3 + RB3)
M3 = np.where(xs3 <= L3, RA3 * xs3, -P3 * (L3 + a3 - xs3))
y3 = np.where(xs3 <= L3, P3 * a3 / (6 * E3 * I3 * L3) * (L3 ** 2 * xs3 - xs3 ** 3),
              -P3 * a3 * L3 / (3 * E3 * I3) * (xs3 - L3)
              - P3 / (6 * E3 * I3) * ((xs3 - L3) ** 2 * (3 * a3 - (xs3 - L3))))


# ===================================================================== figures
def fig_q1():
    X = [0, 4, 10, 17, 22]
    u = [0, uD, uB, uF, 0]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 4.4), sharex=True)
    a1.plot([0, 10, 22], [0, uB * 1e4, 0], "-", color="#1f4e79", label="Hand FE (two linear elements)")
    if FE1:
        a1.plot([4, 10, 17], [FE1["u"][k] * 1e4 for k in ("D", "B", "F")], "x", ms=10, color="#c00000",
                label="ANSYS probes at D, B, F")
    for xx, uu, lab in zip(X[1:4], u[1:4], "DBF"):
        a1.annotate(lab, (xx, uu * 1e4), textcoords="offset points", xytext=(4, 6), fontsize=8)
    a1.set_ylabel("u (10⁻⁴ in)")
    a1.legend(fontsize=8, loc="upper right")
    a1.grid(alpha=.3)
    for e, (x0, x1) in enumerate(((0, 10), (10, 22))):
        a2.hlines(sig1[e], x0, x1, color="#1f4e79", lw=2.5)
        a2.text((x0 + x1) / 2, sig1[e] + (250 if sig1[e] > 0 else -600),
                f"({e + 1}) {sig1[e]:,.0f} psi {'T' if sig1[e] > 0 else 'C'}", ha="center", fontsize=8)
    a2.axhline(0, color="k", lw=.6)
    a2.set_ylabel("σ (psi)")
    a2.set_xlabel("x (in)")
    a2.set_ylim(-3500, 3800)
    a2.grid(alpha=.3)
    fig.tight_layout()
    p = FIG / "q1_u_sigma.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q2():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1, 1.05]})
    J = {"1": (0, 0), "A": (18, 36 * math.sin(th2)), "2": (36, 0)}
    for m in ("1A", "A2"):
        (xa, ya), (xb, yb) = J[m[0]], J[m[1]]
        a1.plot([xa, xb], [ya, yb], color="#c00000", lw=3)
        a1.text((xa + xb) / 2 + (-15 if m == "1A" else 1.5), (ya + yb) / 2, f"{abs(F2):.2f} lb C", fontsize=8, color="#c00000")
    for j, (x, y) in J.items():
        a1.plot(x, y, "o", color="k", ms=5)
        a1.text(x + 1, y + 1.2, j, fontsize=9, weight="bold")
    a1.annotate("", xy=J["A"], xytext=(18, 31.2 + 9), arrowprops=dict(arrowstyle="-|>", lw=1.4))
    a1.text(19, 37, "200 lb", fontsize=8)
    for j, sx in (("1", 1), ("2", -1)):
        x, y = J[j]
        a1.annotate("", xy=(x, y), xytext=(x, y - 8), arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.4))
        a1.annotate("", xy=(x, y), xytext=(x - sx * 8, y), arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.4))
        a1.text(x - 7 if sx > 0 else x - 2, y - 11, f"{R2y:.0f} lb", fontsize=7.5, color="#2e7d32")
        a1.text(x - sx * 9 - (6 if sx > 0 else 0), y + 1.5, f"{R2x:.2f} lb", fontsize=7.5, color="#2e7d32")
    a1.set_aspect("equal")
    a1.set_xlim(-14, 50)
    a1.set_ylim(-13, 42)
    a1.axis("off")
    a1.set_title("Member forces and reactions (statics)", fontsize=9)
    # free body of joint A
    a2.set_aspect("equal")
    for ang, lab in ((240, "F$_{1A}$"), (300, "F$_{A2}$")):
        r_ = math.radians(ang)
        a2.annotate("", xy=(1.6 * math.cos(r_) * 0, 0), xytext=(1.6 * math.cos(r_), 1.6 * math.sin(r_)),
                    arrowprops=dict(arrowstyle="-|>", lw=1.5, color="#c00000"))
        a2.text(1.9 * math.cos(r_) - 0.3, 1.9 * math.sin(r_), lab, fontsize=9, color="#c00000")
    a2.annotate("", xy=(0, -1.6), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    a2.text(0.1, -1.4, "200 lb", fontsize=8)
    a2.plot(0, 0, "o", color="k")
    a2.text(0.15, 0.15, "A", weight="bold")
    a2.text(-2.3, 1.2, "Compressive members\npush on joint A", fontsize=8)
    a2.set_xlim(-2.5, 2.5)
    a2.set_ylim(-2.2, 2.0)
    a2.axis("off")
    a2.set_title("Free body of joint A (60° members)", fontsize=9)
    fig.tight_layout()
    p = FIG / "q2_statics.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q3():
    fig, (a1, a2, a3_) = plt.subplots(3, 1, figsize=(7.2, 6.4), sharex=True)
    a1.fill_between(xs3, V3 / 1e3, step="post", alpha=.25, color="#1f4e79")
    a1.plot(xs3, V3 / 1e3, color="#1f4e79", label="Statics")
    a2.fill_between(xs3, M3 / 1e3, alpha=.25, color="#1f4e79")
    a2.plot(xs3, M3 / 1e3, color="#1f4e79", label="Statics")
    a3_.plot(xs3, y3, color="#1f4e79", label="Elastic curve (Euler–Bernoulli)")
    if FE3 and "smd" in FE3:
        s = FE3["smd"]
        xa = np.array(s["X Coordinate"]) / 0.0254
        va = -np.array(s["SFZ"]) / LBF / 1e3
        ma = -np.array(s["MY"]) / LBFIN / 1e3
        ua = np.array(s["UZ"]) / 0.0254
        a1.plot(xa[::4], va[::4], "x", ms=4, color="#c00000", label="ANSYS shear-moment diagram")
        a2.plot(xa[::4], ma[::4], "x", ms=4, color="#c00000", label="ANSYS shear-moment diagram")
        a3_.plot(xa[::4], ua[::4], "x", ms=4, color="#c00000", label="ANSYS (BEAM188, with shear deformation)")
    a1.set_ylabel("V (kips)")
    a1.axhline(0, color="k", lw=.6)
    a1.grid(alpha=.3)
    a1.legend(fontsize=8, loc="center left", bbox_to_anchor=(0.02, 0.62))
    a2.set_ylabel("M (kip·in)")
    a2.axhline(0, color="k", lw=.6)
    a2.grid(alpha=.3)
    a2.annotate(f"M_B = {MB3 / 1e3:,.0f} kip·in", xy=(L3, MB3 / 1e3), xytext=(110, MB3 / 1e3 * 0.8), ha="center",
                arrowprops=dict(arrowstyle="->"), fontsize=8)
    a3_.set_ylabel("y (in)")
    a3_.set_xlabel("x (in)")
    a3_.axhline(0, color="k", lw=.6)
    a3_.grid(alpha=.3)
    a3_.legend(fontsize=8, loc="lower left")
    a3_.annotate(f"y_max(AB) = {ymax_AB:.3f} in at x = L/√3", xy=(xk, ymax_AB), xytext=(xk, -0.25), ha="center",
                 arrowprops=dict(arrowstyle="->"), fontsize=8)
    for ax in (a1, a2, a3_):
        for xx, lab in ((0, "A"), (L3, "B"), (L3 + a3, "C")):
            ax.axvline(xx, color="#999", lw=.6, ls=":")
    a1.text(0, a1.get_ylim()[1] * 0.85, " A", fontsize=8)
    a1.text(L3, a1.get_ylim()[1] * 0.85, " B", fontsize=8)
    a1.text(L3 + a3 - 8, a1.get_ylim()[1] * 0.85, "C", fontsize=8)
    fig.tight_layout()
    p = FIG / "q3_sfd_bmd_y.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ===================================================================== report
def im(name):
    return AO / f"{name}.png"


def q1(r):
    r.h2("Q1. 1D element: stepped shaft")
    r.p("A round stepped shaft is fixed at both walls and carries 3500 lb along its axis at the step B. "
        "Element (1): 10 in long, $A = 0.8$ in²; element (2): 12 in long, $A = 0.5$ in². Structural steel. "
        "Points D (4 in from the left wall) and F (5 in from the right wall) are marked on the figure.")
    r.img(crop("page01.png", (115, 515, 785, 735), "handout_q1.png"), "Stepped shaft (from the handout).",
          width="70%", border=False)

    if FE1:
        r.h3("a–d. ANSYS Workbench")
        r.bullets([
            "**Geometry:** a 22 in line body along x, split at B (10 in) and at the probe points D (4 in) and F "
            "(17 in); the segments are joined by node merge.",
            "**Cross-sections:** solid circles, d = " + ", ".join(f"{2 * math.sqrt(a / math.pi):.4f} in" for a in A1)
            + f" for elements (1) and (2) (ANSYS areas {FE1['cs_area']['1']:.5f} and {FE1['cs_area']['2']:.5f} in²).",
            "**Material:** ANSYS Structural Steel, as the handout says (E = 200 GPa = "
            f"{E1_ANSYS / 1e6:.4f}×10⁶ psi, ν = 0.3).",
            f"**Elements:** BEAM188 line elements, 1 in element size ({FE1['elements']} elements, {FE1['nodes']} nodes). "
            "With only an axial load the beam elements act as 1D bars.",
            "**Boundary conditions and load:** fixed supports at both walls; 3500 lb in +x at B.",
        ])
        r.img(im("q1_model"), "a. Finite element model: fixed walls (A, B in the ANSYS legend) and the 3500 lb load at "
                              "point B (legend C).")
        r.img(im("q1_ux"), f"b. Directional deformation along the shaft axis (in). Point B moves "
                           f"u_B = {FE1['u']['B']:.4e} in (the maximum).")
        r.img(im("q1_r1"), f"c. Reaction at the left wall: {FE1['rW1']['x']:,.1f} lb (x).")
        r.img(im("q1_r2"), f"c. Reaction at the right wall: {FE1['rW2']['x']:,.1f} lb (x).")
        bt = FE1["beam_tool"]["Direct Stress"]
        r.img(im("q1_direct_stress"), f"d. Beam Tool, direct stress (psi): element (1) {bt['max_psi']:,.1f} psi "
                                      f"(tension), element (2) {bt['min_psi']:,.1f} psi (compression).")

    r.h3("Validation: finite element hand solution, statics and mechanics of materials")
    r.handcalc("Element stiffnesses and global system")
    r.eq(r"[k]^{(e)} = \frac{A_e E}{\ell_e}\begin{bmatrix} 1 & -1 \\ -1 & 1 \end{bmatrix}, \qquad E = 29\times10^6\ \text{psi}")
    for e in range(2):
        r.step(rf"k_{e + 1}", rf"\frac{{A_{e + 1}E}}{{\ell_{e + 1}}}", rf"\frac{{({A1[e]:g})(29\times10^6)}}{{{L1[e]:g}}}",
               th(k1[e]), "lb/in")
    r.eq(r"\begin{bmatrix} k_1 & -k_1 & 0 \\ -k_1 & k_1 + k_2 & -k_2 \\ 0 & -k_2 & k_2 \end{bmatrix}"
         r"\begin{Bmatrix} u_1 \\ u_2 \\ u_3 \end{Bmatrix} = \begin{Bmatrix} R_1 \\ 3500 \\ R_3 \end{Bmatrix},"
         r"\qquad u_1 = u_3 = 0\ \text{(walls)}")
    r.end_handcalc()
    r.handcalc("Displacement of B, reactions and element stresses")
    r.step(r"u_2 = u_B", r"\frac{P}{k_1 + k_2}", rf"\frac{{3500}}{{{th(k1[0])} + {th(k1[1])}}}", f"{sci(uB)}", "in")
    r.step("R_1", r"-k_1 u_2", rf"-({th(k1[0])})({sci(uB)})", th(R1v[0]), "lb", "Acts toward −x (on the shaft).")
    r.step("R_3", r"-k_2 u_2", rf"-({th(k1[1])})({sci(uB)})", th(R1v[2]), "lb", "Acts toward −x.")
    r.step(r"\sum F_x", "R_1 + R_3 + P", rf"{th(R1v[0])} + ({th(R1v[2])}) + 3500", f"{R1v.sum() + P1:.1f}", "lb",
           "Statics: equilibrium is satisfied.")
    r.step(r"\sigma^{(1)}", r"E\,\frac{u_2 - u_1}{\ell_1}", rf"(29\times10^6)\frac{{{sci(uB)} - 0}}{{10}}", th(sig1[0]), "psi",
           f"Tension; force = σA = {force1[0]:,.1f} lb = |R₁| (mechanics of materials).")
    r.step(r"\sigma^{(2)}", r"E\,\frac{u_3 - u_2}{\ell_2}", rf"(29\times10^6)\frac{{0 - {sci(uB)}}}{{12}}", th(sig1[1]), "psi",
           f"Compression; force = σA = {force1[1]:,.1f} lb = R₃.")
    r.step("u_D", r"\tfrac{4}{10}\,u_B", rf"0.4({sci(uB)})", f"{sci(uD)}", "in", "Linear displacement inside element (1).")
    r.step("u_F", r"\tfrac{5}{12}\,u_B", rf"\tfrac{{5}}{{12}}({sci(uB)})", f"{sci(uF)}", "in", "Linear inside element (2).")
    r.end_handcalc()
    r.img(fig_q1(), "Displacement and element stresses along the shaft: hand FE (lines) and ANSYS probes (×).",
          width="85%", border=False)

    if FE1:
        st = {e: FE1["stress_psi"][str(e)] for e in (1, 2)}
        r.table(["Output Results", "Hand FE / statics / MoM", "ANSYS WB", "% Error"],
                [["Reaction force, left wall", f"{R1v[0]:,.1f} lb", f"{FE1['rW1']['x']:,.1f} lb", pct(FE1['rW1']['x'], R1v[0])],
                 ["Reaction force, right wall", f"{R1v[2]:,.1f} lb", f"{FE1['rW2']['x']:,.1f} lb", pct(FE1['rW2']['x'], R1v[2])],
                 ["Stress, element (1)", f"{sig1[0]:,.1f} psi", f"{st[1]:,.1f} psi", pct(st[1], sig1[0])],
                 ["Stress, element (2)", f"{sig1[1]:,.1f} psi", f"{st[2]:,.1f} psi", pct(st[2], sig1[1])],
                 ["Deflection of B", f"{uB:.4e} in", f"{FE1['u']['B']:.4e} in", pct(FE1['u']['B'], uB)],
                 ["Deflection of D (extra)", f"{uD:.4e} in", f"{FE1['u']['D']:.4e} in", pct(FE1['u']['D'], uD)],
                 ["Deflection of F (extra)", f"{uF:.4e} in", f"{FE1['u']['F']:.4e} in", pct(FE1['u']['F'], uF)]],
                "Q1 validation: hand calculation vs. ANSYS", cls="num")
        r.p("The reactions and stresses agree to round-off; they do not depend on E, because both elements have the "
            "same E. The displacements are "
            f"{pct(FE1['u']['B'], uB)} % smaller in ANSYS because its Structural Steel has E = 200 GPa = "
            f"{E1_ANSYS / 1e6:.4f}×10⁶ psi instead of the 29×10⁶ psi used by hand: with ANSYS's E the hand value is "
            f"u_B = {uB_ansysE:.4e} in ({pct(FE1['u']['B'], uB_ansysE)} % from ANSYS). The Beam Tool contour reads "
            f"{bt['max_psi']:,.1f} and {bt['min_psi']:,.1f} psi, a few psi off because ANSYS builds each circle from "
            "a polygon whose area is about 0.005 % smaller; the table uses axial force ÷ ANSYS area.")
        r.table(["Element size (in)", "Elements", "u_B (in)", "R, left wall (lb)"],
                [[f"{s['size_in']:g}", s["elements"], f"{s['uB']:.6e}", f"{s['R1']:,.2f}"] for s in FE1["mesh_study"]],
                "Mesh refinement: no change, because a bar with end loads has a linear displacement field that the "
                "element reproduces exactly", cls="num")


def q2(r):
    r.pagebreak()
    r.h2("Q2. Truss")
    r.p("Two 36 in members at 60° to the horizontal meet at A and are pinned to the ground at both supports. "
        "A = 2.3 in², aluminum alloy with E = 10×10⁶ psi. A 200 lb load acts downward at A.")
    r.img(crop("page04.png", (240, 680, 590, 950), "handout_q2.png"), "Truss (from the handout).", width="45%", border=False)

    if FE2:
        r.h3("a–d. ANSYS Workbench")
        r.bullets([
            "**Geometry:** two 36 in line bodies from the supports (0, 0) and (36, 0) in to A (18, 31.177) in, "
            "joined at A by node merge.",
            f"**Cross-section:** square {math.sqrt(A2):.4f} in × {math.sqrt(A2):.4f} in, so the area is exactly "
            f"{FE2['cs_area']:.2f} in². **Material:** custom Engineering Data entry, E = 10×10⁶ psi, ν = 0.33.",
            f"**Elements:** BEAM188 line elements (needed for the Beam Tool), 2 in element size ({FE2['elements']} elements).",
            "**Supports:** pins at both supports, $u_x = u_y = u_z = 0$. With beam elements the two-bar frame could "
            "swing out of plane about the line through its supports, so the out-of-plane rotations (about x and y) are "
            "also held at the supports; the in-plane rotation stays free, so the supports are still pins.",
            "**Load:** 200 lb in −y at A.",
        ])
        r.img(im("q2_model"), "a. Finite element model: pins at supports 1 and 2 (legend A–D) and the 200 lb load at "
                              "point A (legend E).", width="70%")
        r.img(im("q2_dy"), f"b. Vertical deflection (in). Point A moves {FE2['uA']['y']:.4e} in (down); its horizontal "
                           f"movement is {abs(FE2['uA']['x']):.0e} in (symmetry).", width="70%")
        r.img_row([(im("q2_r1"), f"c. Reaction at support 1: Fx = {FE2['r1']['x']:.2f} lb, Fy = {FE2['r1']['y']:.2f} lb."),
                   (im("q2_r2"), f"c. Reaction at support 2: Fx = {FE2['r2']['x']:.2f} lb, Fy = {FE2['r2']['y']:.2f} lb.")])
        bt = FE2["beam_tool"]["Direct Stress"]
        r.img(im("q2_bt_direct_stress"), f"d. Beam Tool, direct stress (psi): {bt['min_psi']:.2f} psi in both members "
                                         "(compression).", width="70%")

    r.h3("Validation: statics and mechanics of materials")
    r.img(fig_q2(), "Statics of the truss: member forces, reactions and the free body of joint A.", width="95%", border=False)
    r.handcalc("Member forces (joint A) and reactions")
    r.step(r"\sum F_x = 0", r"F_{1A}\cos 60^\circ = F_{A2}\cos 60^\circ", None, r"F_{1A} = F_{A2} = F", "",
           "Symmetry: both members carry the same force.")
    r.step(r"\sum F_y = 0:\ F", r"-\frac{P}{2\sin 60^\circ}", rf"-\frac{{200}}{{2(0.8660)}}", f"{F2:.2f}", "lb",
           "Negative: both members are in compression.")
    r.step(r"\sigma^{(1)} = \sigma^{(2)}", r"\frac{F}{A}", rf"\frac{{{F2:.2f}}}{{2.3}}", f"{sig2:.3f}", "psi",
           "Compression.")
    r.step(r"R_{1y} = R_{2y}", r"\frac{P}{2}", r"\frac{200}{2}", f"{R2y:.0f}", "lb", "Upward.")
    r.step(r"R_{1x} = -R_{2x}", r"|F|\cos 60^\circ", rf"({abs(F2):.2f})(0.5)", f"{R2x:.2f}", "lb",
           "Support 1 pushes in +x and support 2 in −x: the horizontal thrust of the two struts.")
    r.end_handcalc()
    r.handcalc("Deflection of A (truss stiffness, as in the handout)")
    r.step(r"K_{yy}", r"2\,\frac{AE}{L}\sin^2 60^\circ", rf"2\,\frac{{(2.3)(10\times10^6)}}{{36}}(0.75)", th(kA), "lb/in",
           "Vertical stiffness at A; the horizontal terms of the two members cancel by symmetry.")
    r.step(r"U_{Ay}", r"-\frac{P}{K_{yy}}", rf"-\frac{{200}}{{{th(kA)}}}", f"{sci(uAy)}", "in")
    r.step(r"u'_{A}", r"U_{Ay}\cos 30^\circ", rf"({sci(uAy)})(0.8660)", f"{sci(u_axial)}", "in",
           "Displacement of A along each member (shortening).")
    r.step(r"\sigma", r"E\,\frac{u'_A - 0}{L}", rf"(10\times10^6)\frac{{{sci(u_axial)}}}{{36}}", f"{E2 * u_axial / L2:.3f}", "psi",
           "The handout's route: the same stress as from statics.")
    r.end_handcalc()

    if FE2:
        r.table(["Output Results", "Statics / MoM", "ANSYS WB", "% Error"],
                [["Reaction, support 1", f"Fx = {R2x:.2f} lb", f"Fx = {FE2['r1']['x']:.2f} lb", pct(FE2['r1']['x'], R2x)],
                 ["", f"Fy = {R2y:.2f} lb", f"Fy = {FE2['r1']['y']:.2f} lb", pct(FE2['r1']['y'], R2y)],
                 ["Reaction, support 2", f"Fx = {-R2x:.2f} lb", f"Fx = {FE2['r2']['x']:.2f} lb", pct(FE2['r2']['x'], -R2x)],
                 ["", f"Fy = {R2y:.2f} lb", f"Fy = {FE2['r2']['y']:.2f} lb", pct(FE2['r2']['y'], R2y)],
                 ["Stress, element (1)", f"{sig2:.3f} psi", f"{FE2['stress_psi']['1A']:.3f} psi", pct(FE2['stress_psi']['1A'], sig2)],
                 ["Stress, element (2)", f"{sig2:.3f} psi", f"{FE2['stress_psi']['A2']:.3f} psi", pct(FE2['stress_psi']['A2'], sig2)],
                 ["Deflection of A (vertical)", f"{uAy:.4e} in", f"{FE2['uA']['y']:.4e} in", pct(FE2['uA']['y'], uAy)]],
                "Q2 validation: statics / mechanics of materials vs. ANSYS", cls="num")
        r.p("The vertical reactions are exact. The member stresses and the deflection of A differ by less than 0.03 %, "
            "and the horizontal thrust by "
            f"{pct(FE2['r1']['x'], R2x)} %: ANSYS joins the members rigidly at A (beam elements, as the Beam Tool "
            "requires) while the hand solution assumes an ideal pin, so the members also carry a very small bending "
            f"moment (the Beam Tool's combined stress ranges from {FE2['beam_tool']['Minimum Combined Stress']['min_psi']:.2f} "
            f"to {FE2['beam_tool']['Maximum Combined Stress']['max_psi']:.2f} psi around the −50.20 psi direct stress).")
        r.table(["Element size (in)", "Elements", "U_Ay (in)", "Force in member 1-A (lb)"],
                [[f"{s['size_in']:g}", s["elements"], f"{s['uAy']:.6e}", f"{s['F1A']:.4f}"] for s in FE2["mesh_study"]],
                "Mesh refinement", cls="num")


def q3(r):
    r.pagebreak()
    r.h2("Q3. Beam")
    r.p("The overhanging W14×68 steel beam ABC is pinned at A, sits on a roller at B and carries P = 50 kips at the "
        "free end C. L = 180 in, a = 48 in, I = 722 in⁴, E = 29×10⁶ psi.")
    r.img(crop("page05.png", (110, 648, 828, 900), "handout_q3.png"), "Overhanging beam (from the handout).",
          width="85%", border=False)

    if FE3:
        sec = FE3["section"]
        r.h3("a–e. ANSYS Workbench")
        r.bullets([
            "**Geometry:** a 228 in line body along x, split at B (180 in) and at x = L/√3 = "
            f"{xk:.2f} in (where the hand solution puts the peak deflection of span AB), joined by node merge.",
            f"**Cross-section:** I-section with the W14×68 depth (14.0 in) and flange width (10.0 in); the flange and "
            f"web thicknesses (tf = {sec['tf']:.4f} in, tw = {sec['tw']:.4f} in) are chosen so that, without the "
            f"rolled fillets, A = {FE3['cs_ansys']['A_in2']:.2f} in² and I = {FE3['cs_ansys']['IYY_in4']:.1f} in⁴ "
            "match the handout.",
            "**Material:** custom steel entry, E = 29×10⁶ psi, ν = 0.3.",
            f"**Elements:** BEAM188, 2 in element size ({FE3['elements']} elements).",
            "**Supports:** pin at A ($u_x = u_y = u_z = 0$, twist about the beam axis held); roller at B "
            "($u_y = u_z = 0$, x free). **Load:** 50 000 lb in −y at C.",
        ])
        r.img(im("q3_model"), "a. Finite element model: pin at A (legend A, B), roller at B (legend C) and P = 50 kips "
                              "at C (legend D).")
        r.img(im("q3_dy"), f"b. Vertical deflection (in): the largest is {FE3['dy']['min']:.4f} in (down) at the free "
                           f"end C; span AB rises to {FE3['dy']['max']:.4f} in.")
        r.img(im("q3_ra"), f"c. Reaction at pin A: Fy = {FE3['rA']['y']:,.1f} lb (downward).")
        r.img(im("q3_rb"), f"c. Reaction at roller B: Fy = {FE3['rB']['y']:,.1f} lb (upward).")
        r.img(im("q3_sf"), f"d. Beam Results, total shear force (lb): {FE3['sf_max_lbf']:,.0f} lb maximum in the overhang BC.")
        r.img(im("q3_bm"), f"d. Beam Results, total bending moment (lb·in): {FE3['bm_max_lbfin']:,.0f} lb·in maximum over B. "
                           "The signed diagrams, read from Mechanical's Shear-Moment Diagram along the beam axis, are "
                           "plotted against statics in the validation below.")
        bt = FE3["beam_tool_psi"]
        r.img(im("q3_bt_maximum_bending_stress"), f"e. Beam Tool, maximum bending stress (psi): "
                                                  f"{bt['Maximum Bending Stress']['max']:,.1f} psi over the roller B; the direct "
                                                  "stress is zero everywhere (no axial force).")

    r.h3("Validation: statics, elastic curve and mechanics of materials")
    r.handcalc("Reactions (statics)")
    r.step(r"\sum F_x = 0:\ A_x", None, None, "0", "lb", "No horizontal load.")
    r.step(r"\sum M_B = 0:\ A_y", r"-\frac{P a}{L}", r"-\frac{(50\,000)(48)}{180}", th(RA3), "lb", "Downward (the pin holds A down).")
    r.step(r"\sum M_A = 0:\ B_y", r"\frac{P (L + a)}{L}", r"\frac{(50\,000)(228)}{180}", th(RB3), "lb", "Upward.")
    r.step(r"\sum F_y", r"A_y + B_y - P", rf"{th(RA3)} + {th(RB3)} - 50\,000", f"{RA3 + RB3 - P3:.1f}", "lb")
    r.end_handcalc()
    r.handcalc("Shear, moment and bending stress")
    r.step(r"V_{AB}", "A_y", None, th(RA3), "lb", "Constant from A to B.")
    r.step(r"V_{BC}", "A_y + B_y", None, th(RA3 + RB3), "lb", "Constant from B to C (= P).")
    r.step(r"M_B", r"-P a", r"-(50\,000)(48)", th(MB3, 0), r"lb\cdot in", "Largest |M|: hogging over the roller.")
    r.step(r"\sigma_{max}", r"\frac{|M_B|\,c}{I}", rf"\frac{{(2.4\times10^6)(7.0)}}{{722}}", th(sig3), "psi",
           "c = d/2 = 7.0 in; tension on top, compression on the bottom flange over B.")
    r.end_handcalc()
    r.handcalc("Elastic curve of span AB and maximum deflection (the textbook problem, parts a–c)")
    r.eq(r"EI\,y'' = M(x) = -\frac{P a}{L}x \quad\Rightarrow\quad EI\,y = -\frac{P a x^3}{6L} + C_1 x + C_2")
    r.eq(r"y(0) = 0 \Rightarrow C_2 = 0, \qquad y(L) = 0 \Rightarrow C_1 = \frac{P a L}{6}"
         r"\qquad\Rightarrow\qquad y(x) = \frac{P a}{6 E I L}\left(L^2 x - x^3\right)")
    r.step(r"x_m", r"\frac{L}{\sqrt{3}}", r"\frac{180}{\sqrt{3}}", f"{xk:.2f}", "in", "From y'(x) = 0.")
    r.step(r"y_{max,AB}", r"\frac{P a L^2}{9\sqrt{3}\,E I}", r"\frac{(50\,000)(48)(180)^2}{9\sqrt{3}(29\times10^6)(722)}",
           f"{ymax_AB:.4f}", "in", "Upward. This is the handout's y_max = 0.238 in.")
    r.step(r"y_C", r"-\frac{P a^2 (L + a)}{3 E I}", r"-\frac{(50\,000)(48)^2(228)}{3(29\times10^6)(722)}",
           f"{yC:.4f}", "in", "Free end C: the largest vertical deflection of the beam (downward).")
    if FE3:
        d_s = -FE3["uy"]["C"] - abs(yC)
        kAs = P3 * a3 * (L3 + a3) / (L3 * G3 * d_s)
        r.step(r"\delta_{s,C}", r"|y_C|_{ANSYS} - |y_C|_{EB}", rf"{-FE3['uy']['C']:.4f} - {abs(yC):.4f}", f"{d_s:.4f}", "in",
               "Shear deformation, which BEAM188 (Timoshenko) adds. By the unit-load method it equals "
               "$Pa(L+a)/(L\\,\\kappa G A)$, which gives an effective shear area "
               f"κA = {kAs:.2f} in², close to the web area d·tw = {D3 * FE3['section']['tw']:.2f} in², as expected for an I-beam.")
    r.end_handcalc()
    r.img(fig_q3(), "Shear force, bending moment and deflection along the beam: statics / elastic curve (lines) and "
                    "the ANSYS shear-moment diagram (×).", width="88%", border=False)

    if FE3:
        bt = FE3["beam_tool_psi"]
        eb = FE3["eb"]
        r.callout(f"The handout gives y_max = 0.238 in and calls it the deflection at C. That number is the largest "
                  f"(upward) deflection of span AB, at x = L/√3 = {xk:.1f} in, which is what the textbook problem asks "
                  f"for, and ANSYS matches it ({FE3['uy']['K']:.4f} in). The deflection at C is larger: "
                  f"{abs(yC):.4f} in downward by beam theory, and that is the beam's maximum vertical deflection.")
        r.table(["Output Results", "Statics / MoM", "ANSYS WB", "% Error"],
                [["Reaction at pin A", f"Fy = {RA3:,.1f} lb", f"Fy = {FE3['rA']['y']:,.1f} lb", pct(FE3['rA']['y'], RA3)],
                 ["", "Fx = 0 lb", f"Fx = {FE3['rA']['x']:.1f} lb", pct(FE3['rA']['x'], 0)],
                 ["Reaction at roller B", f"Fy = {RB3:,.1f} lb", f"Fy = {FE3['rB']['y']:,.1f} lb", pct(FE3['rB']['y'], RB3)],
                 ["Max. bending moment (at B)", f"{abs(MB3):,.0f} lb·in", f"{FE3['bm_max_lbfin']:,.0f} lb·in", pct(FE3['bm_max_lbfin'], abs(MB3))],
                 ["Max. shear force (BC)", f"{P3:,.0f} lb", f"{FE3['sf_max_lbf']:,.0f} lb", pct(FE3['sf_max_lbf'], P3)],
                 ["Max. bending stress", f"{sig3:,.1f} psi", f"{bt['Maximum Bending Stress']['max']:,.1f} psi",
                  pct(bt['Maximum Bending Stress']['max'], sig3)],
                 ["y_max in span AB (handout: 0.238 in)", f"{ymax_AB:.4f} in", f"{FE3['uy']['K']:.4f} in", pct(FE3['uy']['K'], ymax_AB)],
                 ["Deflection at C, default BEAM188", f"{yC:.4f} in", f"{FE3['uy']['C']:.4f} in", pct(FE3['uy']['C'], yC)],
                 ["Deflection at C, shear-rigid check", f"{yC:.4f} in", f"{eb['uyC']:.4f} in", pct(eb['uyC'], yC)]],
                "Q3 validation: statics / mechanics of materials vs. ANSYS", cls="num")
        r.p("The reactions, shear forces, maximum moment and maximum bending stress agree to round-off, because the beam "
            "is statically determinate and BEAM188 recovers σ = Mc/I exactly. The upward peak of span AB also matches "
            "exactly: the shear in AB is constant and both ends are held, so shear deformation adds nothing at "
            "x = L/√3. At the free end, the default ANSYS deflection is "
            f"{pct(FE3['uy']['C'], yC)} % larger than beam theory because BEAM188 is a Timoshenko element that also "
            "counts shear deformation, which matters on a short, deep beam with a 50-kip shear in the overhang "
            "(a/d ≈ 3.4). A second analysis with the shear stiffness made effectively infinite (APDL SECCONTROL) "
            f"returns {eb['uyC']:.4f} in, the Euler–Bernoulli value.")
        r.table(["Element size (in)", "Elements", "y_C (in)", "y at L/√3 (in)", "Max. bending stress (psi)"],
                [[f"{s['size_in']:g}", s["elements"], f"{s['uyC']:.6f}", f"{s['uyK']:.6f}", f"{s['sb_max']:,.1f}"]
                 for s in FE3["mesh_study"]],
                "Mesh refinement", cls="num")


def build():
    r = Report("In-Class Tutorial: 1D Element, Truss and Beam",
               "Q1 stepped shaft · Q2 two-bar truss · Q3 overhanging W14×68 beam (ANSYS Workbench + validation)",
               due="Mon Oct 5, 2026, 11:59 PM MT (submitted late)")
    q1(r)
    q2(r)
    q3(r)
    out = r.docx(OUT_DOCX)
    print("wrote", out)
    print("Q1 uB", uB, "R", R1v, "sig", sig1)
    print("Q2 F", F2, "sig", sig2, "R", R2x, R2y, "uAy", uAy)
    print("Q3 R", RA3, RB3, "M", MB3, "sig", sig3, "ymaxAB", ymax_AB, "yC", yC)


if __name__ == "__main__":
    build()
