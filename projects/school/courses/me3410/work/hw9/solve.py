"""HW 9: 3D modeling. Hand checks + ANSYS results -> Word.

    python solve.py     (reads ansys_out/q1_results.json and q2_results.json written by the Mechanical scripts)
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle, Wedge  # noqa: E402

import hand as H  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "HW9_3D_Modeling.docx"
AO = HERE / "ansys_out"
FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
Q1 = json.loads((AO / "q1_results.json").read_text())
Q2 = json.loads((AO / "q2_results.json").read_text())
AX = Q1["axisym"]
S3 = Q1["solid3d"]
AXC = AX["convergence"]
S3C = [c for c in S3["convergence"] if not c.get("skipped")]
AXF, S3F = AX["final"], S3["final"]
FULL, HALF = Q2["full"], Q2["half"]
FC = [c for c in FULL["convergence"] if not c.get("skipped")]
HC = [c for c in HALF["convergence"] if not c.get("skipped")]
FF, HF = FULL["final"], HALF["final"]
NEAR = min(AXC, key=lambda c: abs(c["size"] - S3F["size"]))     # 2D mesh closest in size to the 3D final mesh


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100


def sci(x, d=3):
    """1.234e-7 -> '1.234×10⁻⁷' for table cells."""
    m, e = f"{x:.{d}e}".split("e")
    sup = str(int(e)).replace("-", "⁻").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{m}×10{sup}"


def kpa(mpa):
    return mpa * 1000.0


# ------------------------------------------------------------------ figures
def fig_q1_geometry():
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    pts = [(-r, z) for r, z in H.PTS]
    for sgn in (1, -1):
        p = [(sgn * r, z) for r, z in H.PTS]
        ax.add_patch(Polygon(p, closed=True, fc="#dfe7f1", ec="k", lw=1.1))
    ax.plot([0, 0], [-31, 31], "k-.", lw=0.7)
    ax.plot([-52, 52], [0, 0], color="0.5", ls="-.", lw=0.5)

    def dim(x0, y0, x1, y1, txt, off=(0, 0), rot=0):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], txt, ha="center", va="center", fontsize=7.5, rotation=rot,
                bbox=dict(fc="white", ec="none", pad=0.6))
    dim(0, -35, 46, -35, "46 (outer radius)")
    dim(0, -31.5, 30, -31.5, "30", off=(0, 0))
    dim(48, -25, 48, 25, "50", rot=90)
    dim(-48, -6, -48, 6, "12", rot=90)
    dim(-37, -15, -37, 15, "30", rot=90)
    dim(5, 18, 13, 18, "8", off=(0, 2))
    dim(0, 20, 5, 20, "5", off=(0, 2))
    dim(30, 27.5, 46, 27.5, "16", off=(0, 2.2))
    ax.annotate("", (0, 33), (0, 29), arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.text(1.5, 33, "z, ω = 100 rpm", fontsize=8)
    ax.text(-26, 11, "hub", fontsize=7.5, color="0.35")
    ax.text(16, 3.2, "web", fontsize=7.5, color="0.35")
    ax.text(38, 12, "rim", fontsize=7.5, color="0.35", rotation=90)
    ax.set_aspect("equal")
    ax.set_xlim(-55, 56)
    ax.set_ylim(-39, 38)
    ax.axis("off")
    ax.set_title("Rotating part, section through the axis (mm); steel E = 200 GPa, ν = 0.3, ρ = 7850 kg/m³", fontsize=8)
    fig.tight_layout()
    p = FIG / "q1_geometry.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q2_geometry():
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.6), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axs[0]
    t = np.linspace(0, math.pi, 40)
    prof = [(-60, 0), (60, 0), (30, 80)] + [(30 * math.cos(a), 80 + 30 * math.sin(a)) for a in t] + [(-30, 80)]
    ax.add_patch(Rectangle((-60, -30), 120, 30, fc="#c9d6e6", ec="k", lw=1))
    ax.add_patch(Polygon(prof, closed=True, fc="#dfe7f1", ec="k", lw=1))
    ax.add_patch(Circle((0, 80), 15, fc="white", ec="k", lw=1))
    ax.annotate("", (0, 105), (0, 95), arrowprops=dict(arrowstyle="->", color="C3", lw=1.4))
    ax.text(3, 108, "20 kN (+Y)", color="C3", fontsize=8)
    ax.add_patch(Rectangle((-66, -36), 132, 6, fc="white", ec="0.3", hatch="////", lw=0.6))
    ax.text(0, -46, "bottom face fixed", ha="center", fontsize=7.5)
    for x0, y0, x1, y1, tx, off in ((-60, 5, 60, 5, "120", (0, 5)),):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(0, 8, tx, ha="center", fontsize=7.5)
    ax.annotate("", (72, 0), (72, 80), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(74, 40, "80", fontsize=7.5)
    ax.annotate("", (-72, -30), (-72, 0), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(-74, -15, "30", fontsize=7.5, ha="right")
    ax.text(0, 60, "R30 / Ø30 hole\n(30 thick)", ha="center", fontsize=7)
    ax.set_aspect("equal")
    ax.set_xlim(-85, 90)
    ax.set_ylim(-52, 120)
    ax.axis("off")
    ax.set_title("Front view (X–Y), mm", fontsize=8.5)
    ax = axs[1]
    ax.add_patch(Rectangle((-60, -100), 120, 200, fc="#dfe7f1", ec="k", lw=1, joinstyle="round"))
    ax.add_patch(Rectangle((-60, -15), 120, 30, fc="#b9c8dc", ec="k", lw=0.8))
    for sx in (-30, 30):
        for sz in (-60, 60):
            ax.add_patch(Circle((sx, sz), 10, fc="white", ec="k", lw=1))
    ax.annotate("", (-60, 112), (60, 112), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(0, 116, "120", ha="center", fontsize=7.5)
    ax.annotate("", (-70, -100), (-70, 100), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(-72, 0, "200", fontsize=7.5, ha="right", va="center", rotation=90)
    ax.annotate("", (-30, 68), (30, 68), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(0, 71, "60 (x)", ha="center", fontsize=7)
    ax.annotate("", (36, -60), (36, 60), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(38, 0, "120 (z)", fontsize=7, rotation=90, va="center")
    ax.text(0, 0, "upright 30 thick", ha="center", va="center", fontsize=7)
    ax.text(0, -88, "R17.5 corners, 4 × Ø20 holes", ha="center", fontsize=7)
    ax.set_aspect("equal")
    ax.set_xlim(-85, 75)
    ax.set_ylim(-108, 122)
    ax.axis("off")
    ax.set_title("Top view (X–Z), mm", fontsize=8.5)
    fig.tight_layout()
    p = FIG / "q2_geometry.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q1_conv():
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.5))
    na = [c["nodes"] for c in AXC]
    n3 = [c["nodes"] for c in S3C]
    for ax, key, ttl, sc in ((axs[0], "td_max_mm", "Max total deformation (10⁻⁷ mm)", 1e7),
                             (axs[1], "eqv_max_MPa", "Max von Mises (kPa)", 1e3),
                             (axs[2], "eqv_bore_max_MPa", "Von Mises on the bore (kPa)", 1e3)):
        ax.semilogx(na, [c[key] * sc for c in AXC], "o-", label="2D axisymmetric")
        ax.semilogx(n3, [c[key] * sc for c in S3C], "s-", label="3D wedge")
        ax.set_title(ttl, fontsize=8)
        ax.set_xlabel("nodes", fontsize=7.5)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
    axs[0].legend(fontsize=6.5)
    fig.tight_layout()
    p = FIG / "q1_conv.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_q2_conv():
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.5))
    for ax, key, ttl in ((axs[0], "td_max", "Max total deformation (mm)"), (axs[1], "eqv_max", "Max von Mises (MPa)"),
                         (axs[2], "sxy_max", "Max shear stress XY (MPa)")):
        ax.semilogx([c["nodes"] for c in FC], [c[key] for c in FC], "o-", label="full")
        ax.semilogx([c["nodes"] for c in HC], [c[key] for c in HC], "s--", label="half")
        ax.set_title(ttl, fontsize=8)
        ax.set_xlabel("nodes", fontsize=7.5)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
    axs[0].legend(fontsize=6.5)
    fig.tight_layout()
    p = FIG / "q2_conv.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ report
def build():
    r = Report("HW 9: 3D Modeling", "Q1 rotating part: axisymmetric vs. 3D · Q2 lifting bracket: half and full model",
               due="Wed Dec 2, 2026, 11:59 PM")
    im = lambda n: AO / n  # noqa: E731
    r.h2("Summary")
    r.bullets(SUMMARY())

    # ================================================================ Q1
    r.h1("Q1. Rotating part: axisymmetric vs. 3D")
    r.p("The steel part (E = 200 GPa, ν = 0.3, ρ = 7850 kg/m³) turns at 100 rpm about its z-axis. Gravity is ignored. "
        "The section in the handout is drawn as a solid of revolution: a bored hub, a thin web and a heavy rim.")
    r.img(fig_q1_geometry(), "Geometry read from the handout figure (all dimensions in mm).", width="85%", border=False)
    r.p("The handout drawing is not to scale, so the dimensions were taken from its labels: bore radius 5 mm, hub wall "
        "8 mm (r = 5 to 13), hub height 30 mm, web 12 mm thick out to r = 30 mm, rim 16 mm wide (r = 30 to 46) and 50 mm "
        "tall. The part is symmetric about its mid-plane.")
    r.h2("1. Finite element models, boundary conditions and loads")
    r.bullets([
        "**Analysis:** Static Structural, quadratic elements, Structural Steel (E = 200 GPa, ν = 0.3, ρ = 7850 kg/m³).",
        f"**Load:** Rotational Velocity {H.RPM:g} rpm = {H.OMEGA:.4f} rad/s about the axis of the part. Mechanical turns it into "
        "the centrifugal body force ρω²r.",
        "**Axisymmetric model:** one half-section (r ≥ 5 mm) drawn in the XY plane with the axis of revolution along Y, "
        "which is where Mechanical's 2D axisymmetric behavior puts it. Its z-axis is Y here.",
        "**Frictionless supports (the hint):** on the top and bottom edges of the hub (z = ±15 mm), which stops the part "
        "from drifting along the axis but leaves everything free to grow radially. The rim ends, web and bore are free.",
        "**3D model:** the same profile revolved about Z. The load is axisymmetric, so the solid is a 90° wedge with "
        "frictionless supports on its two cut planes (y = 0 and x = 0), plus the same frictionless supports on the hub ends. "
        "A full 360° solid has a free rigid-body rotation about the axis; the solver cannot solve it without extra "
        "constraints, and the weak springs that remove it left rigid-body drift of about 10⁻³ mm in the results "
        "(thousands of times the 10⁻⁷ mm deformation). The wedge is the same physical model with the symmetry made explicit.",
    ])
    r.img_row([(im("axi_model.png"), "Axisymmetric model: frictionless supports on the hub ends (A), rotation (B)"),
               (im("axi_mesh.png"), f"Axisymmetric mesh ({AXF['size']:g} mm, {AXF['nodes']:,} nodes)")], height="2.7in")
    r.img_row([(im("s3d_iso_model.png"), "3D wedge model: hub-end supports (A), symmetry planes (B, C), rotation (D)"),
               (im("s3d_iso_mesh.png"), f"3D mesh ({S3F['size']:g} mm, {S3F['nodes']:,} nodes)")], height="2.5in")

    r.h2("2. Hand calculations")
    r.p("Centrifugal loading is far too small to matter at 100 rpm, so the numbers below are tiny: stresses of a few "
        "kPa and deformations of a fraction of a nanometre. The hand checks are an order of magnitude check on the FE results.")
    r.handcalc("Rotation, mass and the rim as a free rotating ring")
    r.step(r"\omega", r"\frac{2\pi N}{60}", r"\frac{2\pi(100)}{60}", H.OMEGA, "rad/s")
    r.step(r"\rho\omega^2", None, rf"(7850)({H.OMEGA:.4f})^2", H.RHO_W2, "N/m^3", "Body force per unit volume at radius r is ρω²r.")
    r.step(r"V", r"2\pi\bar r A", rf"2\pi({H.Q1_XBAR:.3f})({H.Q1_AREA:.0f})", H.Q1_VOL, "mm^3", "Pappus on the half-section; the CAD solid gives the same volume.")
    r.step(r"m", r"\rho V", rf"(7850)({H.Q1_VOL * 1e-9:.4e})", H.Q1_MASS, "kg")
    r.step(r"\sigma_{\theta,ring}", r"\rho\omega^2 r_m^2", rf"({fmt(H.RHO_W2)})({H.R_MID:.3f})^2", H.SIG_RING, "Pa",
           "Thin-ring hoop stress at the rim's mean radius, r_m = 38 mm.")
    r.step(r"u_{ring}", r"\frac{\sigma_\theta r_m}{E}", rf"\frac{{({fmt(H.SIG_RING)})({H.R_MID:.3f})}}{{2\times10^{{11}}}}", H.U_RING * 1e3, "mm")
    r.end_handcalc()
    r.handcalc("Rim as a rotating annulus (Lamé, plane stress, a = 30 mm, b = 46 mm)")
    r.p(r"$\sigma_\theta=\frac{3+\nu}{8}\rho\omega^2\left(a^2+b^2+\frac{a^2b^2}{r^2}-\frac{1+3\nu}{3+\nu}r^2\right)$, "
        r"$u=\frac{r}{E}(\sigma_\theta-\nu\sigma_r)$, with the surfaces free ($\sigma_r=0$ at a and b).")
    r.step(r"\sigma_\theta(b)", None, None, H.RIM_OUT[1], "Pa", "Outer face of the rim.")
    r.step(r"u(b)", r"\frac{b\,\sigma_\theta(b)}{E}", rf"\frac{{(0.046)({fmt(H.RIM_OUT[1])})}}{{2\times10^{{11}}}}", H.U_RIM_OUT * 1e3, "mm", "Radial growth of the rim's outer face.")
    r.step(r"\sigma_\theta(a)", None, None, H.SIG_TH_RIM_IN, "Pa", "Inner face of the rim: the highest hoop stress in the rim.")
    r.end_handcalc()
    r.handcalc("The whole part as a thin disk with a hole (bore)")
    r.step(r"\sigma_{\theta}(r=5)", r"\frac{3+\nu}{4}\rho\omega^2\left[b^2+\frac{1-\nu}{3+\nu}a^2\right]",
           rf"0.825({fmt(H.RHO_W2)})\left[0.046^2+0.212(0.005)^2\right]", H.SIG_BORE_DISK, "Pa",
           "A uniform disk (a = 5, b = 46 mm) ignores that the rim is 50 mm tall and the web only 12 mm, so the heavy rim "
           "loads the web more than this: expect the real bore stress above it.")
    r.end_handcalc()

    r.h2("3. Mesh convergence")
    rows = []
    for tag, C in (("2D", AXC), ("3D", S3C)):
        for c in C:
            rows.append([tag, f"{c['size']:g}", f"{c['nodes']:,}", sci(c["td_max_mm"], 4), f"{kpa(c['eqv_max_MPa']):.3f}",
                         f"{kpa(c['eqv_bore_max_MPa']):.3f}"])
    r.table(["Model", "Element size (mm)", "Nodes", "Max total def. (mm)", "Max von Mises (kPa)", "Von Mises on the bore (kPa)"],
            rows, "Mesh refinement, quadratic elements", cls="num")
    r.img(fig_q1_conv(), "Convergence of the total deformation, the peak stress and the bore stress.", width="98%", border=False)
    r.p(Q1_MESH_TEXT())

    r.h2("4. Results")
    r.h3("Axisymmetric model (final mesh)")
    r.img_row([(im("axi_td.png"), f"Total deformation: max {sci(AXF['td_max_mm'])} mm"),
               (im("axi_eqv.png"), f"Equivalent stress: max {kpa(AXF['eqv_max_MPa']):.2f} kPa")], height="2.6in")
    r.img_row([(im("axi_ur.png"), f"Radial deformation: {sci(AXF['ur_min_mm'])} to {sci(AXF['ur_max_mm'])} mm"),
               (im("axi_uz.png"), f"Axial deformation: ±{sci(AXF['uz_max_mm'])} mm")], height="2.6in")
    r.h3("3D wedge model (final mesh)")
    r.img_row([(im("s3d_iso_td.png"), f"Total deformation: max {sci(S3F['td_max_mm'])} mm"),
               (im("s3d_iso_eqv.png"), f"Equivalent stress: max {kpa(S3F['eqv_max_MPa']):.2f} kPa")], height="2.5in")
    r.img_row([(im("s3d_td.png"), "Total deformation on the y = 0 cut plane (same section as the 2D model)"),
               (im("s3d_eqv.png"), "Equivalent stress on the cut plane")], height="2.6in")

    r.h2("5. Comparison: axisymmetric vs. 3D")
    ax_b, s3_b = AXC[-1], S3C[-1]
    rows = [
        ["Max total deformation (mm)", sci(AXF["td_max_mm"], 4), sci(S3F["td_max_mm"], 4), f"{pct(S3F['td_max_mm'], AXF['td_max_mm']):.2f}"],
        ["Max radial deformation (mm)", sci(AXF["ur_max_mm"], 4), sci(S3F["ur_max_mm"], 4), f"{pct(S3F['ur_max_mm'], AXF['ur_max_mm']):.2f}"],
        ["Max axial deformation (mm)", sci(AXF["uz_max_mm"], 4), sci(S3F["uz_max_mm"], 4), f"{pct(S3F['uz_max_mm'], AXF['uz_max_mm']):.2f}"],
        ["Von Mises on the bore (kPa)", f"{kpa(AXF['eqv_bore_max_MPa']):.3f}", f"{kpa(S3F['eqv_bore_max_MPa']):.3f}",
         f"{pct(S3F['eqv_bore_max_MPa'], AXF['eqv_bore_max_MPa']):.2f}"],
    ]
    near = min(AXC, key=lambda c: abs(c["size"] - S3F["size"]))
    rows.append([f"Max von Mises, 2D at {near['size']:g} mm vs 3D at {S3F['size']:g} mm (kPa)", f"{kpa(near['eqv_max_MPa']):.3f}",
                 f"{kpa(S3F['eqv_max_MPa']):.3f}", f"{pct(S3F['eqv_max_MPa'], near['eqv_max_MPa']):.2f}"])
    rows.append([f"Max von Mises, 2D at {AXF['size']:g} mm (finest) vs 3D (kPa)", f"{kpa(AXF['eqv_max_MPa']):.3f}",
                 f"{kpa(S3F['eqv_max_MPa']):.3f}", f"{pct(S3F['eqv_max_MPa'], AXF['eqv_max_MPa']):.1f}"])
    r.table(["Quantity", "Axisymmetric", "3D wedge", "Difference (%)"], rows, "Axisymmetric vs. 3D, final meshes", cls="num")
    rows = [
        ["Rim outer radial deformation (mm)", sci(H.U_RIM_OUT * 1e3, 3), sci(AXF["ur_max_mm"], 3), f"{pct(AXF['ur_max_mm'], H.U_RIM_OUT * 1e3):.1f}",
         "Lamé annulus"],
        ["Thin-ring radial deformation (mm)", sci(H.U_RING * 1e3, 3), sci(AXF["ur_max_mm"], 3), f"{pct(AXF['ur_max_mm'], H.U_RING * 1e3):.1f}", "ring at 38 mm"],
        ["Bore stress (kPa)", f"{H.SIG_BORE_DISK / 1e3:.3f}", f"{kpa(AXF['eqv_bore_max_MPa']):.3f}", f"{pct(AXF['eqv_bore_max_MPa'] * 1e6, H.SIG_BORE_DISK):.0f}",
         "uniform thin disk"],
    ]
    r.table(["Hand check", "Hand", "ANSYS (axisym.)", "Difference (%)", "Basis"], rows, "Hand estimates against ANSYS", cls="num")
    r.p(Q1_COMPARE_TEXT())

    # ================================================================ Q2
    r.pagebreak()
    r.h1("Q2. Lifting bracket: half and full 3D models")
    r.p("The bracket is structural steel (E = 200 GPa, ν = 0.3). A 120 × 200 mm base, 30 mm thick, carries an upright with "
        "an eye for a pin. The base is fixed on its bottom face and a 20 kN bearing load lifts the bracket through the "
        "30 mm eye hole.")
    r.img(fig_q2_geometry(), "Geometry as built (mm). The origin sits on the mid-plane of the upright at the top of the base.", width="95%", border=False)
    r.bullets([
        "**Base:** 20 cm long (Z) × 12 cm wide (X) × 3 cm deep (Y), R1.75 cm corner fillets; four Ø2 cm through-holes "
        "centred 12 cm apart lengthwise and 6 cm apart widthwise.",
        "**Upright (profile in the XY plane, from the DesignModeler steps in the handout):** 12 cm at the base, rising "
        "8 cm to the line through the eye centre, where the straight sides end at ±3 cm and an R3 cm arc closes the top; Ø3 cm "
        "eye hole (R1.5 cm); extruded symmetrically 1.5 cm each way for a 3 cm thickness. Its top is 11 cm above the base.",
    ])
    r.h2("1. Finite element models, boundary conditions and loads")
    r.bullets([
        "**Analysis:** Static Structural, 3D solid from STEP, quadratic tetrahedra, Structural Steel.",
        "**Full model:** Fixed Support on the bottom face of the base; **Bearing Load** 20 kN in +Y on the eye hole "
        "(it presses on the half of the hole the pin bears on, as a pin does).",
        "**Half model:** the bracket is symmetric about the mid-plane of the upright (z = 0), so only z ≥ 0 is built. The "
        "cut face gets a **Frictionless Support**; the bearing load is halved to 10 kN. Everything else is as above.",
        "**Mesh controls:** global element size, with half that size on the eye-hole surface.",
    ])
    r.img_row([(im("full_model.png"), "Full model: fixed bottom face and bearing load"),
               (im("half_model.png"), "Half model: fixed bottom face, bearing load (10 kN) and the symmetry plane")], height="2.4in")
    r.img_row([(im("full_bc_bearing.png"), "Full: bearing load, 20 kN (+Y)"),
               (im("half_bc_sym.png"), "Half: frictionless support on the cut plane z = 0 (seen from behind)")], height="2.4in")
    r.img_row([(im("full_mesh.png"), f"Full mesh: {FF['size']:g} mm ({FF['nodes']:,} nodes)"),
               (im("half_mesh.png"), f"Half mesh: {HF['size']:g} mm ({HF['nodes']:,} nodes)")], height="2.4in")

    r.h2("2. Hand calculations")
    r.handcalc("Equilibrium and nominal stresses")
    r.step(r"R_y", r"P", None, H.P, "N", "The bottom face must carry the whole 20 kN (and 10 kN in the half model).")
    r.step(r"\sigma_{root}", r"\frac{P}{w_0\,t}", r"\frac{20\,000}{(120)(30)}", H.SIG_ROOT, "MPa", "Upright section where it meets the base.")
    r.step(r"\sigma_{gross}", r"\frac{P}{w_1\,t}", r"\frac{20\,000}{(60)(30)}", H.SIG_GROSS, "MPa", "Section through the eye centre, hole ignored.")
    r.step(r"\sigma_{net}", r"\frac{P}{(w_1-d)\,t}", r"\frac{20\,000}{(60-30)(30)}", H.SIG_NET, "MPa", "Net section through the eye: the two 15 mm ligaments.")
    r.step(r"\sigma_{bearing}", r"\frac{P}{d\,t}", r"\frac{20\,000}{(30)(30)}", H.SIG_BEAR, "MPa", "Projected-area bearing stress.")
    r.step(r"p_0", r"\frac{4P}{\pi\,d\,t}", r"\frac{4(20\,000)}{\pi(30)(30)}", H.P0_COS, "MPa", "Peak of a cosine-shaped pressure over the loaded half of the hole.")
    r.end_handcalc()
    r.handcalc("Axial stretch of the tapered upright (bar model)")
    r.step(r"w(y)", r"w_0-\frac{w_0-w_1}{80}\,y", r"120-0.75\,y", "120-0.75y", "mm")
    r.step(r"\delta", r"\int_0^{80}\frac{P\,dy}{E\,t\,w(y)}=\frac{P}{E\,t}\,\frac{\ln(w_0/w_1)}{0.75}",
           r"\frac{20\,000}{(200\,000)(30)}\,\frac{\ln 2}{0.75}", H.DELTA_AX, "mm",
           "Lower bound: it leaves out the eye itself and the base plate under the upright.")
    r.end_handcalc()

    r.h2("3. Mesh convergence")
    rows = []
    for tag, C in (("Full", FC), ("Half", HC)):
        for c in C:
            rows.append([tag, f"{c['size']:g} / {c['size'] / 2:g}", f"{c['nodes']:,}", f"{c['td_max']:.5f}", f"{c['dy_max']:.5f}",
                         f"{c['eqv_max']:.1f}", f"{c['sxy_max']:.1f}", f"{c['tmax_max']:.1f}"])
    r.table(["Model", "Global / eye-hole size (mm)", "Nodes", "Max total def. (mm)", "Max Y def. (mm)", "Max von Mises (MPa)",
             "Max τxy (MPa)", "Max τ (MPa)"], rows, "Mesh refinement (quadratic tetrahedra)", cls="num")
    r.img(fig_q2_conv(), "Convergence of deformation and stresses for the full and the half model.", width="98%", border=False)
    r.p(Q2_MESH_TEXT())

    r.h2("4. Results: full bracket")
    q2_results(r, "full", FF, im)
    r.h2("5. Results: half bracket")
    q2_results(r, "half", HF, im)

    r.h2("6. Half vs. full, and hand checks")
    rows = [
        ["Max total deformation (mm)", f"{FF['td_max']:.5f}", f"{HF['td_max']:.5f}", f"{pct(HF['td_max'], FF['td_max']):.2f}"],
        ["Max Y deformation (mm)", f"{FF['dy_max']:.5f}", f"{HF['dy_max']:.5f}", f"{pct(HF['dy_max'], FF['dy_max']):.2f}"],
        ["Max von Mises (MPa)", f"{FF['eqv_max']:.1f}", f"{HF['eqv_max']:.1f}", f"{pct(HF['eqv_max'], FF['eqv_max']):.1f}"],
        ["Max shear stress τxy (MPa)", f"{FF['sxy_max']:.1f}", f"{HF['sxy_max']:.1f}", f"{pct(HF['sxy_max'], FF['sxy_max']):.1f}"],
        ["Max shear stress τmax (MPa)", f"{FF['tmax_max']:.1f}", f"{HF['tmax_max']:.1f}", f"{pct(HF['tmax_max'], FF['tmax_max']):.1f}"],
        ["Reaction ΣFy at the fixed face (N)", f"{-FF['R'][1]:,.0f}", f"{-HF['R'][1]:,.0f} (×2 = {-2 * HF['R'][1]:,.0f})", f"{pct(-2 * HF['R'][1], -FF['R'][1]):.2f}"],
    ]
    r.table(["Quantity", "Full bracket", "Half bracket", "Difference (%)"], rows, "Half model against full model", cls="num")
    rows = [
        ["Reaction ΣFy (N)", f"{H.P:,.0f}", f"{-FF['R'][1]:,.1f}", f"{pct(-FF['R'][1], H.P):.3f}"],
        ["Stretch of upright, bar model (mm)", f"{H.DELTA_AX:.5f}", f"{FF['dy_max']:.5f}", f"×{FF['dy_max'] / H.DELTA_AX:.1f}"],
        ["Net-section stress at the eye (MPa)", f"{H.SIG_NET:.1f}", f"{FF['eqv_bearing_max']:.1f} (peak)", f"×{FF['eqv_bearing_max'] / H.SIG_NET:.1f}"],
        ["Yield safety factor (Sy = 250 MPa)", "—", f"{H.SY / FF['eqv_max']:.2f}", "—"],
    ]
    r.table(["Quantity", "Hand", "ANSYS (full)", "Difference (%) / ratio"], rows, "Hand checks against the full model", cls="num")
    r.p(Q2_COMPARE_TEXT())

    r.h2("7. Summary")
    r.bullets(SUMMARY())
    out = r.docx(OUT_DOCX)
    print("wrote", out)
    if "--pdf" in sys.argv:
        r.pdf(OUT_DOCX.with_name("HW9_preview.pdf"))


def q2_results(r, kind, F, im):
    p = kind + "_"
    r.img(im(p + "td.png"), f"Total deformation (mm): maximum {F['td_max']:.5f} mm at the top of the eye.", width="78%")
    r.img(im(p + "dy.png"), f"Directional deformation in Y (mm): {F['dy_min']:.5f} to {F['dy_max']:.5f} mm.", width="78%")
    r.img(im(p + "eqv.png"), f"Equivalent (von Mises) stress (MPa): maximum {F['eqv_max']:.1f} MPa on the eye hole.", width="78%")
    r.img_row([(im(p + "sxy.png"), f"Shear stress XY (MPa): {F['sxy_min']:.1f} to {F['sxy_max']:.1f}"),
               (im(p + "tmax.png"), f"Maximum shear stress (MPa): up to {F['tmax_max']:.1f}")], height="2.4in")
    if kind == "half":
        r.img(im(p + "eqv_back.png"), "Equivalent stress seen from the cut plane (z = 0), where the symmetry support acts.", width="70%")


def Q1_MESH_TEXT():
    a0, a1 = AXC[0], AXC[-1]
    s0, s1 = S3C[0], S3C[-1]
    return (f"The total deformation is converged on both models: {pct(a1['td_max_mm'], AXC[-2]['td_max_mm']):.2f}% change over the last "
            f"2D step and {pct(s1['td_max_mm'], S3C[-2]['td_max_mm']):.2f}% over the last 3D step. The von Mises stress on the bore, "
            f"a smooth surface, settles at about {kpa(a1['eqv_bore_max_MPa']):.2f} kPa (2D) and {kpa(s1['eqv_bore_max_MPa']):.2f} kPa (3D). "
            f"The overall peak is different: in the 2D model it rises from {kpa(a0['eqv_max_MPa']):.2f} to {kpa(a1['eqv_max_MPa']):.2f} kPa and is "
            "still climbing at the finest mesh, because it sits at the sharp re-entrant corners where the web meets the hub and the "
            "rim. Those corners are stress singularities of the idealized geometry (no fillet), so their peak value keeps growing "
            "with refinement and is not a real stress. Compare models on the bore and on equal element sizes, not on that peak.")


def Q1_COMPARE_TEXT():
    return (f"**The two models agree.** Total deformation differs by {pct(S3F['td_max_mm'], AXF['td_max_mm']):.2f}% "
            f"({sci(AXF['td_max_mm'])} mm axisymmetric, {sci(S3F['td_max_mm'])} mm 3D), the radial and axial parts by "
            f"{pct(S3F['ur_max_mm'], AXF['ur_max_mm']):.1f}% and {pct(S3F['uz_max_mm'], AXF['uz_max_mm']):.1f}%, and the bore "
            f"stress by {pct(S3F['eqv_bore_max_MPa'], AXF['eqv_bore_max_MPa']):.1f}%. The part is axisymmetric, so the 3D wedge only "
            "repeats the 2D result in more elements: the axisymmetric model gets it with about a fifth of the nodes. "
            f"The peak von Mises stress agrees when the element size matches ({kpa(S3F['eqv_max_MPa']):.2f} kPa in 3D at {S3F['size']:g} mm against "
            f"{kpa(NEAR['eqv_max_MPa']):.2f} kPa in 2D at {NEAR['size']:g} mm) and then separates only because the 2D mesh can be refined into "
            "the corner singularity. The maximum deformation is on the rim's outer corners "
            f"(about {sci(AXF['td_max_mm'], 2)} mm, a fifth of a nanometre); the hand estimates land within 10 to 15% on the rim radius "
            "and within about a third on the bore stress, the expected error for treating a stepped part as a plain ring and a plain disk. "
            "Holding the rim ends as well as the hub ends (the other reading of the hint) changes the answer: "
            f"the maximum deformation falls to {sci(AX['variant_rim']['td_max_mm'])} mm, because the rim can no longer shorten axially as it grows.")


def Q2_MESH_TEXT():
    f0, f1 = FC[0], FC[-1]
    return (f"Total deformation changes by {pct(f1['td_max'], FC[-2]['td_max']):.2f}% over the last refinement of the full model and by "
            f"{pct(HC[-1]['td_max'], HC[-2]['td_max']):.2f}% for the half model. The peak von Mises stress, {f1['eqv_max']:.1f} MPa, is at the "
            f"eye-hole surface (x = {FF['max_loc'][0]:.0f}, y = {FF['max_loc'][1]:.0f}, z = {FF['max_loc'][2]:.0f} mm), just above the level of the hole "
            f"centre (y = 80 mm) where the loaded half of the hole ends; it moves by {pct(f1['eqv_max'], FC[-2]['eqv_max']):.1f}% over the last step. "
            "The contour plots show nothing at the junction of the upright and the base, a sharp inside corner that is "
            "a stress singularity in principle, anywhere near the hole peak, so the hole is what governs. "
            "Node counts stay under the 128,000-node limit of ANSYS Student.")


def Q2_COMPARE_TEXT():
    return (f"**The half model reproduces the full model:** total deformation differs by {pct(HF['td_max'], FF['td_max']):.2f}%, Y deformation by "
            f"{pct(HF['dy_max'], FF['dy_max']):.2f}% and the peak von Mises stress by {pct(HF['eqv_max'], FF['eqv_max']):.1f}% "
            "(the two meshes are not identical, so the small scatter in a peak value is mesh noise). It needs about "
            f"{HF['nodes'] / FF['nodes'] * 100:.0f}% of the nodes. The symmetry plane carries no net vertical force, and the force reaction "
            f"on the fixed face of the half model is {-HF['R'][1]:,.0f} N, half the load. "
            f"**Hand checks:** the reaction matches the 20 kN load to {pct(-FF['R'][1], H.P):.3f}%. The nominal section stresses are low "
            f"({H.SIG_ROOT:.1f} MPa at the root, {H.SIG_NET:.1f} MPa net at the eye) and the peak von Mises stress, {FF['eqv_max']:.0f} MPa, is "
            f"{FF['eqv_max'] / H.SIG_NET:.1f} times the net-section average: a stress-concentration factor typical of a pin-loaded eye. The peak "
            f"of the bearing pressure scale (p₀ = {H.P0_COS:.0f} MPa) and the FE shear peak ({FF['sxy_max']:.0f} MPa τxy, {FF['tmax_max']:.0f} MPa τmax) "
            "are the same order, as they should be at the contact. The bar model gives only "
            f"{H.DELTA_AX:.4f} mm of stretch against {FF['dy_max']:.4f} mm in ANSYS: it leaves out the eye, which opens and "
            "elongates under the pin, so it is a lower bound. "
            f"The yield safety factor is {H.SY / FF['eqv_max']:.1f}.")


def SUMMARY():
    return [
        f"Q1: axisymmetric and 3D agree. Max total deformation {sci(AXF['td_max_mm'])} mm (2D) and {sci(S3F['td_max_mm'])} mm (3D), "
        f"{pct(S3F['td_max_mm'], AXF['td_max_mm']):.2f}% apart; bore von Mises {kpa(AXF['eqv_bore_max_MPa']):.2f} and {kpa(S3F['eqv_bore_max_MPa']):.2f} kPa. "
        "Centrifugal stresses at 100 rpm are only a few kPa.",
        f"Q1 peak stress sits at sharp inside corners (singular, mesh-dependent); compare on the bore and at equal mesh size.",
        f"Q2: the half model (z ≥ 0, symmetry support, 10 kN) matches the full model: max total deformation {HF['td_max']:.4f} and "
        f"{FF['td_max']:.4f} mm, max von Mises {HF['eqv_max']:.1f} and {FF['eqv_max']:.1f} MPa.",
        f"Q2 max shear stress τxy {FF['sxy_max']:.1f} MPa (τmax {FF['tmax_max']:.1f} MPa), max Y deformation {FF['dy_max']:.4f} mm, "
        f"peak at the loaded edge of the eye hole; yield safety factor {H.SY / FF['eqv_max']:.1f}.",
        "Reactions match the applied load; hand checks agree in order of magnitude and explain the peaks.",
    ]


if __name__ == "__main__":
    build()
