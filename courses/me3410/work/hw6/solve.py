"""HW 6: plate (L-bracket) under distributed pressure. Hand checks + ANSYS results -> Word.

    python solve.py     (reads ansys_out/results.json from ansys.py via run_ansys.sh)
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle as CirclePatch, Rectangle  # noqa: E402
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullLocator  # noqa: E402

import hand as H  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "HW6_Plate_Pressure.docx"
AO = HERE / "ansys_out"
FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
HANDOUT = HERE.parents[1] / "canvas" / "files" / "_extract" / "PLATE_UNDER_DISTRIBUTED_PRESSURE_V1" / "img" / "image1.png"
RS = json.loads((AO / "results.json").read_text())
FIN = RS["final"]
CONV = RS["convergence"]
AD = RS.get("adaptive", {})


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100


# ------------------------------------------------------------------ figures
def outline():
    """Bracket outline (mm) as one closed polyline, for the dimensioned sketch."""
    pts = [(0, 0), (200, 0)]
    pts += [(200 + 20 * math.sin(a), -20 + 20 * math.cos(a)) for a in np.linspace(0, math.pi, 40)]
    pts += [(90, -40)]
    pts += [(90 - 50 * math.sin(a), -90 + 50 * math.cos(a)) for a in np.linspace(0, math.pi / 2, 30)]
    pts += [(40, -120)]
    pts += [(20 + 20 * math.cos(a), -120 - 20 * math.sin(a)) for a in np.linspace(0, math.pi, 40)]
    pts += [(0, 0)]
    return np.array(pts)


def fig_geometry():
    o = outline()
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.fill(o[:, 0], o[:, 1], color="#dfe7f1", ec="k", lw=1.2)
    for (x, y) in ((20, -20), (200, -20), (20, -120)):
        ax.add_patch(CirclePatch((x, y), 5, fc="white", ec="k", lw=1))
        ax.plot([x - 8, x + 8], [y, y], "k-.", lw=0.5)
        ax.plot([x, x], [y - 8, y + 8], "k-.", lw=0.5)
    ax.add_patch(Rectangle((-8, -132), 8, 140, fc="white", ec="0.3", hatch="////", lw=0.8))
    for xi in np.linspace(0, 200, 11):
        ax.annotate("", (xi, 0.5), (xi, 14), arrowprops=dict(arrowstyle="->", lw=0.8, color="C3"))
    ax.plot([0, 200], [14, 14], color="C3", lw=0.8)
    ax.text(100, 17, "p = 250 N/cm² = 2.5 MPa", ha="center", color="C3")
    ax.text(-12, -60, "fixed (wall)", ha="right", va="center", fontsize=8, rotation=90)
    notes = [((20, -20), "Ø10 at (20, −20)", (35, -15)), ((200, -20), "Ø10 at (200, −20)", (150, -28)),
             ((20, -120), "Ø10 at (20, −120)", (48, -125))]
    for _, s, xy in notes:
        ax.text(*xy, s, fontsize=7.5)
    ax.text(70, -62, "R50", fontsize=8)
    ax.text(222, -45, "R20", fontsize=8)
    ax.text(44, -135, "R20", fontsize=8)
    ax.annotate("", (0, -152), (200, -152), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(100, -160, "L = 200 (wall to hole centre)", ha="center", fontsize=8)
    ax.annotate("", (235, 0), (235, -40), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(238, -20, "40", fontsize=8, va="center")
    ax.annotate("", (-30, 0), (-30, -120), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-33, -60, "H = 120", rotation=90, fontsize=8, va="center", ha="right")
    ax.annotate("", (0, -100), (40, -100), arrowprops=dict(arrowstyle="<->", lw=0.5, color="0.4"))
    ax.text(20, -97, "40", fontsize=7, ha="center", color="0.3")
    ax.text(150, -110, "t = 2 mm, E = 200 GPa, ν = 0.3\norigin at the top-left corner\nall dimensions in mm",
            fontsize=8, ha="center")
    ax.set_aspect("equal")
    ax.set_xlim(-50, 250)
    ax.set_ylim(-170, 25)
    ax.axis("off")
    fig.tight_layout()
    p = FIG / "geometry.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def nice_log(ax, n):
    ax.xaxis.set_major_locator(FixedLocator(n))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([f"{v:,}" for v in n], fontsize=7)


def fig_conv():
    n = [c["nodes"] for c in CONV]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax = axs[0]
    ax.plot(n, [c["eqv_max"] for c in CONV], "o-", color="C3", label="global max (wall/top corner)")
    ax.plot(n, [c["eqv_fillet_max"] for c in CONV], "s-", color="C0", label="max on R50 fillet")
    ax.plot(n, [c["eqv_holes_max"] for c in CONV], "^-", color="C2", label="max on hole edges")
    ax.axhline(H.SIG_PK, color="C0", ls=":", lw=1)
    ax.text(n[0], H.SIG_PK + 1.5, f"beam-theory nominal in the fillet ({H.SIG_PK:.0f} MPa)", fontsize=7, color="C0")
    ax.set(xscale="log", xlabel="nodes", ylabel="von Mises (MPa)")
    nice_log(ax, n)
    ax.legend(fontsize=6.5, loc="upper left")
    ax.grid(alpha=0.3)
    ax = axs[1]
    ax.plot(n, [c["td_max"] for c in CONV], "o-", color="k")
    ax.set(xscale="log", xlabel="nodes", ylabel="max total deformation (mm)")
    nice_log(ax, n)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.6f"))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "convergence.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_section():
    prof = FIN.get("sx_profile")
    if not prof:
        return None
    yv = np.array(prof["Y Coordinate"])
    v = np.array(prof["Values"])
    if len(yv) < 3:
        return None
    y = yv * 1000 if abs(yv).max() < 1 else yv           # PlotData is SI (m, Pa)
    v_mpa = v / 1e6 if abs(v).max() > 1e4 else v
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    ax.plot(v_mpa, y, "o", ms=3, label="ANSYS (path at x = 140 mm)")
    yy = np.linspace(-40, 0, 50)
    ax.plot(H.M(H.X_SEC) * (yy + 20) / H.I_arm, yy, "-", label="beam theory  σ = M y / I")
    ax.axvline(0, color="0.6", lw=0.6)
    ax.set(xlabel="σx (MPa)", ylabel="y (mm)")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "section_140.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ report
def build():
    r = Report("HW 6: Plate Under Distributed Pressure",
               "L-shaped bracket, 2D plane stress in ANSYS Workbench Mechanical",
               due="Wed Oct 28, 2026, 11:59 PM (submitted late)")
    im = lambda n: AO / n  # noqa: E731

    r.h1("Problem")
    r.p("A steel bracket, 0.2 cm thick, is attached to a wall along its left edge and carries a uniform pressure "
        "p = 250 N/cm² on its top edge. It has three holes of 1 cm diameter. E = 200 GPa, ν = 0.3. Required: plane "
        "stress or strain (justified), the FE model with its boundary conditions and loads, mesh refinement (manual and "
        "adaptive), the total deformation, deformed vs. undeformed shape, and the von Mises stress contour.")
    if HANDOUT.exists():
        r.img(HANDOUT, "Bracket and loading (from the assignment handout).", width="70%", border=False)
    r.p("Dimensions not written on the figure were read from it and kept consistent with the given ones: both arms are "
        "4 cm deep, their ends are R2 cm semicircles centred on the end holes, H = 12 cm runs from the top edge to the "
        "lower hole centre and L = 20 cm from the wall to the right-hand hole centre. The model below uses millimetres.")
    r.img(fig_geometry(), "Geometry used in the model (mm).", width="92%", border=False)

    # ---------------------------------------------------------------- 1
    r.h2("1. Plane stress or plane strain?")
    r.p("**Plane stress.** The bracket is a thin plate: t = 2 mm against in-plane dimensions of 120 to 220 mm (t/L ≈ 1/100). "
        "The pressure acts on the edge, in the plane of the plate, and the two flat faces are free of load, so "
        "$\\sigma_z = \\tau_{xz} = \\tau_{yz} = 0$ on both faces and, because the plate is thin, essentially zero through "
        "the thickness. The plate is free to get thinner or thicker (Poisson effect), so $\\varepsilon_z \\neq 0$. Plane strain "
        "is the opposite case ($\\varepsilon_z = 0$, $\\sigma_z \\neq 0$): a body that is long in z, like a dam or a long "
        "pipe, or one whose faces are held against z-motion. Neither applies here.")

    # ---------------------------------------------------------------- 2
    r.h2("2. Finite element model, boundary conditions and loads")
    r.bullets([
        "**Analysis:** Static Structural, geometry imported as a 2D surface body; 2D Behavior = **Plane Stress**, "
        "thickness 2 mm. Elements: quadratic (8-node) plane-stress quadrilaterals (PLANE183).",
        "**Material:** ANSYS Structural Steel, which has exactly the given E = 200 GPa and ν = 0.3 "
        "(its yield strength, 250 MPa, is used only for a factor of safety).",
        "**Boundary condition: Fixed Support on the left edge** (x = 0, 120 mm long), $u_x = u_y = 0$. The hatching in the "
        "figure shows this edge attached to the wall, so it cannot translate or rotate. The three holes have no "
        "pins or bolts drawn in them, so they are left free (traction-free edges).",
        "**Load: Pressure 2.5 MPa** (250 N/cm²) normal to the top edge, over its full 200 mm length "
        f"(resultant {H.W:,.0f} N = p·t·L = 2.5 × 2 × 200).",
        "**Mesh controls:** global element size, plus an Edge Sizing on the R50 fillet and the three holes at "
        "one quarter of the global size.",
    ])
    r.img(im("model.png"), "FE model: fixed support on the wall edge (A) and 2.5 MPa pressure on the top edge (B).", width="85%")
    r.img(im("mesh.png"), f"Final mesh: {FIN['size']:g} mm global size, {FIN['size'] / 4:g} mm on the fillet and holes "
          f"({FIN['nodes']:,} nodes, {FIN['elements']:,} elements).", width="85%")
    r.img(im("mesh_fillet.png"), "Close-up of the mesh at the R50 fillet and the upper-left hole.", width="70%")

    # ---------------------------------------------------------------- hand calcs
    r.h2("3. Hand checks")
    r.handcalc("Statics: load resultant and wall reactions")
    r.step("w", "p\\,t", "(2.5)(2)", H.w, "N/mm", "Edge pressure on a 2 mm plate is a line load.")
    r.step("W", "w\\,L", "(5)(200)", H.W, "N", "Acts at x = 100 mm.")
    r.step(r"\sum F_y = 0:\ R_y", "W", None, H.Ry, "N")
    r.step(r"\sum F_x = 0:\ R_x", None, None, "0", "N")
    r.step(r"\sum M = 0:\ M_{wall}", r"W\,\frac{L}{2}", "(1000)(100)", H.M_wall, r"N\cdot mm",
           "Equal to 100 N·m about any point on the wall, because every load is vertical.")
    r.end_handcalc()

    r.handcalc("Beam theory on the horizontal arm (40 × 2 mm section)")
    r.step("I", r"\frac{t\,h^3}{12}", r"\frac{(2)(40)^3}{12}", H.I_arm, "mm^4")
    r.p("Section x = 140 mm (60 mm of loaded arm to its right, away from the fillet and the end hole):")
    r.step("M(140)", r"\frac{w\,(200-x)^2}{2}", r"\frac{(5)(60)^2}{2}", H.M(H.X_SEC), r"N\cdot mm")
    r.step(r"\sigma_x", r"\pm\frac{M\,c}{I}", rf"\pm\frac{{(9000)(20)}}{{{fmt(H.I_arm)}}}", f"\\pm{H.SIG_SEC:.2f}", "MPa",
           "Tension on the top edge, compression on the bottom (the arm bends down like a cantilever).")
    r.p("Arm root (the fillet region). The section deepens through the R50 fillet, whose centre is at (90, −90): "
        "$h(x) = 90 - \\sqrt{50^2 - (x-90)^2}$ for 40 ≤ x ≤ 90 mm. The moment keeps growing toward the wall, so the "
        "beam-theory edge stress $\\sigma = 6M/(t\\,h^2)$ peaks inside the fillet, not at its end (x = 90 mm gives "
        f"{H.SIG_FIL:.1f} MPa). Scanning x from 40 to 90 mm:")
    r.step(r"x_{peak}", None, None, f"{H.X_PK:.0f}", "mm", f"Section depth there h = {H.H_PK:.1f} mm.")
    r.step(r"M(x_{peak})", r"\frac{w\,(200-x)^2}{2}", rf"\frac{{(5)({200 - H.X_PK:.0f})^2}}{{2}}", H.M(H.X_PK), r"N\cdot mm")
    r.step(r"\sigma_{nom}", r"\frac{6M}{t\,h^2}", rf"\frac{{6({fmt(H.M(H.X_PK))})}}{{(2)({H.H_PK:.1f})^2}}",
           f"{H.SIG_PK:.1f}", "MPa", "Nominal (beam-theory) stress at the fillet edge, before any stress concentration.")
    r.end_handcalc()

    r.handcalc("Tip deflection: unit-load method with the real (variable) section depth")
    r.p("The bracket is treated as a cantilever clamped at the wall, with section depth h(x) taken from the geometry "
        "(140 to 120 mm through the vertical arm, the R50 fillet blending down to 40 mm at x = 90, then 40 mm); holes are "
        "ignored. A unit load at the tip (x = 220 mm) gives m(x) = 220 − x and v = 1:")
    r.eq(r"\delta_{tip} = \int_0^{200}\frac{M(x)\,(220-x)}{E\,I(x)}\,dx + \int_0^{200}\frac{V(x)}{\kappa\,G\,A(x)}\,dx,"
         r"\qquad I(x)=\frac{t\,h(x)^3}{12},\ A(x)=t\,h(x),\ \kappa=\tfrac56,\ G=\frac{E}{2(1+\nu)}")
    r.step(r"\delta_{bending}", None, "\\text{(trapezoid rule, 20,000 steps)}", f"{H.DELTA_B:.4f}", "mm")
    r.step(r"\delta_{shear}", None, None, f"{H.DELTA_S:.4f}", "mm")
    r.step(r"\delta_{stiff}", r"\delta_{bending} + \delta_{shear}", None, f"{H.DELTA:.4f}", "mm",
           "Stiff estimate: assumes every fibre of the deep fillet and vertical-arm sections works in bending.")
    r.p("Flexible estimate: ignore the fillet material and clamp a uniform 40 mm arm at the face of the vertical arm "
        "(x = 40 mm), loaded length $L_c$ = 160 mm, plus the rotation carried out to the tip of the unloaded 20 mm rounded end:")
    r.step(r"\delta_{flex}", r"\frac{w L_c^4}{8EI} + \frac{w L_c^3}{6EI}(20)",
           rf"\frac{{(5)(160)^4}}{{8({fmt(H.E)})({fmt(H.I_arm)})}} + \frac{{(5)(160)^3(20)}}{{6({fmt(H.E)})({fmt(H.I_arm)})}}",
           f"{H.BOUNDS[40.0]:.4f}", "mm")
    r.p("The real tip deflection should fall between these two estimates.")
    r.end_handcalc()

    # ---------------------------------------------------------------- 4 mesh
    r.h2("4. Mesh refinement")
    r.h3("Manual refinement")
    rows = []
    for i, c in enumerate(CONV):
        ch_f = "" if i == 0 else f"{pct(c['eqv_fillet_max'], CONV[i - 1]['eqv_fillet_max']):.2f}"
        ch_t = "" if i == 0 else f"{pct(c['td_max'], CONV[i - 1]['td_max']):.2f}"
        rows.append([f"{c['size']:g} / {c['size'] / 4:g}", f"{c['nodes']:,}", f"{c['td_max']:.5f}", ch_t,
                     f"{c['eqv_fillet_max']:.2f}", ch_f, f"{c['eqv_holes_max']:.2f}", f"{c['eqv_corner_max']:.1f}",
                     f"{c['eqv_max']:.1f}"])
    r.table(["Global / fillet+hole size (mm)", "Nodes", "Max total def. (mm)", "Change (%)", "Max vM on fillet (MPa)",
             "Change (%)", "Max vM on holes (MPa)", "vM at wall/top corner (MPa)", "Global max vM (MPa)"], rows,
            "Manual mesh refinement (quadratic plane-stress elements)", cls="num")
    r.img(fig_conv(), "Convergence: stresses on the fillet and holes and the deformation settle; the global peak at the "
          "wall/top corner keeps rising.", width="98%", border=False)
    c1, c0 = CONV[-1], CONV[-2]
    r.p(f"The deflection changes {pct(c1['td_max'], c0['td_max']):.2f}% and the fillet stress "
        f"{pct(c1['eqv_fillet_max'], c0['eqv_fillet_max']):.2f}% over the last refinement, so both are converged. "
        "The **global** von Mises maximum does not converge. On the 4 and 2 mm meshes it is on the fillet; the stress at "
        "the top-left corner, where the fixed edge meets the loaded top edge, keeps climbing with every refinement ("
        + " → ".join(f"{c['eqv_corner_max']:.0f}" for c in CONV) + " MPa), overtakes the fillet at 1 mm and becomes the "
        "global maximum. That corner is a **stress singularity** of the idealized model: a perfectly rigid "
        "wall that also stops Poisson contraction, meeting a free (here pressure-loaded) edge at 90°, has infinite stress "
        "in elasticity theory, so the finer the mesh the larger the number. It is not a real stress; a real bolted or "
        "welded joint has finite stiffness and some radius. The meaningful peaks are the converged ones away from that "
        "corner, and the optimum mesh is the one where those stop changing. The hole-edge stress changes "
        f"{pct(c1['eqv_holes_max'], c0['eqv_holes_max']):.1f}% over the last step (within 5%, and the holes are well below "
        "the fillet, so they do not govern). Optimum mesh: the final one "
        f"({c1['size']:g} mm global, {c1['size'] / 4:g} mm on the fillet and holes).")
    r.img(im("von_mises_corner_zoom.png"), "Von Mises close-up at the wall/top corner: the stress is concentrated in the "
          "elements touching the corner (singularity).", width="70%")

    r.h3("Adaptive meshing (Convergence tool)")
    if AD:
        r.p("A Convergence object (target: change below 5% between loops) was added to a result. Mechanical then solves, "
            "refines the elements where that result is highest, and re-solves until the target is met or the loop limit is "
            "reached. The local edge sizing was switched off so that only the adaptive tool refines the mesh. Four runs:")
        lab = {"td": ("Max total deformation", "4 mm"), "eqv": ("Global max von Mises", "4 mm"),
               "fillet": ("Max von Mises on the fillet", "4 mm"), "eqv_fine": ("Global max von Mises", "1 mm")}
        rows = []
        for tag in ("td", "fillet", "eqv", "eqv_fine"):
            d = AD.get(tag)
            if not d:
                continue
            if d.get("error"):
                rows.append([lab[tag][0], lab[tag][1], "failed", "", "", "", "", ""])
                continue
            rows.append([lab[tag][0], lab[tag][1], f"{d['loops_max']} / {d['depth']}", d.get("converged") or "",
                         f"{d['last_change_pct']:.2f}" if d.get("last_change_pct") is not None else "",
                         f"{d['nodes']:,}", f"{d['td_max']:.5f}", f"{d['eqv_fillet_max']:.1f}", f"{d['eqv_max']:.1f}"])
        r.table(["Convergence object on", "Start mesh", "Max loops / depth", "Converged?", "Last change (%)", "Nodes",
                 "Max total def. (mm)", "Max vM fillet (MPa)", "Global max vM (MPa)"], rows,
                "Adaptive refinement runs", cls="num")
        if (AO / "adapt_eqv_res.png").exists():
            r.img(AO / "adapt_eqv_res.png", f"Adaptive run on the global von Mises from a 4 mm start: it stopped after "
                  f"one refinement ({AD['eqv']['nodes']:,} nodes) with the peak ({AD['eqv']['eqv_max']:.1f} MPa) on the "
                  "fillet, because on that coarse mesh the corner does not yet stand out.", width="80%")
        if (AO / "adapt_eqv_fine_tip_res.png").exists():
            r.img(AO / "adapt_eqv_fine_tip_res.png", "Adaptive run on the global von Mises from a 1 mm start, close-up 4 mm "
                  f"across the wall/top corner: after {AD['eqv_fine']['loops_max']} loops the peak is "
                  f"{AD['eqv_fine']['eqv_max']:.0f} MPa in the refined elements at the corner. (Mechanical's Mesh view keeps "
                  "showing the original 1 mm mesh; the refinement shows in the small contour facets at the corner.)",
                  width="70%")
        r.p(ADAPT_TEXT(AD))

    # ---------------------------------------------------------------- 5 results
    r.h2("5. Results")
    r.img(im("deformed_vs_undeformed.png"), "Deformed shape (auto-scaled) over the undeformed outline (wireframe). "
          "The arm bends down about the stiff, wall-fixed vertical part; the free end moves most.", width="85%")
    r.img(im("total_deformation.png"), f"Total deformation (mm), maximum {FIN['td_max']:.4f} mm at the free end.", width="85%")
    r.img(im("dir_deformation_y.png"), f"Directional deformation Y (mm), minimum {FIN['dy_min']:.4f} mm.", width="85%")
    r.img(im("von_mises.png"), f"Equivalent (von Mises) stress (MPa). The legend maximum ({FIN['eqv_max']:.0f} MPa) is the "
          "singular wall/top corner; elsewhere the highest stresses are along the top and bottom edges of the arm near the fillet.", width="85%")
    r.img(im("von_mises_fillet_zoom.png"), f"Von Mises close-up at the fillet and arm root: about {FIN['eqv_fillet_max']:.0f} MPa "
          "on the fillet edge, tension on the top edge and compression on the bottom edge.", width="70%")
    sp = fig_section()
    if sp:
        r.img(sp, "Bending stress σx across the arm at x = 140 mm: ANSYS against beam theory.", width="60%", border=False)

    # ---------------------------------------------------------------- 6 compare
    r.h2("6. Hand calculations vs. ANSYS")
    rows = [
        ["Wall reaction R_y (N)", f"{H.Ry:,.1f}", f"{abs(FIN['Ry']):,.2f}", f"{pct(abs(FIN['Ry']), H.Ry):.3f}"],
        ["Wall reaction R_x (N)", "0", f"{FIN['Rx']:.3f}", "—"],
        ["Wall moment M_z (N·mm)", f"{H.M_wall:,.0f}", f"{abs(FIN['Mz']):,.0f}", f"{pct(abs(FIN['Mz']), H.M_wall):.3f}"],
        ["σx, top of section x = 140 (MPa)", f"{H.SIG_SEC:.2f}", f"{FIN['sx_path_max']:.2f}", f"{pct(FIN['sx_path_max'], H.SIG_SEC):.1f}"],
        ["σx, bottom of section x = 140 (MPa)", f"{-H.SIG_SEC:.2f}", f"{FIN['sx_path_min']:.2f}", f"{pct(FIN['sx_path_min'], -H.SIG_SEC):.1f}"],
        ["Peak stress on the fillet edge (MPa)", f"{H.SIG_PK:.1f} (nominal)", f"{FIN['eqv_fillet_max']:.1f}",
         f"Kt ≈ {FIN['eqv_fillet_max'] / H.SIG_PK:.2f}"],
        ["Tip deflection (mm)", f"{H.DELTA:.4f} to {H.BOUNDS[40.0]:.4f}", f"{FIN['td_max']:.4f}", "inside the range"],
    ]
    r.table(["Quantity", "Hand", "ANSYS (final mesh)", "Difference (%)"], rows, "Hand checks against ANSYS", cls="num")
    r.p(COMPARE_TEXT(FIN))

    r.h2("7. Summary")
    r.bullets([
        "Plane stress: thin plate (t/L ≈ 1/100) loaded in its plane with free faces.",
        "Model: fixed left edge, 2.5 MPa on the top edge, quadratic plane-stress elements; equilibrium checks to round-off.",
        f"Mesh: deformation and fillet/hole stresses converge (last change {pct(c1['td_max'], c0['td_max']):.2f}% and "
        f"{pct(c1['eqv_fillet_max'], c0['eqv_fillet_max']):.2f}%); the wall/top corner is a singularity, so its peak "
        "is not used. Adaptive refinement converges on deformation and the fillet stress; on the global maximum it "
        "either misses the corner (coarse start) or chases it without converging (fine start).",
        f"Total deformation {FIN['td_max']:.4f} mm at the free end; the highest meaningful von Mises stress is "
        f"{FIN['eqv_fillet_max']:.0f} MPa on the R50 fillet, a factor of safety of {H.SY / FIN['eqv_fillet_max']:.1f} "
        "against the 250 MPa yield strength of structural steel.",
    ])
    out = r.docx(OUT_DOCX)
    print("wrote", out)


def ADAPT_TEXT(ad):
    td, fil, eq, fine = (ad.get(k, {}) for k in ("td", "fillet", "eqv", "eqv_fine"))
    c1 = CONV[-1]
    out = (f"**Deformation and the fillet stress converge** adaptively in one or two loops, to {td.get('td_max', 0):.4f} mm "
           f"and {fil.get('eqv_fillet_max', 0):.1f} MPa, within {pct(td.get('td_max', 1), c1['td_max']):.2f}% and "
           f"{pct(fil.get('eqv_fillet_max', 1), c1['eqv_fillet_max']):.1f}% of the finest manual mesh. ")
    out += (f"**The global maximum is where adaptive meshing breaks down, as the handout warns.** From the 4 mm start it "
            f"reported \"converged\" at {eq.get('eqv_max', 0):.1f} MPa, but only because the coarse mesh cannot see the "
            f"corner singularity yet ({CONV[0]['eqv_corner_max']:.1f} MPa there on a 4 mm mesh, below the fillet), so it "
            "refined the fillet instead. From the 1 mm "
            "start, where the corner already carries the peak, every loop refines the corner and the peak climbs "
            f"to {fine.get('eqv_max', 0):.0f} MPa after {fine.get('loops_max', 4)} loops (last change "
            f"{fine.get('last_change_pct', 0):.1f}%, not converged); more loops would only push it higher. Meanwhile the "
            f"fillet stress ({fine.get('eqv_fillet_max', 0):.1f} MPa) and deflection ({fine.get('td_max', 0):.4f} mm) in that "
            "run stay where the other runs put them. Adaptive meshing is useful here only when the Convergence object is "
            "put on the deformation or on a stress scoped away from the singular corner.")
    return out


def COMPARE_TEXT(f):
    kt = f["eqv_fillet_max"] / H.SIG_PK
    return (
        "**Reactions** match statics to round-off, which confirms the load (2.5 MPa × 2 mm × 200 mm = 1000 N) and the "
        "support. **Bending stress at x = 140 mm** follows the linear My/I distribution (figure above); ANSYS is "
        f"{H.SIG_SEC - f['sx_path_max']:.2f} MPa below beam theory at the edges, the size of the elasticity correction "
        "beam theory leaves out when the beam's edge carries a distributed pressure (of order p/5 = "
        f"{H.DEEP_CORR:.1f} MPa). **At the fillet** ANSYS gives {f['eqv_fillet_max']:.1f} MPa against a beam-theory "
        f"nominal of {H.SIG_PK:.1f} MPa, an effective stress-concentration factor of {kt:.2f}. That is expected: the "
        "fillet is the inside corner of a knee, where the arm's bottom-edge compression has to turn 90° into the vertical "
        "arm. The stress paths crowd the concave edge (the curved-beam effect), so the edge stress is above the "
        "straight-beam value even with a generous R50 radius. Beam theory does put the peak in the right place: inside "
        "the fillet, toward its upper end where it meets the arm, which is where the contour shows it. **Tip "
        "deflection:** ANSYS "
        f"({f['td_max']:.4f} mm) lies between the stiff ({H.DELTA:.4f} mm) and flexible ({H.BOUNDS[40.0]:.4f} mm) "
        "estimates, closer to the flexible one. The material deep in the fillet corner carries little bending stress "
        "(blue in the contour), so the arm behaves almost as if clamped at the face of the vertical arm, and the "
        "vertical arm itself flexes a little against the wall.")


if __name__ == "__main__":
    build()
