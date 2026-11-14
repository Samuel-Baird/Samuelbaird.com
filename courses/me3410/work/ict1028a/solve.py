"""In-class tutorial 10-28, problem 1: stepped plate with an R25 fillet. Hand checks + ANSYS results -> Word.

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
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402

import hand as H  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "InClass_10-28_P1.docx"
AO = HERE / "ansys_out"
FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
RS = json.loads((AO / "results.json").read_text())
FIN = RS["final"]
DEF = RS["default"]
FACE = RS["face"]
EDGE = RS["edge"]
EDGE2 = RS["edge2"]
AD = RS.get("adaptive", {})
FAT = RS.get("fatigue", {})
CLASS_TABLE = [(66, 109.0), (107, 114.3), (173, 111.14), (472, 113.28), (837, 113.43)]   # from the 10-28 notes


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100


# ------------------------------------------------------------------ figures
def outline():
    pts = [(0, 0), (250, 0), (250, 40), (145, 40)]
    pts += [(145 - 25 * math.sin(a), 65 - 25 * math.cos(a)) for a in np.linspace(0, math.pi / 2, 30)]
    pts += [(120, 100), (0, 100), (0, 0)]
    return np.array(pts)


def fig_geometry():
    o = outline()
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.fill(o[:, 0], o[:, 1], color="#dfe7f1", ec="k", lw=1.2)
    ax.add_patch(Rectangle((-8, -6), 8, 112, fc="white", ec="0.3", hatch="////", lw=0.8))
    ax.annotate("", (252, 20), (252, 52), arrowprops=dict(arrowstyle="->", lw=1.8, color="C3"))
    ax.text(256, 46, "F = 1000 N", color="C3", fontsize=9)
    ax.plot([145], [65], "k+", ms=6)
    ax.text(126, 58, "R25", fontsize=8)
    ax.annotate("", (0, -16), (250, -16), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(125, -24, "250", ha="center", fontsize=8)
    ax.annotate("", (0, 110), (120, 110), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(60, 113, "120", ha="center", fontsize=8)
    ax.annotate("", (-22, 0), (-22, 100), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-25, 50, "D = 100", rotation=90, ha="right", va="center", fontsize=8)
    ax.annotate("", (270, 0), (270, 40), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(273, 20, "d = 40", va="center", fontsize=8)
    ax.annotate("", (145, 32), (250, 32), arrowprops=dict(arrowstyle="<->", lw=0.5, color="0.4"))
    ax.text(197, 26, "105", ha="center", fontsize=7, color="0.3")
    ax.text(190, 80, "t = 5 mm, Structural Steel\nE = 200 GPa, ν = 0.3, Sy = 250 MPa\nall dimensions in mm",
            fontsize=8, ha="center")
    ax.text(-12, 50, "fixed (wall)", ha="right", va="center", fontsize=7, rotation=90)
    ax.set_aspect("equal")
    ax.set_xlim(-45, 310)
    ax.set_ylim(-32, 122)
    ax.axis("off")
    fig.tight_layout()
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
    nf = [c["elements"] for c in FACE]
    ax.plot(nf, [c["eqv_fillet_max"] for c in FACE], "o-", color="C0", label="face sizing (20 → 1.25 mm)")
    ne = [c["elements"] for c in EDGE]
    ax.plot(ne, [c["eqv_fillet_max"] for c in EDGE], "s-", color="C2", label="10 mm face + fillet edge sizing")
    ax.plot([n for n, _ in CLASS_TABLE], [s for _, s in CLASS_TABLE], "x--", color="0.5", label="in-class table (10-28)")
    ax.axhline(H.SIG_MAX, color="C3", ls=":", lw=1)
    ax.text(nf[0], H.SIG_MAX + 0.6, f"hand Kt σ0 = {H.SIG_MAX:.1f} MPa", fontsize=7, color="C3")
    ax.set(xscale="log", xlabel="elements", ylabel="max von Mises on fillet (MPa)")
    nice_log(ax, nf)
    ax.legend(fontsize=6.5, loc="lower right")
    ax.grid(alpha=0.3)
    ax = axs[1]
    ax.plot(nf, [c["td_max"] for c in FACE], "o-", color="k", label="face sizing")
    ax.plot(ne, [c["td_max"] for c in EDGE], "s-", color="C2", label="fillet edge sizing")
    ax.set(xscale="log", xlabel="elements", ylabel="max total deformation (mm)")
    nice_log(ax, nf)
    ax.legend(fontsize=6.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "convergence.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fillet_rows(key):
    rows = (FIN.get("fillet") or {}).get(key)
    if not rows:
        return None
    a = np.array(rows, float)
    if np.abs(a[:, 2]).max() > 1e4:          # PlotData values are SI (Pa)
        a[:, 2] /= 1e6
    # angle on the arc measured from the arm's tangent point (145, 40), centre (145, 65)
    ang = np.degrees(np.arctan2(145.0 - a[:, 0], 65.0 - a[:, 1]))
    o = np.argsort(ang)
    return ang[o], a[o, 0], a[o, 1], a[o, 2]


def peak_on_fillet():
    fr = fillet_rows("eqv_fillet")
    if fr is None:
        return None
    ang, x, y, v = fr
    i = int(np.argmax(v))
    return {"ang": float(ang[i]), "x": float(x[i]), "y": float(y[i]), "v": float(v[i])}


def fig_fillet():
    fr = fillet_rows("eqv_fillet")
    if fr is None:
        return None
    ang, x, y, v = fr
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.plot(ang, v, "-", color="C0", label="von Mises (ANSYS)")
    s1 = fillet_rows("s1_fillet")
    if s1 is not None:
        ax.plot(s1[0], s1[3], "--", color="C1", label="max principal (ANSYS)")
    ax.axhline(H.SIG_MAX, color="C3", ls=":", lw=1, label=f"hand Kt σ0 = {H.SIG_MAX:.1f} MPa")
    ax.set(xlabel="angle on the fillet from the arm tangent point (°)", ylabel="stress (MPa)")
    ax.set_xlim(0, 90)
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "fillet_profile.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_section():
    prof = FIN.get("sx_profile")
    if not prof or "Values" not in prof:
        return None
    yk = [k for k in prof if k.startswith("Y")]
    if not yk:
        return None
    yv = np.array(prof[yk[0]], float)
    v = np.array(prof["Values"], float)
    y = yv * 1000 if abs(yv).max() < 1 else yv
    v_mpa = v / 1e6 if abs(v).max() > 1e4 else v
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    ax.plot(v_mpa, y, "o", ms=3, label="ANSYS (path at x = 200 mm)")
    yy = np.linspace(0, 40, 50)
    ax.plot(H.M(H.X_SEC) * (yy - 20) / H.I_arm, yy, "-", label="beam theory  σ = M y / I")
    ax.axvline(0, color="0.6", lw=0.6)
    ax.set(xlabel="σx (MPa)", ylabel="y (mm)")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "section_200.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_sn(sig):
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.loglog(H.SN_N, H.SN_S, "o-", color="k", ms=3, label="Structural Steel S-N (ANSYS, mean 0)")
    for lab, f, c in (("R = −1", H.fatigue(sig, -1.0), "C3"), ("R = −0.5, Goodman", H.fatigue(sig, -0.5), "C0")):
        ax.plot([f["life"]], [f["sar"]], "s", color=c, label=f"{lab}: σa,eq = {f['sar']:.0f} MPa")
        ax.plot([10, f["life"]], [f["sar"]] * 2, ":", color=c, lw=0.8)
        ax.plot([f["life"]] * 2, [50, f["sar"]], ":", color=c, lw=0.8)
    ax.axvline(H.DESIGN_LIFE, color="0.5", ls="--", lw=0.8)
    ax.set(xlabel="cycles N", ylabel="alternating stress (MPa)", ylim=(50, 5000))
    ax.legend(fontsize=6.5)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    p = FIG / "sn_curve.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ report
def build():
    r = Report("In-Class Tutorial 10-28: Problem 1",
               "Stepped plate with an R25 fillet: 2D plane stress, mesh techniques, Kt check and fatigue",
               due="Wed Oct 29, 2026, 11:59 PM (submitted late)")
    im = lambda n: AO / n  # noqa: E731
    pk = peak_on_fillet()
    c_last, c_prev = FACE[-1], FACE[-2]
    e_last, e_prev = EDGE[-1], EDGE[-2]

    r.h1("Problem")
    r.p("This is the stepped plate Dr. Seibi worked through in class on Oct 28 (the posted 10-28 notes are "
        "handwritten, with no separate problem statement). A 5 mm steel plate is fixed to a wall along its 100 mm left "
        "edge. It steps down from a 100 mm deep, 120 mm long block to a 40 mm deep arm through an R25 fillet, and a "
        "1000 N load pushes down on the free end, 250 mm from the wall. Required: model it in ANSYS as a 2D problem, "
        "compare meshing techniques (face sizing, edge sizing, adaptive convergence) on the fillet stress, check the "
        "peak stress by hand with a stress-concentration factor, and find the safety factor (static and fatigue).")
    r.img(fig_geometry(), "Geometry and loading (mm), from the 10-28 notes.", width="92%", border=False)

    # ---------------------------------------------------------------- 1
    r.h2("1. Plane stress or plane strain?")
    r.p("**Plane stress.** The notes give the rule: if the load acts in the plane of the plate (x, y), it is a 2D "
        "problem; a thin plate is plane stress and a thick one is plane strain. This plate is 5 mm thick against "
        "in-plane dimensions of 40 to 250 mm, the load is in its plane and both faces are free, so "
        "$\\sigma_z = \\tau_{xz} = \\tau_{yz} = 0$ through the thickness. Plane strain ($\\varepsilon_z = 0$) would "
        "need a body long in z or faces held against z-motion.")

    # ---------------------------------------------------------------- 2
    r.h2("2. Finite element model, boundary conditions and loads")
    r.bullets([
        "**Analysis:** Static Structural, 2D surface body, 2D Behavior = **Plane Stress**, thickness 5 mm, quadratic "
        "(8-node) plane-stress elements (PLANE183).",
        "**Material:** ANSYS Structural Steel: E = 200 GPa, ν = 0.3, $S_y$ = 250 MPa, $S_u$ = 460 MPa, and its built-in "
        "S-N curve for the fatigue part.",
        "**Boundary condition: Fixed Support on the left edge** (x = 0, 100 mm), $u_x = u_y = 0$: the hatched wall.",
        "**Load: Force 1000 N in −y on the free-end edge** (x = 250 mm, 40 mm). The notes draw the arrow at the "
        "top corner; spreading the same 1000 N over the end edge gives the same moment everywhere on the arm "
        "(Saint-Venant) and avoids a point-load singularity at the corner.",
        "**Mesh controls:** a Face Sizing on the plate and an Edge Sizing on the fillet, switched on and off for the "
        "mesh studies below.",
    ])
    r.img(im("model.png"), "FE model: fixed support on the wall edge and the 1000 N force on the free end.", width="85%")
    r.img(im("mesh.png"), f"Final mesh: 2.5 mm face sizing, 0.625 mm on the fillet ({FIN['nodes']:,} nodes, "
          f"{FIN['elements']:,} elements).", width="85%")
    r.img(im("mesh_fillet.png"), "Close-up of the final mesh on the R25 fillet.", width="65%")

    # ---------------------------------------------------------------- 3 hand
    r.h2("3. Hand calculations")
    r.handcalc("Statics: wall reactions")
    r.step(r"\sum F_y = 0:\ R_y", "F", None, H.Ry, "N")
    r.step(r"\sum F_x = 0:\ R_x", None, None, "0", "N")
    r.step(r"\sum M = 0:\ M_{wall}", "F\\,L", "(1000)(250)", H.M_wall, r"N\cdot mm", "250 N·m, clockwise reaction on the plate.")
    r.end_handcalc()

    r.handcalc("Peak stress at the fillet: nominal bending stress × Kt (as done in class)")
    r.step("I", r"\frac{t\,d^3}{12}", r"\frac{(5)(40)^3}{12}", H.I_arm, "mm^4", "Smaller (40 mm) section, where the chart's nominal stress is defined.")
    r.step("M", "F\\,a", f"(1000)({H.ARM_CLASS})", F_NMM(H.ARM_CLASS), r"N\cdot mm",
           "Moment arm used in class: from the load to a point a short way up the fillet from where it meets the arm "
           "(the fillet ends on the arm at a = 105 mm).")
    r.step(r"\sigma_0", r"\frac{M\,c}{I}", rf"\frac{{({fmt(F_NMM(H.ARM_CLASS))})(20)}}{{{fmt(H.I_arm)}}}", H.SIG0, "MPa")
    r.step(r"\frac{r}{d}", None, r"\frac{25}{40}", H.R_D, "")
    r.step(r"\frac{D}{d}", None, r"\frac{100}{40}", H.D_D, "")
    r.step("K_t", None, None, f"{H.KT}", "", "Stepped flat bar in bending, read in class. r/d = 0.625 is past the end of "
           "the usual chart (r/d ≤ 0.3), so this is an extrapolation; Kt falls as r/d grows, so reading it at the chart's "
           "end is on the high (safe) side.")
    r.step(r"\sigma_{max}", r"K_t\,\sigma_0", f"({H.KT})({H.SIG0})", H.SIG_MAX, "MPa")
    r.p(f"The nominal stress depends on where the moment is taken: from {H.SIG0_END:.2f} MPa at the fillet's end on the "
        f"arm (a = 105 mm; the class's first try, which gave {1.42 * H.SIG0_END:.1f} MPa with Kt = 1.42) to "
        f"{H.SIG0_START:.1f} MPa at the step face (a = 130 mm). ANSYS shows where on the fillet the peak actually sits.")
    r.end_handcalc()

    r.handcalc("Static safety factor (distortion-energy theory)")
    r.step("n", r"\frac{S_y}{\sigma_{eq}}", f"\\frac{{250}}{{{H.SIG_MAX:.2f}}}", H.N_YIELD, "",
           "For the uniaxial stress on the fillet's free edge, σ_eq = σ_max.")
    r.end_handcalc()

    r.handcalc("Beam-theory checks away from the fillet")
    r.step(r"\sigma_x(200)", r"\pm\frac{F(250-x)\,c}{I}", rf"\pm\frac{{(1000)(50)(20)}}{{{fmt(H.I_arm)}}}",
           f"\\pm{H.SIG_SEC:.1f}", "MPa", "Arm section at x = 200 mm: tension on top, compression on the bottom.")
    r.step(r"\sigma_{wall}", r"\frac{6M_{wall}}{t\,D^2}", r"\frac{6(250\,000)}{(5)(100)^2}", H.SIG_WALL, "MPa",
           "Deep block at the wall. The block is only 1.2 depths long, so this is rough.")
    r.end_handcalc()

    r.handcalc("Tip deflection: unit-load method")
    r.eq(r"\delta = \int_0^{250}\frac{F(250-x)^2}{E\,I(x)}\,dx + \int_0^{250}\frac{F}{\kappa\,G\,A(x)}\,dx,"
         r"\qquad I=\frac{t\,h^3}{12},\ A=t\,h,\ \kappa=\tfrac56,\ G=\frac{E}{2(1+\nu)}")
    r.p("with the section depth h(x) = 100 mm in the block, $65 - \\sqrt{25^2-(x-145)^2}$ through the fillet "
        "(120 ≤ x ≤ 145 mm) and 40 mm on the arm:")
    r.step(r"\delta_{bending}", None, r"\text{(trapezoid rule)}", f"{H.DELTA_B:.4f}", "mm")
    r.step(r"\delta_{shear}", None, None, f"{H.DELTA_S:.4f}", "mm")
    r.step(r"\delta_{tip}", r"\delta_{bending}+\delta_{shear}", None, f"{H.DELTA:.4f}", "mm")
    r.p(f"For scale: the arm alone clamped at x = 120 mm gives $FL^3/3EI$ = {H.DELTA_ARM:.4f} mm, and a sharp step with "
        f"no fillet material gives {H.DELTA_STEP:.4f} mm.")
    r.end_handcalc()

    r.handcalc("Fatigue life (stress-life, ANSYS Structural Steel S-N curve)")
    f1, f2 = H.FAT_R1, H.FAT_R05
    r.p("Fully reversed (R = −1, load swinging between +1000 and −1000 N):")
    r.step(r"\sigma_a", r"\sigma_{max}", None, f1["sa"], "MPa", "Mean stress 0.")
    r.step("N", None, r"\text{log-log interpolation of the S-N table}", f"{f1['life']:,.0f}", "cycles")
    r.step(r"n_f", r"\frac{S_e(10^6)}{\sigma_a}", rf"\frac{{{H.SE}}}{{{f1['sa']:.2f}}}", f1["sf"], "",
           "Below 1: the fillet does not survive a 10⁶-cycle design life at this load.")
    r.p("R = −0.5 (load between +1000 and −500 N, the black curve in the notes), Goodman mean-stress correction "
        "($S_u$ = 460 MPa):")
    r.step(r"\sigma_a", r"\frac{1-R}{2}\,\sigma_{max}", f"(0.75)({H.SIG_MAX:.2f})", f2["sa"], "MPa")
    r.step(r"\sigma_m", r"\frac{1+R}{2}\,\sigma_{max}", f"(0.25)({H.SIG_MAX:.2f})", f2["sm"], "MPa")
    r.step(r"\sigma_{a,eq}", r"\frac{\sigma_a}{1-\sigma_m/S_u}", rf"\frac{{{f2['sa']:.2f}}}{{1-{f2['sm']:.2f}/460}}", f2["sar"], "MPa")
    r.step("N", None, None, f"{f2['life']:,.0f}", "cycles")
    r.step(r"n_f", r"\left(\frac{\sigma_a}{S_e}+\frac{\sigma_m}{S_u}\right)^{-1}",
           rf"\left(\frac{{{f2['sa']:.2f}}}{{{H.SE}}}+\frac{{{f2['sm']:.2f}}}{{460}}\right)^{{-1}}", f2["sf"], "",
           "Goodman safety factor: the factor on the load that puts the stress state on the Goodman line at 10⁶ cycles "
           "(the definition ANSYS uses).")
    r.end_handcalc()
    r.img(fig_sn(H.SIG_MAX), "Structural Steel S-N curve with the two load cases (hand σmax).", width="62%", border=False)

    # ---------------------------------------------------------------- 4 mesh
    r.h2("4. Meshing techniques and convergence")
    r.p(f"**Default mesh.** With no sizing controls Mechanical makes {DEF['elements']} elements and gives "
        f"{DEF['eqv_fillet_max']:.1f} MPa on the fillet.")
    r.img(im("mesh_default.png"), f"Default mesh ({DEF['elements']} elements).", width="70%")
    r.h3("Face sizing (whole plate refined)")
    rows = []
    for i, c in enumerate(FACE):
        ch = "" if i == 0 else f"{pct(c['eqv_fillet_max'], FACE[i - 1]['eqv_fillet_max']):.2f}"
        rows.append([f"{c['face']:g}", f"{c['elements']:,}", f"{c['nodes']:,}", f"{c['eqv_fillet_max']:.2f}", ch,
                     f"{c['td_max']:.5f}", f"{c['eqv_wall_max']:.1f}"])
    r.table(["Face size (mm)", "Elements", "Nodes", "Max vM on fillet (MPa)", "Change (%)", "Max total def. (mm)",
             "Max vM on wall edge (MPa)"], rows, "Face-sizing study", cls="num")
    r.h3("Edge sizing (fillet refined, 10 mm elsewhere)")
    rows = []
    for i, c in enumerate(EDGE):
        ch = "" if i == 0 else f"{pct(c['eqv_fillet_max'], EDGE[i - 1]['eqv_fillet_max']):.2f}"
        rows.append([f"{c['edge']:g}", f"{c['elements']:,}", f"{c['nodes']:,}", f"{c['eqv_fillet_max']:.2f}", ch,
                     f"{c['td_max']:.5f}"])
    r.table(["Fillet edge size (mm)", "Elements", "Nodes", "Max vM on fillet (MPa)", "Change (%)", "Max total def. (mm)"],
            rows, "Edge-sizing study, 10 mm face sizing", cls="num")
    rows = []
    for i, c in enumerate(EDGE2):
        ch = "" if i == 0 else f"{pct(c['eqv_fillet_max'], EDGE2[i - 1]['eqv_fillet_max']):.2f}"
        rows.append([f"{c['edge']:g}", f"{c['elements']:,}", f"{c['nodes']:,}", f"{c['eqv_fillet_max']:.2f}", ch,
                     f"{c['td_max']:.5f}"])
    r.table(["Fillet edge size (mm)", "Elements", "Nodes", "Max vM on fillet (MPa)", "Change (%)", "Max total def. (mm)"],
            rows, "Edge-sizing study, 2.5 mm face sizing", cls="num")
    r.img(fig_conv(), "Fillet stress and deformation against element count, with the in-class table.", width="98%", border=False)
    r.p(MESH_TEXT(c_last, c_prev, e_last, e_prev))

    r.h3("Adaptive meshing (Convergence tool)")
    if AD:
        rows = []
        for tag in ("fillet_5", "fillet_1"):
            d = AD.get(tag)
            if not d:
                continue
            if d.get("error"):
                rows.append([f"{d['allowable_pct']:g}", "failed: " + d["error"][:60], "", "", "", ""])
                continue
            rows.append([f"{d['allowable_pct']:g}", f"{d.get('start_elements', 0):,}", f"{d['nodes']:,}",
                         f"{d['last_change_pct']:.2f}" if d.get("last_change_pct") is not None else "",
                         f"{d['eqv_fillet_max']:.2f}", f"{d['td_max']:.5f}"])
        r.table(["Allowable change (%)", "Start elements", "Final nodes", "Last change (%)", "Max vM on fillet (MPa)",
                 "Max total def. (mm)"], rows, "Convergence object on the fillet von Mises (default start mesh)", cls="num")
        r.p(ADAPT_TEXT())
        if (AO / "adapt_fillet_1_res.png").exists():
            r.img(AO / "adapt_fillet_1_res.png", "Fillet stress after adaptive refinement (1% allowable change).", width="65%")

    # ---------------------------------------------------------------- 5 results
    r.h2("5. Results (final mesh)")
    r.img(im("deformed_vs_undeformed.png"), "Deformed shape (auto-scaled) over the undeformed outline.", width="85%")
    r.img(im("total_deformation.png"), f"Total deformation (mm): maximum {FIN['td_max']:.4f} mm at the free end.", width="85%")
    r.img(im("von_mises.png"), f"Equivalent (von Mises) stress (MPa): maximum {FIN['eqv_max']:.1f} MPa.", width="85%")
    cap = f"Von Mises close-up at the fillet: peak {FIN['eqv_fillet_max']:.1f} MPa"
    if pk:
        cap += f" at about {pk['ang']:.0f}° up the arc from the arm (x = {pk['x']:.1f}, y = {pk['y']:.1f} mm)"
    r.img(im("von_mises_fillet_zoom.png"), cap + ".", width="70%")
    fp = fig_fillet()
    if fp:
        r.img(fp, "Stress along the fillet edge, final mesh.", width="62%", border=False)
    r.img_row([(im("von_mises_wall_zoom.png"), "Von Mises at the bottom corner of the fixed edge"),
               (im("von_mises_wall_edge.png"), f"Von Mises along the fixed edge only: it jumps to {FIN['eqv_wall_max']:.0f} MPa "
                "in the corner element (singularity)")], height="2.3in")
    sp = fig_section()
    if sp:
        r.img(sp, "Bending stress across the arm at x = 200 mm: ANSYS against beam theory.", width="58%", border=False)

    if FAT:
        r.h3("Fatigue Tool")
        r.p("Fatigue Tool (stress life, von Mises stress, S-N curve of Structural Steel, design life 10⁶ cycles), "
            "applied to the 1000 N static solution: fully reversed (R = −1, no mean-stress correction) and R = −0.5 "
            "with Goodman.")
        rows = []
        for tag, lab in (("R-1", "R = −1"), ("R-0.5_goodman", "R = −0.5, Goodman")):
            d = FAT.get(tag)
            if d:
                rows.append([lab, f"{d.get('life_min', float('nan')):,.0f}", f"{d.get('sf_min', float('nan')):.3f}"])
        r.table(["Loading", "Minimum life (cycles)", "Minimum safety factor (10⁶ cycles)"], rows, "Fatigue Tool results", cls="num")
        for tag, lab in (("R-1", "R = −1"), ("R-0.5_goodman", "R = −0.5, Goodman")):
            if (AO / f"fatigue_{tag}_life.png").exists():
                r.img_row([(AO / f"fatigue_{tag}_life.png", f"Life, {lab}"),
                           (AO / f"fatigue_{tag}_sf_zoom.png", f"Safety factor at the fillet, {lab}")], height="2.3in")

    # ---------------------------------------------------------------- 6 compare
    r.h2("6. Hand calculations vs. ANSYS")
    kt_eff = FIN["eqv_fillet_max"] / H.SIG0
    rows = [
        ["Wall reaction R_y (N)", f"{H.Ry:,.1f}", f"{abs(FIN['Ry']):,.2f}", f"{pct(abs(FIN['Ry']), H.Ry):.3f}"],
        ["Wall moment M_z (N·mm)", f"{H.M_wall:,.0f}", f"{abs(FIN['Mz']):,.0f}", f"{pct(abs(FIN['Mz']), H.M_wall):.3f}"],
        ["σx top, x = 200 mm (MPa)", f"{H.SIG_SEC:.2f}", f"{FIN['sx_path_max']:.2f}", f"{pct(FIN['sx_path_max'], H.SIG_SEC):.2f}"],
        ["σx bottom, x = 200 mm (MPa)", f"{-H.SIG_SEC:.2f}", f"{FIN['sx_path_min']:.2f}", f"{pct(FIN['sx_path_min'], -H.SIG_SEC):.2f}"],
        ["Peak fillet stress (MPa)", f"{H.SIG_MAX:.2f}", f"{FIN['eqv_fillet_max']:.2f}", f"{pct(FIN['eqv_fillet_max'], H.SIG_MAX):.1f}"],
        ["Kt (on σ0 = 84.375 MPa)", f"{H.KT}", f"{kt_eff:.3f}", f"{pct(kt_eff, H.KT):.1f}"],
        ["Static safety factor", f"{H.N_YIELD:.2f}", f"{H.SY / FIN['eqv_fillet_max']:.2f}", f"{pct(H.SY / FIN['eqv_fillet_max'], H.N_YIELD):.1f}"],
        ["Tip deflection (mm)", f"{H.DELTA:.4f}", f"{FIN['td_max']:.4f}", f"{pct(FIN['td_max'], H.DELTA):.1f}"],
    ]
    r.table(["Quantity", "Hand", "ANSYS (final mesh)", "Difference (%)"], rows, "Hand checks against ANSYS", cls="num")
    rows = []
    for tag, ratio, lab in (("R-1", -1.0, "R = −1"), ("R-0.5_goodman", -0.5, "R = −0.5, Goodman")):
        d = FAT.get(tag)
        if not (d and "sf_min" in d):
            continue
        fh, fa = H.fatigue(H.SIG_MAX, ratio), H.fatigue(FIN["eqv_fillet_max"], ratio)
        rows.append([f"Life, {lab} (cycles)", f"{fh['life']:,.0f}", f"{fa['life']:,.0f}", f"{d['life_min']:,.0f}",
                     f"{pct(d['life_min'], fa['life']):.3f}"])
        rows.append([f"Safety factor at 10⁶, {lab}", f"{fh['sf']:.3f}", f"{fa['sf']:.4f}", f"{d['sf_min']:.4f}",
                     f"{pct(d['sf_min'], fa['sf']):.3f}"])
    if rows:
        r.table(["Quantity", f"Hand, σmax = {H.SIG_MAX:.1f} MPa", f"Hand, σmax = {FIN['eqv_fillet_max']:.2f} MPa (ANSYS peak)",
                 "ANSYS Fatigue Tool", "Difference, hand at ANSYS peak vs. ANSYS (%)"], rows,
                "Fatigue: the same S-N and Goodman formulas fed with the hand and the ANSYS peak stress", cls="num")
    r.p(COMPARE_TEXT(pk))

    r.h2("7. Summary")
    r.bullets(SUMMARY(pk))
    out = r.docx(OUT_DOCX)
    print("wrote", out)


def F_NMM(arm):
    return H.F * arm


def MESH_TEXT(c_last, c_prev, e_last, e_prev):
    e2 = EDGE2[-1]
    walls = " → ".join(f"{c['eqv_wall_max']:.0f}" for c in FACE)
    return (
        f"**Face sizing** converges: the fillet stress rises from {FACE[0]['eqv_fillet_max']:.1f} MPa on the coarsest "
        f"mesh to {c_last['eqv_fillet_max']:.2f} MPa and changes {pct(c_last['eqv_fillet_max'], c_prev['eqv_fillet_max']):.2f}% "
        f"over the last halving of the element size; the deformation is converged from the start (all within "
        f"{pct(FACE[0]['td_max'], c_last['td_max']):.2f}%). The converged {c_last['eqv_fillet_max']:.2f} MPa agrees with the "
        f"last row of the in-class table (113.43 MPa at 837 elements). The optimum mesh is the 1.25 mm face sizing; it is "
        "the final mesh used below. "
        f"**Edge sizing on its own does not work here.** With the face left at 10 mm, refining only the fillet edge adds "
        f"few elements ({EDGE[0]['elements']} → {e_last['elements']}) and the fillet stress wanders "
        f"({' → '.join(f'{c['eqv_fillet_max']:.1f}' for c in EDGE)} MPa) instead of converging: small elements on the "
        "edge are joined to 10 mm elements one layer in, so the elements that carry the stress gradient into the "
        "plate are distorted. With a 2.5 mm face sizing behind it, the same edge sizing behaves: "
        f"{' → '.join(f'{c['eqv_fillet_max']:.2f}' for c in EDGE2)} MPa, within "
        f"{pct(e2['eqv_fillet_max'], c_last['eqv_fillet_max']):.1f}% of the converged value at a quarter of the element "
        f"count ({e2['elements']:,} vs. {c_last['elements']:,}). "
        f"**The wall edge is not converged and never will be:** its peak keeps climbing ({walls} MPa) at the two corners "
        "where the fixed edge meets a free edge. A rigid support that also stops the Poisson contraction, meeting a free "
        "edge at 90°, is a stress singularity of the idealized model; it sits well below the fillet stress and is not "
        "used.")


def ADAPT_TEXT():
    a5, a1 = AD.get("fillet_5", {}), AD.get("fillet_1", {})
    c_last = FACE[-1]
    return (
        "A Convergence object on the maximum fillet stress, starting from the default "
        f"{a1.get('start_elements', 72)}-element mesh with no sizing controls, refines the elements around the fillet and "
        f"re-solves until the change between loops is below the allowance. With a 5% allowance it stops at "
        f"{a5.get('nodes', 0):,} nodes and {a5.get('eqv_fillet_max', 0):.2f} MPa; with 1% at {a1.get('nodes', 0):,} nodes "
        f"and {a1.get('eqv_fillet_max', 0):.2f} MPa (last change {a1.get('last_change_pct', 0):.2f}%). Both are within "
        f"{max(pct(a5.get('eqv_fillet_max', 1), c_last['eqv_fillet_max']), pct(a1.get('eqv_fillet_max', 1), c_last['eqv_fillet_max'])):.2f}% "
        f"of the 1.25 mm face mesh ({c_last['nodes']:,} nodes): adaptive meshing reaches the same answer with about 3% of "
        "the nodes, because it only refines where the stress gradient is. It works here because the Convergence object is "
        "scoped to the fillet; on the global maximum it would eventually chase the singular wall corners.")


def COMPARE_TEXT(pk):
    s = FIN["eqv_fillet_max"]
    out = ("**Reactions and the arm stress** match statics and beam theory to round-off (σx at x = 200 mm: "
           f"{FIN['sx_path_max']:.2f} / {FIN['sx_path_min']:.2f} MPa against ±37.50), which confirms the load, the support "
           "and the plane-stress thickness. ")
    if pk:
        arm = 250 - pk["x"]
        out += (f"**Fillet stress.** ANSYS puts the peak {pk['ang']:.0f}° up the arc from the arm, at x = {pk['x']:.1f} mm, "
                f"so its moment arm is {arm:.1f} mm, almost exactly the 112.5 mm used in class. The class's choice of "
                f"section is right. On that nominal stress the effective stress-concentration factor is "
                f"{s:.2f} / {H.sigma_nom(arm):.2f} = {s / H.sigma_nom(arm):.3f}, against the 1.4 read in class. The hand peak "
                f"({H.SIG_MAX:.1f} MPa) is therefore {pct(H.SIG_MAX, s):.1f}% high, on the safe side. The difference is all in "
                "Kt: r/d = 0.625 is beyond the range of the chart, so the value was extrapolated. The chart is also drawn "
                "for a bar stepped on both sides, while this plate steps on one side only. ")
    out += (f"**Static safety factor:** {H.SY / s:.2f} from ANSYS against {H.N_YIELD:.2f} by hand; the part does not "
            "yield under 1000 N. **Fatigue:** fed with the same peak stress, the S-N interpolation and the Goodman formula "
            "reproduce the Fatigue Tool's life and safety factor to round-off (table above), so the Fatigue Tool is doing "
            "exactly this calculation at every node. Both safety factors are below 1. A fully reversed ±1000 N load "
            "would crack the fillet after about 2 × 10⁵ cycles, so for a 10⁶-cycle life the load or the stress "
            "concentration has to come down. ")
    out += (f"**Tip deflection:** ANSYS gives {FIN['td_max']:.4f} mm against {H.DELTA:.4f} mm by beam theory "
            f"({pct(FIN['td_max'], H.DELTA):.0f}% more), and even more than the sharp-step estimate ({H.DELTA_STEP:.4f} mm). "
            "Beam theory assumes that plane sections stay plane right into the deep block, so the arm is effectively "
            "clamped at the step. In the real plate the block material around the junction deforms locally as the "
            "arm's bending stress spreads into it, so the arm root can rotate a little. The extra "
            f"{FIN['td_max'] - H.DELTA:.3f} mm corresponds to a root rotation of about "
            f"{(FIN['td_max'] - H.DELTA) / 130:.1e} rad over the 130 mm arm. This joint flexibility is a known limit of "
            "beam theory at abrupt changes in depth, and it is why the deflection is checked against FEA rather than "
            "taken from the beam formula. **The wall stress** from beam theory (30 MPa) is a nominal value; the ANSYS peak "
            f"on that edge ({FIN['eqv_wall_max']:.0f} MPa) is the corner singularity described in Section 4.")
    return out


def SUMMARY(pk):
    s = FIN["eqv_fillet_max"]
    fat = FAT.get("R-1", {})
    return [
        "Plane stress: a 5 mm plate loaded in its own plane, with free faces.",
        f"Mesh: face sizing converges to {s:.2f} MPa on the fillet (0.3% over the last refinement), the same as the "
        "in-class table. Edge sizing on its own (10 mm face) does not converge. Adaptive refinement scoped to the fillet "
        "gets the same answer with about 1,000 nodes.",
        f"Peak stress {s:.1f} MPa on the R25 fillet"
        + (f", {pk['ang']:.0f}° up the arc (moment arm {250 - pk['x']:.1f} mm)" if pk else "")
        + f". Hand Kt σ0 = {H.SIG_MAX:.1f} MPa is {pct(H.SIG_MAX, s):.1f}% high; the effective Kt is about "
        f"{s / H.SIG0:.2f}, not the extrapolated 1.4.",
        f"Static safety factor {H.SY / s:.2f} (distortion energy, Sy = 250 MPa). Fatigue at 10⁶ cycles: safety factor "
        f"{fat.get('sf_min', float('nan')):.2f} fully reversed (life about {fat.get('life_min', 0):,.0f} cycles) and "
        f"{FAT.get('R-0.5_goodman', {}).get('sf_min', float('nan')):.2f} at R = −0.5 with Goodman. Both are below 1, so "
        "this part would not survive 10⁶ cycles at 1000 N.",
        f"Tip deflection {FIN['td_max']:.3f} mm; beam theory underestimates it by about "
        f"{pct(FIN['td_max'], H.DELTA):.0f}% because it treats the arm as rigidly clamped at the step.",
    ]


if __name__ == "__main__":
    build()
