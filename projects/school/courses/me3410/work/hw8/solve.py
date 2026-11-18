"""HW 8: thermal stress in a flanged aluminium pipe elbow. Hand checks + ANSYS results -> Word.

    python solve.py     (reads ansys_out/results.json written by ansys.py through run_ansys.sh)
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
import figs_hw8 as FG  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

OUT_DOCX = HERE.parents[1] / "out" / "HW8_Pipe_Elbow_Thermal.docx"
AO = HERE / "ansys_out"
FIG = FG.FIG
RS = json.loads((AO / "results.json").read_text())
FIN = RS["final"]
CONV = [c for c in RS["convergence"] if not c.get("skipped")]
PROF = RS.get("profiles", {})


def pct(x, ref):
    return abs(x - ref) / abs(ref) * 100


def sgn_pct(x, ref):
    return (x - ref) / abs(ref) * 100


# ------------------------------------------------------------------ path data
def path_xy(key):
    """(distance along the path in mm, value, xyz in mm) from a path result's PlotData; None if missing.
    Mechanical returns the sample points' X/Y/Z coordinates and values; the distance is the arc length."""
    pd = PROF.get(key)
    if not pd or "Values" not in pd:
        return None
    X = np.c_[pd["X Coordinate"], pd["Y Coordinate"], pd["Z Coordinate"]].astype(float)
    if abs(X).max() < 1.0:          # metres
        X = X * 1000
    d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(X, axis=0), axis=1))]
    v = np.array(pd["Values"], float)
    if abs(v).max() > 1e5:          # Pa
        v = v / 1e6
    return d, v, X


def face_r(key):
    """Flange 1 face paths: (radius mm, value)."""
    xy = path_xy(key)
    if xy is None:
        return None
    return np.hypot(xy[2][:, 0], xy[2][:, 1]), xy[1]


def band_max(key, lo, hi):
    """Largest value of a flange-face path between radii lo and hi (away from the bore and rim edges)."""
    fr = face_r(key)
    m = (fr[0] >= lo) & (fr[0] <= hi)
    return float(fr[1][m].max()), float(fr[1][m].mean())


def leg_near(key, upto=10.0):
    xy = path_xy(key)
    m = xy[0] <= upto
    return float(xy[1][m].max())


def rim_at(key, mm):
    xy = path_xy(key)
    if xy is None:
        return None
    return float(np.interp(mm, xy[0], xy[1]))


# ------------------------------------------------------------------ figures
def nice_log(ax, n):
    ax.xaxis.set_major_locator(FixedLocator(n))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([f"{v:,}" for v in n], fontsize=6.5, rotation=30)


def fig_conv():
    n = [c["nodes"] for c in CONV]
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7))
    ax = axs[0]
    ax.plot(n, [c["eqv_max"] for c in CONV], "^--", color="C3", label="global max (fixed-face edge)")
    ax.plot(n, [c["eqv_rim2_max"] for c in CONV], "s-", color="C1", label="flange 2 rim path max")
    ax.plot(n, [c["eqv_legs_max"] for c in CONV], "d-", color="C2", label="leg outer surfaces")
    ax.plot(n, [c["eqv_bend_max"] for c in CONV], "o-", color="C0", label="bend outer surface")
    ax.set(xscale="log", xlabel="nodes", ylabel="von Mises (MPa)")
    nice_log(ax, n)
    ax.legend(fontsize=5.5)
    ax.grid(alpha=0.3)
    ax = axs[1]
    ax.plot(n, [c["fr1"][2] / 1000 for c in CONV], "o-", color="C0", label="$R_z$ face 1 (kN)")
    ax.plot(n, [-c["mr1"][0] / 1e6 for c in CONV], "s-", color="C1", label="$-M_x$ face 1 (kN·m)")
    ax.plot(n, [c["td_max"] * 10 for c in CONV], "d-", color="k", label="max deformation × 10 (mm)")
    ax.set(xscale="log", xlabel="nodes")
    nice_log(ax, n)
    ax.legend(fontsize=5.5)
    ax.grid(alpha=0.3)
    ax = axs[2]
    ax.plot(n, [c["Q_bore"] for c in CONV], "o-", color="C3", label="heat in at the bore (W)")
    ax.axhline(H.Q_TOTAL, color="C3", ls=":", lw=0.8, label="hand estimate")
    ax.set(xscale="log", xlabel="nodes", ylabel="W", ylim=(50.5, 51.5))
    nice_log(ax, n)
    ax.legend(fontsize=5.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "convergence.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_wall():
    """Temperature and heat flux through the leg 1 wall, and sigma_z across the section, against the hand values."""
    t = path_xy("t_wall")
    q = path_xy("q_wall")
    top = path_xy("sz_wall_top")
    bot = path_xy("sz_wall_bot")
    if t is None and top is None:
        return None
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.6))
    r = lambda d: H.RI + 0.02 + d   # noqa: E731  the wall paths start at r = 25.02 mm
    rr = np.linspace(H.RI, H.RO, 30)
    if t is not None:
        ax = axs[0]
        ax.plot(r(t[0]), t[1], "o", ms=2.5, label="ANSYS")
        ax.plot(rr, [H.t_wall(x) for x in rr], "-", label="1D conduction")
        ax.set(xlabel="radius r (mm)", ylabel="T (°C)", title="Temperature, leg 1 wall")
        ax.ticklabel_format(useOffset=False)
        ax.legend(fontsize=6.5)
        ax.grid(alpha=0.3)
    if q is not None:
        ax = axs[1]
        ax.plot(r(q[0]), q[1], "o", ms=2.5, label="ANSYS")
        ax.plot(rr, [H.q_wall(x) for x in rr], "-", label="q'/(2πr)")
        ax.set(xlabel="radius r (mm)", ylabel="q (W/m²)", title="Heat flux, leg 1 wall")
        ax.legend(fontsize=6.5)
        ax.grid(alpha=0.3)
    ax = axs[2]
    yy = np.linspace(-H.RO, H.RO, 50)
    sr = H.section_from_reactions((FIN["fr1"][1], FIN["fr1"][2]), FIN["mr1"][0], H.Z_SEC)
    if top is not None:
        ax.plot(H.RI + 0.02 + top[0], top[1], "o", ms=2.5, color="C0", label="ANSYS")
    if bot is not None:
        ax.plot(-H.RO + 0.02 + bot[0], bot[1], "o", ms=2.5, color="C0")   # bottom path starts at y = -29.98
    for lo, hi in ((-H.RO, -H.RI), (H.RI, H.RO)):
        y = np.linspace(lo, hi, 10)
        ax.plot(y, sr["N"] / H.A_P + sr["M"] * y / H.I_P, "-", color="C1",
                label="N/A + My/I (ANSYS reactions)" if lo > 0 else None)
        ax.plot(y, H.SECK["N"] / H.A_P + H.SECK["M"] * y / H.I_P, "--", color="C2",
                label="hand frame model" if lo > 0 else None)
    ax.axhline(0, color="0.6", lw=0.5)
    ax.set(xlabel="y (mm)", ylabel="σz (MPa)", title=f"σz, leg 1, z = {H.Z_SEC:g} mm")
    ax.legend(fontsize=5.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "wall.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_rim():
    """Flange rims from the fixed-face edge, the fixed face itself (and 2, 5, 10 mm in), and the legs from the flanges."""
    a, b = path_xy("eqv_rim1"), path_xy("eqv_rim2")
    if a is None and b is None:
        return None
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.8))
    ax = axs[0]
    if a is not None:
        ax.plot(a[0], a[1], "o-", ms=2, lw=0.8, label="flange 1")
    if b is not None:
        ax.plot(b[0], b[1], "s-", ms=2, lw=0.8, label="flange 2")
    ax.axhline(H.SY, color="C3", ls="--", lw=0.8)
    ax.text(19.5, H.SY + 5, "yield", color="C3", ha="right", fontsize=6.5)
    ax.set(xlabel="distance from the fixed face (mm)", ylabel="von Mises (MPa)", title="Flange rim (x = 50)")
    ax.legend(fontsize=6)
    ax.grid(alpha=0.3)
    ax = axs[1]
    for k, lab in (("eqv_face_0.02", "on the fixed face"), ("eqv_face_2", "2 mm in"), ("eqv_face_5", "5 mm in"),
                   ("eqv_face_10", "10 mm in")):
        fr = face_r(k)
        if fr is not None:
            ax.plot(fr[0], fr[1], "-", lw=1.1, label=lab)
    ax.axhline(H.SIG_2D, color="k", ls=":", lw=0.9)
    ax.text(26.5, H.SIG_2D - 14, "EαΔT/(1−ν)", fontsize=6.5)
    ax.axhline(H.SY, color="C3", ls="--", lw=0.8)
    ax.set(xlabel="radius r (mm)", ylabel="von Mises (MPa)", title="Flange 1, between bolt holes")
    ax.set_ylim(0, 320)
    ax.legend(fontsize=5.5, loc="lower left")
    ax.grid(alpha=0.3)
    ax = axs[2]
    for k, lab in (("eqv_leg1_bot", "leg 1, y = −30"), ("eqv_leg1_top", "leg 1, y = +30"),
                   ("eqv_leg2_out", "leg 2, z = 200"), ("eqv_leg2_in", "leg 2, z = 140")):
        xy = path_xy(k)
        if xy is not None:
            ax.plot(xy[0], xy[1], "-", lw=1.0, label=lab)
    ax.set(xlabel="distance from the flange (mm)", ylabel="von Mises (MPa)", title="Pipe legs, outside")
    ax.legend(fontsize=5.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "rim_face_legs.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ report
def build():
    r = Report("HW 8: Thermal Stress in a Flanged Pipe Elbow",
               "Aluminum alloy elbow with a flange at each end: steady-state thermal → static structural in ANSYS Mechanical",
               due="Fri Nov 20, 2026, 11:59 PM")
    im = lambda n: AO / n  # noqa: E731
    f = FIN

    r.h1("Problem")
    r.p("Model the pipe elbow of the thermal-stress tutorial in aluminum alloy and add a second flange, with the same "
        "dimensions as the first, at the free end of the pipe. (1) Steady-state thermal analysis with the tutorial's "
        "loading: the FE model with its boundary conditions (initial temperature, temperature, convection), the "
        "temperature distribution and the heat flux. (2) Static structural analysis using the temperature from part 1, "
        "with the outer faces of both flanges fixed: the FE model with its boundary conditions, the total deformation, "
        "the equivalent stress, and whether the elbow fails under this static loading (safety factor).")
    r.p("**Geometry (tutorial dimensions).** Pipe Ø60 / Ø50 mm (5 mm wall). Sweep path: two 170 mm lines at 90° joined "
        "by a R70 fillet, so each straight leg is 100 mm and the bend has a 70 mm centreline radius. Flange: Ø100 / Ø50 mm, "
        "20 mm thick, four Ø10 mm bolt holes on an 80 mm bolt circle. Flange 1 sits on the start of the pipe as in the "
        "tutorial. Flange 2 is the same part placed on the free end, flush with the pipe end (the pipe runs 20 mm into "
        "each flange), so the part is symmetric about the plane that bisects the bend. Axes: flange 1's bolted face is "
        "z = 0, leg 1 runs along +Z, leg 2 along +Y, and flange 2's bolted face is y = 170 mm.")
    r.img(FG.fig_geometry(), "Geometry as modelled (mm).", width="95%", border=False)

    # ================================================================ PART I
    r.h1("Part I: Steady-state thermal analysis")
    r.h2("1. FE model and boundary conditions")
    r.bullets([
        "**Material:** ANSYS Aluminum Alloy. Thermal conductivity is temperature dependent: 114, 144, 165 and "
        "175 W/m·°C at −100, 0, 100 and 200 °C.",
        "**Initial temperature:** 30 °C (the tutorial value). In a steady-state analysis it is only the starting "
        "guess for the iterations; it does not change the answer.",
        "**Temperature 100 °C on the bore:** the inside of the pipe and of both flanges (3 faces).",
        f"**Convection, h = 10 W/m²·°C, ambient 30 °C:** on every outside surface that sees air: the outside of the "
        f"pipe (both legs and the bend), both flange rims and the pipe-side faces of both flanges (7 faces, "
        f"{H.A_CONV:,.0f} mm²).",
        "**Insulated (no load):** the bolted faces of both flanges, which sit against the mating flanges, and the bolt "
        "holes, which are filled by the bolts. This follows the tutorial (\"no heat dissipation at the flange back face\").",
        f"**Mesh:** quadratic tetrahedra, global size {f['size']:g} mm ({f['nodes']:,} nodes, {f['elements']:,} "
        "elements), the same mesh for the thermal and the structural analyses.",
    ])
    r.img(im("th_temp_bc.png"), "Temperature boundary condition: 100 °C on the bore of the pipe and both flanges.", width="72%")
    r.img_row([(im("th_conv.png"), "Convection, 10 W/m²·°C (shown as 1e-5 W/mm²·°C) to 30 °C air"),
               (im("th_conv_back.png"), "Convection (back): bolted faces left insulated")], height="2.3in")
    r.img(im("mesh.png"), f"Mesh, {f['size']:g} mm quadratic tetrahedra ({f['nodes']:,} nodes).", width="72%")

    r.h2("2. Hand calculations")
    r.handcalc("Conduction through the pipe wall in series with convection (per metre of pipe)")
    r.p(f"Radii $r_i$ = {H.RI:g} mm, $r_o$ = {H.RO:g} mm; k = {H.K:g} W/m·°C (aluminum at 100 °C).")
    r.step(r"R'_{wall}", r"\frac{\ln(r_o/r_i)}{2\pi k}", rf"\frac{{\ln(30/25)}}{{2\pi({H.K:g})}}", H.R_WALL, r"m\cdot{}^\circ C/W")
    r.step(r"R'_{conv}", r"\frac{1}{2\pi r_o h}", r"\frac{1}{2\pi(0.030)(10)}", H.R_CONV, r"m\cdot{}^\circ C/W")
    r.step(r"q'", r"\frac{T_i-T_\infty}{R'_{wall}+R'_{conv}}", rf"\frac{{100-30}}{{{fmt(H.R_WALL)}+{fmt(H.R_CONV)}}}",
           H.Q_LINE, "W/m")
    r.step(r"T_o", r"T_i-q'R'_{wall}", rf"100-({H.Q_LINE:.2f})({fmt(H.R_WALL)})", f"{H.T_OUT:.3f}", r"^\circ C",
           f"The wall loses only {H.DT_WALL:.3f} °C: almost all of the resistance is the air film.")
    r.step(r"Bi", r"\frac{h\,t}{k}", rf"\frac{{(10)(0.005)}}{{{H.K:g}}}", H.BI, "",
           "Bi ≪ 0.1, so the metal is practically at one temperature.")
    r.step(r"q''_i", r"\frac{q'}{2\pi r_i}", rf"\frac{{{H.Q_LINE:.2f}}}{{2\pi(0.025)}}", H.Q_IN, "W/m^2", "Heat flux at the bore.")
    r.step(r"q''_o", r"\frac{q'}{2\pi r_o}=h(T_o-T_\infty)", rf"\frac{{{H.Q_LINE:.2f}}}{{2\pi(0.030)}}", H.Q_OUT, "W/m^2",
           "Heat flux at the outside surface.")
    r.end_handcalc()
    r.handcalc("Total heat flow and the flange temperature drop")
    r.step(r"A_{conv}", r"2A_{leg}+A_{bend}+2A_{rim}+2A_{face}",
           rf"2({H.A_LEG:,.0f})+{H.A_BEND:,.0f}+2({H.A_FOD:,.0f})+2({H.A_FIN:,.0f})".replace(",", "{,}"), H.A_CONV, "mm^2",
           r"Leg: 2π(30)(80); bend: π²(70)(30); rim: 2π(50)(20); face: π(50²−30²) − 4π(5²).")
    r.step(r"Q", r"h\,A_{conv}(T_o-T_\infty)", rf"(10)({H.A_CONV / 1e6:.6f})({H.T_OUT:.3f}-30)", H.Q_TOTAL, "W",
           "All outside surfaces are within a fraction of a degree of 100 °C.")
    r.step(r"Q_{flange}", r"h(A_{rim}+A_{face})(100-30)", rf"(10)({(H.A_FOD + H.A_FIN) / 1e6:.6f})(70)", H.Q_FLANGE, "W",
           "Upper bound for one flange.")
    r.step(r"\Delta T_{flange}", r"\frac{Q_{flange}\ln(r_{rim}/r_{bore})}{2\pi k t_f}",
           rf"\frac{{({H.Q_FLANGE:.2f})\ln(50/25)}}{{2\pi({H.K:g})(0.020)}}", H.DT_FLANGE, r"^\circ C",
           "Bore-to-rim drop with all of one flange's heat crossing the full radius (no bolt holes).")
    r.step(r"\Delta T_{flange,holes}", r"\Delta T_{flange}\frac{\ln\frac{35}{25}+\frac{1}{1-f}\ln\frac{45}{35}+\ln\frac{50}{45}}{\ln 2},"
           r"\ f=\frac{4(10)}{2\pi(40)}",
           rf"({H.DT_FLANGE:.4f})({H.LN_HOLES / math.log(2):.4f})", H.DT_FLANGE_H, r"^\circ C",
           f"The holes remove f = {H.F_HOLES:.3f} of the ring r = 35–45 mm. The coldest point can still be a little lower: "
           "a hole shades the rim directly behind it.")
    r.end_handcalc()

    r.h2("3. Results")
    r.img(im("temp.png"), f"Temperature (°C): {f['temp_min']:.3f} to {f['temp_max']:.1f} °C.", width="80%")
    r.img_row([(im("temp_back.png"), "Temperature, seen from flange 1's side"),
               (im("temp_fl2.png"), "Temperature at flange 2: the coolest metal is at the rim")], height="2.3in")
    r.img(im("flux.png"), f"Total heat flux: {f['flux_min']:.0f} to {f['flux_max']:.0f} W/m² (the legend is in W/mm²: "
          f"{f['flux_max'] / 1e6:.4f} W/mm² = {f['flux_max']:.0f} W/m²).", width="80%")
    r.img_row([(im("flux_back.png"), "Total heat flux, flange 1 side"),
               (im("flux_fl2.png"), "Total heat flux at flange 2: highest where the bore meets the flange")], height="2.3in")
    w = fig_wall()
    tq = path_xy("q_wall")
    if w:
        r.img(w, "Through the leg 1 wall at z = 60 mm: temperature and heat flux against the 1D solution, and the axial "
              "stress from Part II.", width="98%", border=False)
    rows = [
        ["Outside wall temperature, leg (°C)", f"{H.T_OUT:.3f}", f"{f['t_wall_min']:.3f}", f"{pct(f['t_wall_min'], H.T_OUT):.3f}"],
        ["Heat flux at the bore, leg (W/m²)", f"{H.Q_IN:.1f}", f"{f['q_wall_max']:.1f}", f"{pct(f['q_wall_max'], H.Q_IN):.1f}"],
        ["Heat flux at the outside, leg (W/m²)", f"{H.Q_OUT:.1f}", f"{f['q_wall_min']:.1f}", f"{pct(f['q_wall_min'], H.Q_OUT):.1f}"],
        ["Total heat flow (W)", f"{H.Q_TOTAL:.2f}", f"{f['Q_bore']:.2f}", f"{pct(f['Q_bore'], H.Q_TOTAL):.2f}"],
        ["Largest drop below 100 °C (flange rim, °C)", f"{H.DT_FLANGE_H:.3f}", f"{100 - f['temp_min']:.3f}",
         f"{pct(100 - f['temp_min'], H.DT_FLANGE_H):.0f}"],
    ]
    r.table(["Quantity", "Hand", "ANSYS", "Difference (%)"], rows, "Part I: hand calculations against ANSYS", cls="num")
    r.p(THERMAL_TEXT())

    # ================================================================ PART II
    r.h1("Part II: Static structural analysis")
    r.h2("4. FE model and boundary conditions")
    r.bullets([
        "**Material:** ANSYS Aluminum Alloy: E = 71 GPa, ν = 0.33, α = 2.3 × 10⁻⁵ /°C, tensile yield 280 MPa, "
        "ultimate 310 MPa.",
        "**Load: Imported Body Temperature** from the steady-state thermal solution (the thermal analysis is linked to the "
        "structural one, as in the tutorial). The stress-free reference temperature is 22 °C, Mechanical's default "
        f"environment temperature used in the tutorial, so the metal heats up by about ΔT = {H.DT:g} °C.",
        "**Fixed Support on the outer (bolted) face of each flange**, as the assignment asks. No other load: the stress "
        "comes only from thermal expansion that the supports prevent.",
        "Same mesh as Part I.",
    ])
    if (AO / "ibt.png").exists():
        r.img(im("ibt.png"), "Imported body temperature from Part I.", width="72%")
    r.img_row([(im("st_fix1.png"), "Fixed support A: flange 1 bolted face (z = 0)"),
               (im("st_fix2.png"), "Fixed support B: flange 2 bolted face (y = 170)")], height="2.3in")

    r.h2("5. Hand calculations")
    r.handcalc("Thermal strain and fully restrained stresses")
    r.step(r"\Delta T", r"T-T_{ref}", r"100-22", H.DT, r"^\circ C", "The thermal result is uniform to within 0.3 °C.")
    r.step(r"\varepsilon_{th}", r"\alpha\,\Delta T", rf"(2.3\times10^{{-5}})({H.DT:g})", H.EPS_TH, "")
    r.step(r"\sigma_{1D}", r"E\alpha\Delta T", rf"(71\,000)({fmt(H.EPS_TH)})", H.SIG_1D, "MPa",
           "A straight bar held at both ends.")
    r.step(r"\sigma_{2D}", r"\frac{E\alpha\Delta T}{1-\nu}", rf"\frac{{{H.SIG_1D:.1f}}}{{1-0.33}}", H.SIG_2D, "MPa",
           "A surface held in both of its directions: the fixed flange faces, which cannot grow radially.")
    r.step(r"\delta", r"\alpha\,\Delta T\,(170)", rf"({fmt(H.EPS_TH)})(170)", H.DELTA, "mm",
           "Free growth of the flange 2 face relative to flange 1, in Y and in Z; the supports force it back to zero.")
    r.end_handcalc()
    r.handcalc("The elbow as a curved beam clamped at both flanges (force method)")
    r.p("Flanges rigid; flexible pipe from z = 20 (flange 1) through the bend to y = 150 (flange 2). Cut at flange 2 "
        "and take the end forces $F_z$, $F_y$ and moment $M$ there as redundants. At a point P of the centreline:")
    r.eq(r"m = M + (y_B-y_P)F_z-(z_B-z_P)F_y,\qquad n=\vec F\cdot\hat t,\qquad v=\vec F\cdot\hat n")
    r.eq(r"f_{ij}=\int \frac{k\,m_i m_j}{EI}ds+\int\frac{n_i n_j}{EA}ds+\int\frac{v_i v_j}{\kappa G A}ds,"
         r"\qquad [f]\{F_z,F_y,M\}^T=-\{\delta,\ \delta,\ 0\}^T")
    r.step("A", r"\pi(r_o^2-r_i^2)", r"\pi(30^2-25^2)", H.A_P, "mm^2")
    r.step("I", r"\frac{\pi}{4}(r_o^4-r_i^4)", r"\frac{\pi}{4}(30^4-25^4)", H.I_P, "mm^4")
    r.step(r"\kappa", r"\frac{6(1+\nu)(1+m^2)^2}{(7+6\nu)(1+m^2)^2+(20+12\nu)m^2}", r"m=\frac{25}{30}", H.KAPPA, "",
           "Cowper's shear coefficient for a hollow circle. The legs are short (80 mm ≈ 2.7 r), so shear matters.")
    r.step(r"h", r"\frac{tR}{r_m^2}", r"\frac{(5)(70)}{27.5^2}", H.H_BEND, "", "Pipe-bend parameter.")
    r.step(r"k", r"\frac{1.65}{h}", rf"\frac{{1.65}}{{{H.H_BEND:.4f}}}", H.K_BEND, "",
           "Bend flexibility factor (von Kármán, ASME B31.3): the bend's cross-section ovalizes, so it bends more easily.")
    r.p("The integrals are evaluated numerically along the centreline (script). Results for three levels of the model:")
    r.table(["Beam model", "End force $F_y = F_z$ (N)", "Moment at a fixed face (N·mm)", "Moment at mid-bend (N·mm)"],
            [[lab, f"{abs(fr['Fz']):,.0f}", f"{abs(fr['M_face2']):,.0f}", f"{abs(fr['m_midbend']):,.0f}"]
             for lab, fr in (("Euler–Bernoulli (bending + axial)", H.FR0), ("+ shear deformation", H.FR1),
                             (f"+ shear + bend flexibility (k = {H.K_BEND:.2f})", H.FRK))],
            "Hand (beam) model of the restrained elbow", cls="num")
    r.img(FG.fig_frame(), "Bending moment along the pipe from the three beam models.", width="92%", border=False)
    s = H.SECK
    r.step(r"\sigma_z(z=60)", r"\frac{N}{A}\pm\frac{M\,r_o}{I}",
           rf"\frac{{{s['N']:,.0f}}}{{{H.A_P:.1f}}}\pm\frac{{({s['M']:,.0f})(30)}}{{{H.I_P:,.0f}}}".replace(",", "{,}"),
           rf"{s['top30']:.1f}\ /\ {s['bot30']:.1f}", "MPa", "Leg 1 at mid-length, top (y = +30) / bottom (y = −30); k-model.")
    r.step(r"\sigma_{bend}", r"i\frac{M_{mid}r_o}{I}+\frac{N}{A},\ i=\frac{0.9}{h^{2/3}}",
           rf"({H.I_SIF:.2f})\frac{{({abs(H.FRK['m_midbend']):,.0f})(30)}}{{{H.I_P:,.0f}}}+\frac{{{abs(H.FRK['n_midbend']):,.0f}}}{{{H.A_P:.1f}}}".replace(",", "{,}"),
           H.SIG_BEND_K, "MPa", f"B31.3-style estimate of the bend peak with the k-model moment; with the shear-only "
           f"model's mid-bend moment it is {H.SIG_BEND_1:.0f} MPa.")
    r.end_handcalc()

    r.h2("6. Mesh convergence")
    rows = []
    for i, c in enumerate(CONV):
        rows.append([f"{c['size']:g}", f"{c['nodes']:,}", f"{c['Q_bore']:.2f}", f"{c['td_max']:.4f}",
                     f"{c['fr1'][2]:,.0f}", f"{-c['mr1'][0]:,.0f}", f"{c['eqv_bend_max']:.1f}", f"{c['eqv_legs_max']:.1f}",
                     f"{c['eqv_rim2_max']:.1f}", f"{c['eqv_max']:.1f}"])
    r.table(["Size (mm)", "Nodes", "Heat flow (W)", "Max def. (mm)", "$R_z$ face 1 (N)", "$-M_x$ face 1 (N·mm)",
             "vM bend (MPa)", "vM legs (MPa)", "vM rim path (MPa)", "vM max (MPa)"], rows,
            "Mesh refinement (quadratic tetrahedra; the finest mesh is near the 128,000-node Student limit)", cls="num")
    r.img(fig_conv(), "Convergence: stresses (left), reactions and deformation (middle), heat flow (right).", width="98%",
          border=False)
    r.p(MESH_TEXT())

    r.h2("7. Results")
    r.img(im("deformed.png"), "Total deformation on the deformed shape (exaggerated): the bend is pushed out the most, "
          "because the fixed flanges stop the pipe from growing along its length.", width="75%")
    r.img(im("td.png"), f"Total deformation (mm): maximum {f['td_max']:.4f} mm.", width="78%")
    r.img(im("eqv.png"), f"Equivalent (von Mises) stress (MPa), true-scale deformation: maximum {f['eqv_max']:.0f} MPa.",
          width="80%")
    r.img_row([(im("eqv_back.png"), "Equivalent stress from flange 1's side"),
               (im("eqv_fl2.png"), "Flange 2: the peak sits on the edge of the fixed face")], height="2.3in")
    r.img_row([(im("eqv_bend.png"), f"Bend outer surface: {f['eqv_bend_max']:.0f} MPa max"),
               (im("eqv_bore.png"), f"Bore: {f['eqv_bore_max']:.0f} MPa max")], height="2.3in")
    rim = fig_rim()
    if rim:
        r.img(rim, "Equivalent stress along lines: the flange rims starting at the fixed-face edge (left), across "
              "flange 1 between two bolt holes on and below the fixed face (middle), and along the outside of the legs "
              "starting at the flanges (right).", width="98%", border=False)
    r.img_row([(im("epel.png"), f"Equivalent elastic strain: max {f['epel_max']:.2e}"),
               (im("s1.png"), f"Maximum principal stress: max {f['s1_max']:.0f} MPa")], height="2.3in")
    F1, M1 = f["fr1"], f["mr1"]
    F2, M2 = f["fr2"], f["mr2"]
    r.table(["Support", "$R_x$ (N)", "$R_y$ (N)", "$R_z$ (N)", "$M_x$ (N·mm)", "$M_y$ (N·mm)", "$M_z$ (N·mm)"],
            [["A: flange 1"] + [f"{v:,.0f}" for v in F1 + M1], ["B: flange 2"] + [f"{v:,.0f}" for v in F2 + M2]],
            "Reactions at the fixed faces (moments about each face centre)", cls="num")
    r.p(f"The two supports carry equal and opposite forces (sum {abs(F1[1] + F2[1]):.1f} N in Y and {abs(F1[2] + F2[2]):.1f} N "
        "in Z), as they must with no external load, and the moments balance the couple of the two forces about the "
        f"face centres: $M_{{x,A}}+M_{{x,B}}+(170)R_{{z,B}}-(170)R_{{y,B}}$ = "
        f"{abs(M1[0] + M2[0] + 170 * F2[2] - 170 * F2[1]):,.0f} N·mm (B is at y = z = 170).")

    r.h2("8. Hand calculations vs. ANSYS")
    sr = H.section_from_reactions((F1[1], F1[2]), M1[0], H.Z_SEC)
    rows = [
        ["End force $R_y=R_z$ (N)", f"{abs(H.FR1['Fz']):,.0f} / {abs(H.FRK['Fz']):,.0f}", f"{F1[2]:,.0f}",
         f"{sgn_pct(F1[2], abs(H.FR1['Fz'])):+.0f} / {sgn_pct(F1[2], abs(H.FRK['Fz'])):+.0f}"],
        ["Moment at a fixed face (N·mm)", f"{abs(H.FR1['M_face1']):,.0f} / {abs(H.FRK['M_face1']):,.0f}", f"{abs(M1[0]):,.0f}",
         f"{sgn_pct(abs(M1[0]), abs(H.FR1['M_face1'])):+.1f} / {sgn_pct(abs(M1[0]), abs(H.FRK['M_face1'])):+.1f}"],
        ["σz leg 1, z = 60, top (MPa)", f"{H.SEC1['top30']:.1f} / {H.SECK['top30']:.1f}", f"{f['sz_wall_top_max']:.1f}", "—"],
        ["σz leg 1, z = 60, bottom (MPa)", f"{H.SEC1['bot30']:.1f} / {H.SECK['bot30']:.1f}", f"{f['sz_wall_bot_min']:.1f}", "—"],
        ["σz top, statics from ANSYS reactions (MPa)", f"{sr['top30']:.1f}", f"{f['sz_wall_top_max']:.1f}",
         f"{pct(f['sz_wall_top_max'], sr['top30']):.1f}"],
        ["σz bottom, statics from ANSYS reactions (MPa)", f"{sr['bot30']:.1f}", f"{f['sz_wall_bot_min']:.1f}",
         f"{pct(f['sz_wall_bot_min'], sr['bot30']):.1f}"],
        ["Peak stress in the bend (MPa)", f"{H.SIG_BEND_K:.0f} to {H.SIG_BEND_1:.0f} (B31.3 estimate)",
         f"{f['eqv_bend_max']:.1f}", "within range"],
        ["von Mises 2 mm below the bolted face (MPa)", f"{H.SIG_2D:.0f} (EαΔT/(1−ν))",
         f"{band_max('eqv_face_2', 27.5, 47.5)[1]:.0f} (mean, r = 27.5–47.5)",
         f"{sgn_pct(band_max('eqv_face_2', 27.5, 47.5)[1], H.SIG_2D):+.0f}"],
    ]
    r.table(["Quantity", "Hand (shear / + bend flex.)", "ANSYS (final mesh)", "Difference (%)"], rows,
            "Part II: hand calculations against ANSYS", cls="num")
    r.p(COMPARE_TEXT(sr))

    r.h2("9. Safety factor: does the elbow fail?")
    sf_rows, verdict, _ = SAFETY()
    r.table(["Location", "von Mises (MPa)", "n = Sy/σ", "Comment"], sf_rows,
            "Safety factor n = Sy / σ_vM against yield (Sy = 280 MPa)", cls="num")
    r.img_row([(im("sf.png"), f"Safety factor (Stress Tool): min {f.get('sf_min', 0):.2f} at the fixed-face edge"),
               (im("sf_back.png"), "Safety factor from flange 1's side")], height="2.3in")
    r.p(verdict)

    r.h2("10. Summary")
    r.bullets(SUMMARY())
    out = r.docx(OUT_DOCX)
    print("wrote", out)


# ------------------------------------------------------------------ text
def THERMAL_TEXT():
    f = FIN
    return (
        f"The whole elbow sits within {100 - f['temp_min']:.2f} °C of the bore temperature. With h = 10 W/m²·°C the air "
        f"film's resistance is about {H.R_CONV / H.R_WALL:,.0f} times that of the 5 mm aluminum wall (Bi = {H.BI:.1e}), "
        "so the metal cannot hold a temperature difference: the wall drops only "
        f"{H.DT_WALL:.3f} °C, which the hand calculation and ANSYS agree on. The coolest metal is at the rims of the "
        "flanges, the points farthest from the bore. Heat flux follows q'/(2πr) through the pipe wall "
        f"({H.Q_IN:.0f} W/m² at the bore, {H.Q_OUT:.0f} W/m² outside) and peaks where the bore meets a flange, because the "
        "flange's extra surface draws heat through the short path near the bore. The total heat delivered at the bore, "
        f"{f['Q_bore']:.2f} W, equals the convection loss to within {pct(f['Q_bore'], H.Q_TOTAL):.2f}% of the hand value "
        f"({H.Q_TOTAL:.2f} W). Compared with the tutorial's steel elbow (99.1 to 100 °C), aluminum conducts about 2.7 "
        "times better, so its temperature is even more uniform.")


def MESH_TEXT():
    c0, c1 = CONV[0], CONV[-1]
    return (
        f"From {c0['nodes']:,} to {c1['nodes']:,} nodes the heat flow ({c1['Q_bore']:.2f} W), the reactions "
        f"({pct(c1['fr1'][2], CONV[-2]['fr1'][2]):.2f}% change in the last step), the maximum deformation and the stresses in "
        f"the bend ({c0['eqv_bend_max']:.0f} → {c1['eqv_bend_max']:.0f} MPa) settle; these are the results used. "
        "The leg maximum moves around (it sits on the sharp, unfilleted corner where the pipe enters a flange), so the "
        "legs are judged on line results along their outside, which peak 2–3 mm from that corner. The global maximum "
        "is different again: it sits on the edge where a fixed flange face meets the flange rim, the bore or a bolt "
        "hole. A Fixed Support stops every displacement of that face, including the radial thermal growth "
        "the flange would have, and a fully fixed face meeting a free face is a stress singularity of the idealized "
        f"model: the peak value ({' → '.join(f'{c['eqv_max']:.0f}' for c in CONV)} MPa) depends on the mesh and is not a "
        "real stress. Following the tutorial, the stress a short distance from that edge is used instead (section 9).")


def COMPARE_TEXT(sr):
    f = FIN
    return (
        "**Reactions.** The plain (Euler–Bernoulli) beam model is twice as stiff as the elbow. The legs are short "
        "(80 mm ≈ 2.7 pipe radii), so shear deformation is as large as bending deformation, and the bend ovalizes. With "
        f"shear included the hand end force is {abs(H.FR1['Fz']):,.0f} N; adding the von Kármán factor gives "
        f"{abs(H.FRK['Fz']):,.0f} N. ANSYS ({f['fr1'][2]:,.0f} N) falls between the two. That is expected: k = "
        f"{H.K_BEND:.2f} assumes long straight pipe on both sides of the bend, while here the stiff flanges sit only "
        "80 mm away and partly stop the ovalization, so the real bend is stiffer than k says. The moment at the fixed "
        f"faces agrees within {max(pct(abs(f['mr1'][0]), abs(H.FR1['M_face1'])), pct(abs(f['mr1'][0]), abs(H.FRK['M_face1']))):.1f}% "
        "for both hand models. "
        f"**Section stress.** Using ANSYS's own reactions and statics, the axial stress at mid-leg is {sr['top30']:.1f} / "
        f"{sr['bot30']:.1f} MPa (top / bottom); ANSYS gives {f['sz_wall_top_max']:.1f} / {f['sz_wall_bot_min']:.1f} MPa. "
        "The solid model therefore behaves like a beam there; the few MPa of difference is local wall bending carried "
        "from the bend and the flange. "
        f"**Bend.** The B31.3-style estimate of the bend peak spans {H.SIG_BEND_K:.0f} to {H.SIG_BEND_1:.0f} MPa, depending "
        f"on which beam model supplies the mid-bend moment, and ANSYS's {f['eqv_bend_max']:.0f} MPa falls inside it, as "
        "its reactions do. The stress intensification factor is a "
        "code factor meant for long tangents. **Bolted faces.** The fixed support also stops each flange from growing "
        "radially. That is the plane-restraint case: just below the face the flange is held in both in-plane directions "
        f"and free normal to it, so σ_vM ≈ EαΔT/(1−ν) = {H.SIG_2D:.0f} MPa. ANSYS gives "
        f"{band_max('eqv_face_2', 27.5, 47.5)[1]:.0f} MPa on average 2 mm below the face, between two bolt holes. The "
        "stress then fades within 10 mm of the face as the flange's own stiffness takes over (section 7, middle plot).")


def SAFETY():
    """Rows of the safety-factor table, the verdict text and the governing (non-singular) stresses."""
    f = FIN
    sy = H.SY
    rim2 = max(rim_at("eqv_rim1", 2.0), rim_at("eqv_rim2", 2.0))
    rim5 = max(rim_at("eqv_rim1", 5.0), rim_at("eqv_rim2", 5.0))
    legs = max(leg_near(k) for k in ("eqv_leg1_bot", "eqv_leg1_top", "eqv_leg2_out", "eqv_leg2_in"))
    face_on, face_on_avg = band_max("eqv_face_0.02", 27.5, 47.5)
    face_2, face_2_avg = band_max("eqv_face_2", 27.5, 47.5)
    rows = [
        ["Bend, outer surface", f"{f['eqv_bend_max']:.1f}", f"{sy / f['eqv_bend_max']:.2f}", "converged"],
        ["Pipe legs next to the flanges (first 10 mm)", f"{legs:.1f}", f"{sy / legs:.2f}", "line results, outer surface"],
        ["Flange rim, 5 mm from the fixed face", f"{rim5:.1f}", f"{sy / rim5:.2f}", "tutorial method"],
        ["Flange rim, 2 mm from the fixed face", f"{rim2:.1f}", f"{sy / rim2:.2f}", "tutorial method"],
        ["Flange body 2 mm below the bolted face", f"{face_2:.1f} (mean {face_2_avg:.0f})", f"{sy / face_2:.2f}",
         f"hand EαΔT/(1−ν) = {H.SIG_2D:.0f}"],
        ["On the bolted face, away from its edges", f"{face_on:.1f} (mean {face_on_avg:.0f})", f"{sy / face_on:.2f}",
         "nodal values on a fixed face"],
        ["Edges of the bolted faces and bore (global max)", f"{f['eqv_max']:.1f}", f"{sy / f['eqv_max']:.2f}",
         "singular, grows with the mesh"],
    ]
    real = {"bend": f["eqv_bend_max"], "legs": legs, "rim": rim2, "face_2": face_2, "face_on": face_on}
    worst = max(real.values())
    n = sy / worst
    n2 = sy / face_2
    if n >= 1.0:
        verdict = (
            "**Verdict: the elbow does not fail under this static thermal load, but the margin at the bolted faces is "
            f"small.** The pipe is comfortable: the bend has n = {sy / f['eqv_bend_max']:.1f} and the legs next to the "
            f"flanges n = {sy / legs:.1f}. The most stressed region is the flange material at the bolted faces. A Fixed "
            "Support stops the flange from growing radially there, which is a biaxial restraint: just below the face "
            f"ANSYS gives {face_2_avg:.0f}–{face_2:.0f} MPa, against the hand value EαΔT/(1−ν) = {H.SIG_2D:.0f} MPa "
            f"(n = {n2:.2f}). On the face itself the nodal values reach {face_on:.0f} MPa (n = {n:.2f}), still below the "
            "280 MPa yield strength. Following the tutorial, the stress 2 mm from the edge of the fixed face is "
            f"{rim2:.0f} MPa (n = {sy / rim2:.2f}). Only the edges of the fixed faces exceed yield "
            f"({f['eqv_max']:.0f} MPa, Stress Tool minimum {f.get('sf_min', 0):.2f}); those values are singularities that "
            "keep growing with the mesh, so they are not used. In the real part, a thin layer yielding at a sharp edge "
            "does not make it fail under a thermal load either: thermal stress is displacement-controlled (secondary), so "
            "local yielding relaxes it instead of letting it grow. The fixed-face model is also conservative: a real "
            "bolted flange is not welded to its mate and can slide a little radially against the gasket, which relieves "
            f"the restraint that causes the highest stresses. With n ≈ {n:.1f}–{n2:.1f} at the flanges, though, repeated "
            "heat-up and cool-down cycles would deserve a fatigue check.")
    else:
        verdict = (
            f"**Verdict: the elbow yields.** Even away from the singular edges the stress reaches {worst:.0f} MPa, above "
            f"the 280 MPa yield strength (n = {n:.2f}), so the design fails the static check.")
    return rows, verdict, real


def SUMMARY():
    f = FIN
    _, _, real = SAFETY()
    return [
        f"Thermal: the aluminum elbow is at {f['temp_min']:.2f}–100 °C throughout (Bi = {H.BI:.1e}); heat flux "
        f"{f['flux_min']:.0f}–{f['flux_max']:.0f} W/m², total heat flow {f['Q_bore']:.2f} W (hand {H.Q_TOTAL:.2f} W).",
        f"Structural: fixing both flange faces stops {H.DELTA:.3f} mm of thermal growth in Y and in Z. The supports push "
        f"back with {f['fr1'][2]:,.0f} N in each direction and {abs(f['mr1'][0]) / 1e6:.2f} kN·m; the hand beam models "
        f"bracket the force ({abs(H.FRK['Fz']):,.0f} to {abs(H.FR1['Fz']):,.0f} N) and match the moment within 2%.",
        f"Total deformation: maximum {f['td_max']:.3f} mm. Equivalent stress: {f['eqv_bend_max']:.0f} MPa in the bend, "
        f"about {real['legs']:.0f} MPa in the pipe next to the flanges, {real['face_2']:.0f} MPa in the flanges just "
        f"below the bolted faces (hand {H.SIG_2D:.0f} MPa); the {f['eqv_max']:.0f} MPa maximum is a singular edge of a "
        "fixed face.",
        f"Safety factor against yield: {H.SY / f['eqv_bend_max']:.1f} in the bend, {H.SY / real['legs']:.1f} in the legs, "
        f"{H.SY / real['face_on']:.2f}–{H.SY / real['face_2']:.2f} at the bolted faces. The elbow does not fail under the "
        "static thermal load; the bolted flange faces have the smallest margin.",
    ]


if __name__ == "__main__":
    build()
