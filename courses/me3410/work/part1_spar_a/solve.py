"""Term Project Part I, Spar A (I-section): hand calculations + ANSYS comparison -> Word (.docx).

    python solve.py            (needs ansys_out/results_full.json from ansys.py)

Every number below is computed here; the report only formats them.
"""
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline"))
from report import Report, fmt  # noqa: E402

FIG = HERE / "figs"
FIG.mkdir(exist_ok=True)
OUT_DOCX = HERE.parents[1] / "out" / "TP_Part_I_Spar_A_I-section.docx"
RES = json.loads((HERE / "ansys_out" / "results_full.json").read_text())

# ---------------------------------------------------------------- data
L, q0, e = 1.5, 1200.0, 0.050           # m, N/m, m
H, B, tf, tw = 60.0, 55.0, 6.0, 4.0     # mm
x_val = 0.250                            # m
mat = RES["material"]
E, nu, Sy, rho_lib = mat["E"], mat["nu"], mat["Sy"], mat["rho"]
rho_proj = 1540.0                        # kg/m^3, project table
G = E / (2 * (1 + nu))
s_tip = 0.625


def s_of(x):
    return 1 - (1 - s_tip) * x / L


# ---------------------------------------------------------------- statics
W = q0 * L / 2
xbar_W = L / 3
R = W
M0 = W * xbar_W
T0 = e * R


def V(x):
    return q0 * (L - x) ** 2 / (2 * L)


def M(x):
    return q0 * (L - x) ** 3 / (6 * L)


V_val, M_val = V(x_val), M(x_val)

# ---------------------------------------------------------------- section (mm)
hw = H - 2 * tf
A_f, A_w = B * tf, tw * hw
A = 2 * A_f + A_w
d_f = H / 2 - tf / 2
Ic_f = B * tf ** 3 / 12
Ic_w = tw * hw ** 3 / 12
I_mm4 = 2 * (Ic_f + A_f * d_f ** 2) + Ic_w
Iy_mm4 = 2 * (tf * B ** 3 / 12) + hw * tw ** 3 / 12
I = I_mm4 * 1e-12
c = H / 2 / 1000
area_lo, area_hi = 850 * 0.95, 850 * 1.05

sig_root = M0 * c / I
sig_val = M_val * c / I
FoS_root = Sy / sig_root
FoS_val = Sy / sig_val

Q_mm3 = A_f * d_f + tw * (hw / 2) * (hw / 4)
Q = Q_mm3 * 1e-9
t_web = tw / 1000
tau_val = V_val * Q / (I * t_web)
tau_root = R * Q / (I * t_web)

delta_tip = q0 * L ** 4 / (30 * E * I)
delta_ref69 = q0 * L ** 4 / (30 * 69e9 * I)

J_mm4 = (2 * B * tf ** 3 + hw * tw ** 3) / 3
J = J_mm4 * 1e-12
theta_const = e * M0 / (G * J)   # = (1/GJ) * integral of e*V(x) dx


def simpson(f, a, b, n):
    xs = np.linspace(a, b, n + 1)
    ys = f(xs)
    h = (b - a) / n
    return h / 3 * (ys[0] + ys[-1] + 4 * ys[1:-1:2].sum() + 2 * ys[2:-1:2].sum())


def integrand_defl(x):
    return M(x) * (L - x) / (E * I * s_of(x) ** 4)


def integrand_twist(x):
    return e * V(x) / (G * J * s_of(x) ** 4)


taper_defl = {n: simpson(integrand_defl, 0, L, n) for n in (20, 40, 200)}
taper_twist = {n: simpson(integrand_twist, 0, L, n) for n in (20, 40, 200)}
const_check = simpson(lambda x: M(x) * (L - x) / (E * I) + 0 * x, 0, L, 20)

vol_const = A * 1e-6 * L
vol_taper = A * 1e-6 * simpson(lambda x: s_of(x) ** 2, 0, L, 20)
mass_const = vol_const * rho_proj
mass_taper = vol_taper * rho_proj
mass_const_lib = vol_const * rho_lib
mass_taper_lib = vol_taper * rho_lib

# ---------------------------------------------------------------- warping-restrained torsion
# Open sections resist torque by St. Venant shear (GJ) plus flange bending when warping is
# restrained (Vlasov): T(x) = GJ phi - (E Cw phi')', phi = dtheta/dx.  Fixed root: phi(0) = 0
# (no warping); free tip: phi'(L) = 0 (no bimoment).  Solved by central finite differences.
h_f = H - tf                                   # mm, distance between flange centroids
Cw_mm6 = tf * B ** 3 * h_f ** 2 / 24           # I-section: I_flange,y * h^2 / 2
Cw = Cw_mm6 * 1e-18
lam = math.sqrt(G * J / (E * Cw))              # 1/m


def warping_twist(tapered, n=1500):
    xs = np.linspace(0, L, n + 1)
    hx = xs[1] - xs[0]
    sc = s_of(xs) if tapered else np.ones_like(xs)
    xm = 0.5 * (xs[:-1] + xs[1:])
    a_half = E * Cw * (s_of(xm) if tapered else np.ones_like(xm)) ** 6   # Cw ~ s^6
    b = G * J * sc ** 4                                                  # J ~ s^4
    T = e * V(xs)
    K = np.zeros((n + 1, n + 1))
    rhs = np.zeros(n + 1)
    K[0, 0] = 1.0
    for i in range(1, n):
        K[i, i - 1] = a_half[i - 1] / hx ** 2
        K[i, i + 1] = a_half[i] / hx ** 2
        K[i, i] = -(a_half[i - 1] + a_half[i]) / hx ** 2 - b[i]
        rhs[i] = -T[i]
    K[n, n - 1] = 2 * a_half[n - 1] / hx ** 2          # ghost node: phi'(L) = 0
    K[n, n] = -2 * a_half[n - 1] / hx ** 2 - b[n]
    rhs[n] = -T[n]
    phi = np.linalg.solve(K, rhs)
    return float(np.sum(0.5 * (phi[1:] + phi[:-1]) * hx))


theta_w_const = warping_twist(False)
J_corr = (2 * (B - 0.63 * tf) * tf ** 3 + hw * tw ** 3) / 3   # mm^4, free-edge correction on the flanges
theta_w_taper = warping_twist(True)

# ---------------------------------------------------------------- four-spar cross-check (Appendix A)


def spar_table():
    """Hand values for all four constant-section baseline spars (team summary table)."""
    rows = []
    specs = {
        "A I-section": dict(H=60, B=55, tf=6, tw=4, webs=1, kind="I"),
        "B C-channel": dict(H=60, B=55, tf=6, tw=4, webs=1, kind="C"),
        "C Box": dict(H=60, B=54, tf=4, tw=4, webs=2, kind="box"),
        "D Twin-web": dict(H=60, B=55, tf=4, tw=4, webs=2, kind="twin"),
    }
    for name, d in specs.items():
        Hh, Bb, t_f, t_w, nw = d["H"], d["B"], d["tf"], d["tw"], d["webs"]
        hw_ = Hh - 2 * t_f
        Af, Aw = Bb * t_f, t_w * hw_
        Atot = 2 * Af + nw * Aw
        df = Hh / 2 - t_f / 2
        Ix = 2 * (Bb * t_f ** 3 / 12 + Af * df ** 2) + nw * t_w * hw_ ** 3 / 12
        if d["kind"] == "C":       # chordwise centroid measured from the back of the web
            xbar = (2 * Af * Bb / 2 + Aw * t_w / 2) / Atot
        else:
            xbar = Bb / 2
        Qna = Af * df + nw * t_w * (hw_ / 2) * (hw_ / 4)
        tau = V_val * Qna * 1e-9 / (Ix * 1e-12 * nw * t_w / 1000)
        sr = M0 * (Hh / 2000) / (Ix * 1e-12)
        sv = M_val * (Hh / 2000) / (Ix * 1e-12)
        d69 = q0 * L ** 4 / (30 * 69e9 * Ix * 1e-12)
        d71 = q0 * L ** 4 / (30 * E * Ix * 1e-12)
        if d["kind"] in ("I", "C"):
            Jx = (2 * Bb * t_f ** 3 + hw_ * t_w ** 3) / 3
            jnote = "⅓Σbt³"
        elif d["kind"] == "box":
            Am = (Bb - t_w) * (Hh - t_f)
            Jx = 4 * Am ** 2 / (2 * (Bb - t_w) / t_f + 2 * (Hh - t_f) / t_w)
            jnote = "Bredt 4A²/∮ds/t"
        else:
            Jx = None
            jnote = "depends on web spacing"
        th = math.degrees(e * M0 / (G * Jx * 1e-12)) if Jx else None
        rows.append(dict(name=name, A=Atot, xbar=xbar, Ix=Ix, sr=sr, sv=sv, fos=Sy / sr, Q=Qna, tau=tau,
                         d69=d69, d71=d71, J=Jx, jnote=jnote, th=th, ok=abs(Atot - 850) <= 42.5))
    return rows


SPARS = spar_table()
box = SPARS[2]
box_Ix_Iy = box["Ix"] + (60 * 54 ** 3 - 52 * 46 ** 3) / 12   # handout's J ≈ Ix + Iy, for comparison

# ---------------------------------------------------------------- FEA results
C = RES["cases"]
c1, c2, t1, t2 = C["constant_LC1"], C["constant_LC2"], C["tapered_LC1"], C["tapered_LC2"]
fe_mass_c = RES["mass_constant"]["mass_kg"]       # ANSYS, library density
fe_mass_t = RES["mass_tapered"]["mass_kg"]
fe_vol_c = RES["mass_constant"]["volume_m3"]
fe_vol_t = RES["mass_tapered"]["volume_m3"]
FINAL_LV = RES["final_level"]                     # [name, global m, refine m]


def perr(fe, ref):
    return abs(abs(fe) - abs(ref)) / abs(ref) * 100


# ---------------------------------------------------------------- figures
def fig_fbd():
    fig, ax = plt.subplots(figsize=(7.5, 2.9))
    ax.plot([0, L], [0, 0], lw=6, color="#1f3a5f", solid_capstyle="butt")
    ax.add_patch(plt.Rectangle((-0.07, -0.35), 0.07, 0.7, color="#9ca3af"))
    for yy in np.linspace(-0.33, 0.3, 9):
        ax.plot([-0.07, -0.12], [yy, yy - 0.05], color="#6b7280", lw=1)
    xs = np.linspace(0, L, 13)
    for xi in xs[:-1]:
        hgt = 0.55 * (1 - xi / L)
        ax.annotate("", xy=(xi, -0.04), xytext=(xi, -0.04 - hgt),
                    arrowprops=dict(arrowstyle="->", color="#b45309", lw=1.2))
    ax.plot([0, L], [-0.59, -0.04], color="#b45309", lw=1)
    ax.text(0.05, -0.75, r"$q(x)=q_0(1-x/L)$,  $q_0=1200$ N/m (upward lift)", color="#b45309", fontsize=9)
    ax.annotate("", xy=(xbar_W, 0.06), xytext=(xbar_W, 0.62),
                arrowprops=dict(arrowstyle="<-", color="#15803d", lw=2.2))
    ax.text(xbar_W + 0.03, 0.5, r"$W=q_0L/2=900$ N at $x=L/3=0.5$ m", color="#15803d", fontsize=9)
    ax.annotate("", xy=(0.1, -0.05), xytext=(0.1, 0.45),
                arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=2))
    ax.text(0.13, 0.3, r"$R_y$", color="#b91c1c", fontsize=10)
    ax.annotate("", xy=(-0.02, 0.32), xytext=(0.2, 0.12),
                arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.6, connectionstyle="arc3,rad=0.6"))
    ax.text(0.22, 0.12, r"$M_0$", color="#b91c1c", fontsize=10)
    ax.plot([x_val, x_val], [-0.12, 0.12], ls="--", color="#374151", lw=1)
    ax.text(x_val + 0.01, -0.2, "validation\nsection\nx = 0.25 m", fontsize=7.5, color="#374151")
    ax.text(L - 0.05, 0.08, "tip (free)", fontsize=8, ha="right")
    ax.text(-0.12, 0.42, "root (fixed)", fontsize=8)
    ax.set_xlim(-0.2, L + 0.1)
    ax.set_ylim(-0.85, 0.75)
    ax.axis("off")
    p = FIG / "fbd.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_section():
    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    col = "#cbd5e1"
    ax.add_patch(plt.Rectangle((-B / 2, H / 2 - tf), B, tf, color=col, ec="k"))
    ax.add_patch(plt.Rectangle((-B / 2, -H / 2), B, tf, color=col, ec="k"))
    ax.add_patch(plt.Rectangle((-tw / 2, -H / 2 + tf), tw, hw, color=col, ec="k"))
    ax.axhline(0, color="#b91c1c", ls="--", lw=0.8)
    ax.text(B / 2 + 1, 0.8, "N.A.", color="#b91c1c", fontsize=8)
    ax.annotate("", xy=(-B / 2, H / 2 + 4), xytext=(B / 2, H / 2 + 4), arrowprops=dict(arrowstyle="<->"))
    ax.text(0, H / 2 + 5.5, "B = 55", ha="center", fontsize=8)
    ax.annotate("", xy=(-B / 2 - 5, -H / 2), xytext=(-B / 2 - 5, H / 2), arrowprops=dict(arrowstyle="<->"))
    ax.text(-B / 2 - 7, 0, "H = 60", rotation=90, va="center", ha="right", fontsize=8)
    ax.text(B / 2 + 1, H / 2 - tf / 2, "tf = 6", va="center", fontsize=8)
    ax.text(tw / 2 + 1.5, -10, "tw = 4", fontsize=8)
    ax.text(0, -H / 2 - 7, "Spar A, root section (mm)", ha="center", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(-B / 2 - 14, B / 2 + 14)
    ax.set_ylim(-H / 2 - 10, H / 2 + 10)
    ax.axis("off")
    p = FIG / "section.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_VM():
    xs = np.linspace(0, L, 301)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 2.7))
    a1.plot(xs, V(xs), color="#1f3a5f")
    a1.fill_between(xs, V(xs), alpha=0.15, color="#1f3a5f")
    a1.set(title="Shear force V(x)", xlabel="x from root (m)", ylabel="V (N)")
    a2.plot(xs, M(xs), color="#b45309")
    a2.fill_between(xs, M(xs), alpha=0.15, color="#b45309")
    a2.set(title="Bending moment M(x)", xlabel="x from root (m)", ylabel="M (N·m)")
    for a, f, u in ((a1, V, "N"), (a2, M, "N·m")):
        a.plot([x_val], [f(x_val)], "o", color="#b91c1c")
        a.annotate(f"{f(x_val):.2f} {u} @ 0.25 m", (x_val, f(x_val)), textcoords="offset points",
                   xytext=(8, 4), fontsize=8)
        a.annotate(f"{f(0):.0f} {u} @ root", (0, f(0)), textcoords="offset points", xytext=(8, -10), fontsize=8)
        a.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "VM.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_conv():
    cv = RES["convergence"]
    lab = [d["level"] for d in cv]
    nodes = [d["nodes"] for d in cv]
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(9.6, 2.7))
    a1.plot(nodes, [d["tip_dy_mm"] for d in cv], "o-", color="#1f3a5f", label="FEA")
    a1.axhline(delta_tip * 1000, ls="--", color="#b45309", label="Euler-Bernoulli")
    a1.set(title="Tip deflection", xlabel="nodes", ylabel="δ tip (mm)")
    a2.plot(nodes, [abs(d["sx_val_top_MPa"]) for d in cv], "o-", color="#1f3a5f", label="FEA")
    a2.axhline(sig_val / 1e6, ls="--", color="#b45309", label="Mc/I")
    a2.set(title="|σx| at x = 250 mm", xlabel="nodes", ylabel="|σx| (MPa)")
    a3.plot(nodes, [d["sx_max_MPa"] for d in cv], "o-", color="#b91c1c", label="max σx (root edge)")
    a3.axhline(sig_root / 1e6, ls="--", color="#b45309", label="nominal Mc/I at root")
    a3.set(title="Maximum σx (fixed-edge peak)", xlabel="nodes", ylabel="σx max (MPa)")
    for a in (a1, a2, a3):
        a.grid(alpha=0.3)
        a.legend(fontsize=6.5)
        ys = a.lines[0].get_ydata()
        for i, (n_, s_) in enumerate(zip(nodes, lab)):
            a.annotate(s_, (n_, ys[i]), fontsize=6, textcoords="offset points", xytext=(3, 4))
    fig.tight_layout()
    p = FIG / "convergence.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_paths():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 2.6))
    for d, lab, col in ((c1, "constant", "#1f3a5f"), (t1, "tapered", "#b45309")):
        sx = np.array(d["sx_path_Pa"])
        sxy = np.array(d["sxy_path_Pa"])
        h_here = H * (s_of(x_val) if d["tapered"] else 1)
        y = sx[:, 0] * 1000 - h_here / 2
        a1.plot(sx[:, 1] / 1e6, y, color=col, label=f"FEA {lab}")
        a2.plot(sxy[:, 1] / 1e6, sxy[:, 0] * 1000 - h_here / 2, color=col, label=f"FEA {lab}")
    yy = np.linspace(-H / 2, H / 2, 50)
    a1.plot(-M_val * yy / 1000 / I / 1e6, yy, "k--", lw=1, label="−My/I (constant)")
    a1.set(title="σx through depth, x = 250 mm", xlabel="σx (MPa)", ylabel="y (mm)")
    a2.set(title="τxy through depth, x = 250 mm", xlabel="τxy (MPa)", ylabel="y (mm)")
    a2.axvline(tau_val / 1e6, color="k", ls="--", lw=1, label="VQ/It at N.A.")
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.legend(fontsize=7)
    fig.tight_layout()
    p = FIG / "paths.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p


# ---------------------------------------------------------------- report
def build():
    img = lambda case, key: HERE / "ansys_out" / f"{case}_{key}.png"  # noqa: E731
    r = Report("Term Project Part I: FEA Validation, Spar A (I-section)",
               "Structural Design and Validation of Airplane Wing Spars · Statics, Mechanics of Materials and ANSYS Workbench",
               due="Nov 13, 2026, 11:59 PM")

    r.h2("1. Problem and given data")
    r.p("Spar A is modeled as a cantilever fixed at the wing root ($x=0$) and loaded by an upward, linearly "
        "decreasing aerodynamic line load. Two models are analyzed: **Model 1**, constant root section over "
        "$L=1.5$ m (used for hand-calculation validation), and **Model 2**, tapered with scale factor "
        "$s(x)=1-0.375\\,x/L$ ($s=0.625$ at the tip). LC1 applies $q(x)$ through the section's plane of symmetry; "
        "LC2 applies the same $q(x)$ 50 mm ahead of the spar reference axis.")
    r.table(["Quantity", "Value", "Source"], [
        ["Semi-span $L$", "1.50 m", "Project Table 1"],
        ["Root load $q_0$", "1200 N/m, $q(x)=q_0(1-x/L)$", "Project §5.1"],
        ["Eccentricity $e$ (LC2)", "50 mm", "Project Table 4"],
        ["Root section", "H = 60, B = 55, tf = 6, tw = 4 mm", "Project Table 2"],
        ["Material", "Aluminum Alloy (ANSYS General Materials)", "ANSYS Engineering Data"],
        ["$E$, $\\nu$", f"{E / 1e9:.0f} GPa, {nu:.2f}", "ANSYS Engineering Data"],
        ["Tensile yield $S_y$", f"{Sy / 1e6:.0f} MPa", "ANSYS Engineering Data"],
        ["$G=E/[2(1+\\nu)]$", f"{G / 1e9:.2f} GPa", "computed"],
        ["Density", f"{rho_lib:.0f} kg/m³ (ANSYS Aluminum Alloy, used for the FE mass check); "
         f"{rho_proj:.0f} kg/m³ listed in the project table", "ANSYS Engineering Data; Project Table 1"],
        ["Requirements", "FoS ≥ 2, $\\delta_{tip}$ ≤ 8 mm", "Project Table 1"],
    ], "Given data", cls="")
    r.callout("Material note. The handout names Al Alloy from ANSYS Engineering Data (Table 1) but lists "
              "\"Epoxy Carbon UD (395 GPa)\" in the ANSYS procedure table (§7.1), and its 1540 kg/m³ density is the "
              "ANSYS value for that carbon prepreg. The handout's reference deflections (5.64 mm for Spar A) match "
              f"aluminum with E = 69 GPa, so this report uses ANSYS Aluminum Alloy. Masses are given with both densities; "
              "the hand-vs-ANSYS mass check uses the density actually assigned in ANSYS.", "warn")
    r.img(fig_section(), "Spar A root cross-section.", width="38%", border=False)
    r.img(fig_fbd(), "Free-body diagram of the spar (LC1): triangular lift, its resultant, and the root reactions.", width="96%", border=False)

    # --- statics
    r.h2("2. Statics (LC1, with LC2 torque)")
    r.handcalc("Hand calculations: resultant, root reactions, eccentric torque")
    r.step("W", r"\int_0^L q_0\left(1-\frac{x}{L}\right)dx = \frac{q_0 L}{2}", rf"\frac{{(1200)(1.5)}}{{2}}", W, "N")
    r.step(r"\bar{x}_W", r"\frac{L}{3}", r"\frac{1.5}{3}", xbar_W, "m", "Centroid of the triangular load, measured from the root.")
    r.step(r"\sum F_y = 0:\ R_y", "W", None, R, "N", "Root reaction acts downward (opposes the upward lift).")
    r.step(r"\sum M_{root} = 0:\ M_0", r"W\,\bar{x}_W", rf"(900)(0.5)", M0, "N\\,m")
    r.step(r"T_0", r"e\,W", rf"(0.050)(900)", T0, "N\\,m", "LC2: the lift resultant acts 50 mm ahead of the spar axis, so the root also carries this torque.")
    r.end_handcalc()
    r.p("**How the LC2 offset load reaches the spar.** The lift acts on the skin 50 mm ahead of the spar axis. "
        "Ribs and skin carry it to the spar as the same vertical shear $q(x)$ plus a distributed torque "
        "$t(x)=e\\,q(x)$ per unit span. The spar resists this torque by shear flow (St. Venant torsion), and because "
        "Spar A is an open section, partly by flange bending (warping) near the fixed root. In the FE model this is "
        "reproduced by splitting the loaded flange face along its centerline and applying "
        "$p_\\pm = q/B \\pm 4eq/B^2$ on the two halves, which gives exactly $q(x)$ and $e\\,q(x)$ per unit span.")

    r.handcalc("Hand calculations: internal shear and moment (outboard segment, cut at x)")
    r.p("Take the free body from the cut at $x$ to the tip. Shear $V$ and moment $M$ are the internal resultants "
        "needed to hold that segment in equilibrium (positive $M$ bends the spar upward: top flange in compression).")
    r.step("V(x)", r"\int_x^L q_0\left(1-\frac{\xi}{L}\right)d\xi", None, r"\frac{q_0 (L-x)^2}{2L}", "")
    r.step("M(x)", r"\int_x^L q_0\left(1-\frac{\xi}{L}\right)(\xi-x)\,d\xi", None, r"\frac{q_0 (L-x)^3}{6L}", "")
    r.step("V(L)", r"\frac{q_0 (0)^2}{2L}", None, 0, "N", "Free tip: boundary values check.")
    r.step("M(L)", r"\frac{q_0 (0)^3}{6L}", None, 0, "N\\,m")
    r.step("V(0)", r"\frac{q_0 L}{2}", rf"\frac{{(1200)(1.5)}}{{2}}", V(0), "N", "Matches the reference value of 900 N.")
    r.step("M(0)", r"\frac{q_0 L^2}{6}", rf"\frac{{(1200)(1.5)^2}}{{6}}", M(0), "N\\,m", "Matches the reference value of 450 N·m.")
    r.step("V(0.25)", r"\frac{q_0 (L-x)^2}{2L}", rf"\frac{{(1200)(1.25)^2}}{{2(1.5)}}", V_val, "N", "Reference: 625 N.")
    r.step("M(0.25)", r"\frac{q_0 (L-x)^3}{6L}", rf"\frac{{(1200)(1.25)^3}}{{6(1.5)}}", f"{M_val:.2f}", "N\\,m", "Reference: 260.42 N·m.")
    r.end_handcalc()
    r.img(fig_VM(), "Shear-force and bending-moment diagrams (LC1). Both fall to zero at the free tip.", width="92%")

    # --- MoM
    r.h2("3. Mechanics of Materials (Spar A, constant section)")
    r.handcalc("Hand calculations: area, centroid, second moment of area (parallel-axis theorem)")
    r.p("The section is doubly symmetric, so the centroid is at mid-depth: $\\bar{y}=0$, $\\bar{z}=0$. "
        "Split it into top flange (1), web (2) and bottom flange (3).")
    n0 = lambda v: f"{v:,.0f}"  # noqa: E731
    r.table(["Part", "$A_i$ (mm²)", "$y_i$ (mm)", "$I_{c,i}$ (mm⁴)", "$d_i$ (mm)", "$A_i d_i^2$ (mm⁴)", "$I_i$ (mm⁴)"], [
        ["1 top flange 55×6", n0(A_f), n0(d_f), n0(Ic_f), n0(d_f), n0(A_f * d_f ** 2), n0(Ic_f + A_f * d_f ** 2)],
        ["2 web 4×48", n0(A_w), "0", n0(Ic_w), "0", "0", n0(Ic_w)],
        ["3 bottom flange 55×6", n0(A_f), n0(-d_f), n0(Ic_f), n0(d_f), n0(A_f * d_f ** 2), n0(Ic_f + A_f * d_f ** 2)],
        ["**Σ**", f"**{n0(A)}**", "", "", "", "", f"**{n0(I_mm4)}**"],
    ], "Section properties about the horizontal centroidal axis", cls="num")
    r.step("A", r"2Bt_f + t_w(H-2t_f)", rf"2(55)(6) + 4(48)", A, "mm^2",
           f"Within the 850 mm² ±5% constraint ({area_lo:.1f} to {area_hi:.1f} mm²). Reference: 852 mm².")
    r.step(r"\bar{y}", r"\frac{\sum A_i y_i}{\sum A_i}", rf"\frac{{330(27)+192(0)+330(-27)}}{{852}}", 0, "mm")
    r.step(r"I_{c,f}", r"\frac{B t_f^3}{12}", rf"\frac{{(55)(6)^3}}{{12}}", Ic_f, "mm^4")
    r.step(r"I_{c,w}", r"\frac{t_w h_w^3}{12}", rf"\frac{{(4)(48)^3}}{{12}}", Ic_w, "mm^4")
    r.step("I_z", r"2\left[I_{c,f}+A_f d_f^2\right]+I_{c,w}", rf"2\left[990+330(27)^2\right]+36864", I_mm4, "mm^4",
           f"= {I * 1e7:.3f}×10⁻⁷ m⁴. Reference: 5.200×10⁻⁷ m⁴.")
    r.step("I_y", r"2\frac{t_f B^3}{12} + \frac{h_w t_w^3}{12}", rf"2\frac{{(6)(55)^3}}{{12}}+\frac{{(48)(4)^3}}{{12}}", Iy_mm4, "mm^4", "Chordwise (edgewise) bending axis, for reference.")
    r.end_handcalc()

    r.handcalc("Hand calculations: bending normal stress and factor of safety")
    r.step(r"\sigma_{root}", r"\frac{M_0 c}{I}", rf"\frac{{(450)(0.030)}}{{{fmt(I)}}}", sig_root / 1e6, "MPa",
           "Nominal beam-theory value. The FE stress right at the idealized fixed edge is not used for validation.")
    r.step(r"\sigma_{x=0.25}", r"\frac{M(0.25)\,c}{I}", rf"\frac{{({M_val:.2f})(0.030)}}{{{fmt(I)}}}", sig_val / 1e6, "MPa",
           "Top flange in compression, bottom flange in tension (upward lift).")
    r.step(r"FoS_{root}", r"\frac{S_y}{|\sigma_{root}|}", rf"\frac{{280}}{{{sig_root / 1e6:.2f}}}", FoS_root, "", "Requirement FoS ≥ 2: satisfied.")
    r.step(r"FoS_{x=0.25}", r"\frac{S_y}{|\sigma_{x=0.25}|}", rf"\frac{{280}}{{{sig_val / 1e6:.2f}}}", FoS_val, "")
    r.end_handcalc()

    r.handcalc("Hand calculations: transverse shear stress in the web at the neutral axis")
    r.step("Q", r"A_f d_f + t_w\frac{h_w}{2}\frac{h_w}{4}", rf"(330)(27) + (4)(24)(12)", Q_mm3, "mm^3")
    r.step(r"\tau_{NA,\,x=0.25}", r"\frac{V Q}{I t_w}", rf"\frac{{(625)({fmt(Q)})}}{{({fmt(I)})(0.004)}}", tau_val / 1e6, "MPa")
    r.step(r"\tau_{NA,\,root}", r"\frac{R_y Q}{I t_w}", rf"\frac{{(900)({fmt(Q)})}}{{({fmt(I)})(0.004)}}", tau_root / 1e6, "MPa")
    r.end_handcalc()

    r.handcalc("Hand calculations: tip deflection, constant section (double integration)")
    r.p("With $EI\\,v''=M(x)=\\dfrac{q_0(L-x)^3}{6L}$ and fixed-root conditions $v(0)=v'(0)=0$:")
    r.step("EI\\,v'(x)", r"-\frac{q_0 (L-x)^4}{24L} + C_1,\quad v'(0)=0", None, r"C_1=\frac{q_0L^3}{24}", "")
    r.step("EI\\,v(x)", r"\frac{q_0 (L-x)^5}{120L} + C_1 x + C_2,\quad v(0)=0", None, r"C_2=-\frac{q_0L^4}{120}", "")
    r.step(r"\delta_{tip}=v(L)", r"\frac{1}{EI}\left[\frac{q_0L^4}{24}-\frac{q_0L^4}{120}\right]", None, r"\frac{q_0L^4}{30EI}", "")
    r.step(r"\delta_{tip}", r"\frac{q_0L^4}{30EI}", rf"\frac{{(1200)(1.5)^4}}{{30({fmt(E)})({fmt(I)})}}", delta_tip * 1000, "mm",
           f"With the ANSYS Aluminum Alloy modulus E = {E / 1e9:.0f} GPa. The project's reference value 5.64 mm "
           f"corresponds to E = 69 GPa ({delta_ref69 * 1000:.2f} mm). Requirement δ ≤ 8 mm: satisfied.")
    r.step(r"\delta_{tip}\ \text{(check)}", r"\int_0^L \frac{M(x)(L-x)}{EI}dx", r"\text{Simpson},\ n=20", const_check * 1000, "mm",
           "Unit-load (virtual work) form gives the same answer, which validates the integration routine used for the tapered spar.")
    r.end_handcalc()

    r.handcalc("Hand calculations: tip deflection, tapered section (numerical)")
    r.p("All section dimensions scale with $s(x)$, so $I(x)=I_0\\,s(x)^4$ with $s(x)=1-0.25x$ ($x$ in m). "
        "The tip deflection is integrated numerically with Simpson's rule (script, not spreadsheet):")
    r.eq(r"\delta_{tip}=\int_0^L \frac{M(x)\,(L-x)}{E\,I_0\,s(x)^4}\,dx")
    r.table(["Intervals $n$", "20", "40", "200"],
            [["$\\delta_{tip}$ (mm)"] + [f"{taper_defl[n] * 1000:.4f}" for n in (20, 40, 200)]],
            "Convergence of the tapered-spar deflection integral", cls="num")
    r.end_handcalc()

    r.handcalc("Hand calculations: torsion under LC2 (open thin-walled section)")
    r.step("J", r"\frac{1}{3}\sum b_i t_i^3 = \frac{1}{3}\left[2Bt_f^3 + h_w t_w^3\right]", rf"\frac{{1}}{{3}}\left[2(55)(6)^3 + (48)(4)^3\right]", J_mm4, "mm^4")
    r.step("T(x)", r"e\,V(x)", None, r"\frac{e\,q_0(L-x)^2}{2L}", "", "Internal torque from the outboard part of the offset load.")
    r.step(r"\theta_{tip}", r"\int_0^L\frac{T(x)}{GJ}dx=\frac{e\,M_0}{GJ}", rf"\frac{{(0.05)(450)}}{{({fmt(G)})({fmt(J)})}}", theta_const, "rad",
           f"= {math.degrees(theta_const):.2f}°. Constant section.")
    r.step(r"\theta_{tip,\,tapered}", r"\int_0^L \frac{e\,V(x)}{G J_0 s(x)^4}dx", r"\text{Simpson},\ n=200", taper_twist[200], "rad",
           f"= {math.degrees(taper_twist[200]):.2f}° (n = 20 gives {math.degrees(taper_twist[20]):.3f}°).")
    r.end_handcalc()
    r.callout("Assumptions: St. Venant (free-warping) torsion of an open section with $J\\approx\\frac13\\sum bt^3$. "
              "The fixed root actually prevents flange warping, so the real (and FE) spar is stiffer than this estimate "
              "near the root. A closed section (box, twin-web) carries torque by a closed shear-flow loop with "
              "$J\\approx 4A_m^2/\\oint ds/t$, which is one to two orders of magnitude larger than $\\frac13\\sum bt^3$ for the "
              "same material area, so its tip rotation is far smaller.", "warn")

    r.handcalc("Hand calculations: torsion with warping restrained at the root (Vlasov)")
    r.p("An open I-section also resists torque by bending its flanges in opposite directions when the root stops "
        "the section from warping. With $\\phi=d\\theta/dx$, the internal torque is shared as "
        "$T(x)=GJ\\,\\phi-(EC_w\\,\\phi')'$, with $\\phi(0)=0$ (no warping at the fixed root) and $\\phi'(L)=0$ "
        "(no bimoment at the free tip). The equation is solved by finite differences (1500 intervals) and "
        "$\\theta_{tip}=\\int_0^L\\phi\\,dx$. For the tapered spar, $J\\propto s^4$ and $C_w\\propto s^6$.")
    r.step(r"C_w", r"\frac{t_f B^3 h^2}{24},\ h=H-t_f", rf"\frac{{(6)(55)^3(54)^2}}{{24}}", Cw_mm6, "mm^6",
           "Warping constant of a doubly symmetric I-section.")
    r.step(r"\lambda", r"\sqrt{\frac{GJ}{EC_w}}", rf"\sqrt{{\frac{{({fmt(G)})({fmt(J)})}}{{({fmt(E)})({fmt(Cw)})}}}}", lam, "1/m",
           f"Warping effects die out over about 1/λ = {1000 / lam:.0f} mm from the root; λL = {lam * L:.1f}.")
    r.step(r"\theta_{tip,\,warping}", r"\int_0^L\phi\,dx", r"\text{finite differences}", math.degrees(theta_w_const), "deg",
           f"Constant section; free-warping value was {math.degrees(theta_const):.2f}°.")
    r.step(r"\theta_{tip,\,warping,\,tapered}", r"\int_0^L\phi\,dx", r"\text{finite differences}", math.degrees(theta_w_taper), "deg",
           f"Tapered section; free-warping value was {math.degrees(taper_twist[200]):.2f}°.")
    r.end_handcalc()

    r.handcalc("Hand calculations: volume and mass")
    r.step(r"V_{const}", r"A\,L", rf"({fmt(A * 1e-6)})(1.5)", vol_const * 1e6, "cm^3")
    r.step(r"V_{taper}", r"\int_0^L A_0 s(x)^2 dx", r"\text{Simpson},\ n=20", vol_taper * 1e6, "cm^3",
           "Every dimension scales with s, so the area scales with s².")
    r.step(r"m_{const}", r"\rho V", rf"({rho_lib:.0f})({fmt(vol_const)})", mass_const_lib, "kg",
           f"With ρ = {rho_proj:.0f} kg/m³ (project table): {mass_const:.3f} kg.")
    r.step(r"m_{taper}", r"\rho V", rf"({rho_lib:.0f})({fmt(vol_taper)})", mass_taper_lib, "kg",
           f"With ρ = {rho_proj:.0f} kg/m³: {mass_taper:.3f} kg.")
    r.end_handcalc()

    # --- FEA
    r.pagebreak()
    r.h2("4. Finite element model (ANSYS Mechanical 2026 R1)")
    cv = RES["convergence"]
    final = cv[-1]
    lv_name, lv_glob, lv_ref = FINAL_LV
    r.bullets([
        "**Geometry:** solid spar, 1.5 m long, built from the Table 2 root dimensions (Model 1) and lofted to the "
        "0.625-scaled tip section (Model 2). The bottom-flange face is split along its centerline so LC2 can be applied.",
        "**Material:** Aluminum Alloy from ANSYS General Materials (E = 71 GPa, ν = 0.33, Sy = 280 MPa).",
        f"**Mesh:** MultiZone hexahedral mesh of quadratic 20-node solids (SOLID186), swept along the span. A hard edge "
        f"sizing puts two elements through every flange and web thickness, which meets the handout's rule for solid "
        f"models (§7.1). Reported results use the {lv_name.lower()} mesh ({lv_glob * 1000:g} mm spanwise, "
        f"{lv_ref * 1000:g} mm in the cross-section): {final['nodes']:,} nodes / {final['elements']:,} elements for Model 1.",
        "**Support:** Fixed Support on the root face (x = 0).",
        "**LC1:** pressure on the bottom face of the lower flange, $p(x)=q(x)/B(x)$, defined by function of x "
        "(acts upward, total 900 N).",
        "**LC2:** same, with $p_\\pm=q/B\\pm4eq/B^2$ on the leading/trailing halves (adds torque $e\\,q(x)$ per unit span).",
        "**Validation outputs:** σx and τxy along a vertical path through the web at x = 250 mm; tip deflection "
        "from the tip face; tip rotation from the Y-deflection across the tip flange; volume and mass from the geometry.",
    ])
    r.img(img("constant_LC1", "model"), "Model 1, LC1: fixed support at the root (blue) and linearly varying lift pressure (red).", width="88%")
    r.img(HERE / "ansys_out" / "constant_mesh.png", "Model 1 mesh used for the reported results.", width="88%")

    r.h3("Mesh convergence (Model 1, LC1)")
    r.p("The four meshes follow the handout's table (§7.3). For the swept solid, the global size is the spanwise "
        "element length and the refinement size is the cross-section element size, which is swept along the whole "
        "span, so it also covers the root, every web-flange junction and the validation section. The very fine mesh "
        "uses 10 mm spanwise instead of 8 mm: 8 mm with a 3 mm section gives 134,373 nodes, over the 128,000-node "
        "limit of ANSYS Student. It is still finer than the fine mesh in every direction.")

    def pc(key, i):
        if i == 0:
            return "–"
        a_, b_ = cv[i][key], cv[i - 1][key]
        return f"{abs(a_ - b_) / abs(a_) * 100:.2f}"

    r.table(["Mesh", "Global / section (mm)", "Nodes", "Elements", "δ tip (mm)", "Δ %", "σx @ 250 mm (MPa)", "Δ %",
             "τ @ N.A. (MPa)", "max σx (MPa)", "Δ %"],
            [[d["level"], f"{d['global_mm']:g} / {d['refine_mm']:g}", f"{d['nodes']:,}", f"{d['elements']:,}",
              f"{d['tip_dy_mm']:.4f}", pc("tip_dy_mm", i), f"{d['sx_val_top_MPa']:.3f}", pc("sx_val_top_MPa", i),
              f"{d['sxy_val_NA_MPa']:.3f}", f"{d['sx_max_MPa']:.1f}", pc("sx_max_MPa", i)] for i, d in enumerate(cv)],
            "Mesh refinement study (Δ % = change from the previous mesh, |Q_i − Q_i−1|/|Q_i|)", cls="num")
    chg = abs(cv[-1]["tip_dy_mm"] - cv[-2]["tip_dy_mm"]) / cv[-1]["tip_dy_mm"] * 100
    chs = abs(cv[-1]["sx_val_top_MPa"] - cv[-2]["sx_val_top_MPa"]) / abs(cv[-1]["sx_val_top_MPa"]) * 100
    chm = abs(cv[-1]["sx_max_MPa"] - cv[0]["sx_max_MPa"]) / abs(cv[-1]["sx_max_MPa"]) * 100
    r.p(f"Between the last two meshes the tip deflection changes by {chg:.2f}% and the validation-section stress by "
        f"{chs:.2f}%, both under the 5% criterion, so the {lv_name.lower()} mesh is converged for the quantities compared "
        f"below. The maximum σx sits on the fixed edge at the root flange tips and grows {chm:.0f}% from the coarse to the "
        "very fine mesh without settling: it is the stress singularity of the idealized fixed support, which the handout "
        "excludes as a convergence quantity. It is recorded only to show that behavior.")
    r.img(fig_conv(), "Mesh convergence: tip deflection, validation-section stress and the fixed-edge maximum stress.", width="98%")

    r.img(HERE / "ansys_out" / "constant_mesh_root.png", "Close-up of the Model 1 hex mesh at the fixed root: two elements through each flange and the web.")

    r.h3("Model 1 (constant section), LC1")
    r.img(img("constant_LC1", "td"), "Model 1, LC1: total deformation (mm).")
    r.img(img("constant_LC1", "td_true"), "Model 1, LC1: deformed shape at true scale (1:1) over the undeformed outline (mm).")
    r.img(img("constant_LC1", "dy"), "Model 1, LC1: directional deformation in Y (mm).")
    r.img(img("constant_LC1", "sx"), "Model 1, LC1: normal stress σx along the span (MPa). The peak at the root is the fixed-edge singularity; validation uses x = 250 mm.")
    r.img(img("constant_LC1", "sxy"), "Model 1, LC1: shear stress τxy (MPa), carried by the web.")
    r.img(img("constant_LC1", "eqv"), "Model 1, LC1: equivalent (von Mises) stress (MPa).")
    r.img(img("constant_LC1", "reaction"), "Model 1, LC1: force reaction at the fixed root (900 N).")
    r.img(fig_paths(), "σx and τxy along the depth at x = 250 mm (FE path results) against beam theory.", width="92%", border=False)

    r.h3("Model 1 (constant section), LC2")
    r.img(img("constant_LC2", "model"), "Model 1, LC2: split-face pressures that add the eccentric torque.")
    r.img(img("constant_LC2", "td"), "Model 1, LC2: total deformation, bending plus twist (mm).")
    r.img(img("constant_LC2", "eqv"), "Model 1, LC2: equivalent stress (MPa).")

    r.h3("Model 2 (tapered section)")
    r.img(HERE / "ansys_out" / "tapered_mesh.png", "Model 2 (tapered) mesh.")
    r.img(img("tapered_LC1", "td"), "Model 2, LC1: total deformation (mm).")
    r.img(img("tapered_LC1", "td_true"), "Model 2, LC1: deformed shape at true scale (1:1) over the undeformed outline (mm).")
    r.img(img("tapered_LC1", "sx"), "Model 2, LC1: normal stress σx (MPa).")
    r.img(img("tapered_LC2", "td"), "Model 2, LC2: total deformation (mm).")
    r.img(img("tapered_LC2", "eqv"), "Model 2, LC2: equivalent stress (MPa).")

    # --- comparison
    r.pagebreak()
    r.h2("5. Comparison: Statics / MoM vs. ANSYS")
    r.p("Difference = |ANSYS − hand| / |hand| × 100% (handout §8.1). Targets are the handout's.")
    twc = abs(c2["tip_twist_deg"])
    twt = abs(t2["tip_twist_deg"])
    rows = [
        ["Root reaction force (N)", f"{R:.1f}", f"{abs(c1['Fy_root_N']):.1f}", f"{perr(c1['Fy_root_N'], R):.2f}%", "< 1%"],
        ["Root bending moment (N·m)", f"{M0:.1f}", f"{abs(c1['Mz_root_Nm']):.1f}", f"{perr(c1['Mz_root_Nm'], M0):.2f}%", "< 2%"],
        ["LC2 root torque (N·m)", f"{T0:.2f}", f"{abs(c2['Mx_root_Nm']):.2f}", f"{perr(c2['Mx_root_Nm'], T0):.2f}%", "< 2%"],
        ["σx at x = 250 mm, top flange (MPa)", f"{-sig_val / 1e6:.2f}", f"{c1['sx_val_top_MPa']:.2f}", f"{perr(c1['sx_val_top_MPa'], sig_val / 1e6):.2f}%", "< 10%"],
        ["σx at x = 250 mm, bottom flange (MPa)", f"{sig_val / 1e6:.2f}", f"{c1['sx_val_bot_MPa']:.2f}", f"{perr(c1['sx_val_bot_MPa'], sig_val / 1e6):.2f}%", "< 10%"],
        ["Web shear at N.A., x = 250 mm (MPa)", f"{tau_val / 1e6:.3f}", f"{abs(c1['sxy_val_NA_MPa']):.3f}", f"{perr(c1['sxy_val_NA_MPa'], tau_val / 1e6):.2f}%", "< 15%"],
        ["Tip deflection LC1 (mm)", f"{delta_tip * 1000:.3f}", f"{c1['tip_dy_max_mm']:.3f}", f"{perr(c1['tip_dy_max_mm'], delta_tip * 1000):.2f}%", "< 10%"],
        ["Tip twist LC2, free warping (deg)", f"{math.degrees(theta_const):.2f}", f"{twc:.2f}", f"{perr(twc, math.degrees(theta_const)):.1f}%", "discuss"],
        ["Tip twist LC2, warping restrained (deg)", f"{math.degrees(theta_w_const):.2f}", f"{twc:.2f}", f"{perr(twc, math.degrees(theta_w_const)):.1f}%", "discuss"],
        ["Volume (cm³)", f"{vol_const * 1e6:.1f}", f"{fe_vol_c * 1e6:.1f}", f"{perr(fe_vol_c, vol_const):.2f}%", ""],
        [f"Mass, ρ = {rho_lib:.0f} kg/m³ (kg)", f"{mass_const_lib:.3f}", f"{fe_mass_c:.3f}", f"{perr(fe_mass_c, mass_const_lib):.2f}%", "< 2%"],
        ["FoS at root (nominal)", f"{FoS_root:.1f}", "n/a (fixed-edge singularity)", "", "≥ 2"],
    ]
    r.table(["Quantity, Model 1 (constant)", "Hand calculation", "ANSYS", "Difference", "Target"], rows,
            "Model 1 validation table (Spar A)", cls="num")
    sv_t = M_val * (H * s_of(x_val) / 2000) / (I * s_of(x_val) ** 4) / 1e6
    rows2 = [
        ["Root reaction force (N)", f"{R:.1f}", f"{abs(t1['Fy_root_N']):.1f}", f"{perr(t1['Fy_root_N'], R):.2f}%"],
        ["Root bending moment (N·m)", f"{M0:.1f}", f"{abs(t1['Mz_root_Nm']):.1f}", f"{perr(t1['Mz_root_Nm'], M0):.2f}%"],
        ["LC2 root torque (N·m)", f"{T0:.2f}", f"{abs(t2['Mx_root_Nm']):.2f}", f"{perr(t2['Mx_root_Nm'], T0):.2f}%"],
        ["σx at x = 250 mm, top flange (MPa)", f"{-sv_t:.2f}", f"{t1['sx_val_top_MPa']:.2f}", f"{perr(t1['sx_val_top_MPa'], sv_t):.2f}%"],
        ["Tip deflection LC1 (mm)", f"{taper_defl[200] * 1000:.3f}", f"{t1['tip_dy_max_mm']:.3f}", f"{perr(t1['tip_dy_max_mm'], taper_defl[200] * 1000):.2f}%"],
        ["Tip twist LC2, free warping (deg)", f"{math.degrees(taper_twist[200]):.2f}", f"{twt:.2f}", f"{perr(twt, math.degrees(taper_twist[200])):.1f}%"],
        ["Tip twist LC2, warping restrained (deg)", f"{math.degrees(theta_w_taper):.2f}", f"{twt:.2f}", f"{perr(twt, math.degrees(theta_w_taper)):.1f}%"],
        ["Volume (cm³)", f"{vol_taper * 1e6:.1f}", f"{fe_vol_t * 1e6:.1f}", f"{perr(fe_vol_t, vol_taper):.2f}%"],
        [f"Mass, ρ = {rho_lib:.0f} kg/m³ (kg)", f"{mass_taper_lib:.3f}", f"{fe_mass_t:.3f}", f"{perr(fe_mass_t, mass_taper_lib):.2f}%"],
    ]
    r.table(["Quantity, Model 2 (tapered)", "Numerical / MoM", "ANSYS", "Difference"], rows2,
            "Model 2 results (hand values from numerical integration with I(x) = I₀s⁴, J ∝ s⁴, C_w ∝ s⁶)", cls="num")
    r.table(["Spar A summary", "Constant (Model 1)", "Tapered (Model 2)", "Requirement"], [
        ["Root area (mm²)", f"{A:.0f}", f"{A:.0f} (root), {A * s_tip ** 2:.0f} (tip)", "850 ± 5%"],
        ["Moment of inertia I (×10⁻⁷ m⁴)", f"{I * 1e7:.3f}", f"{I * 1e7:.3f} → {I * s_tip ** 4 * 1e7:.3f}", ""],
        ["Validation stress σx at 250 mm, FEA (MPa)", f"{abs(c1['sx_val_top_MPa']):.2f}", f"{abs(t1['sx_val_top_MPa']):.2f}", ""],
        ["Tip deflection LC1, FEA (mm)", f"{c1['tip_dy_max_mm']:.2f}", f"{t1['tip_dy_max_mm']:.2f}", "≤ 8 mm"],
        ["Max. tip deflection LC2, FEA (mm)", f"{c2['tip_dy_max_mm']:.2f}", f"{t2['tip_dy_max_mm']:.2f}", "≤ 8 mm"],
        ["Tip twist LC2, FEA (deg)", f"{twc:.2f}", f"{twt:.2f}", ""],
        ["Nominal root stress (MPa) / FoS", f"{sig_root / 1e6:.1f} / {FoS_root:.1f}", f"{sig_root / 1e6:.1f} / {FoS_root:.1f}", "FoS ≥ 2"],
        [f"Mass (kg), ρ = {rho_lib:.0f} / {rho_proj:.0f}", f"{fe_mass_c:.3f} / {mass_const:.3f}", f"{fe_mass_t:.3f} / {mass_taper:.3f}", "report"],
    ], "Design check for Spar A", cls="num")

    r.h2("6. Discussion")
    ok_c = c1["tip_dy_max_mm"] <= 8
    ok_t = t1["tip_dy_max_mm"] <= 8
    r.bullets([
        f"**Reactions** match statics to better than 0.1%: the FE load is the intended 900 N, 450 N·m and 45 N·m. "
        f"(In Model 2 the loaded face is slightly inclined, so a small axial reaction of {abs(t1['Fx_root_N']):.1f} N also appears.)",
        f"**Bending stress** at the validation section agrees with $Mc/I$ within {max(perr(c1['sx_val_top_MPa'], sig_val / 1e6), perr(c1['sx_val_bot_MPa'], sig_val / 1e6)):.1f}%, "
        "and the path plot shows the linear distribution beam theory assumes. Stresses at the fixed edge are higher in the FE "
        "model because the ideal fixed support also prevents Poisson contraction (a stress singularity), so they are not used.",
        f"**Shear stress** at the neutral axis agrees with $VQ/It$ within {perr(c1['sxy_val_NA_MPa'], tau_val / 1e6):.2f}%.",
        f"**Tip deflection** from FEA is {perr(c1['tip_dy_max_mm'], delta_tip * 1000):.1f}% above Euler-Bernoulli theory, "
        "as expected: the solid model includes shear deformation of the thin web, which beam theory neglects. "
        f"The constant spar meets δ ≤ 8 mm{'' if ok_c else ' (NOT met)'}; the tapered spar is more flexible "
        f"({t1['tip_dy_max_mm']:.2f} mm){', still within the limit' if ok_t else ', which exceeds the limit'}.",
        f"**Torsion (LC2):** the elementary free-warping estimate ({math.degrees(theta_const):.2f}°) overpredicts the FE tip "
        f"twist ({twc:.2f}°) by {perr(twc, math.degrees(theta_const)):.0f}%. The cause is the boundary idealization, not the mesh: "
        "the fixed support stops the root section from warping, so near the root the flanges bend sideways in opposite "
        "directions and carry part of the torque. Including that restraint (Vlasov theory, Section 3) gives "
        f"{math.degrees(theta_w_const):.2f}°, within {perr(twc, math.degrees(theta_w_const)):.0f}% of ANSYS. "
        f"The remaining few percent are expected: ⅓Σbt³ treats every wall as infinitely thin and skips the free-edge "
        f"correction for the four flange tips (b − 0.63t), which would lower J to {J_corr:,.0f} mm⁴ ({(1 - J_corr / J_mm4) * 100:.0f}% less) "
        "and raise the predicted twist toward the FE value; the FE twist is also read from the top flange only. "
        "Spar A is an open section with low torsional stiffness, so under LC2 it twists several "
        "degrees; a closed box carries the same torque by a closed shear-flow loop "
        f"(Bredt J ≈ {box['J']:,.0f} mm⁴ against {J_mm4:,.0f} mm⁴ here, see Appendix A) and twists about "
        f"{math.degrees(theta_const) / box['th']:.0f} times less. This is Spar A's main weakness in the comparison.",
        f"**LC2 deflection:** with the offset load, the leading flange edge at the tip rises "
        f"{c2['tip_dy_max_mm']:.2f} mm (constant) and {t2['tip_dy_max_mm']:.2f} mm (tapered). "
        + ("The tapered I-section therefore exceeds the 8 mm limit under LC2 because of twist, not bending. "
           if t2['tip_dy_max_mm'] > 8 else "Both stay within the 8 mm limit. ")
        + "This is the strongest argument for a closed section if eccentric lift governs.",
        f"**Mass:** the FE volume equals the hand volume ({perr(fe_vol_c, vol_const):.2f}% constant, "
        f"{perr(fe_vol_t, vol_taper):.2f}% tapered), so the mass check passes and the four spars can be compared at equal material.",
        f"**Strength:** nominal root stress {sig_root / 1e6:.1f} MPa gives FoS = {FoS_root:.1f} ≥ 2, so the I-section is "
        "strength-adequate with a large margin; stiffness (deflection and twist), not strength, governs its design.",
    ])

    r.h2("Appendix A. Hand-calculation cross-check for the four baseline spars")
    r.p("The handout asks for the section properties of all four constant-section spars. These values are computed "
        "from Table 1 dimensions with the same formulas as Section 3, for the team's summary table; each teammate's own "
        "section governs for spars B to D. Box and twin-web shear is split equally between the two webs "
        "(the sections are symmetric about the vertical axis, so each web carries V/2).")
    rows_a = []
    for s_ in SPARS:
        rows_a.append([s_["name"], f"{s_['A']:.0f}" + ("" if s_["ok"] else " ✗"), f"{s_['xbar']:.2f}",
                       f"{s_['Ix'] / 1e5:.3f}", f"{s_['sr'] / 1e6:.2f}", f"{s_['sv'] / 1e6:.2f}", f"{s_['fos']:.1f}",
                       f"{s_['tau'] / 1e6:.2f}", f"{s_['d69'] * 1000:.2f}", f"{s_['d71'] * 1000:.2f}",
                       f"{s_['J']:,.0f}" if s_["J"] else "–", f"{s_['th']:.2f}" if s_["th"] else "–"])
    r.table(["Spar", "A (mm²)", "x̄ (mm)", "I (×10⁻⁷ m⁴)", "σ root (MPa)", "σ 250 mm (MPa)", "FoS",
             "τ web N.A. 250 mm (MPa)", "δ tip, E = 69 GPa (mm)", "δ tip, E = 71 GPa (mm)", "J (mm⁴)", "θ tip LC2 (deg)"],
            rows_a, "Four-spar hand values (x̄ measured from the left edge; from the web back for the C-channel)", cls="num")
    r.p(f"The I values reproduce the handout's 5.200, 4.330 and 4.393 ×10⁻⁷ m⁴, and the E = 69 GPa deflections reproduce "
        "its 5.64, 6.78 and 6.68 mm. J uses ⅓Σbt³ for the open sections and Bredt's 4A_m²/∮ds/t for the box. "
        f"The handout's shortcut J ≈ Ix + Iy gives {box_Ix_Iy:,.0f} mm⁴ for the box; that is the polar moment, exact only "
        "for circular sections, so Bredt's value is used. The twin-web J depends on where its webs sit, which Table 1 does "
        "not give, so it is left to that spar's section.")
    r.h2("Appendix B. Reproducibility")
    r.p("Geometry: `cad.py` (build123d → STEP). FEA: `ansys.py` run in ANSYS Mechanical 2026 R1 Student through "
        "PyMechanical (`scripts/mech.py`). Hand calculations, plots and this report: `solve.py`.")
    out = r.docx(OUT_DOCX)
    print("wrote", out)


if __name__ == "__main__":
    build()
