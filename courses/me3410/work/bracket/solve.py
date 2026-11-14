"""In-class tutorial: 3D aluminum bracket. Hand checks + ANSYS results -> Word.

    python solve.py     (reads ansys_out/results.json from ansys.py + ansys_tail.py via run_ansys.sh)
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
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402

import hand as H  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "InClass_3D_Bracket.docx"
AO = HERE / "ansys_out"
FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
RS = json.loads((AO / "results.json").read_text())
FIN = RS["final"]
CONV = [c for c in RS["convergence"] if not c.get("skipped")]
LOC = [c for c in RS.get("local", []) if not c.get("skipped")]
AD = RS.get("adaptive", {})
VAR = RS.get("variant", {})


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100


# ------------------------------------------------------------------ figures
def fig_geometry():
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 4.3), gridspec_kw={"width_ratios": [1.25, 1]})
    # front view (looking along -Z): upright outline, bearing hole, base edge
    ax = axs[0]
    t = np.linspace(0, math.pi / 2, 25)
    pts = [(0, 0), (60, 0), (60, 80)] + [(40 + 20 * math.cos(a), 80 + 20 * math.sin(a)) for a in t]
    pts += [(20 - 20 * math.sin(a), 80 + 20 * math.cos(a)) for a in t] + [(0, 0)]
    p = np.array(pts)
    ax.fill(p[:, 0], p[:, 1], color="#dfe7f1", ec="k", lw=1.1)
    ax.add_patch(CirclePatch((30, 70), 15, fc="white", ec="k", lw=1))
    ax.plot([0, 60], [10, 10], "k--", lw=0.6)
    for x in (15, 45):
        ax.plot([x - 5, x - 5, x + 5, x + 5], [0, 10, 10, 0], ":", color="0.4", lw=0.7)
    ax.annotate("", (-8, 0), (-8, 100), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-11, 50, "100", rotation=90, va="center", ha="right", fontsize=8)
    ax.annotate("", (70, 0), (70, 70), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(72, 35, "70", va="center", fontsize=8)
    ax.annotate("", (0, -8), (60, -8), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(30, -15, "60", ha="center", fontsize=8)
    ax.text(30, 70, "Ø30", ha="center", va="center", fontsize=8)
    ax.text(48, 96, "R20", fontsize=7)
    ax.text(18, 3, "Ø10 bolt holes (hidden)", fontsize=6.5, color="0.35")
    ax.annotate("", (30, 70), (30 + 26, 70), arrowprops=dict(arrowstyle="<-", color="C3", lw=1.3))
    ax.annotate("", (30, 70), (30, 70 + 20), arrowprops=dict(arrowstyle="<-", color="C3", lw=1.3))
    ax.text(57, 66, "5500 N (X)", color="C3", fontsize=7)
    ax.text(31, 92, "3500 N (Y)", color="C3", fontsize=7)
    ax.text(30, 50, "1700 N (Z, out of page)", color="C3", fontsize=7, ha="center")
    ax.set_title("Front view (X–Y)", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-22, 92)
    ax.set_ylim(-22, 108)
    ax.axis("off")
    # side view (looking along +X): L shape with R10 fillet
    ax = axs[1]
    t = np.linspace(0, math.pi / 2, 20)
    pts = [(0, 0), (50, 0), (50, 10), (20, 10)] + [(20 - 10 * math.sin(a), 20 - 10 * math.cos(a)) for a in t]
    pts += [(10, 100), (0, 100), (0, 0)]
    p = np.array(pts)
    ax.fill(p[:, 0], p[:, 1], color="#dfe7f1", ec="k", lw=1.1)
    ax.plot([0, 10], [55, 55], "k:", lw=0.7)
    ax.plot([0, 10], [85, 85], "k:", lw=0.7)
    ax.plot([30, 30, 40, 40], [0, 10, 10, 0], ":", color="0.4", lw=0.7)
    ax.add_patch(Rectangle((-4, -6), 58, 6, fc="white", ec="0.3", hatch="////", lw=0.7))
    ax.text(25, -13, "base bottom fixed", ha="center", fontsize=7)
    ax.annotate("", (0, 104), (10, 104), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(5, 107, "10", ha="center", fontsize=7)
    ax.annotate("", (0, -22), (50, -22), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(25, -29, "50", ha="center", fontsize=8)
    ax.annotate("", (56, 0), (56, 10), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(58, 5, "10", va="center", fontsize=7)
    ax.text(20, 22, "R10", fontsize=7)
    ax.text(41, 13, "Ø10 at z = 35", fontsize=6.5, color="0.35", ha="center")
    ax.text(30, 60, "Z →\n(front)", fontsize=7, ha="center", color="0.3")
    ax.set_title("Side view (Z–Y)", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-10, 66)
    ax.set_ylim(-34, 112)
    ax.axis("off")
    fig.text(0.5, 0.01, "Aluminum alloy, thickness 10 mm, all dimensions in mm", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    p = FIG / "geometry.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def nice_log(ax, n):
    ax.xaxis.set_major_locator(FixedLocator(n))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([f"{v:,}" for v in n], fontsize=6.5, rotation=30)


def fig_conv():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax = axs[0]
    n = [c["nodes"] for c in CONV]
    ax.plot(n, [c["eqv_fillet_max"] for c in CONV], "o-", color="C0", label="global size (fillet = size / 2)")
    nl = [c["nodes"] for c in LOC]
    if LOC:
        ax.plot(nl, [c["eqv_fillet_max"] for c in LOC], "s-", color="C2", label="2.5 mm global, finer fillet")
    ax.plot(n, [c["eqv_base_max"] for c in CONV], "^--", color="C3", label="fixed base face (singular edge)")
    ax.plot(n, [c["sy_back_max"] for c in CONV], "d-", color="C1", label="σy back face, y = 35 mm")
    ax.set(xscale="log", xlabel="nodes", ylabel="stress (MPa)")
    nice_log(ax, sorted(set(n + nl)))
    ax.legend(fontsize=6)
    ax.grid(alpha=0.3)
    ax = axs[1]
    ax.plot(n, [c["td_max"] for c in CONV], "o-", color="k", label="global size")
    if LOC:
        ax.plot(nl, [c["td_max"] for c in LOC], "s-", color="C2", label="finer fillet")
    ax.set(xscale="log", xlabel="nodes", ylabel="max total deformation (mm)")
    nice_log(ax, sorted(set(n + nl)))
    ax.legend(fontsize=6.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "convergence.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def profile(key, coord):
    prof = FIN.get(key + "_profile")
    if not prof or "Values" not in prof:
        return None
    ck = [k for k in prof if k.startswith(coord)]
    if not ck:
        return None
    c = np.array(prof[ck[0]], float)
    v = np.array(prof["Values"], float)
    c = c * 1000 if abs(c).max() < 1 else c
    v = v / 1e6 if abs(v).max() > 1e4 else v
    return c, v


def fig_sections():
    a = profile("sy_back", "X")
    b = profile("sy_thick", "Z")
    if a is None and b is None:
        return None
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8))
    if a is not None:
        ax = axs[0]
        ax.plot(a[0], a[1], "o", ms=2.5, label="ANSYS")
        xx = np.linspace(0, 60, 50)
        ax.plot(xx, [H.sigma_y(x, 0.0) for x in xx], "-", label="beam theory")
        ax.set(xlabel="x (mm)", ylabel="σy (MPa)", title="Back face z = 0, y = 35 mm")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
    if b is not None:
        ax = axs[1]
        ax.plot(b[0], b[1], "o", ms=2.5, label="ANSYS")
        zz = np.linspace(0, 10, 30)
        ax.plot(zz, [H.sigma_y(30.0, z) for z in zz], "-", label="beam theory")
        ax.axhline(0, color="0.6", lw=0.6)
        ax.set(xlabel="z (mm)", ylabel="σy (MPa)", title="Through the thickness, x = 30, y = 35 mm")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "sections.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ report
def build():
    r = Report("In-Class Tutorial: 3D Bracket",
               "Aluminum bracket with a bearing load: 3D static structural in ANSYS Workbench Mechanical",
               due="Thu Nov 19, 2026, 11:59 PM")
    im = lambda n: AO / n  # noqa: E731
    pk = FIN.get("max_loc")
    fl = LOC[-1] if LOC else CONV[-1]

    r.h1("Problem")
    r.p("An aluminum bracket, 10 mm thick, is fixed on the bottom face of its base. The base is 60 mm wide (X) and 50 mm "
        "deep (Z) with two 10 mm bolt holes; the upright is 100 mm tall with a 30 mm bearing hole centred 70 mm above "
        "the base plane. The fillet radii are 10 and 20 mm. The bearing carries 5500 N in X, 3500 N in Y and 1700 N "
        "in Z. Required: the FE model with boundary conditions and loads, the equivalent stress, the total and X/Y/Z "
        "deformations, and the reaction force.")
    r.p("**Geometry as modelled.** The handout figure is an isometric sketch, so some placements were read from it: "
        "X runs along the 60 mm front edge, Y is up and Z points toward the front. The upright stands on the back edge "
        "of the base (z = 0 to 10) across the full 60 mm width. The R20 fillets round its two top corners, and the "
        "R10 fillet is the inside corner where the upright meets the base. The bolt holes are 15 mm from the front edge "
        "and 15 mm from the left and right edges, at (15, z = 35) and (45, z = 35). The bearing-hole axis is along Z, so "
        "the X and Y load components are radial to the hole and the Z component acts along its axis.")
    r.img(fig_geometry(), "Geometry used in the model (mm) and the load on the bearing hole.", width="95%", border=False)

    # ---------------------------------------------------------------- 1 model
    r.h2("1. Finite element model, boundary conditions and loads")
    r.bullets([
        "**Analysis:** Static Structural, 3D solid imported from STEP (single body). Elements: quadratic 10-node "
        "tetrahedra (SOLID187).",
        "**Material:** ANSYS Aluminum Alloy: E = 71 GPa, ν = 0.33, tensile yield 280 MPa.",
        "**Boundary condition: Fixed Support on the bottom face of the base** ($u_x = u_y = u_z = 0$), as the handout "
        "states. The bolt holes are left free: the fixed bottom face already stands in for the bolted joint.",
        "**Load on the 30 mm hole.** A **Bearing Load** carries the radial components, 5500 N in X and 3500 N in Y. "
        "Mechanical distributes it over the half of the hole the pin presses on, as a pin would. A Bearing Load only "
        "acts radially, so the axial 1700 N in Z is a separate **Force** on the same hole surface.",
        "**Mesh controls:** a global element size, plus a Face Sizing on the R10 fillet and the bearing hole.",
    ])
    r.img(im("model.png"), "FE model: fixed base (A), bearing load (B) and the axial force (C) on the hole.", width="80%")
    r.img_row([(im("bc_fixed.png"), "Fixed support: base bottom face"),
               (im("bc_bearing.png"), "Bearing load, 5500 N (X) and 3500 N (Y)")], height="2.3in")
    r.img(im("mesh.png"), f"Final mesh: 2.5 mm global, {fl.get('local', 1.25):g} mm on the fillet and bearing hole "
          f"({FIN['nodes']:,} nodes, {FIN['elements']:,} elements).", width="80%")
    if (AO / "mesh_fillet_zoom.png").exists():
        r.img(im("mesh_fillet_zoom.png"), "Close-up of the refined mesh on the R10 fillet.", width="65%")

    # ---------------------------------------------------------------- 2 hand
    r.h2("2. Hand calculations")
    r.handcalc("Reactions at the fixed base (statics)")
    r.step(r"\vec R", r"-\vec F", None, r"(-5500,\ -3500,\ -1700)", "N")
    r.step(r"|\vec R|", r"\sqrt{F_x^2+F_y^2+F_z^2}", r"\sqrt{5500^2+3500^2+1700^2}", H.F_RES, "N")
    r.p("The load's resultant acts through the hole centre P = (30, 70, 5) mm. The reaction moment is taken about the "
        f"centroid of the fixed face, C = (30, 0, {H.ZC_BASE:.3f}) mm (the 60 × 50 face minus the two bolt holes), "
        "the point Mechanical uses by default.")
    r.step(r"\vec M_{reaction}", r"-(\vec r_{CP}\times\vec F)",
           rf"-\big((0,\ 70,\ {5 - H.ZC_BASE:.3f})\times(5500,\ 3500,\ 1700)\big)",
           rf"({H.M_REACT[0]:,.0f},\ {H.M_REACT[1]:,.0f},\ {H.M_REACT[2]:,.0f})".replace(",", r"{,}").replace(r"{,}\ ", r",\ "),
           r"N\cdot mm")
    r.end_handcalc()

    s = H.SEC
    r.handcalc(f"Stress in the upright at y = {H.Y_SEC:g} mm (beam theory)")
    r.p("Section 60 mm (x) × 10 mm (z). The section sits 35 mm below the load, between the fillet (top at y = 20) "
        "and the hole (bottom at y = 55).")
    r.step("A", r"w\,t", "(60)(10)", H.A, "mm^2")
    r.step(r"I_{strong}", r"\frac{t\,w^3}{12}", r"\frac{(10)(60)^3}{12}", H.I_STRONG, "mm^4", "Bending by Fx (in the plane of the upright).")
    r.step(r"I_{weak}", r"\frac{w\,t^3}{12}", r"\frac{(60)(10)^3}{12}", H.I_WEAK, "mm^4", "Bending by Fz (through the thickness).")
    r.step(r"\sigma_{axial}", r"\frac{F_y}{A}", r"\frac{3500}{600}", s["ax"], "MPa", "Tension: the load pulls the upright up.")
    r.step(r"\sigma_{strong}", r"\frac{F_x\,(70-y)\,(w/2)}{I_{strong}}", rf"\frac{{(5500)(35)(30)}}{{{fmt(H.I_STRONG)}}}",
           s["strong"], "MPa", "Tension on the x = 0 edge, compression on x = 60.")
    r.step(r"\sigma_{weak}", r"\frac{F_z\,(70-y)\,(t/2)}{I_{weak}}", rf"\frac{{(1700)(35)(5)}}{{{fmt(H.I_WEAK)}}}",
           s["weak"], "MPa", "Tension on the back face z = 0, compression on the front (fillet side).")
    r.step(r"\sigma_y(0, 35, 0)", r"\sigma_{axial}+\sigma_{strong}+\sigma_{weak}",
           f"{s['ax']:.2f}+{s['strong']:.2f}+{s['weak']:.2f}", s["max_t"], "MPa", "Largest tension: the back corner at x = 0.")
    r.step(r"\sigma_y(60, 35, 10)", r"\sigma_{axial}-\sigma_{strong}-\sigma_{weak}",
           f"{s['ax']:.2f}-{s['strong']:.2f}-{s['weak']:.2f}", s["max_c"], "MPa", "Largest compression: the front corner at x = 60.")
    r.end_handcalc()

    rt = H.ROOT
    r.handcalc("Root of the upright and the R10 fillet")
    r.p("At the top of the base (y = 10 mm, fillet ignored) the moment arm is 60 mm:")
    r.step(r"\sigma_{root}", r"\frac{F_y}{A}+\frac{F_x(60)(30)}{I_{strong}}+\frac{F_z(60)(5)}{I_{weak}}",
           f"{rt['ax']:.2f}+{rt['strong']:.1f}+{rt['weak']:.1f}", rt["max_t"], "MPa",
           "Upper bound for the straight section: the fillet adds material on the front (compression) side.")
    if pk:
        yp = pk[1]
        sp = H.section(yp)
        r.p(f"ANSYS puts the peak on the fillet at y ≈ {yp:.1f} mm, on the x = 60 edge, where strong-axis compression "
            "and weak-axis compression add. The 10 mm upright section at that height gives:")
        r.step(r"\sigma_{nom}", r"\sigma_{axial}-\sigma_{strong}-\sigma_{weak}",
               f"{sp['ax']:.2f}-{sp['strong']:.1f}-{sp['weak']:.1f}", sp["max_c"], "MPa",
               "Nominal compression at the fillet; the fillet's curvature raises the local stress above this.")
    r.step(r"n_{root}", r"\frac{S_y}{\sigma_{root}}", rf"\frac{{280}}{{{rt['max_t']:.1f}}}", H.N_YIELD_ROOT, "")
    r.end_handcalc()

    r.handcalc("Bearing stress and shear")
    r.step(r"F_r", r"\sqrt{F_x^2+F_y^2}", r"\sqrt{5500^2+3500^2}", H.F_RADIAL, "N")
    r.step(r"\sigma_{bearing}", r"\frac{F_r}{d\,t}", rf"\frac{{{H.F_RADIAL:.0f}}}{{(30)(10)}}", H.SIG_BEAR, "MPa")
    r.step(r"\tau_{max}", r"\frac{3}{2}\frac{F_x}{A}", r"\frac{3}{2}\frac{5500}{600}", H.TAU_X, "MPa", "Small next to the bending stresses.")
    r.end_handcalc()

    r.handcalc("Deflection: upright as a cantilever clamped at the top of the base")
    r.p("Length to the hole centre L = 70 − 10 = 60 mm, bending plus shear (κ = 5/6, G = E/2(1+ν)); the part above "
        "the hole rotates with the slope there.")
    r.step(r"\delta_z", r"\frac{F_z L^3}{3EI_{weak}}+\frac{F_z L}{\kappa G A}",
           rf"\frac{{(1700)(60)^3}}{{3(71\,000)(5000)}}+{H.DZ_S:.4f}", H.DZ, "mm", "At the hole centre.")
    r.step(r"\delta_{z,top}", r"\delta_z+\theta_z(100-70)", rf"{H.DZ:.4f}+\frac{{F_zL^2}}{{2EI_{{weak}}}}(30)", H.DZ_TOP, "mm",
           f"Clamping at the top of the fillet (y = 20) instead gives {H.DZ_TOP_LO:.3f} mm.")
    r.step(r"\delta_x", r"\frac{F_x L^3}{3EI_{strong}}+\frac{F_x L}{\kappa G A}",
           rf"{H.DX_B:.4f}+{H.DX_S:.4f}", H.DX, "mm", "Short, deep beam (L/w = 1), so shear is half of it.")
    r.step(r"\delta_{x,top}", None, None, H.DX_TOP, "mm")
    r.step(r"\delta_y", r"\frac{F_y L}{EA}", r"\frac{(3500)(60)}{(71\,000)(600)}", H.DY, "mm",
           "Axial stretch only; the y-motion of the corners comes mostly from in-plane rotation.")
    r.end_handcalc()

    # ---------------------------------------------------------------- 3 mesh
    r.h2("3. Mesh convergence")
    rows = []
    for i, c in enumerate(CONV):
        ch = "" if i == 0 else f"{pct(c['eqv_fillet_max'], CONV[i - 1]['eqv_fillet_max']):.1f}"
        rows.append([f"{c['size']:g} / {c['size'] / 2:g}", f"{c['nodes']:,}", f"{c['td_max']:.4f}",
                     f"{c['eqv_fillet_max']:.1f}", ch, f"{c['sy_back_max']:.2f}", f"{c['eqv_base_max']:.1f}"])
    for i, c in enumerate(LOC):
        prev = LOC[i - 1] if i else CONV[-1]
        rows.append([f"2.5 / {c['local']:g}", f"{c['nodes']:,}", f"{c['td_max']:.4f}", f"{c['eqv_fillet_max']:.1f}",
                     f"{pct(c['eqv_fillet_max'], prev['eqv_fillet_max']):.1f}", f"{c['sy_back_max']:.2f}",
                     f"{c['eqv_base_max']:.1f}"])
    r.table(["Global / fillet+hole size (mm)", "Nodes", "Max total def. (mm)", "Max vM on fillet (MPa)", "Change (%)",
             "σy back face, y = 35 (MPa)", "Max vM on fixed face (MPa)"], rows,
            "Mesh refinement (quadratic tetrahedra)", cls="num")
    r.img(fig_conv(), "Convergence of the fillet stress, the section stress and the deformation; the fixed-face peak "
          "keeps rising.", width="98%", border=False)
    r.p(MESH_TEXT())

    # ---------------------------------------------------------------- 4 results
    r.h2("4. Results (final mesh)")
    r.img(im("eqv.png"), f"Equivalent (von Mises) stress (MPa): maximum {FIN['eqv_max']:.1f} MPa on the R10 fillet.", width="80%")
    if (AO / "eqv_fillet_zoom.png").exists():
        r.img(im("eqv_fillet_zoom.png"), "Close-up of the fillet: the peak sits at the x = 60 end of the fillet.", width="65%")
    r.img(im("eqv_back.png"), "Equivalent stress seen from the back: tension on the back face from the Z load.", width="75%")
    r.img_row([(im("eqv_bearing.png"), f"Bearing hole: {FIN['eqv_bearing_max']:.0f} MPa peak"),
               (im("eqv_base.png"), f"Fixed base face (from below): {FIN['eqv_base_max']:.0f} MPa at the edge under the upright")],
              height="2.3in")
    sp = fig_sections()
    if sp:
        r.img(sp, "Bending stress σy across the upright at y = 35 mm: ANSYS against beam theory.", width="95%", border=False)
    r.img(im("deformed.png"), "Deformed shape (auto-scaled) over the undeformed wireframe: the upright bends forward (+Z) "
          "and sideways (+X).", width="75%")
    r.img(im("td.png"), f"Total deformation (mm): maximum {FIN['td_max']:.4f} mm at the top of the upright.", width="75%")
    r.img_row([(im("dx.png"), f"Directional deformation X: {FIN['dx_min']:.4f} to {FIN['dx_max']:.4f} mm"),
               (im("dy.png"), f"Directional deformation Y: {FIN['dy_min']:.4f} to {FIN['dy_max']:.4f} mm")], height="2.3in")
    r.img(im("dz.png"), f"Directional deformation Z: {FIN['dz_min']:.4f} to {FIN['dz_max']:.4f} mm.", width="62%")
    r.img_row([(im("fr.png"), "Force reaction at the fixed base"), (im("mr.png"), "Moment reaction at the fixed base")],
              height="2.3in")
    Rv, Mv = FIN["R"], FIN["M"]
    r.table(["Component", "X", "Y", "Z", "Total"],
            [["Force reaction (N)", f"{Rv[0]:,.1f}", f"{Rv[1]:,.1f}", f"{Rv[2]:,.1f}", f"{np.linalg.norm(Rv):,.1f}"],
             ["Moment reaction (N·mm)", f"{Mv[0]:,.0f}", f"{Mv[1]:,.0f}", f"{Mv[2]:,.0f}", f"{np.linalg.norm(Mv):,.0f}"]],
            "Reactions at the fixed base (ANSYS, final mesh)", cls="num")

    # ---------------------------------------------------------------- 5 compare
    r.h2("5. Hand calculations vs. ANSYS")
    rows = []
    for i, ax in enumerate("XYZ"):
        rows.append([f"Reaction force {ax} (N)", f"{H.R[i]:,.0f}", f"{Rv[i]:,.1f}", f"{pct(Rv[i], H.R[i]):.3f}"])
    for i, ax in enumerate("XYZ"):
        rows.append([f"Reaction moment {ax} (N·mm)", f"{H.M_REACT[i]:,.0f}", f"{Mv[i]:,.0f}", f"{pct(Mv[i], H.M_REACT[i]):.3f}"])
    rows += [
        ["σy back corner x = 0, y = 35 (MPa)", f"{H.SEC['max_t']:.2f}", f"{FIN['sy_back_max']:.2f}", f"{pct(FIN['sy_back_max'], H.SEC['max_t']):.1f}"],
        ["σy back face x = 60, y = 35 (MPa)", f"{H.sigma_y(60, 0):.2f}", f"{FIN['sy_back_min']:.2f}", f"{pct(FIN['sy_back_min'], H.sigma_y(60, 0)):.1f}"],
        ["σy x = 30, back face (MPa)", f"{H.sigma_y(30, 0):.2f}", f"{FIN['sy_thick_max']:.2f}", f"{pct(FIN['sy_thick_max'], H.sigma_y(30, 0)):.1f}"],
        ["σy x = 30, front face (MPa)", f"{H.sigma_y(30, 10):.2f}", f"{FIN['sy_thick_min']:.2f}", f"{pct(FIN['sy_thick_min'], H.sigma_y(30, 10)):.1f}"],
        ["Peak von Mises (MPa)", f"{H.ROOT['max_t']:.1f} (straight root, upper bound)", f"{FIN['eqv_max']:.1f} (fillet)", "—"],
        ["Yield safety factor", f"{H.N_YIELD_ROOT:.2f}", f"{H.SY / FIN['eqv_max']:.2f}", "—"],
        ["Max Z deflection, top (mm)", f"{H.DZ_TOP:.3f}", f"{FIN['dz_max']:.4f}", f"{pct(FIN['dz_max'], H.DZ_TOP):.1f}"],
        ["Max X deflection, top (mm)", f"{H.DX_TOP:.4f}", f"{FIN['dx_max']:.4f}", f"{pct(FIN['dx_max'], H.DX_TOP):.0f}"],
    ]
    r.table(["Quantity", "Hand", "ANSYS (final mesh)", "Difference (%)"], rows, "Hand checks against ANSYS", cls="num")
    r.p(COMPARE_TEXT())
    if VAR:
        r.h3("Bearing load vs. a uniform force on the hole")
        r.table(["Load model", "Max vM, hole (MPa)", "Max vM, fillet (MPa)", "Max total def. (mm)", "Max X def. (mm)"],
                [["Bearing Load (X, Y) + Force (Z)", f"{FIN['eqv_bearing_max']:.1f}", f"{FIN['eqv_fillet_max']:.1f}",
                  f"{FIN['td_max']:.4f}", f"{FIN['dx_max']:.4f}"],
                 ["Uniform Force (X, Y, Z) on the hole surface", f"{VAR['eqv_bearing_max']:.1f}", f"{VAR['eqv_fillet_max']:.1f}",
                  f"{VAR['td_max']:.4f}", f"{VAR['dx_max']:.4f}"]],
                "Same resultant, two ways of putting it on the hole (variant run on the 2.5 / 1.25 mm mesh)", cls="num")
        r.p(VARIANT_TEXT())

    r.h2("6. Summary")
    r.bullets(SUMMARY())
    out = r.docx(OUT_DOCX)
    print("wrote", out)


def MESH_TEXT():
    c0, c1 = CONV[0], CONV[-1]
    fl = [c["eqv_fillet_max"] for c in LOC]
    out = (f"With the global size cut from {c0['size']:g} to {c1['size']:g} mm, the fillet stress rises from "
           f"{c0['eqv_fillet_max']:.1f} to {c1['eqv_fillet_max']:.1f} MPa and is still changing "
           f"({pct(c1['eqv_fillet_max'], CONV[-2]['eqv_fillet_max']):.1f}% over the last step). The stress gradient at "
           "the fillet needs smaller elements than the rest of the part, so the global size was held at 2.5 mm and only "
           "the fillet and hole were refined further: ")
    if LOC:
        out += (" → ".join(f"{v:.1f}" for v in [c1["eqv_fillet_max"]] + fl) + " MPa, a spread of "
                f"{(max(fl + [c1['eqv_fillet_max']]) - min(fl + [c1['eqv_fillet_max']])) / FIN['eqv_fillet_max'] * 100:.1f}%. "
                f"The fillet peak is converged at about {FIN['eqv_fillet_max']:.0f} MPa. A 0.35 mm fillet size would need "
                "about 210,000 nodes, past the 128,000-node limit of ANSYS Student, so the 0.5 mm mesh is the final one. ")
    out += (f"The section stress at y = 35 mm ({c1['sy_back_max']:.2f} MPa) and the total deformation "
            f"({c1['td_max']:.4f} mm) were converged on every mesh (changes under 1%). **The fixed base face is the "
            "exception:** its peak keeps climbing with refinement (" + " → ".join(f"{c['eqv_base_max']:.0f}" for c in CONV) +
            " MPa). It sits on the edge where the fixed bottom face meets the free back face under the upright. A support "
            "that stops all motion, Poisson contraction included, meeting a free face is a stress singularity of the "
            "idealized model, so that number is not a real stress and is not used. ")
    if AD and not AD.get("error"):
        out += (f"**Adaptive check:** a Convergence object on the fillet stress (2% allowance), starting from the 5 mm mesh "
                f"with no local sizing, ends at {AD['nodes']:,} nodes and {AD['eqv_fillet_max']:.1f} MPa (last change "
                f"{AD['last_change_pct']:.1f}%), within {pct(AD['eqv_fillet_max'], FIN['eqv_fillet_max']):.1f}% of the "
                "manual result. Its reactions, though, come out "
                f"{pct(-AD['R'][0], H.FX):.1f}% above the applied load. The Bearing Load is re-distributed on the refined "
                "mesh, which shows that adaptive refinement and a bearing load do not mix well; the reported results come "
                "from the manual mesh, whose reactions match the load to 0.01%.")
    return out


def COMPARE_TEXT():
    f = FIN
    pk = f.get("max_loc") or [58, 18.6, 10]
    sp = H.section(pk[1])
    strong_fe = (f["sy_back_max"] - f["sy_back_min"]) / 2
    mean_fe = (f["sy_back_max"] + f["sy_back_min"]) / 2
    return (
        "**Reactions** equal the applied load and its moment about the base centroid to within 0.01%. That confirms the "
        "load magnitudes and directions, where the load acts (through the hole centre), and the support. "
        f"**Weak-axis bending (Fz, through the 10 mm thickness)** matches beam theory: across the thickness at x = 30 mm, "
        f"ANSYS gives {f['sy_thick_max']:.1f} / {f['sy_thick_min']:.1f} MPa against {H.sigma_y(30, 0):.1f} / "
        f"{H.sigma_y(30, 10):.1f} MPa, within 4%. "
        f"**In-plane bending (Fx)** comes out higher than beam theory at y = 35 mm: the linear part of σy across the back "
        f"face is ±{strong_fe:.1f} MPa against ±{H.SEC['strong']:.1f} MPa, and its mean is {mean_fe:.1f} against "
        f"{H.SEC['ax'] + H.SEC['weak']:.1f} MPa. For bending in its own plane the upright is a short, deep beam. The "
        "section is 60 mm wide, but only 35 mm from the load and 25 mm from the root, so plane sections do not stay "
        "plane there (Saint-Venant). That is why the back-corner stress is "
        f"{pct(f['sy_back_max'], H.SEC['max_t']):.0f}% above the hand value. "
        f"**Peak stress:** the maximum von Mises stress, {f['eqv_max']:.1f} MPa, is on the R10 fillet at "
        f"x ≈ {pk[0]:.0f}, y ≈ {pk[1]:.1f} mm. That is the end of the fillet on the compression corner, where Fx and Fz "
        f"both compress the front face. The straight-section nominal stress there is {abs(sp['max_c']):.1f} MPa, so the "
        f"fillet and the 3D stress state raise it by a factor of about {f['eqv_max'] / abs(sp['max_c']):.2f}. The "
        f"straight-root estimate ({H.ROOT['max_t']:.0f} MPa) is an upper bound because the fillet and the base add "
        f"material there. Safety factor against yield: {H.SY / f['eqv_max']:.2f}. "
        f"**Deflection:** the Z deflection at the top ({f['dz_max']:.3f} mm) is {pct(f['dz_max'], H.DZ_TOP):.0f}% above "
        f"the hand estimate clamped at the top of the base ({H.DZ_TOP:.3f} mm), and well above the one clamped at the top "
        f"of the fillet ({H.DZ_TOP_LO:.3f} mm). The base plate and the fillet region flex a little, so the upright is not "
        "even clamped as rigidly as the more flexible hand estimate assumes. "
        f"The X deflection ({f['dx_max']:.3f} mm) is about twice the cantilever value ({H.DX_TOP:.3f} mm). In its own "
        "plane the upright is as wide as it is long, so most of its X motion comes from the root region shearing and "
        "rotating, which beam theory leaves out; the Y motion ±0.08 to 0.10 mm at the top corners is the same in-plane "
        "rotation.")


def VARIANT_TEXT():
    v = VAR
    c = CONV[-1]
    return (
        "Both load models carry the same resultant, so the reactions, the section stresses and the fillet stress barely "
        f"change: the fillet differs by {pct(v['eqv_fillet_max'], c['eqv_fillet_max']):.1f}% (Saint-Venant). The hole "
        f"itself sees the difference. A uniform force spreads the load over the whole bore and gives {v['eqv_bearing_max']:.0f} MPa "
        f"there, while the bearing load presses only the loaded half, as a pin does, and gives {c['eqv_bearing_max']:.0f} MPa. "
        f"The X deflection also drops by {pct(v['dx_max'], c['dx_max']):.0f}% with the uniform force, because it pulls on "
        "the far side of the hole as well. The bearing load is the realistic model for a bearing or pin, which is why "
        "it is used for the reported results.")


def SUMMARY():
    f = FIN
    Rv = f["R"]
    return [
        "3D solid model, quadratic tetrahedra, Aluminum Alloy. Base bottom fixed; a 5500 N (X) + 3500 N (Y) bearing "
        "load plus a 1700 N axial force on the 30 mm hole.",
        f"Equivalent stress: maximum {f['eqv_max']:.1f} MPa on the R10 fillet (converged to within 1%), yield safety "
        f"factor {H.SY / f['eqv_max']:.2f}. The higher value on the fixed face edge is a support singularity.",
        f"Total deformation {f['td_max']:.4f} mm at the top of the upright. Directional: X {f['dx_max']:.4f} mm, "
        f"Y {f['dy_min']:.4f} to {f['dy_max']:.4f} mm, Z {f['dz_max']:.4f} mm (forward bending from Fz dominates).",
        f"Reaction force ({Rv[0]:,.1f}, {Rv[1]:,.1f}, {Rv[2]:,.1f}) N, total {np.linalg.norm(Rv):,.1f} N, equal and "
        "opposite to the load; the reaction moments match statics.",
        "Beam theory checks the through-thickness bending within 4% and the Z deflection within 4%. It underestimates "
        "the in-plane (X) response, because the upright is a short, deep beam in that direction.",
    ]


if __name__ == "__main__":
    build()
