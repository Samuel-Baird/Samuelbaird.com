"""HW 8 figures that do not need ANSYS: geometry views and the hand (beam) model."""
import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle as CirclePatch, Rectangle, Arc  # noqa: E402

import hand as H  # noqa: E402

FIG = Path(__file__).parent / "figs"
FIG.mkdir(exist_ok=True)
FILL = "#dfe7f1"


def fig_geometry():
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 4.0), gridspec_kw={"width_ratios": [1.35, 1]})
    # side view in the YZ plane (Z to the right, Y up)
    ax = axs[0]
    th = np.linspace(0, math.pi / 2, 60)
    for r, ls in ((H.RO, "-"), (H.RI, "--")):
        for sgn in (1, -1):
            off = sgn * r
            # leg 1 (y = +-r), bend (radius 70 -+ r), leg 2 (z = 170 +- r)
            zs = [0, H.L_LEG] + list(H.L_LEG + (H.R_BEND - off) * np.sin(th)) + [H.SPAN - off, H.SPAN - off]
            ys = [off, off] + list(H.R_BEND - (H.R_BEND - off) * np.cos(th)) + [H.R_BEND, H.SPAN]
            ax.plot(zs, ys, ls, color="k" if ls == "-" else "0.45", lw=1.0 if ls == "-" else 0.7)
    ax.add_patch(Rectangle((0, -H.R_FO), H.T_F, 2 * H.R_FO, fc=FILL, ec="k", lw=1.1))
    ax.add_patch(Rectangle((H.SPAN - H.R_FO, H.SPAN - H.T_F), 2 * H.R_FO, H.T_F, fc=FILL, ec="k", lw=1.1))
    ax.plot([0, H.L_LEG], [0, 0], "-.", color="C0", lw=0.6)
    ax.plot(H.L_LEG + H.R_BEND * np.sin(th), H.R_BEND * (1 - np.cos(th)), "-.", color="C0", lw=0.6)
    ax.plot([H.SPAN, H.SPAN], [H.R_BEND, H.SPAN], "-.", color="C0", lw=0.6)
    # fixed faces
    ax.add_patch(Rectangle((-6, -H.R_FO), 6, 2 * H.R_FO, fc="white", ec="0.3", hatch="////", lw=0.6))
    ax.add_patch(Rectangle((H.SPAN - H.R_FO, H.SPAN), 2 * H.R_FO, 6, fc="white", ec="0.3", hatch="////", lw=0.6))
    ax.text(24, -42, "flange 1\nfixed face z = 0", fontsize=6.5, ha="left", va="center")
    ax.text(H.SPAN + 52, H.SPAN + 3, "flange 2\nfixed face y = 170", fontsize=6.5, ha="left", va="center")
    ax.annotate("", (0, -72), (H.L_LEG, -72), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(50, -82, "100", ha="center", fontsize=7)
    ax.annotate("", (0, -94), (H.SPAN, -94), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(85, -104, "170", ha="center", fontsize=7)
    ax.annotate("", (H.SPAN + 62, H.R_BEND), (H.SPAN + 62, H.SPAN), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(H.SPAN + 65, 120, "100", fontsize=7, va="center")
    ax.plot(H.L_LEG, H.R_BEND, "+", color="C0")
    ax.annotate("R70", (H.L_LEG + 49.5, H.R_BEND - 49.5), (H.L_LEG - 5, H.R_BEND + 4), fontsize=7, color="C0",
                arrowprops=dict(arrowstyle="->", lw=0.6, color="C0"))
    ax.text(35, 36, "Ø60 / Ø50 pipe", fontsize=7)
    ax.text(H.T_F + 2, 52, "20", fontsize=6.5)
    ax.annotate("", (-14, H.SPAN), (-14, 0), arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.annotate("", (40, -116), (0, -116), arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.text(-17, H.SPAN - 5, "Y", fontsize=8, ha="right")
    ax.text(43, -118, "Z", fontsize=8, va="center")
    ax.set_title("Side view (Y–Z plane)", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-30, 260)
    ax.set_ylim(-126, 190)
    ax.axis("off")
    # flange face
    ax = axs[1]
    ax.add_patch(CirclePatch((0, 0), H.R_FO, fc=FILL, ec="k", lw=1.1))
    ax.add_patch(CirclePatch((0, 0), H.RO, fc="none", ec="0.45", lw=0.7, ls="--"))
    ax.add_patch(CirclePatch((0, 0), H.R_FI, fc="white", ec="k", lw=1.0))
    for x, y in ((40, 0), (-40, 0), (0, 40), (0, -40)):
        ax.add_patch(CirclePatch((x, y), 5, fc="white", ec="k", lw=0.9))
    ax.add_patch(CirclePatch((0, 0), 40, fc="none", ec="C0", lw=0.5, ls="-."))
    ax.annotate("", (-50, -60), (50, -60), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(0, -68, "Ø100", ha="center", fontsize=7)
    ax.annotate("", (-40, 58), (40, 58), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(0, 61, "80 (bolt circle Ø80)", ha="center", fontsize=7)
    ax.text(0, 0, "Ø50", ha="center", va="center", fontsize=7)
    ax.text(40, 9, "4 × Ø10", fontsize=7, ha="center")
    ax.set_title("Flange (both ends), 20 mm thick", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-62, 62)
    ax.set_ylim(-76, 72)
    ax.axis("off")
    fig.text(0.5, 0.01, "Aluminum alloy; dimensions in mm (tutorial dimensions, second flange added at the free end)",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    p = FIG / "geometry.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_frame():
    """Bending moment along the pipe centreline for the three hand models."""
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for fr, lab, st in ((H.FR0, "Euler–Bernoulli", ":"), (H.FR1, "+ shear (Timoshenko)", "--"),
                        (H.FRK, f"+ bend flexibility k = {H.K_BEND:.2f}", "-")):
        P = fr["P"]
        ds = np.r_[0, np.cumsum(np.hypot(np.diff(P[:, 0]), np.diff(P[:, 1])))]
        ax.plot(ds, fr["m"] / 1e6, st, lw=1.3, label=lab)
    L1 = H.L_FREE
    L2 = L1 + H.R_BEND * math.pi / 2
    for x in (L1, L2):
        ax.axvline(x, color="0.6", lw=0.6)
    ax.text(L1 / 2, 0.98, "leg 1", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7)
    ax.text((L1 + L2) / 2, 0.98, "R70 bend", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7)
    ax.text(L2 + L1 / 2, 0.98, "leg 2", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7)
    ax.axhline(0, color="k", lw=0.5)
    ax.set(xlabel="distance along the centreline from flange 1 (mm)", ylabel="bending moment $M_x$ (kN·m)")
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 0.86), ncol=3)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = FIG / "frame_moment.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


if __name__ == "__main__":
    print(fig_geometry(), fig_frame())
