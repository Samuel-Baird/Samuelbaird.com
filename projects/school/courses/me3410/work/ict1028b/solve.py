"""In-class tutorial 10-28, problem 2 (bonus): long pressurized concrete block with a circular cavity.
Hand checks + ANSYS results -> Word.

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
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402

import hand as H  # noqa: E402
from figs_geo import fig_geometry  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "InClass_10-28_P2.docx"
AO = HERE / "ansys_out"
FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
RS = json.loads((AO / "results.json").read_text())
FIN, DEF, FACE, EDGE = RS["final"], RS["default"], RS["face"], RS["edge"]
NOH = RS.get("nohole", {})
RAD = RS.get("radius", {})
AD = RS.get("adaptive", {})
MC = RS.get("mohr", {})


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100


def im(name):
    return AO / name


def mpa(a):
    a = np.asarray(a, float)
    a = np.where(np.abs(a) > 1e20, np.nan, a)               # path points inside the hole come back as 1e302
    return a / 1e6 if np.nanmax(np.abs(a)) > 1e4 else a      # PlotData values come back in Pa


def mm(a):
    a = np.asarray(a, float)
    return a * 1000 if np.nanmax(np.abs(a)) < 1.0 else a


# ------------------------------------------------------------------ data extraction
def hole_table(d=FIN):
    """Hole-edge nodes: angle (deg, from +x, CCW), sigma_theta, eqv, s1, s3 (MPa), sorted by angle."""
    prof = d.get("hole") or {}
    have, rows = prof.get("have", []), prof.get("rows", [])
    if not rows:
        return None
    a = np.array(rows, float)
    cols = {k: mpa(a[:, 2 + i]) for i, k in enumerate(have)}
    th = np.arctan2(a[:, 1] - H.HY, a[:, 0] - H.HX)
    s, c = np.sin(th), np.cos(th)
    st = cols["sx"] * s ** 2 + cols["sy"] * c ** 2 - 2 * cols["sxy"] * s * c
    o = np.argsort(th)
    out = {"deg": np.degrees(th[o]), "x": a[o, 0], "y": a[o, 1], "st": st[o]}
    for k in ("eqv", "s1", "s3"):
        out[k] = cols[k][o]
    return out


def at_points(d, th_deg):
    """sigma_theta from the hole table at the nodes nearest the requested angles."""
    t = hole_table(d)
    return [float(t["st"][np.argmin(np.abs(((t["deg"] - a + 180) % 360) - 180))]) for a in th_deg]


def path_xy(pd):
    x, y = mm(pd["X Coordinate"]), mm(pd["Y Coordinate"])
    return x, y, mpa(pd["Values"])


def nominal_fe():
    """sigma_x, sigma_y at the hole centre (100, 50) in the model without the hole."""
    p = NOH.get("paths") or {}
    if not p.get("sx_h50"):
        return None
    xs, _, sx = path_xy(p["sx_h50"])
    _, _, sy = path_xy(p["sy_h50"])
    return float(np.interp(H.HX, xs, sx)), float(np.interp(H.HX, xs, sy))


NOM = nominal_fe()
SXF, SYF = NOM if NOM else (H.SX_NOM, H.SY_NOM)
KF = H.kirsch(SXF, SYF)
HT = hole_table()
ST_A = at_points(FIN, [0, 180])               # sides of the hole (right, left)
ST_B = at_points(FIN, [90, -90])              # top, bottom


# ------------------------------------------------------------------ figures
def nice_log(ax, n):
    ax.xaxis.set_major_locator(FixedLocator(n))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([f"{v:,}" for v in n], fontsize=6.5, rotation=30)


def fig_conv():
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7))
    nf, ne = [c["elements"] for c in FACE], [c["elements"] for c in EDGE]
    for ax, key, lab, sgn in ((axs[0], "s3_hole_min", "min principal on hole (MPa)", 1),
                              (axs[1], "s1_hole_max", "max principal on hole (MPa)", 1),
                              (axs[2], "dy_min", "max downward displacement (mm)", -1)):
        ax.plot(nf, [sgn * c[key] for c in FACE], "o-", color="C0", label="face sizing 20 → 2.5 mm")
        ax.plot(ne, [sgn * c[key] for c in EDGE], "s-", color="C2", label="2.5 mm face + edge 2 → 0.25 mm")
        if key in AD.get("hole_2", {}):
            ax.plot([AD["hole_2"]["elements"]], [sgn * AD["hole_2"][key]], "D", color="C3", label="adaptive (2%)")
        ax.set(xscale="log", xlabel="elements")
        ax.set_ylabel(lab, fontsize=7.5)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
        nice_log(ax, nf)
    axs[0].legend(fontsize=6, loc="best")
    fig.tight_layout()
    p = FIG / "convergence.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_hole():
    if HT is None:
        return None
    th = np.linspace(-180, 180, 361)
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.plot(HT["deg"], HT["st"], ".", ms=3, color="k", label="ANSYS, σθ at hole-edge nodes")
    ax.plot(th, [H.sig_theta(H.SX_NOM, H.SY_NOM, math.radians(t)) for t in th], "-", color="C3", lw=1.2,
            label=f"Kirsch, hand nominal (σx = {H.SX_NOM:.0f}, σy = {H.SY_NOM:.1f} MPa)")
    if NOM:
        ax.plot(th, [H.sig_theta(SXF, SYF, math.radians(t)) for t in th], "--", color="C0", lw=1.2,
                label=f"Kirsch, FE nominal without hole (σx = {SXF:.1f}, σy = {SYF:.1f} MPa)")
    ax.axhline(H.ST, color="C1", lw=0.8, ls=":")
    ax.axhline(-H.SC, color="C1", lw=0.8, ls=":")
    ax.text(-178, H.ST + 3, "tensile strength 3 MPa", fontsize=6.5, color="C1")
    ax.text(-178, -H.SC + 3, "compressive strength 40 MPa", fontsize=6.5, color="C1")
    ax.set(xlabel="angle on the hole edge θ (deg, from +x, counter-clockwise)", ylabel="tangential stress σθ (MPa)",
           xlim=(-180, 180))
    ax.set_xticks(range(-180, 181, 45))
    ax.legend(fontsize=6.5, loc="lower center")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "hole_profile.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_section():
    p = NOH.get("paths") or {}
    pf = FIN.get("paths") or {}
    if not p.get("sy_h50"):
        return None
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    x, _, sy = path_xy(p["sy_h50"])
    ax.plot(x, sy, "-", color="C0", label="ANSYS σy, no hole")
    if pf.get("sy_h50"):
        xh, _, syh = path_xy(pf["sy_h50"])
        ax.plot(xh, syh, "-", color="0.55", lw=0.9, label="ANSYS σy, with the hole")
    xs = np.linspace(0, 400, 50)
    ax.plot(xs, [H.sig_y_beam(v) for v in xs], "--", color="C3", label="beam theory: −N/A + M(x − 200)/I")
    _, _, sx = path_xy(p["sx_h50"])
    ax.plot(x, sx, "-", color="C2", lw=0.9, label="ANSYS σx, no hole")
    ax.axvspan(75, 125, color="0.9", zorder=0)
    ax.text(100, 2, "hole", ha="center", fontsize=7)
    ax.set(xlabel="x along y = 50 mm (mm)", ylabel="stress (MPa)", xlim=(0, 400))
    ax.legend(fontsize=6.5, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    q = FIG / "section_y50.png"
    fig.savefig(q, dpi=200)
    plt.close(fig)
    return q


def rad_rows():
    rows = []
    for r in sorted([5.0, 10.0, 20.0, 30.0, 40.0]):
        d = FIN if r == 20.0 else RAD.get(f"{r:g}")
        if d:
            rows.append((r, d))
    return rows


def fig_radius():
    rr = rad_rows()
    if len(rr) < 3:
        return None
    r = [a for a, _ in rr]
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    ax.plot(r, [-d["s3_fillet_min"] for _, d in rr], "o-", color="C0", label="|min principal| on fillet")
    ax.plot(r, [d["eqv_fillet_max"] for _, d in rr], "s-", color="k", label="von Mises on fillet")
    ax.plot(r, [d["s1_fillet_max"] for _, d in rr], "^-", color="C3", label="max principal on fillet")
    ax.set(xlabel="fillet radius r (mm)", ylabel="peak stress on the fillet (MPa)")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "fillet_radius.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ report
def build():
    r = Report("In-Class Tutorial 10-28: Problem 2 (bonus)",
               "Long pressurized concrete block with a circular cavity: 2D plane strain, stress concentration, mesh study",
               due="Wed Oct 29, 2026, 11:59 PM (submitted late)")

    r.h1("Problem")
    r.p("Q2 of the handout *Plane Strain-Stress Tutorial (V2)* used in class on Oct 28; the Canvas assignment gives "
        "bonus points for it. A long concrete block (500 mm out of plane) with a Ø50 mm bolt hole sits on a rigid base. "
        "Its 150 mm wide left part, 200 mm tall, carries q = 50 MPa on top. The 100 mm tall right part carries "
        "q = 25 MPa on its last 150 mm. A lateral pressure p = 10 MPa acts on both vertical sides. An R20 fillet joins "
        "the two parts. The handout gives no task list for Q2, so this follows the Q1 list: plane stress or strain, "
        "geometry, maximum von Mises stress and its location, σx, σy and τxy, maximum vertical displacement, stress "
        "concentration (hole and fillet radius), a mesh convergence study, and a comparison with an approximate "
        "beam-theory calculation. Because the material is concrete, failure is also checked with the tensile and "
        "compressive strengths.")
    r.img(fig_geometry(FIG / "geometry.png"), "Geometry and loading (mm), redrawn from the handout.", width="88%", border=False)
    r.h3("Data and assumptions")
    r.bullets([
        "**Concrete** (handout): E = 30 GPa, ν = 0.20, compressive strength 40 MPa, tensile strength 3 MPa. ANSYS's "
        "library concrete has ν = 0.18, so a copy with the handout's values was imported. The thermal expansion "
        "coefficient is given, but no temperature change is, so there is no thermal load.",
        "**Hole position** from the text: centre 100 mm from the y-axis and 50 mm from the base. The handout figure "
        "places it about 135 mm from the left edge (not to scale); the text governs.",
        "**Right-hand load length:** the table gives a 150 mm right top, but the base is 400 mm and the left top is "
        "150 mm, so the right top surface is 250 mm long (including the fillet). The figure draws the 25 MPa arrows "
        "and the 150 mm dimension over the last 150 mm only, so the load acts on x = 250 to 400 mm. The top surface "
        "from the fillet to x = 250 mm is unloaded.",
        "**Base:** drawn with ground hatching and pin symbols along its whole length, so it is modelled as a fixed "
        "support (u_x = u_y = 0). It must at least take u_x somewhere: the two lateral pressures act on different "
        "heights (200 mm and 100 mm), so they leave a net 1000 N/mm push to the right.",
        "**Forces per unit length:** ANSYS plane strain works per unit thickness (1 mm here), so reactions are in N "
        "per mm of block length. For the whole 500 mm block, multiply by 500.",
    ])

    # ------------------------------------------------------------ 1 plane strain
    r.h2("1. Plane stress or plane strain?")
    r.p("**Plane strain.** The block is 500 mm long out of plane, against a 400 × 200 mm cross-section. The loads "
        "and supports are the same in every cross-section along its length. Away from its ends, each slice is "
        "held by its neighbours and cannot stretch or shrink along z: $\\varepsilon_z = \\gamma_{xz} = \\gamma_{yz} = 0$. "
        "The stress σz is then not zero; it builds up to $\\sigma_z = \\nu(\\sigma_x + \\sigma_y)$. Plane stress "
        "(σz = 0) would need a thin plate with free faces, which is the case of Q1 (t = 5 mm). The model is a 2D surface "
        "body with 2D Behavior = **Plane Strain**.")

    # ------------------------------------------------------------ 2 FE model
    r.h2("2. Finite element model")
    r.bullets([
        "**Analysis:** Static Structural, 2D, Plane Strain, quadratic 8-node quadrilaterals (PLANE183).",
        "**Fixed Support** on the base edge (y = 0, 400 mm).",
        "**Pressure 50 MPa** on the left top edge (150 mm); **pressure 25 MPa** on the right top from x = 250 to 400 mm "
        "(the CAD edge is split at x = 250 mm so the load covers exactly that length); **pressure 10 MPa** on the left "
        "(200 mm) and right (100 mm) edges. A pressure always pushes normal to the edge, so each one points into the block.",
        f"**Mesh:** a face sizing on the block plus an edge sizing on the hole and the fillet. Final mesh: 2.5 mm face, "
        f"0.5 mm on the hole and fillet: {FIN['nodes']:,} nodes, {FIN['elements']:,} elements.",
    ])
    r.img(im("model.png"), "FE model: fixed base, four pressures.", width="80%")
    r.img_row([(im("mesh.png"), f"Final mesh ({FIN['elements']:,} elements)"),
               (im("mesh_hole.png"), "Mesh around the hole (0.5 mm on the edge)")], height="2.2in")

    # ------------------------------------------------------------ 3 hand
    r.h2("3. Hand calculations")
    r.handcalc("Statics (per mm of block length)")
    r.step(r"F_y", r"q_1 b_1 + q_2 b_2", rf"(50)(150) + (25)(150)", H.FY, "N/mm", "Total vertical load.")
    r.step(r"R_y", None, None, H.RY, "N/mm", f"Base reaction, up. For the whole 500 mm block: {H.RY * H.T_LONG / 1e6:.3f} MN.")
    r.step(r"R_x", r"-(p\,h_L - p\,h_R)", r"-[(10)(200) - (10)(100)]", H.RX, "N/mm",
           "The left side has twice the loaded height, so the base must push back to the left.")
    r.step(r"\bar x", r"\dfrac{F_1 x_1 + F_2 x_2}{F_y}", r"\dfrac{(7500)(75) + (3750)(325)}{11\,250}", H.XBAR, "mm",
           "Line of action of the vertical load, left of the base centre (x = 200).")
    r.end_handcalc()

    r.handcalc("Beam theory on the horizontal section through the hole, y = 50 mm (gross section, no hole)")
    r.p("Treat the block above y = 50 mm as a short column and the section as a 400 mm × 1 mm rectangle: "
        "$\\sigma_y = -N/A + M(x - 200)/I$, with N and M from the loads above the section.")
    r.step(r"A,\ I", None, r"400,\ \dfrac{400^3}{12}", rf"{H.A_S:.0f}\ \mathrm{{mm^2}},\ {fmt(H.I_S)}", "mm^4")
    r.step(r"M", r"(\bar x - 200)(-F_y) - (75)(p\cdot150) + (25)(p\cdot50)",
           r"(-41.67)(-11\,250) - (75)(1500) + (25)(500)", H.M_S, "N·mm/mm",
           "Moment of the loads above the section about its centroid (200, 50), counter-clockwise positive.")
    r.step(r"\sigma_{avg}", r"-\dfrac{F_y}{A}", r"-\dfrac{11\,250}{400}", H.SIG_AVG, "MPa")
    r.step(r"\sigma_y(x)", r"\sigma_{avg} + \dfrac{M}{I}(x - 200)", rf"-28.13 + {H.SLOPE:.5f}\,(x - 200)",
           f"{H.sig_y_beam(0):.2f}\\ \\text{{at }}x{{=}}0\\ \\ldots\\ {H.sig_y_beam(400):.2f}\\ \\text{{at }}x{{=}}400", "MPa",
           "The resultant sits left of centre, so the left side carries more compression.")
    r.step(r"\sigma_{y,nom}", r"\sigma_y(100)", rf"-28.13 + {H.SLOPE:.5f}\,(-100)", H.SY_NOM, "MPa",
           "Nominal vertical stress where the hole centre is.")
    r.step(r"\sigma_{x,nom}", r"-p", None, H.SX_NOM, "MPa", "At y = 50 mm both sides are pressurised: σx ≈ −p across the block.")
    r.step(r"\sigma_{z,nom}", r"\nu(\sigma_x + \sigma_y)", rf"0.20\,({H.SX_NOM:.0f} {H.SY_NOM:+.2f})", H.SZ_NOM, "MPa",
           "Plane strain.")
    r.end_handcalc()

    r.handcalc("Hole: Kirsch solution (circular hole in a large plate, remote σx and σy)")
    r.eq(r"\sigma_\theta(\theta) = (\sigma_x + \sigma_y) - 2(\sigma_x - \sigma_y)\cos 2\theta,\qquad \sigma_r = \tau_{r\theta} = 0\ \text{on the edge}")
    r.step(r"\sigma_{\theta,A}", r"3\sigma_y - \sigma_x", rf"3({H.SY_NOM:.2f}) - ({H.SX_NOM:.0f})", H.K["A"], "MPa",
           "Points A: the two sides of the hole (θ = 0°, 180°), compressive.")
    r.step(r"\sigma_{\theta,B}", r"3\sigma_x - \sigma_y", rf"3({H.SX_NOM:.0f}) - ({H.SY_NOM:.2f})", H.K["B"], "MPa",
           "Points B: top and bottom of the hole (θ = ±90°), tensile. Vertical compression opens the hole sideways "
           "and pulls its crown and invert apart.")
    r.step(r"K_t", r"\dfrac{\sigma_{\theta,A}}{\sigma_{y,nom}}", rf"\dfrac{{{H.K['A']:.2f}}}{{{H.SY_NOM:.2f}}}",
           H.K["A"] / H.SY_NOM, "", "Below the uniaxial 3 because the lateral pressure relieves the sides.")
    r.end_handcalc()

    r.handcalc("Failure check (brittle Coulomb-Mohr: S_t = 3 MPa, S_c = 40 MPa)")
    r.eq(r"\frac{1}{n} = \frac{\sigma_1}{S_t} - \frac{\sigma_3}{S_c}\quad(\sigma_1 \ge 0 \ge \sigma_3),\qquad "
         r"n = \frac{S_t}{\sigma_1}\ \text{or}\ \frac{S_c}{-\sigma_3}\ \text{if both have one sign}")
    s1f, s3f = sorted([H.SX_NOM, H.SY_NOM, H.SZ_NOM], reverse=True)[::2]
    r.step(r"n_{q_1}", r"\dfrac{S_c}{q_1}", r"\dfrac{40}{50}", H.N_Q1, "",
           "Directly under the 50 MPa load, σ3 = −50 MPa (σx and σz are smaller compressions): the applied pressure "
           "alone exceeds the crushing strength, so the whole left column fails in compression.")
    r.step(r"n_{q_2}", r"\dfrac{S_c}{q_2}", r"\dfrac{40}{25}", H.N_Q2, "", "Under the 25 MPa load: safe.")
    r.step(r"n_{far}", r"\dfrac{S_c}{-\sigma_3}", rf"\dfrac{{40}}{{{-s3f:.2f}}}", H.N_FAR, "",
           "At the hole level, with the beam-theory nominal stress spread over the whole section: just above 1.")
    r.step(r"n_A", r"\dfrac{S_c}{-\sigma_{\theta,A}}", rf"\dfrac{{40}}{{{-H.K['A']:.2f}}}", H.N_A, "",
           "Sides of the hole: σ1 = σr = 0, σ3 = σθ. Crushing.")
    r.step(r"n_B", r"\dfrac{S_t}{\sigma_{\theta,B}}", rf"\dfrac{{3}}{{{H.K['B']:.2f}}}", H.N_B, "",
           "Top and bottom of the hole: σ1 = σθ > 0, σ3 = σr = 0. Tensile cracking.")
    r.end_handcalc()

    r.handcalc("Vertical displacement of the left top (column bounds, plane strain)")
    r.eq(r"\varepsilon_y = \frac{(1-\nu^2)\sigma_y - \nu(1+\nu)\sigma_x}{E},\qquad \delta = \varepsilon_y\,h_L")
    r.step(r"\delta_{upper}", r"\dfrac{(1-\nu^2)(-q_1) - \nu(1+\nu)(-p)}{E}\,h_L",
           r"\dfrac{0.96(-50) - 0.24(-10)}{30\,000}(200)", H.DY_UPPER, "mm",
           "If the 50 MPa went straight down through the 200 mm without spreading.")
    r.step(r"\delta_{lower}", r"\dfrac{(1-\nu^2)\sigma_{avg} - \nu(1+\nu)(-p)}{E}\,h_L",
           r"\dfrac{0.96(-28.13) - 0.24(-10)}{30\,000}(200)", H.DY_LOWER, "mm",
           "If the load spread over the whole base at once.")
    r.step(r"\delta_{hole}", r"\displaystyle\int_0^{200} \frac{(1-\nu^2)\left(-\dfrac{q_1 b_1}{w(y)}\right) - \nu(1+\nu)(-p)}{E}\,dy",
           None, H.DY_HOLE, "mm",
           "The column of the first estimate, but the hole takes its chord out of the 150 mm width: "
           "w(y) = 150 − 2√(25² − (y − 50)²) for 25 < y < 75 mm, else 150 (column stress up to "
           f"{-H.SIG_NET:.0f} MPa of compression at the hole centre). Integrated numerically.")
    r.end_handcalc()

    # ------------------------------------------------------------ 4 mesh
    r.h2("4. Mesh convergence")
    rows = [["default", f"{DEF['elements']:,}", f"{DEF['nodes']:,}", f"{DEF['s3_hole_min']:.2f}", f"{DEF['s1_hole_max']:.3f}",
             f"{DEF['eqv_max']:.1f}", f"{DEF['dy_min']:.5f}"]]
    for c in FACE:
        rows.append([f"face {c['face']:g} mm", f"{c['elements']:,}", f"{c['nodes']:,}", f"{c['s3_hole_min']:.2f}",
                     f"{c['s1_hole_max']:.3f}", f"{c['eqv_max']:.1f}", f"{c['dy_min']:.5f}"])
    for c in EDGE:
        rows.append([f"face 2.5 + edge {c['edge']:g} mm", f"{c['elements']:,}", f"{c['nodes']:,}", f"{c['s3_hole_min']:.2f}",
                     f"{c['s1_hole_max']:.3f}", f"{c['eqv_max']:.1f}", f"{c['dy_min']:.5f}"])
    a = AD.get("hole_2")
    if a and "s3_hole_min" in a:
        rows.append([f"adaptive, 2% on hole von Mises", f"{a['elements']:,}", f"{a['nodes']:,}", f"{a['s3_hole_min']:.2f}",
                     f"{a['s1_hole_max']:.3f}", f"{a['eqv_max']:.1f}", f"{a['dy_min']:.5f}"])
    r.table(["Mesh", "Elements", "Nodes", "Min principal on hole (MPa)", "Max principal on hole (MPa)",
             "Max von Mises, whole model (MPa)", "Min u_y (mm)"], rows, "Mesh convergence study", cls="num")
    r.img(fig_conv(), "Convergence of the hole stresses and the displacement.", width="100%", border=False)
    r.p(MESH_TEXT())

    # ------------------------------------------------------------ 5 results
    r.h2("5. Results (final mesh)")
    r.img(im("deformed_vs_undeformed.png"), "Deformed shape (auto-scaled) over the undeformed outline.", width="78%")
    r.img_row([(im("td.png"), f"Total deformation (mm): max {FIN['td_max']:.4f} mm"),
               (im("dy.png"), f"Vertical deformation u_y (mm): min {FIN['dy_min']:.4f} mm")], height="2.2in")
    r.img(im("eqv.png"), f"Equivalent (von Mises) stress (MPa): maximum {FIN['eqv_max']:.1f} MPa.", width="78%")
    r.p(EQV_TEXT())
    r.img_row([(im("eqv_fillet_zoom.png"), f"Von Mises at the R20 fillet: peak {FIN['eqv_fillet_max']:.1f} MPa"),
               (im("eqv_hole_zoom.png"), f"Von Mises around the hole: up to {FIN['eqv_hole_max']:.1f} MPa")], height="2.2in")
    r.h3("Normal and shear stresses")
    r.img_row([(im("sx.png"), f"σx (MPa): {FIN['sx_min']:.1f} to {FIN['sx_max']:.1f}"),
               (im("sy.png"), f"σy (MPa): {FIN['sy_min']:.1f} to {FIN['sy_max']:.1f}")], height="2.2in")
    r.img_row([(im("sxy.png"), f"τxy (MPa): {FIN['sxy_min']:.1f} to {FIN['sxy_max']:.1f}"),
               (im("sz.png"), f"σz (MPa), plane strain: {FIN['sz_min']:.1f} to {FIN['sz_max']:.1f}")], height="2.2in")
    r.img_row([(im("s1_hole_zoom.png"), f"Max principal at the hole: up to {FIN['s1_hole_max']:.2f} MPa (tension)"),
               (im("s3_hole_zoom.png"), f"Min principal at the hole: down to {FIN['s3_hole_min']:.1f} MPa")], height="2.2in")
    r.h3("Stress concentration at the hole")
    hp = fig_hole()
    if hp:
        r.img(hp, "Tangential stress around the hole edge: ANSYS against the Kirsch solution.", width="90%", border=False)
    r.p(HOLE_TEXT())
    sp = fig_section()
    if sp:
        r.img(sp, "Stresses along y = 50 mm (through the hole centre): ANSYS against beam theory.", width="82%", border=False)
    r.p(SECTION_TEXT())
    r.h3("Fillet radius and the stress concentration at the step")
    fr = fig_radius()
    rows = [[f"R{rr:g}", f"{d['elements']:,}", f"{d['eqv_fillet_max']:.1f}", f"{d['s3_fillet_min']:.1f}",
             f"{d['s1_fillet_max']:.2f}"] for rr, d in rad_rows()]
    r.table(["Fillet", "Elements", "Max von Mises on fillet (MPa)", "Min principal on fillet (MPa)",
             "Max principal on fillet (MPa)"], rows, "Fillet radius study (same mesh controls: 2.5 mm face, 0.5 mm edges)",
            cls="num")
    if fr:
        r.img(fr, "Peak fillet stress against fillet radius.", width="66%", border=False)
    r.img_row([(im("s3_fillet_zoom.png"), f"Min principal at the R20 fillet: {FIN['s3_fillet_min']:.1f} MPa"),
               (im("s1_fillet_zoom.png"), f"Max principal at the R20 fillet: {FIN['s1_fillet_max']:.2f} MPa")], height="2.2in")
    r.p(FILLET_TEXT())
    if MC.get("sf_min") is not None:
        r.h3("Failure: Mohr-Coulomb stress tool")
        r.img_row([(im("mohr_coulomb_sf.png"), f"Mohr-Coulomb safety factor: minimum {MC['sf_min']:.2f}"),
                   (im("mohr_coulomb_sf_hole.png"), "Mohr-Coulomb safety factor around the hole")], height="2.2in")
        r.p(MOHR_TEXT())

    # ------------------------------------------------------------ 6 compare
    r.h2("6. Hand calculations vs. ANSYS")
    rows = [
        ["Base reaction R_y (N/mm)", f"{H.RY:,.1f}", f"{FIN['Ry']:,.2f}", f"{pct(FIN['Ry'], H.RY):.3f}"],
        ["Base reaction R_x (N/mm)", f"{H.RX:,.1f}", f"{FIN['Rx']:,.2f}", f"{pct(FIN['Rx'], H.RX):.3f}"],
    ]
    if NOM:
        rows += [["Nominal σy at (100, 50), no hole (MPa)", f"{H.SY_NOM:.2f}", f"{SYF:.2f}", f"{pct(SYF, H.SY_NOM):.1f}"],
                 ["Nominal σx at (100, 50), no hole (MPa)", f"{H.SX_NOM:.2f}", f"{SXF:.2f}", f"{pct(SXF, H.SX_NOM):.1f}"]]
    rows += [
        ["σθ at the hole sides A (MPa), mean of θ = 0°, 180°", f"{H.K['A']:.1f}", f"{np.mean(ST_A):.1f}",
         f"{pct(np.mean(ST_A), H.K['A']):.1f}"],
        ["σθ at the hole top/bottom B (MPa), mean of ±90°", f"{H.K['B']:.2f}", f"{np.mean(ST_B):.2f}",
         f"{pct(np.mean(ST_B), H.K['B']):.1f}"],
        ["Kirsch with the FE nominal: σθ,A / σθ,B (MPa)", f"{KF['A']:.1f} / {KF['B']:.2f}",
         f"{np.mean(ST_A):.1f} / {np.mean(ST_B):.2f}", f"{pct(np.mean(ST_A), KF['A']):.1f} / {pct(np.mean(ST_B), KF['B']):.1f}"],
        ["Max downward displacement, column with the hole (mm)", f"{-H.DY_HOLE:.4f}", f"{-FIN['dy_min']:.4f}",
         f"{pct(FIN['dy_min'], H.DY_HOLE):.1f}"],
    ]
    if MC.get("sf_min") is not None:
        n_crown, n_sides = MC["sf_min"], 40 / -FIN["s3_hole_min"]
        rows += [["Coulomb-Mohr n, hole crown (tension)", f"{H.N_B:.3f}", f"{n_crown:.3f}", f"{pct(n_crown, H.N_B):.1f}"],
                 ["Coulomb-Mohr n, hole sides (crushing)", f"{H.N_A:.3f}", f"{n_sides:.3f}", f"{pct(n_sides, H.N_A):.1f}"],
                 ["Coulomb-Mohr n, under the 50 MPa load", f"{H.N_Q1:.3f}", "below 1 (whole left column)", ""]]
    r.table(["Quantity", "Hand", "ANSYS (final mesh)", "Difference (%)"], rows, "Hand checks against ANSYS", cls="num")
    r.p(COMPARE_TEXT())

    r.h2("7. Summary")
    r.bullets(SUMMARY())
    out = r.docx(OUT_DOCX)
    print("wrote", out)


# ------------------------------------------------------------------ text
def fillet_peak(d=FIN):
    fp = d.get("fillet") or {}
    if not fp.get("rows"):
        return None
    a = np.array(fp["rows"], float)
    cols = {k: mpa(a[:, 2 + i]) for i, k in enumerate(fp["have"])}
    i = int(np.argmax(cols["eqv"]))
    # angle on the arc from the tangent point on the tall wall (150, 120), centre (170, 120)
    phi = math.degrees(math.atan2(120.0 - a[i, 1], 170.0 - a[i, 0]))
    return {"x": float(a[i, 0]), "y": float(a[i, 1]), "phi": phi, "eqv": float(cols["eqv"][i]), "s3": float(cols["s3"][i])}


def section_check():
    p = NOH.get("paths") or {}
    x, _, sy = path_xy(p["sy_h50"])
    return {"N": float(np.trapezoid(sy, x)), "M": float(np.trapezoid(sy * (x - 200.0), x)),
            "at": dict((v, float(np.interp(v, x, sy))) for v in (0, 100, 200, 300, 400))}


def MESH_TEXT():
    f0, f2, f3 = FACE[0], FACE[-2], FACE[-1]
    e0, e3 = EDGE[0], EDGE[-1]
    span = lambda key: max(abs(c[key]) for c in EDGE) - min(abs(c[key]) for c in EDGE)
    return (
        f"**Face sizing** from 20 mm to 2.5 mm ({f0['elements']:,} → {f3['elements']:,} elements): the compression at the "
        f"hole sides goes {f0['s3_hole_min']:.1f} → {f3['s3_hole_min']:.1f} MPa and changes "
        f"{pct(f3['s3_hole_min'], f2['s3_hole_min']):.2f}% over the last halving. The tension at the hole crown is more "
        f"sensitive ({f0['s1_hole_max']:.2f} → {f3['s1_hole_max']:.2f} MPa, {pct(f3['s1_hole_max'], f2['s1_hole_max']):.1f}% "
        f"in the last step): it is a small, sharp peak that coarse elements average away. The fillet stress converges "
        f"slowest ({f0['eqv_fillet_max']:.0f} → {f3['eqv_fillet_max']:.1f} MPa), and the displacement is converged from "
        f"the start ({pct(f0['dy_min'], f3['dy_min']):.2f}% between the coarsest and finest). "
        f"**Edge sizing** on the hole and the fillet, on top of the 2.5 mm face, from 2 mm to 0.25 mm: the hole and "
        f"fillet stresses move by at most {span('s3_hole_min'):.2f} MPa ({span('s3_hole_min') / abs(e3['s3_hole_min']) * 100:.2f}%) "
        f"and {span('eqv_fillet_max'):.2f} MPa ({span('eqv_fillet_max') / e3['eqv_fillet_max'] * 100:.1f}%), and the "
        f"displacement not at all. The results are mesh-independent. The final mesh is the 2.5 mm face with 0.5 mm on "
        f"the hole and the fillet ({FIN['elements']:,} elements). There is no singular point to chase in this model: the "
        "corners where the fixed base meets the loaded sides stay at the column stress, because the side pressure acts "
        "right down to the base. Adaptive refinement (a Convergence object on the hole stress) was also tried, but "
        "Mechanical stops it with a mesh-refinement failure on this plane-strain model, so convergence rests on these "
        "eight manual meshes.")


def EQV_TEXT():
    pk = fillet_peak()
    loc = (f" at x = {pk['x']:.1f} mm, y = {pk['y']:.1f} mm, {pk['phi']:.0f}° along the arc from the tall wall"
           if pk else "")
    return (
        f"**Maximum von Mises stress: {FIN['eqv_max']:.1f} MPa on the R20 fillet{loc}.** It is the inside corner where "
        "the heavily loaded left column meets the lower right part, and the stress there is almost purely compressive "
        f"(min principal {FIN['s3_fillet_min']:.1f} MPa, max principal only {FIN['s1_fillet_max']:.2f} MPa). The second "
        f"peak is at the sides of the hole ({FIN['eqv_hole_max']:.1f} MPa). Von Mises is reported because the tutorial "
        "asks for it, but it is a ductile-yield measure: it does not tell tension from compression, and concrete is "
        "about 13 times stronger in compression than in tension. The failure check below uses Coulomb-Mohr instead. "
        f"The maximum downward displacement is {-FIN['dy_min']:.4f} mm, at the top of the left column (total "
        f"{FIN['td_max']:.4f} mm, including the {FIN['dx_max']:.3f} mm sideways push of the left side).")


def HOLE_TEXT():
    return (
        f"ANSYS gives the largest compression at the hole sides ({min(HT['st']):.1f} MPa, at θ = "
        f"{HT['deg'][int(np.argmin(HT['st']))]:.0f}°) and tension at the crown ({max(HT['st']):.2f} MPa at θ = "
        f"{HT['deg'][int(np.argmax(HT['st']))]:.0f}°), the pattern of the Kirsch solution. With the hand (beam-theory) "
        f"nominal stresses, Kirsch is too low: {H.K['A']:.1f} MPa at the sides and {H.K['B']:.2f} MPa at the crown. The "
        f"reason is the nominal σy, not the Kirsch formula. Without the hole, ANSYS gives σy = {SYF:.1f} MPa and "
        f"σx = {SXF:.2f} MPa at (100, 50), against {H.SY_NOM:.1f} and {H.SX_NOM:.0f} MPa from beam theory: the 50 MPa load "
        "is only 150 mm above the hole and has not spread across the 400 mm section yet. Fed with the FE nominal "
        f"stresses, Kirsch gives {KF['A']:.1f} MPa at the sides, within {pct(np.mean(ST_A), KF['A']):.1f}% of ANSYS "
        f"(mean of the two sides). The crown and the invert differ ({ST_B[0]:.1f} and {ST_B[1]:.1f} MPa against "
        f"{KF['B']:.1f}): Kirsch assumes an infinite plate in a uniform stress field, but here the invert is only 25 mm "
        "above the fixed base, which holds the material under the hole, and σy changes along x across the hole. The "
        f"effective stress-concentration factor at the sides is {np.mean(ST_A) / SYF:.2f} on the FE nominal σy (3 for "
        "uniaxial compression; the lateral pressure lowers it).")


def SECTION_TEXT():
    c = section_check()
    a = c["at"]
    return (
        "On the section through the hole centre, ANSYS (no hole) and beam theory carry the same force and moment: "
        f"integrating the ANSYS σy across y = 50 mm gives {c['N']:,.1f} N/mm and {c['M']:,.0f} N·mm/mm about x = 200, "
        f"against {-H.FY:,.0f} N/mm and {H.M_S:,.0f} N·mm/mm by statics. The distribution is different. Beam theory "
        f"spreads it linearly ({H.sig_y_beam(0):.1f} → {H.sig_y_beam(400):.1f} MPa). In ANSYS the left column still "
        f"carries about {a[100]:.0f} MPa at y = 50, the material under the unloaded top between the fillet and x = 250 "
        f"is nearly idle ({a[200]:.1f} MPa at x = 200), and the right part carries about {a[300]:.0f} MPa under its 25 MPa "
        "load. The section is 400 mm wide but only 150 mm below the load, so plane sections do not stay plane "
        "(Saint-Venant: a load needs about one section width to spread out). Beam theory is fine for the resultants "
        "and the trend, not for the local stress at the hole.")


def FILLET_TEXT():
    rr = rad_rows()
    lo, hi = rr[0], rr[-1]
    return (
        f"The fillet radius controls the step stress: the peak compression on the fillet falls from "
        f"{lo[1]['s3_fillet_min']:.0f} MPa at R{lo[0]:g} to {hi[1]['s3_fillet_min']:.0f} MPa at R{hi[0]:g}, and the von Mises "
        f"peak from {lo[1]['eqv_fillet_max']:.0f} to {hi[1]['eqv_fillet_max']:.0f} MPa. Up to R30 the fillet is the most "
        f"stressed point of the block; at R40 the hole takes over (fillet {hi[1]['eqv_fillet_max']:.0f} MPa against "
        f"{hi[1]['eqv_hole_max']:.0f} MPa at the hole). As r → 0 the corner becomes a "
        "sharp re-entrant corner, where linear elasticity gives an infinite stress, so a generous fillet is the main "
        f"design lever at the step. The fillet barely changes the hole stress ({lo[1]['s3_hole_min']:.0f} to "
        f"{hi[1]['s3_hole_min']:.0f} MPa) or the displacement. The fillet is in compression on all radii (max principal "
        "≤ 1.6 MPa), so it would crush rather than crack.")


def MOHR_TEXT():
    return (
        f"Mechanical's stress tool with the Mohr-Coulomb theory, limits set to the material's ultimate strengths "
        f"(3 MPa tension, 40 MPa compression; the default yield limits are zero for concrete), gives a minimum safety "
        f"factor of **{MC['sf_min']:.3f}**, at the hole crown: there σ1 = {FIN['s1_hole_max']:.2f} MPa and σ3 ≈ 0, so "
        f"n = 3 / {FIN['s1_hole_max']:.2f} = {3 / FIN['s1_hole_max']:.3f}. Three kinds of region are below 1 (red): "
        f"(1) **the whole left column**, which carries about 50 MPa of compression against a 40 MPa crushing strength "
        f"(n ≈ {H.N_Q1:.2f}, as in the hand check); (2) **the hole**, which cracks at its crown and invert and crushes at "
        f"its sides (n ≈ 40 / {-FIN['s3_hole_min']:.0f} = {40 / -FIN['s3_hole_min']:.2f}); and (3) **the step**: the fillet "
        f"crushes (n ≈ {1 / (FIN['s1_fillet_max'] / 3 - FIN['s3_fillet_min'] / 40):.2f}), and the unloaded top surface just "
        "right of it is pulled into a few MPa of tension (σx) as the left column pushes down beside it, enough to crack "
        f"plain concrete. The right part under 25 MPa is safe (n ≈ {H.N_Q2:.1f} by hand; 1 to 5 in the plot). "
        "**Verdict: the block fails under these loads.** The 50 MPa top pressure alone is 25% above the crushing "
        "strength of this concrete; the hole and the step make it worse locally. A linear elastic model cannot follow "
        "what happens after the first crack or crush, so these numbers say where and roughly how badly it fails, not "
        "the collapse load.")


def COMPARE_TEXT():
    return (
        "**Equilibrium** is exact: both reactions match statics to round-off, and the ANSYS σy across the hole "
        "section integrates to the statics force and moment. **Hole stresses:** the hand Kirsch values are "
        f"{pct(np.mean(ST_A), H.K['A']):.0f}% low at the sides because the beam-theory nominal stress is low (the load "
        "has not spread by y = 50 mm); with the nominal stress from ANSYS, Kirsch agrees with ANSYS to "
        f"{pct(np.mean(ST_A), KF['A']):.1f}% at the sides. The crown tension is between the Kirsch value with the FE "
        "nominal and the invert value, for the reasons above. **Displacement:** the column estimate with the hole taken "
        f"out of the column width ({-H.DY_HOLE:.3f} mm) is {pct(FIN['dy_min'], H.DY_HOLE):.1f}% below ANSYS "
        f"({-FIN['dy_min']:.4f} mm). Without the hole the same check is closer: ANSYS {-NOH.get('dy_min', 0):.4f} mm "
        f"against {-H.DY_UPPER:.3f} mm ({pct(NOH.get('dy_min', 1), H.DY_UPPER):.1f}%). The remaining difference is the "
        "local spreading and the shear around the hole, which a 1D column cannot see. **Safety factors:** by hand, "
        f"crushing at the hole sides governs (n = {H.N_A:.2f}; crown {H.N_B:.2f}). In ANSYS the crown governs "
        f"(n = {MC.get('sf_min', float('nan')):.3f}) because its crown tension ({FIN['s1_hole_max']:.1f} MPa) is more "
        f"than three times the hand Kirsch value ({H.K['B']:.2f} MPa): a small change in the nominal stresses moves "
        "3σx − σy a lot when the two terms nearly cancel. The sides agree better once the FE nominal stress is used. "
        f"Both find the left column crushing under the 50 MPa load (n = {H.N_Q1:.2f}). Every route gives n < 1.")


def SUMMARY():
    rr = dict((f"{a:g}", d) for a, d in rad_rows())
    return [
        "Plane strain: a 500 mm long block with the same section, loads and supports along its length; "
        f"σz = ν(σx + σy) reaches {FIN['sz_min']:.0f} MPa.",
        f"Reactions {FIN['Ry']:,.0f} N/mm up and {-FIN['Rx']:,.0f} N/mm to the left (×500 mm: {FIN['Ry'] * 0.5 / 1000:.3f} MN "
        "and 0.5 MN), equal to statics.",
        f"Maximum von Mises {FIN['eqv_max']:.1f} MPa on the R20 fillet (compression); {FIN['eqv_hole_max']:.1f} MPa at the "
        "hole sides.",
        f"Maximum downward displacement {-FIN['dy_min']:.3f} mm at the top of the left column (column estimate with "
        f"the hole {-H.DY_HOLE:.3f} mm).",
        f"Hole: σθ = {min(HT['st']):.0f} MPa at the sides and +{max(HT['st']):.1f} MPa at the crown. Kirsch matches "
        f"the sides within {pct(np.mean(ST_A), KF['A']):.0f}% once it is fed the true nominal stress (σy = {SYF:.1f} MPa, "
        f"not the beam-theory {H.SY_NOM:.1f}).",
        f"Fillet radius: peak compression {rr['5']['s3_fillet_min']:.0f} MPa at R5, {FIN['s3_fillet_min']:.0f} at R20, "
        f"{rr['40']['s3_fillet_min']:.0f} at R40.",
        "Mesh: eight meshes; the final 2.5 mm / 0.5 mm mesh is converged to well under 1% on the hole stresses.",
        f"The block fails (Mohr-Coulomb minimum n = {MC.get('sf_min', float('nan')):.2f}): the 50 MPa load crushes the "
        f"left column (n = {H.N_Q1:.2f}), the hole cracks at its crown and crushes at its sides, and the step crushes at "
        "the fillet with a tension crack beside it. The right part under 25 MPa is safe.",
    ]


if __name__ == "__main__":
    if "--peek" in sys.argv:
        print("nominal FE", NOM, "Kirsch FE", KF, "hand", H.K)
        print("ST_A", ST_A, "ST_B", ST_B)
        if HT is not None:
            i, j = int(np.argmin(HT["st"])), int(np.argmax(HT["st"]))
            print("hole min st %.2f at %.0f deg, max %.2f at %.0f deg" % (HT["st"][i], HT["deg"][i], HT["st"][j], HT["deg"][j]))
        for k in ("eqv_max", "eqv_min", "s1_max", "s3_min", "sz_min", "sz_max", "sx_min", "sx_max", "sy_min", "sy_max",
                  "sxy_min", "sxy_max", "td_max", "dy_min", "dx_min", "dx_max", "Rx", "Ry", "eqv_hole_max",
                  "s1_hole_max", "s3_hole_min", "eqv_fillet_max", "s1_fillet_max", "s3_fillet_min"):
            print(k, FIN.get(k))
        for rr, d in rad_rows():
            print("R", rr, d["eqv_fillet_max"], d["s3_fillet_min"], d["s1_fillet_max"])
        print("mohr", MC, "adaptive", {k: {kk: v for kk, v in d.items() if not kk.startswith("img")} for k, d in AD.items()})
        print("problems", RS.get("problems"))
    else:
        build()
