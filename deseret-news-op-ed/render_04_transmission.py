"""
Chart 04 - "Transmission gap" column chart.

Among U.S. adults raised highly religious (weekly attendance + religion very
important to the family), the share who are still highly religious today, by
birth decade. Seven gray columns; the two end values are set large in the
Oswald numeral face in ink. No yellow anywhere: across this set of charts
yellow means Latter-day Saints, who are not a series here. Single series ->
no legend. Every number is read from data/oped_data.json at run time.
"""
from __future__ import annotations

import json
import math
import sys

import matplotlib.transforms as mtransforms
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path
from matplotlib.textpath import TextPath

import dn_style as dn

STEM = "04_transmission"

TITLE = "A religious upbringing ‘sticks’ less than it used to"
DEK = ("Among U.S. adults who grew up attending religious services weekly in a family "
       "where religion was very important: the share who still attend weekly and say "
       "religion is very important in their lives today, by birth decade. 2023-24.")

# ---- Layout knobs (figure fractions / points) ------------------------------
AX_LEFT, AX_RIGHT = 0.095, dn.MARGIN_R
AX_BOTTOM = 0.255
HEADER_GAP = 0.05          # between the header's returned y and the axes top
COL_WIDTH = 0.55           # of the slot
CORNER_PT = 2.0            # rounded data-end radius, square at the baseline
HERO_PT = 34               # Oswald numeral face for the two end values (ink)
HALO_PAD = 0.12            # paper halo around a hero value, in em (masks the gridline)
MID_PT = 14                # muted values over the five middle columns
GAP_PT = 6                 # air between a column top and its label box
LABEL_ROW_PT = 16.5        # pitch of the three x-label rows


def r0(v: float) -> str:
    """Round half up for display."""
    return f"{int(math.floor(v + 0.5))}%"


def data_per_pt(ax) -> tuple[float, float]:
    """(x, y) data units per typographic point for this axes. Depends only on
    the figure size in inches, so it is identical for the PNG and the SVG."""
    fig = ax.figure
    w_pt = ax.get_position().width * fig.get_figwidth() * 72
    h_pt = ax.get_position().height * fig.get_figheight() * 72
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return (x1 - x0) / w_pt, (y1 - y0) / h_pt


def column_path(x0: float, x1: float, h: float, rx: float, ry: float) -> Path:
    """A column with rounded top corners and a square baseline."""
    k = 0.5522847498  # cubic bezier circle constant
    rx = min(rx, (x1 - x0) / 2)
    ry = min(ry, h / 2)
    verts = [
        (x0, 0), (x0, h - ry),
        (x0, h - ry + k * ry), (x0 + rx - k * rx, h), (x0 + rx, h),
        (x1 - rx, h),
        (x1 - rx + k * rx, h), (x1, h - ry + k * ry), (x1, h - ry),
        (x1, 0), (x0, 0),
    ]
    codes = [Path.MOVETO, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CLOSEPOLY]
    return Path(verts, codes)


def boxed_value(ax, x: float, y_top: float, text: str, prop, size_pt: float, *,
                boxstyle: str, facecolor: str, color: str, gap_pt: float):
    """A value label whose box hugs the numerals' ink (not the font's line
    box), sitting `gap_pt` above the column top at data (x, y_top). The box
    style's pad / rounding_size are in em of `size_pt`, exactly as they are
    for a matplotlib text bbox, so any bbox-style geometry carries over."""
    kx, ky = data_per_pt(ax)
    tp = TextPath((0, 0), text, size=size_pt, prop=prop)
    bx0, by0, bx1, by1 = tp.get_extents().extents
    w_pt, h_pt = bx1 - bx0, by1 - by0
    # Ink box in data units; the boxstyle pads outward from it.
    pad_pt = float(boxstyle.split("pad=")[1].split(",")[0]) * size_pt
    ink_x0 = x - (w_pt / 2) * kx
    ink_y0 = y_top + (gap_pt + pad_pt) * ky
    box = FancyBboxPatch((ink_x0, ink_y0), w_pt * kx, h_pt * ky, boxstyle=boxstyle,
                         mutation_scale=size_pt * kx, mutation_aspect=ky / kx,
                         facecolor=facecolor, edgecolor="none", linewidth=0,
                         zorder=5, clip_on=False)
    ax.add_patch(box)
    p = prop.copy()
    p.set_size(size_pt)
    t = ax.text(x, ink_y0 - by0 * ky, text, fontproperties=p, color=color,
                ha="center", va="baseline", zorder=6, clip_on=False)
    return box, t


def main() -> None:
    with open(dn.DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["transmission_2023_24"]["by_birth_decade"]
    pub = data["published"]["transmission_still_highly_religious"]
    values = [r["still_highly_religious_pct"] for r in rows]
    ns = [r["raised_highly_religious_unweighted_n"] for r in rows]

    # Cross-check the two end values against Pew's published 51% / 28%.
    assert r0(values[0]) == f"{pub['ages 74+']}%", (values[0], pub)
    assert r0(values[-1]) == f"{pub['ages 18-24']}%", (values[-1], pub)
    assert max(values) <= 60, "values exceed the 0-60 axis"

    n_min_i = min(range(len(ns)), key=lambda i: ns[i])
    n_max_i = max(range(len(ns)), key=lambda i: ns[i])

    fonts = dn.load_fonts()
    fig = dn.new_figure()
    y_head = dn.draw_header(fig, fonts, TITLE, DEK)

    dn.draw_footer(fig, fonts, ["Source: Pew Research Center, Religious Landscape Study, 2023-24."])

    # ---- Axes -----------------------------------------------------------------
    ax_top = y_head - HEADER_GAP
    ax = fig.add_axes([AX_LEFT, AX_BOTTOM, AX_RIGHT - AX_LEFT, ax_top - AX_BOTTOM])
    ax.set_xlim(-0.5, len(rows) - 0.5)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_yticklabels([f"{t}%" for t in (0, 20, 40, 60)])
    ax.set_xticks([])
    dn.style_axes(ax, fonts=fonts, grid_axis="y", show_bottom=True)

    kx, ky = data_per_pt(ax)
    half = COL_WIDTH / 2
    columns = []
    for i, v in enumerate(values):
        p = PathPatch(column_path(i - half, i + half, v, CORNER_PT * kx, CORNER_PT * ky),
                      facecolor=dn.GRAY1, edgecolor="none", linewidth=0, zorder=3)
        ax.add_patch(p)
        columns.append(p)

    # ---- Value labels ---------------------------------------------------------
    # End columns: hero numerals in ink on a paper halo (same treatment as the
    # hero values in charts 02 and 06); middle columns: small muted values.
    value_marks = []   # (box, text) per column
    for i, v in enumerate(values):
        if i in (0, len(values) - 1):
            value_marks.append(boxed_value(
                ax, i, v, r0(v), fonts["numeral"], HERO_PT, boxstyle=f"square,pad={HALO_PAD}",
                facecolor=dn.PAPER, color=dn.INK, gap_pt=GAP_PT))
        else:
            value_marks.append(boxed_value(
                ax, i, v, r0(v), fonts["sans_medium"], MID_PT, boxstyle="square,pad=0.2",
                facecolor=dn.PAPER, color=dn.MUTED, gap_pt=GAP_PT))

    # ---- Two-tier x labels: birth decade (ink) over approximate age (muted) ----
    # Row 1: "Born 1950s"; the first slot wraps its qualifier onto row 2
    # ("or earlier"); row 3 carries the age for every slot so the ages align.
    xlabels = []

    def row_offset(row: int) -> mtransforms.Transform:
        dy = -(8 + row * LABEL_ROW_PT) / 72  # inches below the baseline
        return ax.get_xaxis_transform() + mtransforms.ScaledTranslation(0, dy, fig.dpi_scale_trans)

    for i, r in enumerate(rows):
        parts = r["birth_decade"].split(" ", 1)
        t1 = ax.text(i, 0, f"Born {parts[0]}", transform=row_offset(0), ha="center", va="top",
                     fontproperties=dn.fp(fonts, "sans_medium", dn.SIZE["label"]), color=dn.INK,
                     clip_on=False)
        xlabels.append(t1)
        if len(parts) > 1:
            t2 = ax.text(i, 0, parts[1], transform=row_offset(1), ha="center", va="top",
                         fontproperties=dn.fp(fonts, "sans_medium", dn.SIZE["label"]), color=dn.INK,
                         clip_on=False)
            xlabels.append(t2)
        age = r["approx_age_at_survey"]
        if i in (0, len(rows) - 1):
            age = f"ages {age}"
        t3 = ax.text(i, 0, age, transform=row_offset(2), ha="center", va="top",
                     fontproperties=dn.fp(fonts, "sans", dn.SIZE["tick"]), color=dn.MUTED,
                     clip_on=False)
        xlabels.append(t3)

    # ---- Self-check: on canvas, inside the rail, nothing overlapping ---------
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    W, H = fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi

    def ext(artist):
        bb = artist.get_window_extent(ren)
        return (bb.x0 / W, bb.y0 / H, bb.x1 / W, bb.y1 / H)

    named = {}     # name -> (group, extent)
    for k, t in enumerate(fig.texts):
        named[f"fig_text{k}:{t.get_text()[:28]!r}"] = ("fig", ext(t))
    for k, (box, t) in enumerate(value_marks):
        named[f"value{k}_box:{t.get_text()}"] = (f"v{k}", ext(box))
        named[f"value{k}_text:{t.get_text()}"] = (f"v{k}", ext(t))
    for k, t in enumerate(xlabels):
        named[f"xlab{k}:{t.get_text()}"] = (f"x{k}", ext(t))
    for k, t in enumerate(ax.get_yticklabels()):
        named[f"ytick{k}:{t.get_text()}"] = (f"y{k}", ext(t))
    for k, p in enumerate(columns):
        named[f"column{k}"] = (f"c{k}", ext(p))

    problems = []
    for name, (grp, (x0, y0, x1, y1)) in named.items():
        if x0 < 0 or y0 < 0 or x1 > 1 or y1 > 1:
            problems.append(f"OFF-CANVAS {name}: {x0:.3f},{y0:.3f},{x1:.3f},{y1:.3f}")
        if grp == "fig" and (x0 < dn.MARGIN_L - 0.003 or x1 > dn.MARGIN_R + 0.003):
            problems.append(f"OUTSIDE-RAIL {name}: x {x0:.3f}-{x1:.3f}")
    keys = list(named)
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            ga, (ax0, ay0, ax1, ay1) = named[keys[a]]
            gb, (bx0, by0, bx1, by1) = named[keys[b]]
            if ga == gb:
                continue  # a value's own box and text
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                problems.append(f"OVERLAP {keys[a]} x {keys[b]}")

    print(f"header y = {y_head:.3f}; axes = {[round(v, 3) for v in ax.get_position().bounds]}")
    for name in keys:
        x0, y0, x1, y1 = named[name][1]
        print(f"  {name:44s} x {x0:.3f}-{x1:.3f}  y {y0:.3f}-{y1:.3f}")
    for p in problems:
        print("  !!", p)
    if problems:
        print("SELF-CHECK FAILED", file=sys.stderr)

    written = dn.save(fig, STEM)
    for p in written:
        print("wrote", p)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
