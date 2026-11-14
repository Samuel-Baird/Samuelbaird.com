"""Test 1 (1D element, truss, beam): hand calculations, statics/MoM checks, ANSYS comparison -> Word.

    python solve.py            (reads ansys_out/q*_results.json from ansys_q1.py, ansys_q2.py, ansys_q3.py)
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "Test1_1D_Truss_Beam.docx"
HANDOUT = HERE.parents[1] / "canvas" / "files" / "_extract" / "TEST_1_10_7_2027_V1" / "img"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
AO = HERE / "ansys_out"


def load(name):
    p = AO / name
    return json.loads(p.read_text()) if p.exists() else None


FE1, FE2, FE3 = load("q1_results.json"), load("q2_results.json"), load("q3_results.json")


def z(x):
    """Clean signed zero (-0.0 -> 0.0) for printing."""
    return 0.0 if abs(x) < 5e-4 else x


def pct(fe, hand):
    if abs(hand) < 1e-9:
        return "— (both ≈ 0)" if abs(fe) < 1e-3 else "—"
    return f"{abs(fe - hand) / abs(hand) * 100:.3f}"


def bm(M, scale=1.0, f="{:.4g}"):
    rows = [" & ".join(("0" if abs(v) < 1e-9 else f.format(v / scale)) for v in r) for r in M]
    return r"\begin{bmatrix}" + r" \\ ".join(rows) + r"\end{bmatrix}"


# ===================================================================== Q1 stepped shaft (lb, in)
E1 = 10.6e6
L = np.array([12.0, 9.0, 8.0])
A = np.array([0.75, 0.5, 1.0])
F2, F3 = 4000.0, 1500.0
k = A * E1 / L
K1 = np.zeros((4, 4))
for e in range(3):
    K1[e:e + 2, e:e + 2] += k[e] * np.array([[1, -1], [-1, 1]])
F1v = np.array([0.0, F2, F3, 0.0])
Kr1 = K1[1:3, 1:3]
u23 = np.linalg.solve(Kr1, F1v[1:3])
U1 = np.array([0.0, u23[0], u23[1], 0.0])
R1v = K1 @ U1 - F1v
u_mid1 = 0.5 * U1[0] + 0.5 * U1[1]                     # N1 = N2 = 1/2 at the midpoint
sig1 = E1 * np.diff(U1) / L                            # psi, per element
force1 = sig1 * A
X1 = np.concatenate([[0.0], np.cumsum(L)])             # node x positions

# ===================================================================== Q2 truss (N, m)
J2 = {"A": (0.0, 0.0), "B": (1.5, 0.0), "C": (3.0, 0.0), "D": (4.5, 0.0), "E": (6.0, 0.0),
      "H": (1.5, 1.0), "G": (3.0, 2.0), "J": (4.5, 1.0)}
M2 = ["AB", "BC", "CD", "DE", "AH", "HG", "GJ", "JE", "BH", "CG", "DJ", "HC", "CJ"]
LOAD2 = {"A": 17e3, "H": 32e3, "G": 17e3, "J": 32e3, "E": 25e3}     # downward
AREA2, E2 = 800e-6, 200e9
WTOT = sum(LOAD2.values())
# Global equilibrium (A: roller, vertical reaction only; E: pin)
Ax = 0.0
Ay = sum(p * (6.0 - J2[j][0]) for j, p in LOAD2.items()) / 6.0   # sum of moments about E = 0
Ey = WTOT - Ay
Ex = -Ax
# Method of joints as one linear system: 8 joints x 2 equations, unknowns 13 member forces + Ay, Ex, Ey
names = list(J2)
Aeq = np.zeros((16, 16))
beq = np.zeros(16)
for mi, m in enumerate(M2):
    a, b = m[0], m[1]
    (xa, ya), (xb, yb) = J2[a], J2[b]
    Lm = math.hypot(xb - xa, yb - ya)
    c, s = (xb - xa) / Lm, (yb - ya) / Lm
    ia, ib = names.index(a), names.index(b)
    Aeq[2 * ia, mi] += c                      # tension pulls joint a toward b
    Aeq[2 * ia + 1, mi] += s
    Aeq[2 * ib, mi] -= c
    Aeq[2 * ib + 1, mi] -= s
iA, iE = names.index("A"), names.index("E")
Aeq[2 * iA + 1, 13] = 1.0                    # Ay
Aeq[2 * iE, 14] = 1.0                        # Ex
Aeq[2 * iE + 1, 15] = 1.0                    # Ey
for j, p in LOAD2.items():
    beq[2 * names.index(j) + 1] += p          # sum Fy: members + reaction - load = 0
sol2 = np.linalg.solve(Aeq, beq)
F_mem = dict(zip(M2, sol2[:13]))
assert abs(sol2[13] - Ay) < 1e-6 and abs(sol2[15] - Ey) < 1e-6 and abs(sol2[14]) < 1e-6

# Truss direct-stiffness solution for the joint deflections (checks the ANSYS deformation plots)
K2 = np.zeros((16, 16))
for m in M2:
    (xa, ya), (xb, yb) = J2[m[0]], J2[m[1]]
    Lm = math.hypot(xb - xa, yb - ya)
    c, s = (xb - xa) / Lm, (yb - ya) / Lm
    T = np.array([[c * c, c * s, -c * c, -c * s], [c * s, s * s, -c * s, -s * s],
                  [-c * c, -c * s, c * c, c * s], [-c * s, -s * s, c * s, s * s]])
    ia, ib = names.index(m[0]), names.index(m[1])
    idx = [2 * ia, 2 * ia + 1, 2 * ib, 2 * ib + 1]
    K2[np.ix_(idx, idx)] += AREA2 * E2 / Lm * T
F2v = np.zeros(16)
for j, p in LOAD2.items():
    F2v[2 * names.index(j) + 1] = -p
fixed2 = [2 * iA + 1, 2 * iE, 2 * iE + 1]
free2 = [d for d in range(16) if d not in fixed2]
U2 = np.zeros(16)
U2[free2] = np.linalg.solve(K2[np.ix_(free2, free2)], F2v[free2])
U2_mm = {j: (U2[2 * i] * 1e3, U2[2 * i + 1] * 1e3) for i, j in enumerate(names)}

# ===================================================================== Q3 box beam (lb, in)
P3, a3, L3 = 500.0, 16.0, 44.0
x1, x2 = a3, a3 + 12.0
bo, ti = 4.0, 0.5
bi = bo - 2 * ti
I3 = (bo ** 4 - bi ** 4) / 12.0
A3 = bo ** 2 - bi ** 2
c3 = bo / 2
PSI = 6894.757293168
E3 = 200e9 / PSI                       # ANSYS Structural Steel, 200 GPa
NU3 = 0.3
G3 = E3 / (2 * (1 + NU3))
RA3 = (P3 * (L3 - x1) + P3 * (L3 - x2)) / L3        # sum of moments about the roller
RB3 = 2 * P3 - RA3
Mmax3 = RA3 * x1
sig3 = Mmax3 * c3 / I3
d_eb = P3 * a3 * (3 * L3 ** 2 - 4 * a3 ** 2) / (24 * E3 * I3)   # midspan, two symmetric loads
xs3 = np.linspace(0, L3, 4401)
V3 = RA3 - P3 * (xs3 >= x1) - P3 * (xs3 >= x2)
M3 = RA3 * xs3 - P3 * np.clip(xs3 - x1, 0, None) - P3 * np.clip(xs3 - x2, 0, None)


# ===================================================================== figures
def fig_q1():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True)
    a1.plot(X1, U1 * 1e3, "o-", color="#1f4e79", label="Hand FE (linear elements)")
    a1.plot([6.0], [u_mid1 * 1e3], "s", color="#1f4e79", mfc="white", label="Midpoint of element (1)")
    if FE1:
        xa = [6.0, 12.0, 21.0]
        a1.plot(xa, [FE1["u"][k_] * 1e3 for k_ in ("1m", "2", "3")], "x", ms=10, color="#c00000", label="ANSYS probes")
    a1.set_ylabel("u (10⁻³ in)")
    a1.legend(fontsize=8, loc="upper right")
    a1.grid(alpha=.3)
    for e in range(3):
        a2.hlines(sig1[e], X1[e], X1[e + 1], color="#1f4e79", lw=2.5)
        a2.text((X1[e] + X1[e + 1]) / 2, sig1[e] + (250 if sig1[e] > 0 else -550), f"({e + 1}) {sig1[e]:,.0f} psi",
                ha="center", fontsize=8)
    a2.axhline(0, color="k", lw=.6)
    a2.set_ylabel("σ (psi)")
    a2.set_xlabel("x (in)")
    a2.set_ylim(-3600, 4600)
    a2.grid(alpha=.3)
    fig.tight_layout()
    p = FIG / "q1_u_sigma.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q2():
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    for m in M2:
        (xa, ya), (xb, yb) = J2[m[0]], J2[m[1]]
        f = F_mem[m]
        col = "#c00000" if f < -1 else ("#1f4e79" if f > 1 else "#888888")
        ax.plot([xa, xb], [ya, yb], color=col, lw=3 if abs(f) > 1 else 1.5, ls="-" if abs(f) > 1 else "--")
        lab = "0" if abs(f) < 1 else f"{abs(f) / 1e3:.2f} {'T' if f > 0 else 'C'}"
        ax.text((xa + xb) / 2, (ya + yb) / 2 + 0.06, lab, ha="center", fontsize=7.5,
                bbox=dict(fc="white", ec="none", pad=0.5))
    for j, (x, y) in J2.items():
        ax.plot(x, y, "o", color="k", ms=4)
        ax.text(x - 0.12, y + 0.1, j, fontsize=9, weight="bold")
    for j, p in LOAD2.items():
        x, y = J2[j]
        ax.annotate("", xy=(x, y + 0.02), xytext=(x, y + 0.55), arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.2))
        ax.text(x + 0.05, y + 0.45, f"{p / 1e3:g} kN", fontsize=7.5, color="#555")
    ax.annotate("", xy=(0, -0.02), xytext=(0, -0.55), arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.6))
    ax.text(0.06, -0.5, f"$A_y$ = {Ay / 1e3:.1f} kN", color="#2e7d32", fontsize=8)
    ax.annotate("", xy=(6, -0.02), xytext=(6, -0.55), arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.6))
    ax.text(5.0, -0.5, f"$E_y$ = {Ey / 1e3:.1f} kN", color="#2e7d32", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(-0.4, 6.5)
    ax.set_ylim(-0.7, 2.7)
    ax.axis("off")
    ax.set_title("Member forces from the method of joints (kN; T = tension, C = compression)", fontsize=9)
    fig.tight_layout()
    p = FIG / "q2_member_forces.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q3():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True)
    a1.fill_between(xs3, V3, step="post", alpha=.25, color="#1f4e79")
    a1.plot(xs3, V3, color="#1f4e79", label="Statics")
    a2.fill_between(xs3, M3, alpha=.25, color="#1f4e79")
    a2.plot(xs3, M3, color="#1f4e79", label="Statics")
    if FE3 and "smd" in FE3:
        s = FE3["smd"]
        xa = np.array(s["X Coordinate"]) / 0.0254
        va = -np.array(s["SFZ"]) / 4.4482216152605        # N -> lbf, sign to the textbook convention
        ma = -np.array(s["MY"]) / 0.1129848290276167       # N m -> lbf in
        a1.plot(xa[::2], va[::2], "x", ms=4, color="#c00000", label="ANSYS shear-moment diagram")
        a2.plot(xa[::2], ma[::2], "x", ms=4, color="#c00000", label="ANSYS shear-moment diagram")
    a1.set_ylabel("V (lb)")
    a1.axhline(0, color="k", lw=.6)
    a1.grid(alpha=.3)
    a1.legend(fontsize=8, loc="upper right")
    a2.set_ylabel("M (lb·in)")
    a2.set_xlabel("x (in)")
    a2.grid(alpha=.3)
    a2.legend(fontsize=8, loc="lower center")
    a2.annotate(f"M_max = {Mmax3:,.0f} lb·in", xy=(22, Mmax3), xytext=(22, Mmax3 * 0.55), ha="center",
                arrowprops=dict(arrowstyle="->"), fontsize=8)
    fig.tight_layout()
    p = FIG / "q3_sfd_bmd.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ===================================================================== report
def im(name):
    return AO / f"{name}.png"


def q1(r):
    r.h2("Q1. 1D element: stepped shaft (20 points)")
    r.p("The round stepped shaft is fixed at both walls (nodes 1 and 4) and carries 4000 lb at node 2 and "
        "1500 lb at node 3, both along the shaft axis. $E = 10.6\\times10^6$ psi, ν = 0.3. Element lengths "
        "12, 9 and 8 in; areas 0.75, 0.5 and 1 in².")
    r.img(HANDOUT / "image1.png", "Stepped shaft (from the test).", width="70%", border=False)

    r.h3("Part I. Hand calculations (finite element method, 7 steps)")
    r.handcalc("Step 1: discretize and select the element type")
    r.p("Three two-node 1D bar elements, four nodes, one axial displacement per node: "
        "$\\{u_1, u_2, u_3, u_4\\}$. Inside an element $u(x) = N_1 u_i + N_2 u_j$ with $N_1 = 1 - x/L$, $N_2 = x/L$.")
    r.table(["Element", "Nodes", "L (in)", "A (in²)", "k = AE/L (lb/in)"],
            [[f"({e + 1})", f"{e + 1}–{e + 2}", f"{L[e]:g}", f"{A[e]:g}", f"{k[e]:,.1f}"] for e in range(3)],
            "Element data ($E$ = 10.6×10⁶ psi)", cls="num")
    r.end_handcalc()

    r.handcalc("Step 2–3: element stiffness matrices and strain–displacement relation")
    r.eq(r"[k]^{(e)} = \frac{A_e E}{L_e}\begin{bmatrix} 1 & -1 \\ -1 & 1 \end{bmatrix}, \qquad \varepsilon = \frac{u_j - u_i}{L}, \qquad \sigma = E\varepsilon")
    for e in range(3):
        r.step(rf"k_{e + 1}", rf"\frac{{A_{e + 1}E}}{{L_{e + 1}}}", rf"\frac{{({A[e]:g})(10.6\times10^6)}}{{{L[e]:g}}}",
               f"{k[e]:,.1f}".replace(",", r"\,"), "lb/in")
    r.end_handcalc()

    r.handcalc("Step 4: assemble the global stiffness matrix")
    r.eq(r"[K] = \begin{bmatrix} k_1 & -k_1 & 0 & 0 \\ -k_1 & k_1 + k_2 & -k_2 & 0 \\ 0 & -k_2 & k_2 + k_3 & -k_3 \\ 0 & 0 & -k_3 & k_3 \end{bmatrix}"
         rf" = 10^{{5}}\ {bm(K1, 1e5, '{:.5g}')}\ \text{{lb/in}}")
    r.end_handcalc()

    r.handcalc("Step 5: apply boundary conditions and loads")
    r.p("Both walls are fixed: $u_1 = u_4 = 0$. Nodal loads $F_2 = 4000$ lb and $F_3 = 1500$ lb (+x). "
        "Striking rows and columns 1 and 4:")
    r.eq(rf"10^{{5}}\ {bm(Kr1, 1e5, '{:.5g}')} \begin{{Bmatrix}} u_2 \\ u_3 \end{{Bmatrix}} = \begin{{Bmatrix}} 4000 \\ 1500 \end{{Bmatrix}}\ \text{{lb}}")
    r.end_handcalc()

    r.handcalc("Step 6: solve for the nodal displacements")
    det = Kr1[0, 0] * Kr1[1, 1] - Kr1[0, 1] ** 2
    r.step("u_2", r"\frac{F_2(k_2 + k_3) + F_3 k_2}{(k_1 + k_2)(k_2 + k_3) - k_2^2}",
           rf"\frac{{4000({fmt(Kr1[1, 1])}) + 1500({fmt(k[1])})}}{{{fmt(det)}}}", f"{U1[1]:.6f}", "in")
    r.step("u_3", r"\frac{F_3(k_1 + k_2) + F_2 k_2}{(k_1 + k_2)(k_2 + k_3) - k_2^2}",
           rf"\frac{{1500({fmt(Kr1[0, 0])}) + 4000({fmt(k[1])})}}{{{fmt(det)}}}", f"{U1[2]:.6f}", "in")
    r.step(r"u\big|_{x = 6\ \text{in}}", r"N_1 u_1 + N_2 u_2 = \tfrac12 u_1 + \tfrac12 u_2",
           rf"\tfrac12(0) + \tfrac12({U1[1]:.6f})", f"{u_mid1:.6f}", "in",
           "Midpoint of element (1): the linear shape functions are both 1/2 there.")
    r.end_handcalc()

    r.handcalc("Step 7: reactions and element stresses")
    r.eq(r"\{R\} = [K]\{u\} - \{F\}")
    r.step("R_1", r"-k_1 u_2", rf"-({fmt(k[0])})({U1[1]:.6f})", f"{R1v[0]:,.1f}", "lb", "Acts in −x (toward the left wall).")
    r.step("R_4", r"-k_3 u_3", rf"-({fmt(k[2])})({U1[2]:.6f})", f"{R1v[3]:,.1f}", "lb", "Acts in −x.")
    r.step(r"\sum F_x", "R_1 + R_4 + F_2 + F_3", rf"{R1v[0]:,.1f} + ({R1v[3]:,.1f}) + 4000 + 1500",
           f"{R1v[0] + R1v[3] + F2 + F3:.1f}", "lb", "Equilibrium is satisfied.")
    names_u = ["u_1", "u_2", "u_3", "u_4"]
    for e in range(3):
        kind = "tension" if sig1[e] > 0 else "compression"
        r.step(rf"\sigma^{{({e + 1})}}", rf"E\,\frac{{{names_u[e + 1]} - {names_u[e]}}}{{L_{e + 1}}}",
               rf"(10.6\times10^6)\frac{{{U1[e + 1]:.6f} - ({U1[e]:.6f})}}{{{L[e]:g}}}",
               f"{sig1[e]:,.1f}".replace(",", r"\,"), "psi",
               f"Element ({e + 1}): {kind}, axial force {force1[e]:,.1f} lb." + (" (Asked for in the test.)" if e == 0 else ""))
    r.end_handcalc()
    r.img(fig_q1(), "Hand FE displacement and element stresses along the shaft; ANSYS probe values marked ×.",
          width="85%", border=False)

    if not FE1:
        return
    r.pagebreak()
    r.h3("Part II. ANSYS Workbench")
    r.bullets([
        "**Geometry:** a 29 in line body along x, split at the nodes (and at x = 6 in, the midpoint of element 1, "
        "so the midpoint displacement can be probed). The segments are joined by node merge.",
        "**Cross-sections:** solid circles with the given areas: d = "
        + ", ".join(f"{2 * math.sqrt(a / math.pi):.4f} in" for a in A) + " for elements (1), (2), (3).",
        "**Material:** $E = 10.6\\times10^6$ psi, ν = 0.3 (custom Engineering Data entry).",
        "**Elements:** BEAM188 line elements, 1 in element size (" + f"{FE1['elements']} elements). "
        "With only axial loads the beam elements behave as bars, so the answer is the same as the 1D element model.",
        "**Supports and loads:** fixed supports at nodes 1 and 4; 4000 lb at node 2 and 1500 lb at node 3 in +x.",
    ])
    r.img(im("q1_model"), "Finite element model with the fixed walls (A, B) and the two axial loads (C, D).")
    r.img(im("q1_mesh"), f"Mesh: {FE1['elements']} beam elements, {FE1['nodes']} nodes.")
    r.img(im("q1_ux"), f"Directional deformation along the shaft axis (x), in: u₂ = {FE1['u']['2']:.6f} in "
                       f"(maximum), u₃ = {FE1['u']['3']:.6f} in.")
    r.img(im("q1_r1"), f"Reaction at the left wall (node 1): {FE1['r1']['x']:,.1f} lb in x.")
    r.img(im("q1_r4"), f"Reaction at the right wall (node 4): {FE1['r4']['x']:,.1f} lb in x.")
    bt = FE1["beam_tool"]["Direct Stress"]
    r.img(im("q1_direct_stress"), f"Beam Tool, direct stress (psi): element (1) {bt['max_psi']:,.1f} psi (tension), "
                                  f"element (3) {bt['min_psi']:,.1f} psi; element (2) "
                                  f"{FE1['axial_lbf']['2'] / FE1['cs_area']['2']:,.1f} psi.")
    r.table(["Element size (in)", "Elements", "u₂ (in)", "u₃ (in)", "R₁ (lb)"],
            [[f"{s['size_in']:g}", s["elements"], f"{s['u2']:.6f}", f"{s['u3']:.6f}", f"{s['R1']:,.2f}"]
             for s in FE1["mesh_study"]],
            "Mesh refinement: the results do not change, because a bar under end loads has a linear displacement "
            "field that the element reproduces exactly", cls="num")

    r.h3("Part III. Hand calculations vs. ANSYS")
    st_fe = {e: FE1["axial_lbf"][str(e)] / FE1["cs_area"][str(e)] for e in (1, 2, 3)}
    r.table(["Output Results", "Statics/MOM (FE hand)", "ANSYS WB", "% Error"],
            [["Reaction Force at node 1", f"{R1v[0]:,.1f} lb", f"{FE1['r1']['x']:,.1f} lb", pct(FE1['r1']['x'], R1v[0])],
             ["Reaction Force at node 4", f"{R1v[3]:,.1f} lb", f"{FE1['r4']['x']:,.1f} lb", pct(FE1['r4']['x'], R1v[3])],
             ["Stress at Element (1)", f"{sig1[0]:,.1f} psi", f"{st_fe[1]:,.1f} psi", pct(st_fe[1], sig1[0])],
             ["Stress at Element (2)", f"{sig1[1]:,.1f} psi", f"{st_fe[2]:,.1f} psi", pct(st_fe[2], sig1[1])],
             ["Stress at Element (3)", f"{sig1[2]:,.1f} psi", f"{st_fe[3]:,.1f} psi", pct(st_fe[3], sig1[2])],
             ["Displacement u₂", f"{U1[1]:.6f} in", f"{FE1['u']['2']:.6f} in", pct(FE1['u']['2'], U1[1])],
             ["Displacement u₃", f"{U1[2]:.6f} in", f"{FE1['u']['3']:.6f} in", pct(FE1['u']['3'], U1[2])],
             ["Displacement, midpoint of (1)", f"{u_mid1:.6f} in", f"{FE1['u']['1m']:.6f} in", pct(FE1['u']['1m'], u_mid1)]],
            "Table 1 of the test, extended to every element stress and displacement", cls="num")
    r.p("ANSYS matches the hand solution. The ANSYS stresses in the table are the element axial force divided by "
        "the cross-section area ANSYS used; ANSYS builds a circle from a polygon, so its area is "
        f"{FE1['cs_area']['1']:.5f} in² rather than 0.75 in². That makes the ANSYS shaft very slightly softer, so its "
        f"displacements are {pct(FE1['u']['2'], U1[1])}% larger, and the Beam Tool contour reads "
        f"{bt['max_psi']:,.1f} psi for element (1) (a {pct(bt['max_psi'], sig1[0])}% difference). The reactions do "
        "not depend on the area, and they agree to round-off.")


def q2(r):
    r.pagebreak()
    r.h2("Q2. Truss (15 points)")
    r.p("All members have a 20 × 40 mm rectangular section (A = 800 mm²) and are structural steel. "
        "F1 = 17 kN (at A and G), F2 = 32 kN (at H and J), F3 = 25 kN (at E), all downward. "
        "A is a roller (vertical reaction only); E is a pin.")
    r.img(HANDOUT / "image2.png", "Truss geometry and loading (from the test).", width="75%", border=False)

    if FE2:
        r.h3("Part I. ANSYS Workbench")
        r.bullets([
            "**Geometry:** 13 line bodies (one per member) on the joint coordinates in the figure, joined at the "
            "8 joints by node merge.",
            "**Cross-section:** rectangle 20 mm × 40 mm (A = 800 mm²). **Material:** ANSYS Structural Steel "
            "(E = 200 GPa, ν = 0.3).",
            f"**Elements:** BEAM188 line elements (needed for the Beam Tool), 0.1 m element size ({FE2['elements']} elements).",
            "**Supports:** roller at A: $u_y = 0$ (x free); pin at E: $u_x = u_y = 0$. To keep the 2D truss from "
            "moving out of its plane, $u_z = 0$ at A and E and the rotations about x and y are fixed at E; the "
            "in-plane rotation stays free, so these add no in-plane restraint.",
            "**Loads:** the five joint forces in −y, including F1 at A and F3 at E, which sit on the supports.",
        ])
        r.img(im("q2_model"), "Finite element model with the supports (A–C) and the five loads (D–H).")
        r.img(im("q2_dx"), f"Directional deformation X (mm): from {FE2['dx_mm']['min']:.3f} to {FE2['dx_mm']['max']:.3f} mm "
                           "(the roller at A slides in +x).")
        r.img(im("q2_dy"), f"Directional deformation Y (mm): maximum downward deflection {FE2['dy_mm']['min']:.3f} mm.")
        r.img(im("q2_ra"), f"Reaction at roller A: Fx = {FE2['rA']['x']:.1f} N, Fy = {FE2['rA']['y'] / 1e3:,.3f} kN.")
        r.img(im("q2_re"), f"Reaction at pin E: Fx = {FE2['rE']['x']:.1e} N, Fy = {FE2['rE']['y'] / 1e3:,.3f} kN.")
        btd = FE2["beam_tool_MPa"]["Direct Stress"]
        r.img(im("q2_bt_direct_stress"), f"Beam Tool, direct stress in each member (MPa): {btd['max']:.2f} MPa "
                                         f"(bottom chord, tension) to {btd['min']:.2f} MPa (end top chords AH and JE, compression).")
        r.img(im("q2_axial"), "Axial force in each member (N).")
        r.table(["Member", "Axial force (kN)", "Direct stress (MPa)", "T / C"],
                [[f"{m[0]}{m[1]}", f"{FE2['axial_N'][m] / 1e3:.3f}", f"{FE2['stress_MPa'][m]:.2f}",
                  "≈ 0" if abs(FE2["axial_N"][m]) < 500 else ("T" if FE2["axial_N"][m] > 0 else "C")] for m in M2],
                "ANSYS direct stress in each member (axial force / 800 mm²)", cls="num")

    r.h3("Part II. Statics")
    r.handcalc("Free body of the whole truss")
    r.p("Unknowns: $A_y$ (roller), $E_x$ and $E_y$ (pin). All loads are vertical.")
    r.step(r"\sum F_x = 0:\ E_x", None, None, "0", "kN", "No horizontal load, and the roller at A carries none.")
    terms = " + ".join(f"{p / 1e3:g}({6.0 - J2[j][0]:g})" for j, p in LOAD2.items() if 6.0 - J2[j][0] > 0)
    r.step(r"\sum M_E = 0:\ A_y", r"\frac{\sum F_i\,(6 - x_i)}{6}", rf"\frac{{{terms}}}{{6}}", f"{Ay / 1e3:.2f}", "kN",
           "Moments about E (counter-clockwise positive); F3 at E has no moment arm.")
    r.step(r"\sum F_y = 0:\ E_y", r"\sum F_i - A_y", rf"{WTOT / 1e3:g} - {Ay / 1e3:.2f}", f"{Ey / 1e3:.2f}", "kN")
    r.p("These are the total support reactions. Part of each comes straight from the load applied on the support "
        f"(17 kN at A, 25 kN at E); the rest, {(Ay - 17e3) / 1e3:.1f} kN at each support, enters the members.")
    r.end_handcalc()
    r.p("Joint equilibrium at all eight joints (16 equations, solved together) gives every member force; members BH "
        "and DJ are zero-force members, as joints B and D show by inspection ($\\sum F_y = 0$ with no vertical load).")
    r.img(fig_q2(), "Member forces from statics.", width="95%", border=False)

    if FE2:
        r.table(["Output Results", "Statics", "ANSYS WB", "% Error"],
                [["Reaction Force at Roller A", f"Fx = {Ax:.0f} kN", f"Fx = {z(FE2['rA']['x'] / 1e3):.3f} kN", pct(FE2['rA']['x'], Ax)],
                 ["", f"Fy = {Ay / 1e3:.2f} kN", f"Fy = {FE2['rA']['y'] / 1e3:.3f} kN", pct(FE2['rA']['y'], Ay)],
                 ["Reaction Force at pin E", f"Fx = {z(Ex):.0f} kN", f"Fx = {z(FE2['rE']['x'] / 1e3):.3f} kN", pct(FE2['rE']['x'], Ex)],
                 ["", f"Fy = {Ey / 1e3:.2f} kN", f"Fy = {FE2['rE']['y'] / 1e3:.3f} kN", pct(FE2['rE']['y'], Ey)]],
                "Table 2 of the test: statics vs. ANSYS reactions", cls="num")
        rows = []
        for m in M2:
            fs, fa = F_mem[m] / 1e3, FE2["axial_N"][m] / 1e3
            rows.append([f"{m[0]}{m[1]}", f"{z(fs):.3f}", f"{fa:.3f}", f"{z(fs) * 1e3 / AREA2 / 1e6:.2f}",
                         f"{FE2['stress_MPa'][m]:.2f}", pct(fa, fs) if abs(fs) > 1e-6 else "— (zero-force)"])
        r.table(["Member", "Force, statics (kN)", "Force, ANSYS (kN)", "σ statics (MPa)", "σ ANSYS (MPa)", "% Error"], rows,
                "Extra check: member forces and stresses, method of joints vs. ANSYS", cls="num")
        jrow = []
        for j in names:
            ux, uy = U2_mm[j]
            fx, fy = FE2["joints_mm"][j]["x"], FE2["joints_mm"][j]["y"]
            jrow.append([j, f"{ux:.4f}", f"{fx:.4f}", f"{uy:.4f}", f"{fy:.4f}"])
        r.table(["Joint", "uₓ truss FE (mm)", "uₓ ANSYS (mm)", "u_y truss FE (mm)", "u_y ANSYS (mm)"], jrow,
                "Extra check: joint deflections, pin-jointed truss stiffness solution (hand FE) vs. ANSYS", cls="num")
        r.p("The reactions agree to round-off: the truss is statically determinate, so the reactions depend only on "
            "the loads and the geometry, not on the element type. The member forces agree to within "
            f"{max(abs(FE2['axial_N'][m] - F_mem[m]) / abs(F_mem[m]) * 100 for m in M2 if abs(F_mem[m]) > 1):.1f} %. "
            "The small differences, and the 0.1 kN in the zero-force "
            "members BH and DJ, come from ANSYS modelling the joints as rigid (beam elements, as the Beam Tool "
            "requires) while the statics solution assumes ideal pins, so the members also carry a little bending.")
        r.table(["Element size (m)", "Elements", "u_y at G (mm)", "Force in CG (kN)"],
                [[f"{s['size_m']:g}", s["elements"], f"{s['uyG'] * 1e3:.4f}", f"{s['F_CG'] / 1e3:.3f}"] for s in FE2["mesh_study"]],
                "Mesh refinement", cls="num")


def q3(r):
    r.pagebreak()
    r.h2("Q3. Simply supported beam (15 points)")
    r.p("The 44 in beam is pinned at the left end and on a roller at the right end and carries two P = 500 lb loads "
        "at 16 in and 28 in. The section is a 4 × 4 in square tube with a ½ in wall. Structural steel.")
    r.img(HANDOUT / "image3.png", "Beam, loading and cross-section (from the test).", width="70%", border=False)
    if FE3:
        r.h3("Part I. ANSYS Workbench")
        r.bullets([
            "**Geometry:** a 44 in line body split at the loads (16 in, 28 in) and at midspan (22 in), joined by node merge.",
            f"**Cross-section:** hollow rectangle 4 × 4 in, ½ in walls (ANSYS: A = {FE3['cs']['A_in2']:.3f} in², "
            f"I = {FE3['cs']['IZZ_in4']:.4f} in⁴). **Material:** ANSYS Structural Steel (E = 200 GPa = "
            f"{E3 / 1e6:.3f}×10⁶ psi, ν = 0.3).",
            f"**Elements:** BEAM188, 1 in element size ({FE3['elements']} elements).",
            "**Supports:** pin at the left end ($u_x = u_y = u_z = 0$, twist about the beam axis fixed); roller at "
            "the right end ($u_y = u_z = 0$, x free). **Loads:** 500 lb in −y at x = 16 in and x = 28 in.",
        ])
        r.img(im("q3_model"), "Finite element model with the pin (A, B), the roller (C) and the two 500 lb loads.")
        r.img(im("q3_dy"), f"Directional (vertical) deflection, in: {FE3['dy']['min']:.6f} in at midspan.")
        r.img(im("q3_rl"), f"Reaction at the pin (left): Fx = {FE3['rL']['x']:.1f} lb, Fy = {FE3['rL']['y']:.1f} lb.")
        r.img(im("q3_rr"), f"Reaction at the roller (right): Fx = {FE3['rR']['x']:.1f} lb, Fy = {FE3['rR']['y']:.1f} lb.")
        r.img(im("q3_sf"), f"Total shear force (lb): {FE3['sf_max_lbf']:.1f} lb in the outer spans, zero between the loads.")
        r.img(im("q3_bm"), f"Total bending moment (lb·in): maximum {FE3['bm_max_lbfin']:,.1f} lb·in, constant between the loads.")
        r.img(fig_q3(), "Shear force and bending moment diagrams: statics (line) and the ANSYS Shear-Moment Diagram "
                        "along the beam axis (×, exported from Mechanical and plotted with the textbook sign convention).",
              width="85%", border=False)
        bt = FE3["beam_tool_psi"]
        r.img(im("q3_bt_maximum_combined_stress"), f"Beam Tool, maximum combined stress (psi): {bt['Maximum Combined Stress']['max']:,.1f} psi "
                                                   "between the loads (bending only; the direct stress is zero).")
    r.h3("Part II. Statics and mechanics of materials")
    r.handcalc("Reactions (statics)")
    r.step(r"\sum F_x = 0:\ A_x", None, None, "0", "lb", "No horizontal load.")
    r.step(r"\sum M_B = 0:\ A_y", r"\frac{P(L - 16) + P(L - 28)}{L}", rf"\frac{{500(28) + 500(16)}}{{44}}", f"{RA3:.1f}", "lb")
    r.step(r"\sum F_y = 0:\ B_y", r"2P - A_y", rf"1000 - {RA3:.1f}", f"{RB3:.1f}", "lb", "Symmetric loading, so each support carries P.")
    r.end_handcalc()
    r.handcalc("Maximum bending moment and stress (mechanics of materials)")
    r.step(r"M_{max}", r"A_y\,a", rf"({RA3:.0f})(16)", f"{Mmax3:,.0f}".replace(",", r"\,"), r"lb\cdot in",
           "Constant between the two loads (16 in ≤ x ≤ 28 in), where V = 0.")
    r.step("I", r"\frac{b_o^4 - b_i^4}{12}", rf"\frac{{4^4 - 3^4}}{{12}}", f"{I3:.4f}", "in^4", "Inner side: 4 − 2(½) = 3 in.")
    r.step(r"\sigma_{max}", r"\frac{M_{max}\,c}{I}", rf"\frac{{({Mmax3:.0f})(2)}}{{{I3:.4f}}}", f"{sig3:,.1f}".replace(",", r"\,"), "psi",
           "Tension on the bottom face, compression on the top face.")
    r.end_handcalc()
    r.handcalc("Midspan deflection (extra check of the deflection plot)")
    r.step(r"\delta_{b}", r"\frac{P a (3L^2 - 4a^2)}{24 E I}", rf"\frac{{500(16)(3\cdot44^2 - 4\cdot16^2)}}{{24({fmt(E3)})({I3:.4f})}}",
           f"{d_eb:.6f}", "in", "Euler–Bernoulli (bending only), two symmetric loads.")
    if FE3:
        d_fe = -FE3["uy"]["M"]
        d_s = d_fe - d_eb
        kA = P3 * a3 / (G3 * d_s)
        r.step(r"\delta_{s}", r"\delta_{ANSYS} - \delta_b", rf"{d_fe:.6f} - {d_eb:.6f}", f"{d_s:.6f}", "in",
               f"Shear deformation, which BEAM188 (Timoshenko) includes. It equals $Pa/(\\kappa G A)$ with "
               f"$\\kappa A$ = {kA:.2f} in², a little below the 4 in² of the two side walls, as expected for a tube.")
    r.end_handcalc()
    if FE3:
        bt = FE3["beam_tool_psi"]
        r.table(["Output Results", "Statics/MOM", "ANSYS WB", "% Error"],
                [["Max. Bending Stress", f"σ_max = {sig3:,.1f} psi", f"σ_max = {bt['Maximum Bending Stress']['max']:,.1f} psi",
                  pct(bt["Maximum Bending Stress"]["max"], sig3)],
                 ["Max. Bending Moment", f"M_max = {Mmax3:,.0f} lb·in", f"M_max = {FE3['bm_max_lbfin']:,.1f} lb·in", pct(FE3['bm_max_lbfin'], Mmax3)],
                 ["Reaction Force at the pin (left support)", "Fx = 0 lb", f"Fx = {FE3['rL']['x']:.1f} lb", pct(FE3['rL']['x'], 0)],
                 ["", f"Fy = {RA3:.1f} lb", f"Fy = {FE3['rL']['y']:.1f} lb", pct(FE3['rL']['y'], RA3)],
                 ["Reaction Force at the roller (right support)", "Fx = 0 lb", f"Fx = {FE3['rR']['x']:.1f} lb", pct(FE3['rR']['x'], 0)],
                 ["", f"Fy = {RB3:.1f} lb", f"Fy = {FE3['rR']['y']:.1f} lb", pct(FE3['rR']['y'], RB3)],
                 ["Midspan deflection (extra)", f"{d_eb:.6f} in (bending only)", f"{-FE3['uy']['M']:.6f} in", pct(-FE3['uy']['M'], d_eb)]],
                "Table 3 of the test: statics/MoM vs. ANSYS", cls="num")
        r.p("The reactions, the maximum moment and the maximum bending stress agree to round-off: the beam is "
            "statically determinate, and BEAM188 recovers σ = Mc/I exactly for this section. The midspan deflection "
            f"is {pct(-FE3['uy']['M'], d_eb)} % larger in ANSYS because its Timoshenko beam element also includes "
            "shear deformation, which the Euler–Bernoulli formula leaves out and which is noticeable on a short, "
            "deep beam (L/h = 11). Adding the shear term above closes the gap.")
        r.table(["Element size (in)", "Elements", "Midspan deflection (in)", "Max. bending stress (psi)"],
                [[f"{s['size_in']:g}", s["elements"], f"{s['uy_mid']:.7f}", f"{s['sb_max']:,.2f}"] for s in FE3["mesh_study"]],
                "Mesh refinement", cls="num")


def build():
    r = Report("Test 1: 1D Element, Truss and Beam", "Q1 stepped shaft (FE hand solution + ANSYS) · Q2 truss · Q3 simply supported beam",
               due="Wed Oct 14, 2026, 11:59 PM MT (submitted late)")
    q1(r)
    q2(r)
    q3(r)
    out = r.docx(OUT_DOCX)
    print("wrote", out)
    print("Q1 u2 u3 umid", U1[1], U1[2], u_mid1, "R", R1v[0], R1v[3], "sig", sig1)
    print("Q2 Ay Ey", Ay, Ey, "F", {m: round(v / 1e3, 3) for m, v in F_mem.items()})
    print("Q3 R", RA3, "M", Mmax3, "sig", sig3, "I", I3, "d_eb", d_eb)


if __name__ == "__main__":
    build()
