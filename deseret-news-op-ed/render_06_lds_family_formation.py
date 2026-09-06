"""
Chart 06 - LDS family formation: two small multiples (currently married;
three or more children) for Latter-day Saints, all Christians and the
religiously unaffiliated, Pew RLS 2023-24 public-use microdata.

Every plotted number is read from data/oped_data.json at run time.
"""
from __future__ import annotations

import json
import math
import textwrap

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import dn_style as dn

STEM = "06_lds_family_formation"

GROUPS = ["Latter-day Saints", "All Christians", "Religiously unaffiliated"]


def pct_label(v: float) -> str:
    """Display rounding only (half up); the JSON keeps the precision."""
    return f"{math.floor(v + 0.5):.0f}%"


def tip_rounded_bar(ax, fig, *, y: float, w: float, h: float, r_px: float, color: str) -> None:
    """A horizontal bar growing from x=0 with a rounded data-end (radius r_px
    device pixels) and a square baseline end. Built as a Path in data units so
    the arc stays circular regardless of the axes' aspect."""
    pos = ax.get_position()
    ax_w_px = pos.width * fig.get_figwidth() * fig.dpi
    ax_h_px = pos.height * fig.get_figheight() * fig.dpi
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    rx = min(r_px * (x1 - x0) / ax_w_px, w)
    ry = min(r_px * (y1 - y0) / ax_h_px, h / 2)
    k = 0.5523  # cubic-Bezier quarter-circle constant
    yb, yt = y - h / 2, y + h / 2
    verts = [
        (0, yb), (w - rx, yb),
        (w - rx + k * rx, yb), (w, yb + ry - k * ry), (w, yb + ry),
        (w, yt - ry),
        (w, yt - ry + k * ry), (w - rx + k * rx, yt), (w - rx, yt),
        (0, yt), (0, yb),
    ]
    codes = [Path.MOVETO, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", zorder=3))


def main() -> None:
    with open(dn.DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)

    marital = data["marital_2023_24"]
    fert = data["fertility_2023_24"]["born_1960s_1970s"]["groups"]

    panels = [
        {
            "heading": "Currently married",
            "sub": "share of all adults",
            "values": [marital[g]["married_pct"] for g in GROUPS],
            "n": [marital[g]["unweighted_n"] for g in GROUPS],
        },
        {
            "heading": "Three or more children",
            "sub": "share of adults born in the 1960s-70s",
            "values": [fert[g]["share_3_or_more_pct"] for g in GROUPS],
            "n": [fert[g]["unweighted_n"] for g in GROUPS],
        },
    ]

    fonts = dn.load_fonts()
    fig = dn.new_figure()

    title = "Latter-day Saints are more likely to be married and to have larger families"
    dek = ("Share of U.S. adults who are currently married, and share of adults born in the "
           "1960s and 1970s (roughly ages 44 to 64) who have had three or more children, "
           "by religious group, 2023-24.")
    y_header = dn.draw_header(fig, fonts, title, dek)

    # ---- Footer (source + unweighted n, read from the JSON) -----------------
    nm, nf = panels[0]["n"], panels[1]["n"]
    # dn_style's footer band fits two 10.5pt lines (a third runs off the
    # canvas), so source + caveat share line 1 and the six unweighted n share
    # line 2. The source clause follows the template shared by every chart in
    # the set: "Source: Pew Research Center, Religious Landscape Study,
    # <waves>; public-use microdata, weighted." The right edge of line 1 is
    # measured against MARGIN_R below (see the overflow check).
    source_line = ("Source: Pew Research Center, Religious Landscape Study, 2023-24; "
                   "public-use microdata, weighted. "
                   "Latter-day Saint fertility bar is approximate (small cohort).")
    n_line = (f"Unweighted n - married: Latter-day Saints {nm[0]:,}, all Christians {nm[1]:,}, "
              f"unaffiliated {nm[2]:,}; three or more children: {nf[0]:,}, {nf[1]:,} "
              f"and {nf[2]:,}, respectively.")
    for para in (source_line, n_line):
        for ln in textwrap.wrap(para, width=165):
            print(f"footer[{len(ln):3d}]: {ln}")
    dn.draw_footer(fig, fonts, [source_line, n_line])

    # ---- Legend row (2+ series) just under the dek ---------------------------
    y_legend = y_header - 0.012
    dn.legend_swatches(fig, fonts, [(g, dn.SERIES[g]) for g in GROUPS], x=dn.MARGIN_L, y=y_legend)

    # ---- Measure the row-label column so both panels start after it ----------
    renderer = fig.canvas.get_renderer()
    label_fp = dn.fp(fonts, "sans_medium", 14)
    max_w = 0.0
    for g in GROUPS:
        t = fig.text(0, 0, g, fontproperties=label_fp)
        bb = t.get_window_extent(renderer=renderer)
        max_w = max(max_w, bb.width / (fig.get_figwidth() * fig.dpi))
        t.remove()
    label_gap = 0.018
    x_left = dn.MARGIN_L + max_w + label_gap

    # ---- Two axes sharing one vertical band -> rows align exactly -------------
    ax_bottom, ax_top = 0.215, 0.575
    ax_h = ax_top - ax_bottom
    panel_gap = 0.055
    # The last tick label ("100%") is centered on the panel's right edge, so
    # pull that edge in by half the label's width: the label then ends exactly
    # at the MARGIN_R text rail, flush with the footer credit above it.
    t = fig.text(0, 0, "100%", fontproperties=dn.fp(fonts, "sans", dn.SIZE["tick"]))
    tick_half_w = t.get_window_extent(renderer=renderer).width / (fig.get_figwidth() * fig.dpi) / 2
    t.remove()
    x_right_edge = dn.MARGIN_R - tick_half_w
    panel_w = (x_right_edge - x_left - panel_gap) / 2
    ylim = (-0.5, len(GROUPS) - 0.5)
    ys = list(range(len(GROUPS) - 1, -1, -1))  # LDS on top
    bar_h = 0.42  # 42% of the slot

    for i, panel in enumerate(panels):
        x0 = x_left + i * (panel_w + panel_gap)
        ax = fig.add_axes([x0, ax_bottom, panel_w, ax_h])
        ax.set_xlim(0, 100)
        ax.set_ylim(*ylim)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels([f"{v}%" for v in (0, 25, 50, 75, 100)])
        ax.set_yticks([])
        dn.style_axes(ax, fonts=fonts, grid_axis="x", show_bottom=True)

        for y, g, v in zip(ys, GROUPS, panel["values"]):
            tip_rounded_bar(ax, fig, y=y, w=v, h=bar_h, r_px=9, color=dn.SERIES[g])
            ax.text(v + 1.8, y, pct_label(v), fontproperties=dn.fp(fonts, "numeral", 32),
                    color=dn.INK, ha="left", va="center", zorder=4)

        # Panel heading + muted sub-heading, left-aligned with the panel's zero line.
        fig.text(x0, ax_top + 0.052, panel["heading"], fontproperties=dn.fp(fonts, "sans_semibold", 15),
                 color=dn.INK, ha="left", va="baseline")
        fig.text(x0, ax_top + 0.022, panel["sub"], fontproperties=dn.fp(fonts, "sans", 12.5),
                 color=dn.MUTED, ha="left", va="baseline")

        # Row labels once, at the far left, aligned to the shared rows.
        if i == 0:
            for y, g in zip(ys, GROUPS):
                y_fig = ax_bottom + ax_h * (y - ylim[0]) / (ylim[1] - ylim[0])
                fig.text(x_left - label_gap, y_fig, g, fontproperties=label_fp,
                         color=dn.INK, ha="right", va="center")

    # ---- Overflow self-check: every text artist must stay on the canvas, and
    # footer/header text must stay inside the MARGIN_L..MARGIN_R rail. --------
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    fw, fh = fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi
    worst_right = 0.0
    for t in fig.texts:
        bb = t.get_window_extent(renderer=renderer)
        x0f, x1f, y0f, y1f = bb.x0 / fw, bb.x1 / fw, bb.y0 / fh, bb.y1 / fh
        worst_right = max(worst_right, x1f)
        if x0f < 0 or y0f < 0 or x1f > 1 or y1f > 1:
            raise RuntimeError(f"text runs off the canvas: {t.get_text()[:40]!r} {bb}")
        if x1f > dn.MARGIN_R + 0.001:
            raise RuntimeError(f"text crosses the right rail ({x1f:.4f} > {dn.MARGIN_R}): {t.get_text()[:60]!r}")
    print(f"right-most text edge: {worst_right:.4f} (rail {dn.MARGIN_R})")

    written = dn.save(fig, STEM)
    for p in written:
        print("wrote", p)
    for panel in panels:
        print(panel["heading"], [pct_label(v) for v in panel["values"]], panel["n"])


if __name__ == "__main__":
    main()
