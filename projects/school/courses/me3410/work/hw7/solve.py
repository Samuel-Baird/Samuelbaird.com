"""HW 7: 2D & 3D models. Hand checks + ANSYS results -> Word.

    python solve.py     (reads ansys_out/q1_results.json and q2_results.json)
"""
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "HW7_2D_3D_Models.docx"
AO = HERE / "ansys_out"
FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
HANDOUT = HERE.parents[1] / "canvas" / "files" / "_extract" / "HW_7_2_3D_Models_V1" / "img"
Q1 = json.loads((AO / "q1_results.json").read_text())
Q2 = json.loads((AO / "q2_results.json").read_text())

# ------------------------------------------------------------------ Q1 hand checks
F = 15000.0
RP = 3.5
xA, yA = RP * math.cos(math.radians(210)), RP * math.sin(math.radians(210))
xB, yB = RP * math.cos(math.radians(330)), RP * math.sin(math.radians(330))
xC, yC = 0.0, RP
AB = xB - xA
By = F * (yC - yA) / AB          # sum of moments about A
Ay = -By
Ax_plus_Bx = -F

# ------------------------------------------------------------------ Q2 hand checks
P = 4000.0
a, b = 37.5, 39.5
t = b - a
PSI_PER_GPA = 1e9 / 6894.757
MATS = [
    ("E-Glass", "E-Glass", 73.0 * PSI_PER_GPA, 0.22, "ANSYS Composite Materials library", 159.0, 1, 500_000),
    ("S-Glass", "S-Glass", 90.0 * PSI_PER_GPA, 0.22, "ANSYS Composite Materials library", 155.5, 2, 665_000),
    ("Kevlar 49", "Kevlar 49 (handout)", 19.0e6, 0.36, "HW 7 table (not in the ANSYS library); ν = 0.36 assumed", 89.9, 4, 400_000),
    ("Carbon fiber", "Carbon Fiber 230 GPa (isotropic)", 230.0 * PSI_PER_GPA, 0.20,
     "ANSYS Carbon Fiber (230 GPa), fiber-direction E and ν used as isotropic", 108.9, 7, 470_000),
]
LIMIT = 0.075


def lame_u(r, E, nu):
    k = P * a ** 3 / (b ** 3 - a ** 3)
    return k / E * ((1 - 2 * nu) * r + (1 + nu) * b ** 3 / (2 * r ** 2))


def lame_sr(r):
    return P * a ** 3 / (b ** 3 - a ** 3) * (1 - b ** 3 / r ** 3)


def lame_st(r):
    return P * a ** 3 / (b ** 3 - a ** 3) * (1 + b ** 3 / (2 * r ** 3))


def thin_u(E, nu):
    rm = (a + b) / 2
    return P * rm ** 2 * (1 - nu) / (2 * E * t)


def conv_plot(rows, key, ylabel, fname, title):
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    for label, data in rows:
        ax.plot([d["nodes"] for d in data], [d[key] for d in data], "o-", label=label)
    ax.set(xlabel="nodes", ylabel=ylabel, title=title)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = FIG / fname
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100 if abs(ref) > 1e-12 else 0.0


def build():
    r = Report("HW 7: 2D and 3D Models", "Q1 triangular plate (plane stress vs. 3D) · Q2 spherical pressure vessel material selection",
               due="Wed Nov 11, 2026, 11:59 PM (submitted late)")
    im = lambda n: AO / n  # noqa: E731

    # =========================================================== Q1
    r.h1("Q1. Triangular plate with three pin holes")
    r.p("Equilateral triangle, 8 in sides, 1 in thick, with a 3.5 in central hole and three 0.5 in holes on a 3.5 in radius "
        "toward the corners. Holes A and B carry cylindrical supports (fixed radially and axially, free tangentially); "
        "a 15,000 lbf horizontal load in the mid-plane acts at hole C. No material is specified, so ANSYS's default "
        "Structural Steel is used (E = 29.0×10⁶ psi, ν = 0.3).")

    r.h2("1. Plane stress or plane strain?")
    r.p("**Plane stress.** The plate is thin compared with its in-plane size (t = 1 in vs. 8 in sides), all loads act in "
        "the mid-plane, and both faces are free of traction, so $\\sigma_z = \\tau_{xz} = \\tau_{yz} \\approx 0$ through the "
        "thickness. Plane strain would need a body that is long in z, or faces restrained against z-motion; neither applies.")

    r.h2("2. Models, boundary conditions and loads")
    r.bullets([
        "**2D:** surface body in the XY plane, 2D behavior = Plane Stress, thickness 1 in, quadratic elements.",
        "**3D:** the same profile extruded 1 in (z = −0.5 to +0.5 in, so the load acts in the mid-plane), swept quadratic "
        "hexahedra with 4 elements through the thickness (fewer nodes than tetrahedra for the same accuracy).",
        "**Supports A and B:** Cylindrical Support on each hole (radial fixed, axial fixed, tangential free), i.e. a pin that lets the plate rotate.",
        "**Load at C:** 15,000 lbf in +x applied as a deformable Remote Force through the centre of hole C (a pin pulling on the hole). "
        "A Bearing Load was tried first, but on 2D edges its total changed with the mesh (15,137 to 15,610 lbf), so it was "
        "replaced to keep both models loaded identically and in exact equilibrium.",
        "**Mesh control:** a sizing on the three pin holes at ¼ of the global element size.",
    ])
    f2, f3 = Q1["2d"]["final"]["images"], Q1["3d"]["final"]["images"]
    r.img(im("q1_2d_model.png"), "2D plane-stress model: cylindrical supports at A and B, remote force at C.")
    r.img(im("q1_2d_mesh.png"), f"2D mesh used for the reported results ({Q1['2d']['final']['nodes']:,} nodes).")
    r.img(im("q1_3d_model.png"), "3D model: cylindrical supports at A and B, remote force at C.")
    r.img(im("q1_3d_mesh.png"), f"3D mesh used for the reported results ({Q1['3d']['final']['nodes']:,} nodes).")

    r.h2("3. Mesh refinement")
    rows = []
    for k in ("2d", "3d"):
        conv = Q1[k]["convergence"]
        for i, d in enumerate(conv):
            ch = "" if i == 0 else f"{pct(d['eqv_max_psi'], conv[i - 1]['eqv_max_psi']):.1f}"
            rows.append([k.upper(), f"{d['size_in']:g} / {d['size_in'] / 4:g}", f"{d['nodes']:,}", f"{d['eqv_max_psi']:,.0f}", ch,
                         f"{d['td_C_avg_in']:.5f}"])
    r.table(["Model", "Global / hole size (in)", "Nodes", "Max von Mises (psi)", "Change (%)", "Total def. at C (in)"], rows,
            "Manual mesh refinement (global size reduced; pin holes refined to a quarter of it)", cls="num")
    r.img(conv_plot([("2D plane stress", Q1["2d"]["convergence"]), ("3D", Q1["3d"]["convergence"])], "eqv_max_psi",
                    "max von Mises (psi)", "q1_conv.png", "Convergence of peak von Mises stress"),
          "Peak von Mises stress against number of nodes.", width="88%", border=False)
    c2, c3 = Q1["2d"]["convergence"], Q1["3d"]["convergence"]
    ch2 = pct(c2[-1]["eqv_max_psi"], c2[-2]["eqv_max_psi"])
    ch3 = pct(c3[-1]["eqv_max_psi"], c3[-2]["eqv_max_psi"])
    r.p(f"Manual refinement: the 2D peak changes {ch2:.1f}% and the 3D peak {ch3:.1f}% over the last refinement, and the "
        "deformation at C is converged to four digits in both. In both models the peak is on the edge of the large central "
        "hole, a real (free-edge) stress concentration, so the converged value is meaningful. The swept hex mesh lets the 3D "
        "study reach 108,000 nodes, under the 128,000-node student limit.")
    ad = []  # adaptive-convergence results are not reported (see adaptive() in ansys_q1.py)
    if ad:
        r.h3("Convergence tool (adaptive refinement on von Mises)")
        r.p("As in class, a Convergence object was added to the equivalent-stress result: Mechanical refines the mesh where "
            "the stress is highest and re-solves until the peak changes by less than the allowable amount between loops "
            "(start from a coarse free mesh, refinement depth 2).")
        r.table(["Model", "Start size (in)", "Allowable change", "Converged", "Last change", "Nodes", "Max von Mises (psi)", "Total def. at C (in)"],
                [[k.upper(), f"{d['start_size_in']:g}", f"{d['allowable_pct']:g}%", d["converged"],
                  f"{d['last_change_pct']:.2f}%" if d.get("last_change_pct") is not None else "—", f"{d['nodes']:,}",
                  f"{d['eqv_max_psi']:,.0f}", f"{d['td_C_avg_in']:.5f}"] for k, d in ad],
                "Adaptive convergence on peak von Mises stress", cls="num")
        for k, d in ad:
            if (AO / f"q1_{k}_adaptive_mesh.png").exists():
                r.img(AO / f"q1_{k}_adaptive_mesh.png", f"{k.upper()}: mesh after adaptive refinement, concentrated at the pin holes.")

    r.h2("4. Comparison of the 2D and 3D results")
    r.handcalc("Hand check: reactions from statics")
    r.p("Pins A and B give four unknowns and three equations, so the vertical reactions follow from statics while the "
        "horizontal load splits between A and B (by symmetry, equally).")
    r.step(r"\sum M_A = 0:\ B_y", r"\frac{F\,(y_C - y_A)}{x_B - x_A}", rf"\frac{{(15000)({yC - yA:.3f})}}{{{AB:.3f}}}", f"{By:,.1f}", "lbf")
    r.step(r"\sum F_y = 0:\ A_y", r"-B_y", None, f"{Ay:,.1f}", "lbf")
    r.step(r"\sum F_x = 0:\ A_x + B_x", r"-F", None, f"{Ax_plus_Bx:,.0f}", "lbf", "Symmetry: A_x = B_x = −7,500 lbf.")
    r.end_handcalc()
    q2d, q3d = Q1["2d"]["final"], Q1["3d"]["final"]
    rows = [
        ["Reaction A, x (lbf)", f"{-F / 2:,.1f}", f"{q2d['RA']['x']:,.1f}", f"{q3d['RA']['x']:,.1f}"],
        ["Reaction A, y (lbf)", f"{Ay:,.1f}", f"{q2d['RA']['y']:,.1f}", f"{q3d['RA']['y']:,.1f}"],
        ["Reaction B, x (lbf)", f"{-F / 2:,.1f}", f"{q2d['RB']['x']:,.1f}", f"{q3d['RB']['x']:,.1f}"],
        ["Reaction B, y (lbf)", f"{By:,.1f}", f"{q2d['RB']['y']:,.1f}", f"{q3d['RB']['y']:,.1f}"],
        ["Σ Fx = A_x + B_x + 15,000 (lbf)", "0", f"{q2d['RA']['x'] + q2d['RB']['x'] + F:,.1f}", f"{q3d['RA']['x'] + q3d['RB']['x'] + F:,.1f}"],
        ["Σ Fy = A_y + B_y (lbf)", "0", f"{q2d['RA']['y'] + q2d['RB']['y']:,.1f}", f"{q3d['RA']['y'] + q3d['RB']['y']:,.1f}"],
        ["Max von Mises (psi)", "", f"{q2d['eqv_max_psi']:,.0f}", f"{q3d['eqv_max_psi']:,.0f}"],
        ["Total deformation at C (in)", "", f"{q2d['td_C_avg_in']:.5f}", f"{q3d['td_C_avg_in']:.5f}"],
        ["X deformation at C (in)", "", f"{q2d['dx_C_avg_in']:.5f}", f"{q3d['dx_C_avg_in']:.5f}"],
        ["Y deformation at C (in)", "", f"{q2d['dy_C_avg_in']:.6f}", f"{q3d['dy_C_avg_in']:.6f}"],
    ]
    r.table(["Result", "Statics", "2D plane stress", "3D"], rows, "2D vs. 3D results (point C values are averages over hole C)", cls="num")
    d_td = pct(q3d["td_C_avg_in"], q2d["td_C_avg_in"])
    d_vm = pct(q3d["eqv_max_psi"], q2d["eqv_max_psi"])
    r.bullets([
        "**(a, b) Reactions and equilibrium:** both models give $A_y = -B_y$ = 12,990 lbf, matching statics, and the horizontal "
        "reactions add to −15,000 lbf, so ΣF = 0 in both.",
        f"**(c) Von Mises:** the contour patterns match: the highest stress is on the edge of the large hole, with secondary "
        f"peaks beside the pin holes. The peak value differs by {d_vm:.1f}% (2D {q2d['eqv_max_psi']:,.0f} psi vs. 3D "
        f"{q3d['eqv_max_psi']:,.0f} psi), so the two models are not identical. The difference comes from the supports: the 3D "
        "cylindrical supports fix the pin-hole faces axially, restraining through-thickness (Poisson) deformation that plane "
        "stress lets happen freely, which changes how load flows around the large hole. Plane stress is slightly conservative "
        "here.",
        f"**(d, e) Deformation of C:** total and X deformation agree within {d_td:.1f}%; Y deformation at C is nearly zero "
        "in both (the load is horizontal). The plane-stress assumption is therefore justified for this plate.",
    ])
    for kind, lab in (("2d", "2D"), ("3d", "3D")):
        r.img(im(f"q1_{kind}_eqv.png"), f"{lab}: equivalent (von Mises) stress (psi).")
        r.img(im(f"q1_{kind}_td_C.png"), f"{lab}: total deformation at hole C (in).")
        r.img(im(f"q1_{kind}_dx_C.png"), f"{lab}: directional deformation X at hole C (in).")
        r.img(im(f"q1_{kind}_dy_C.png"), f"{lab}: directional deformation Y at hole C (in).")
        r.img(im(f"q1_{kind}_fr_A.png"), f"{lab}: reaction at A.")
        r.img(im(f"q1_{kind}_fr_B.png"), f"{lab}: reaction at B.")

    # =========================================================== Q2
    r.pagebreak()
    r.h1("Q2. Spherical pressure vessel for liquid hydrogen")
    r.p(f"Internal pressure {P:,.0f} psi, inner diameter 75 in (a = {a} in), wall 2 in (b = {b} in). Requirement: radial "
        f"expansion ≤ {LIMIT} in. Materials from the ANSYS Engineering Data library where available, as instructed.")
    r.h2("1–2. Model and boundary conditions")
    r.bullets([
        "**2D axisymmetric model.** A sphere under internal pressure is axisymmetric in geometry, load and supports about "
        "any diameter, so a meridian section revolved about the Y axis represents the whole vessel exactly. Because it is "
        "also symmetric about the equator, a quarter annulus (x ≥ 0, y ≥ 0) is enough.",
        "**Frictionless support on the equator edge (y = 0):** symmetry, $u_y = 0$.",
        "**Frictionless support on the axis edge (x = 0):** points on the axis cannot move radially, $u_x = 0$.",
        "**Pressure:** 4,000 psi normal to the inner surface.",
        "**Results:** radial deformation and radial stress in a cylindrical coordinate system at the centre (its X axis is "
        "radial in the meridian plane); hoop stress = Z (circumferential) normal stress.",
    ])
    r.img(im("q2_model.png"), "Axisymmetric quarter model: frictionless supports (A, B) and internal pressure (C).")
    r.img(im("q2_mesh.png"), "Mesh (quadratic, 0.125 in elements: 16 through the wall).")
    rows = [[f"{c['size_in']:g}", f"{c['nodes']:,}", f"{c['ur_max_in']:.6f}", f"{c['sh_max_psi']:,.0f}"] for c in Q2["convergence"]]
    r.table(["Element size (in)", "Nodes", "Max radial deformation (in)", "Max hoop stress (psi)"], rows,
            "Mesh refinement (E-Glass): results do not change with refinement", cls="num")

    r.handcalc("Hand check: thick-walled sphere (Lamé) and thin-wall estimate")
    km = P * a ** 3 / (b ** 3 - a ** 3)
    r.eq(r"u(r) = \frac{p\,a^3}{E\,(b^3-a^3)}\left[(1-2\nu)\,r + \frac{(1+\nu)\,b^3}{2r^2}\right],\qquad "
         r"\sigma_r = \frac{p\,a^3}{b^3-a^3}\left(1-\frac{b^3}{r^3}\right),\qquad \sigma_\theta = \frac{p\,a^3}{b^3-a^3}\left(1+\frac{b^3}{2r^3}\right)")
    r.step(r"\frac{p\,a^3}{b^3-a^3}", None, rf"\frac{{(4000)(37.5)^3}}{{(39.5)^3-(37.5)^3}}", f"{km:,.1f}", "psi")
    r.step(r"\sigma_\theta(a)", r"\frac{p\,a^3}{b^3-a^3}\left(1+\frac{b^3}{2a^3}\right)", None, f"{lame_st(a):,.0f}", "psi")
    r.step(r"\sigma_r(a)", r"-p", None, f"{lame_sr(a):,.0f}", "psi")
    for name, _, E, nu, *_ in MATS:
        r.step(rf"u_{{\text{{{name}}}}}(a)", None,
               rf"\frac{{{km:,.1f}}}{{{E / 1e6:.3f}\times10^{{6}}}}\left[(1-2({nu}))(37.5) + \frac{{(1+{nu})(39.5)^3}}{{2(37.5)^2}}\right]",
               f"{lame_u(a, E, nu):.5f}", "in")
    r.end_handcalc()

    r.h2("3. Maximum radial deformation by material")
    rows = []
    for name, ans_name, E, nu, src, wt, cost, ts in MATS:
        fe = Q2["materials"][ans_name]["ur_max_in"]
        ok = fe <= LIMIT
        rows.append([name, f"{E / 1e6:.2f}", f"{nu:.2f}", f"{fe:.4f}", f"{lame_u(a, E, nu):.4f}", f"{thin_u(E, nu):.4f}",
                     "Yes" if name == "Kevlar 49" else ("meets limit" if ok else "No")])
    r.table(["Fiber", "E (Msi)", "ν", "Max radial deformation, ANSYS (in)", "Lamé (in)", "Thin wall (in)", "Selected"], rows,
            f"Radial deformation against the {LIMIT} in limit", cls="num")
    r.p("Material sources: " + "; ".join(f"**{n}**: {src}" for n, _, _, _, src, *_ in MATS) + ".")

    r.h2("4. Selected material: Kevlar 49")
    kev = Q2["materials"]["Kevlar 49 (handout)"]
    car = Q2["materials"]["Carbon Fiber 230 GPa (isotropic)"]
    r.p(f"E-glass ({Q2['materials']['E-Glass']['ur_max_in']:.4f} in) and S-glass ({Q2['materials']['S-Glass']['ur_max_in']:.4f} in) "
        f"expand more than {LIMIT} in. Kevlar 49 ({kev['ur_max_in']:.4f} in) and carbon fiber ({car['ur_max_in']:.4f} in) both "
        "meet the limit. **Kevlar 49 is selected** because it satisfies the stiffness requirement with margin, is the "
        "lightest (89.9 lb/ft³ vs. 108.9 for carbon) and is cheaper (cost factor 4 vs. 6–8). Strength is not limiting: "
        f"the peak hoop stress is {kev['sh_max_psi']:,.0f} psi against a tensile strength of 400,000 psi (factor of safety "
        f"{400000 / kev['sh_max_psi']:.1f}), and the radial stress is only −4,000 psi at the inner wall against a compressive "
        "strength of 128,000 psi. Carbon fiber is the alternative if the smallest expansion matters more than cost and weight. "
        "(A real liquid-hydrogen tank would also need a liner, because fiber composites alone are permeable to hydrogen, and "
        "properties at cryogenic temperature; both are beyond this assignment.)")
    r.callout("Kevlar 49 is not in the ANSYS Engineering Data libraries, so it was defined from the HW 7 table "
              "(E = 19.0×10⁶ psi, 89.9 lb/ft³) with ν = 0.36 assumed. The three library fibers come straight from ANSYS's "
              "Composite Materials library.", "warn")

    r.h2("5–7. Contours for the selected material (Kevlar 49)")
    r.img(im("q2_kevlar_ur.png"), "Kevlar 49: radial (directional) deformation (in).")
    r.img(im("q2_kevlar_sr.png"), "Kevlar 49: radial stress (psi): −4,000 psi at the inner wall, 0 at the outer wall.")
    r.img(im("q2_kevlar_sh.png"), "Kevlar 49: hoop (circumferential) stress (psi).")
    r.p(f"ANSYS against Lamé for Kevlar 49: radial deformation {kev['ur_max_in']:.5f} vs. {lame_u(a, 19.0e6, 0.36):.5f} in, "
        f"hoop stress {kev['sh_max_psi']:,.0f} vs. {lame_st(a):,.0f} psi, radial stress {kev['sr_min_psi']:,.0f} vs. "
        f"{lame_sr(a):,.0f} psi.")
    out = r.docx(OUT_DOCX)
    print("wrote", out)


if __name__ == "__main__":
    build()
