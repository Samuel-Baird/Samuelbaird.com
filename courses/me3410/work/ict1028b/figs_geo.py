"""Geometry/loading figure for problem 2 (drawn from the handout figure, in our own style)."""
import math

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402


def outline(r=20.0):
    pts = [(0, 0), (400, 0), (400, 100), (150 + r, 100)]
    pts += [(150 + r - r * math.sin(a), 100 + r - r * math.cos(a)) for a in np.linspace(0, math.pi / 2, 30)]
    pts += [(150, 200), (0, 200), (0, 0)]
    return np.array(pts)


def arrows(ax, xs, ys, dx, dy, color):
    for x, y in zip(xs, ys):
        ax.annotate("", (x, y), (x - dx, y - dy), arrowprops=dict(arrowstyle="->", lw=1.0, color=color))


def fig_geometry(path):
    o = outline()
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.fill(o[:, 0], o[:, 1], color="#e4e4e0", ec="k", lw=1.2)
    ax.add_patch(Circle((100, 50), 25, fc="white", ec="k", lw=1.0))
    ax.plot([70, 130], [50, 50], "k-.", lw=0.5)
    ax.plot([100, 100], [20, 80], "k-.", lw=0.5)
    ax.add_patch(Rectangle((-10, -9), 420, 9, fc="white", ec="0.3", hatch="////", lw=0.8))
    red, blue = "#c0392b", "#1f5fa8"
    arrows(ax, np.linspace(5, 145, 8), [201] * 8, 0, -22, red)
    ax.text(75, 228, "q = 50 MPa", color=red, ha="center", fontsize=8.5)
    arrows(ax, np.linspace(255, 395, 8), [101] * 8, 0, -22, red)
    ax.text(325, 128, "q = 25 MPa", color=red, ha="center", fontsize=8.5)
    arrows(ax, [-1] * 7, np.linspace(10, 190, 7), 18, 0, blue)
    ax.text(-22, 100, "p = 10 MPa", color=blue, rotation=90, va="center", ha="right", fontsize=8.5)
    arrows(ax, [401] * 4, np.linspace(12, 88, 4), -18, 0, blue)
    ax.text(424, 50, "p = 10 MPa", color=blue, rotation=90, va="center", ha="left", fontsize=8.5)
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.annotate("", (0, -22), (400, -22), **kw)
    ax.text(200, -34, "400", ha="center", fontsize=8)
    ax.annotate("", (0, 246), (150, 246), **kw)
    ax.text(75, 250, "150", ha="center", fontsize=8)
    ax.annotate("", (250, 146), (400, 146), **kw)
    ax.text(325, 150, "150 (loaded)", ha="center", fontsize=8)
    ax.annotate("", (-46, 0), (-46, 200), **kw)
    ax.text(-50, 150, "200", rotation=90, ha="right", va="center", fontsize=8)
    ax.annotate("", (446, 0), (446, 100), **kw)
    ax.text(450, 75, "100", rotation=90, va="center", fontsize=8)
    dim = dict(arrowprops=dict(arrowstyle="<->", lw=0.5, color="0.35"))
    ax.plot([0, 75], [50, 50], ":", lw=0.5, color="0.35")
    ax.annotate("", (40, 0), (40, 50), **dim)
    ax.text(44, 22, "50", fontsize=7, color="0.3")
    ax.plot([100, 100], [80, 116], ":", lw=0.5, color="0.35")
    ax.annotate("", (0, 112), (100, 112), **dim)
    ax.text(50, 116, "100", ha="center", fontsize=7, color="0.3")
    ax.text(100, 84, "Ø50", ha="center", fontsize=8)
    ax.annotate("R20", (155.9, 105.9), (185, 140), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.text(300, 40, "Concrete, E = 30 GPa, ν = 0.20\n500 mm long (out of plane)\nall dimensions in mm",
            ha="center", fontsize=7.5)
    ax.text(200, -14.5, "fixed base", ha="center", va="center", fontsize=7, bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_aspect("equal")
    ax.set_xlim(-75, 470)
    ax.set_ylim(-42, 262)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path
