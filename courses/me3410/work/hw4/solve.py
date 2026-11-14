"""HW 4: truss element. Direct-stiffness hand solution, statics check, ANSYS comparison -> Word.

    python solve.py            (reads ansys_out/results.json from ansys.py)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "HW4_Truss_Element.docx"
HANDOUT_FIG = HERE.parents[1] / "canvas" / "files" / "_extract" / "HW_4_TRUSS_ELEMENT_2_1_1" / "img" / "image1.png"

A = 15e-4          # m^2 (15 cm^2)
E = 70e9           # Pa
P = 2000.0         # N, downward at joint 4
J = {1: (0.0, 0.0), 2: (1.5, 0.0), 3: (0.0, 1.0), 4: (1.5, 1.0)}
MEMBERS = [(1, 2), (2, 3), (3, 4), (2, 4)]
FIXED = [1, 3]

# ---------------------------------------------------------------- direct stiffness
def dofs(n):
    return [2 * (n - 1), 2 * (n - 1) + 1]


elems = []
K = np.zeros((8, 8))
for e, (i, j) in enumerate(MEMBERS, start=1):
    (xi, yi), (xj, yj) = J[i], J[j]
    L = math.hypot(xj - xi, yj - yi)
    c, s = (xj - xi) / L, (yj - yi) / L
    k = A * E / L
    T = np.array([[c * c, c * s, -c * c, -c * s], [c * s, s * s, -c * s, -s * s],
                  [-c * c, -c * s, c * c, c * s], [-c * s, -s * s, c * s, s * s]])
    ke = k * T
    idx = dofs(i) + dofs(j)
    K[np.ix_(idx, idx)] += ke
    elems.append(dict(e=e, i=i, j=j, L=L, c=c, s=s, k=k, ke=ke, idx=idx,
                      theta=math.degrees(math.atan2(yj - yi, xj - xi))))

F = np.zeros(8)
F[dofs(4)[1]] = -P
fixed = sum((dofs(n) for n in FIXED), [])
free = [d for d in range(8) if d not in fixed]
Kr = K[np.ix_(free, free)]
Ur = np.linalg.solve(Kr, F[free])
U = np.zeros(8)
U[free] = Ur
Rall = K @ U - F
for el in elems:
    u = U[el["idx"]]
    el["sigma"] = E / el["L"] * np.array([-el["c"], -el["s"], el["c"], el["s"]]) @ u
    el["force"] = el["sigma"] * A

# statics (method of joints) for verification
F34 = 0.0
F24 = -P                                   # joint 4, sum Fy: -F24 - P = 0  -> compression
L23 = math.hypot(1.5, 1.0)
F23 = -F24 / (1.0 / L23)                   # joint 2, sum Fy: F23 (1/L23) + F24 = 0
F12 = -F23 * (1.5 / L23)                   # joint 2, sum Fx: -F12 - F23 (1.5/L23) = 0
stat = {1: F12, 2: F23, 3: F34, 4: F24}
# Reactions from joint equilibrium (member force + reaction = 0 at each support joint).
# Joint 3: member 2-3 in tension pulls joint 3 toward joint 2, direction (+1.5, -1)/L23.
R3x = -(F23 * 1.5 / L23)
R3y = -(F23 * -1.0 / L23)
# Joint 1: member 1-2 pulls joint 1 toward joint 2, direction (+1, 0).
R1x = -F12
R1y = 0.0
stat_R = {"R1x": R1x, "R1y": R1y, "R3x": R3x, "R3y": R3y}

RES_PATH = HERE / "ansys_out" / "results.json"
FE = json.loads(RES_PATH.read_text()) if RES_PATH.exists() else None


def bm(M, scale=1e6, fmt="{:.3f}"):
    rows = [" & ".join(("0" if abs(v) < 1e-9 else fmt.format(v / scale)) for v in r) for r in M]
    return r"\begin{bmatrix}" + r" \\ ".join(rows) + r"\end{bmatrix}"


def build():
    r = Report("HW 4: Truss Element", "Q1 finite element hand solution · Q2 ANSYS Workbench verification",
               due="Sun Sep 27, 2026, 11:59 PM (submitted late)")
    r.h2("Problem")
    r.p("The four-member truss is pinned to the wall at joints 1 and 3 and carries a 2 kN downward load at "
        "joint 4. Every member has $A = 15\\ \\text{cm}^2$ and is aluminum alloy with $E = 70$ GPa. "
        "Find the joint deflections, member stresses and reactions by the finite element (direct stiffness) "
        "method, verify them, and repeat the analysis in ANSYS.")
    if HANDOUT_FIG.exists():
        r.img(HANDOUT_FIG, "Truss geometry and loading (from the assignment handout).", width="55%", border=False)

    r.h2("Q1. Finite element hand solution")
    r.handcalc("Step 1: discretize and number")
    r.p("4 nodes (2 DOF each: $u$, $v$) and 4 two-node truss elements. Global DOF order: "
        "$\\{u_1, v_1, u_2, v_2, u_3, v_3, u_4, v_4\\}$.")
    r.table(["Element", "Nodes i–j", "L (m)", "θ (deg)", "c = cos θ", "s = sin θ", "AE/L (N/m)"],
            [[el["e"], f"{el['i']}–{el['j']}", f"{el['L']:.4f}", f"{el['theta']:.2f}", f"{el['c']:.4f}",
              f"{el['s']:.4f}", f"{el['k'] / 1e8:.4f}×10⁸"] for el in elems],
            "Element data ($A$ = 15×10⁻⁴ m², $E$ = 70 GPa)", cls="num")
    r.end_handcalc()

    r.handcalc("Step 2: element stiffness matrices in global coordinates")
    r.eq(r"[k]^{(e)} = \frac{AE}{L}\begin{bmatrix} c^2 & cs & -c^2 & -cs \\ cs & s^2 & -cs & -s^2 \\ -c^2 & -cs & c^2 & cs \\ -cs & -s^2 & cs & s^2 \end{bmatrix}")
    for el in elems:
        names = ",".join([f"u_{el['i']}", f"v_{el['i']}", f"u_{el['j']}", f"v_{el['j']}"])
        r.eq(rf"[k]^{{({el['e']})}} = 10^{{6}}\ {bm(el['ke'])}\ \text{{N/m}}\qquad ({names})")
    r.end_handcalc()

    r.handcalc("Step 3: assemble the global stiffness matrix")
    r.eq(rf"[K] = \sum_e [k]^{{(e)}} = 10^{{6}}\ {bm(K)}\ \text{{N/m}}")
    r.end_handcalc()

    r.handcalc("Step 4: apply boundary conditions and loads")
    r.p("Pins at joints 1 and 3: $u_1 = v_1 = u_3 = v_3 = 0$. The only load is $F_{4y} = -2000$ N. "
        "Striking the fixed rows and columns leaves the reduced system for $\\{u_2, v_2, u_4, v_4\\}$:")
    r.eq(rf"10^{{6}}\ {bm(Kr)} \begin{{Bmatrix}} u_2 \\ v_2 \\ u_4 \\ v_4 \end{{Bmatrix}} = \begin{{Bmatrix}} 0 \\ 0 \\ 0 \\ -2000 \end{{Bmatrix}}\ \text{{N}}")
    r.end_handcalc()

    r.handcalc("Step 5: solve for the joint displacements")
    names = ["u_2", "v_2", "u_4", "v_4"]
    for nm, val in zip(names, Ur):
        r.step(nm, None, None, f"{val * 1000:.5f}", "mm")
    r.p("Joints 1 and 3 are pinned, so their displacements are zero.")
    r.end_handcalc()

    r.handcalc("Step 6: member stresses")
    r.eq(r"\sigma^{(e)} = \frac{E}{L}\begin{bmatrix} -c & -s & c & s \end{bmatrix}\begin{Bmatrix} u_i \\ v_i \\ u_j \\ v_j \end{Bmatrix}")
    for el in elems:
        u = U[el["idx"]]
        r.step(rf"\sigma^{{({el['e']})}}", None,
               rf"\frac{{70\times10^9}}{{{el['L']:.4f}}}\left[({-el['c']:.4f})({u[0]*1e3:.4f}) + ({-el['s']:.4f})({u[1]*1e3:.4f}) + ({el['c']:.4f})({u[2]*1e3:.4f}) + ({el['s']:.4f})({u[3]*1e3:.4f})\right]\times10^{{-3}}",
               f"{el['sigma'] / 1e6:.4f}", "MPa",
               f"Member {el['i']}–{el['j']}: force {el['force']:.1f} N ({'tension' if el['force'] > 1e-6 else ('compression' if el['force'] < -1e-6 else 'zero-force member')}).")
    r.end_handcalc()

    r.handcalc("Step 7: reaction forces")
    r.eq(r"\{R\} = [K]\{U\} - \{F\}")
    for lab, d in (("R_{1x}", 0), ("R_{1y}", 1), ("R_{3x}", 4), ("R_{3y}", 5)):
        r.step(lab, None, None, f"{Rall[d]:.1f}", "N")
    r.step(r"\sum F_x", r"R_{1x} + R_{3x}", f"{Rall[0]:.1f} + ({Rall[4]:.1f})", f"{Rall[0] + Rall[4]:.1f}", "N")
    r.step(r"\sum F_y", r"R_{1y} + R_{3y} - 2000", f"{Rall[1]:.1f} + {Rall[5]:.1f} - 2000", f"{Rall[1] + Rall[5] - P:.1f}", "N")
    r.step(r"\sum M_{1}", r"-R_{3x}(1.0) - 2000(1.5)", f"-({Rall[4]:.1f})(1.0) - 2000(1.5)", f"{-Rall[4] * 1.0 - P * 1.5:.1f}", "N\\,m",
           "Moments about joint 1 (counter-clockwise positive): the structure is in equilibrium.")
    r.end_handcalc()

    r.h3("Verification by statics (method of joints)")
    r.handcalc("Independent check")
    r.step(r"\text{Joint 4: } \sum F_x = 0", r"F_{34}", None, f"{F34:.0f}", "N", "Member 3–4 is a zero-force member.")
    r.step(r"\text{Joint 4: } \sum F_y = 0", r"-F_{24} - 2000 = 0 \Rightarrow F_{24}", None, f"{F24:.0f}", "N", "Compression.")
    r.step(r"\text{Joint 2: } \sum F_y = 0", r"F_{23}\frac{1}{\sqrt{3.25}} + F_{24} = 0 \Rightarrow F_{23}", None, f"{F23:.1f}", "N", "Tension.")
    r.step(r"\text{Joint 2: } \sum F_x = 0", r"-F_{12} - F_{23}\frac{1.5}{\sqrt{3.25}} = 0 \Rightarrow F_{12}", None, f"{F12:.1f}", "N", "Compression.")
    r.end_handcalc()
    rows = []
    for el in elems:
        sf = stat[el["e"]]
        rows.append([f"{el['e']} ({el['i']}–{el['j']})", f"{sf:.1f}", f"{el['force']:.1f}", f"{sf / A / 1e6:.4f}", f"{el['sigma'] / 1e6:.4f}"])
    r.table(["Member", "Force, statics (N)", "Force, FE hand (N)", "σ statics (MPa)", "σ FE hand (MPa)"], rows,
            "Statics vs. finite element hand solution: identical, as expected for a statically determinate truss", cls="num")

    if FE:
        r.pagebreak()
        r.h2("Q2. ANSYS Workbench solution")
        r.bullets([
            "**Geometry:** four line bodies (one per member) imported from STEP and joined at the joints by node merge.",
            "**Cross-section:** square, side $\\sqrt{15}$ cm = 38.73 mm, so $A$ = 15 cm².",
            f"**Model type:** {FE['model_type_note']}",
            "**Material:** aluminum alloy with $E$ = 70 GPa as given (ν = 0.33).",
            "**Supports:** joints 1 and 3 fixed in translation (pins); out-of-plane motion restrained.",
            "**Load:** 2 kN in −Y at joint 4.",
        ])
        im = lambda k: HERE / "ansys_out" / f"{k}.png"  # noqa: E731
        for key, cap in (("model", "Finite element model with supports (A, B) and the 2 kN load at joint 4."),
                         ("td", "Total deformation (mm)."), ("dx", "Directional deformation X (mm)."),
                         ("dy", "Directional deformation Y (mm)."), ("axial", "Direct (axial) stress in each member (MPa)."),
                         ("r1", "Reaction at joint 1."), ("r3", "Reaction at joint 3.")):
            if im(key).exists():
                r.img(im(key), cap)
        r.h3("Comparison")
        rows = []
        jn = FE["joints"]
        for nm, val, key in (("u₂", Ur[0], ("2", "x")), ("v₂", Ur[1], ("2", "y")), ("u₄", Ur[2], ("4", "x")), ("v₄", Ur[3], ("4", "y"))):
            fe = jn[key[0]][key[1]] * 1000
            rows.append([nm + " (mm)", f"{val * 1000:.5f}", f"{fe:.5f}", f"{abs(fe - val * 1000) / max(abs(val * 1000), 1e-12) * 100:.2f}"])
        for el in elems:
            fe = FE["stress_MPa"][str(el["e"])]
            hand = el["sigma"] / 1e6
            pct = "—" if abs(hand) < 1e-9 else f"{abs(fe - hand) / abs(hand) * 100:.2f}"
            rows.append([f"σ member {el['i']}–{el['j']} (MPa)", f"{hand:.4f}", f"{fe:.4f}", pct])
        for lab, d, key in (("R1x (N)", 0, ("r1", "x")), ("R1y (N)", 1, ("r1", "y")), ("R3x (N)", 4, ("r3", "x")), ("R3y (N)", 5, ("r3", "y"))):
            fe = FE[key[0]][key[1]]
            pct = "—" if abs(Rall[d]) < 1e-6 else f"{abs(fe - Rall[d]) / abs(Rall[d]) * 100:.2f}"
            rows.append([lab, f"{Rall[d]:.1f}", f"{fe:.1f}", pct])
        r.table(["Quantity", "FE hand calculation", "ANSYS", "% diff"], rows, "Hand calculation vs. ANSYS", cls="num")
        r.p("ANSYS reproduces the hand solution: the structure is statically determinate and each member carries "
            "only axial load, so the two-node truss element is exact and the results agree to round-off.")
    out = r.docx(OUT_DOCX)
    print("wrote", out)
    print("U (mm):", np.round(Ur * 1000, 5), "sigma (MPa):", [round(el["sigma"] / 1e6, 4) for el in elems],
          "R:", np.round(Rall[[0, 1, 4, 5]], 2))


if __name__ == "__main__":
    build()
