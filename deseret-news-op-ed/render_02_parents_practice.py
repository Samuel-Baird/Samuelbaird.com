"""
Chart 02 - "Parents and religious practice" (Deseret News op-ed chart set).

Three horizontal bars: the share of parents of children under 18 at home who
do at least one of three religious-practice items - Latter-day Saints, all
Christians, religiously unaffiliated - from the 2023-24 Pew Religious
Landscape Study public-use file. Each row pairs a label column (row label +
a three-line mini table of the component items) with a bar and a hero value.
There is no legend row: every row is one entity named by its own label. Each
hero value wears an invisible paper halo so the gridline that falls behind it
(100% behind "84%", 75% behind "70%", 25% behind "21%") is masked rather than
drawn through the numeral, and every tick keeps its hairline.

Header and footer are the house ones (dn.draw_header / dn.draw_footer) so the
credit, rule and source rows land on the same pixels as the rest of the set.

Every number is read from data/oped_data.json at run time and rounded only
for display; nothing is typed in by hand. The component items and the
headline share the same base (all parents of children under 18 at home), so
the mini table agrees with Pew's published 58% / 48% for Christian parents.

Run:  PYTHONIOENCODING=utf-8 python render_02_parents_practice.py
"""
from __future__ import annotations

import json

from matplotlib.textpath import TextPath
from matplotlib.transforms import blended_transform_factory

import dn_style as dn

STEM = "02_parents_practice"

# (JSON key, row label) - top to bottom. Color follows the entity (dn.SERIES).
GROUPS = [
    ("Latter-day Saints", "Latter-day Saint parents"),
    ("All Christians", "All Christian parents"),
    ("Religiously unaffiliated", "Religiously unaffiliated parents"),
]
# (JSON key, short label) for the component mini table under each row label.
COMPONENTS = [
    ("pray_or_read_scripture_pct", "Pray or read scripture with them"),
    ("religious_education_pct", "Religious education"),
    ("religious_school_or_homeschool_pct", "Religious school or homeschool"),
]

# A self-contained factual headline (no dependence on chart 01). At 27pt
# Newsreader Bold the two wrapped lines measure ~8.9 in and ~9.3 in against a
# 10.7 in text rail; the layout check below confirms neither crosses MARGIN_R.
TITLE = ("Most Latter-day Saint and Christian parents practice religion with their children; "
         "few unaffiliated parents do")
TITLE_WRAP = 57
DEK = ("Share of parents of children under 18 who do at least one of the following: "
       "pray or read scripture with their children, send them to Sunday school or another "
       "religious education program, or homeschool them or send them to a religious school. 2023-24.")

# ---- layout knobs (figure fractions unless noted) ----------------------------
COL_W = 0.28            # label column width (fits "Religiously unaffiliated parents" at 15pt)
COL_GAP = 0.02          # gap between label column and the bars
AX_RIGHT = 0.935        # bars' right edge; leaves room for "84%" at the tip
AX_BOTTOM = 0.195       # tick labels hang below this, above the footer credit
BAR_H = 0.42            # bar height as a fraction of the row slot
LABEL_DY = 0.042        # row-label center above the slot center
COMP_DY0 = 0.009        # first component line center above the slot center
COMP_PITCH = 0.027      # component line pitch
LABEL_PT = 15           # row label (sans semibold)
COMP_PT = 13            # component line (sans / sans semibold)
VALUE_PT = 40           # bar-tip value (Oswald)
VALUE_OFFSET = 1.4      # data units between bar tip and value (clears the halo pad)
HALO_PAD = 0.12         # paper halo around the hero value, in units of its font size
AX_TOP_GAP = 0.045      # dek bottom -> top of the bar axes


def pct(v: float) -> str:
    """Round for display only."""
    return f"{v:.0f}%"


def fig_box(fig, artist, renderer):
    """An artist's window extent as (x0, y0, x1, y1) in figure fractions."""
    W = fig.get_figwidth() * fig.dpi
    H = fig.get_figheight() * fig.dpi
    bb = artist.get_window_extent(renderer=renderer)
    return (bb.x0 / W, bb.y0 / H, bb.x1 / W, bb.y1 / H)


def layout_check(boxes, *, x_max: float = 0.95, y_min: float = 0.0):
    """boxes: [(group, label, (x0, y0, x1, y1))]. Print them; fail on canvas
    overflow or on overlaps between boxes from different groups."""
    problems = []
    print(f"{'x0':>6} {'x1':>6} {'y0':>6} {'y1':>6}  text")
    for _, label, (x0, y0, x1, y1) in boxes:
        print(f"{x0:6.3f} {x1:6.3f} {y0:6.3f} {y1:6.3f}  {label[:72]}")
        if x0 < 0.0 or x1 > x_max or y0 < y_min or y1 > 1.0:
            problems.append(f"OUT OF BOUNDS: {label[:50]!r} ({x0:.3f},{y0:.3f})-({x1:.3f},{y1:.3f})")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ga, la, (ax0, ay0, ax1, ay1) = boxes[i]
            gb, lb, (bx0, by0, bx1, by1) = boxes[j]
            if ga is not None and ga == gb:
                continue
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                problems.append(f"OVERLAP: {la[:40]!r} <> {lb[:40]!r}")
    for p in problems:
        print(p)
    if problems:
        raise SystemExit("layout check failed")
    print("layout check: OK")


def main() -> None:
    with open(dn.DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)
    pp = data["parents_practice_2023_24"]
    pub = data["published"]["parents_at_least_one_practice"]

    fonts = dn.load_fonts()
    fig = dn.new_figure()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = []

    # ---- header (house) --------------------------------------------------------
    dn.draw_header(fig, fonts, TITLE, DEK, title_wrap=TITLE_WRAP)
    header_texts = list(fig.texts)
    for t in header_texts:
        b = fig_box(fig, t, renderer)
        boxes.append(("header", t.get_text().replace("\n", " / "), b))
        if b[2] > dn.MARGIN_R + 1e-6:
            raise SystemExit(f"header line runs past the right rail ({b[2]:.3f} > {dn.MARGIN_R}): "
                             f"{t.get_text()[:60]!r}")
    dek_bottom = min(fig_box(fig, t, renderer)[1] for t in header_texts)

    # ---- footer (house) --------------------------------------------------------
    footer = [
        "Source: Pew Research Center, Religious Landscape Study, 2023-24.",
    ]
    before = set(id(t) for t in fig.texts)
    dn.draw_footer(fig, fonts, footer)
    footer_texts = [t for t in fig.texts if id(t) not in before]
    for t in footer_texts:
        b = fig_box(fig, t, renderer)
        boxes.append(("footer", t.get_text().replace("\n", " / "), b))
        if b[2] > dn.MARGIN_R + 1e-6:
            raise SystemExit(f"footer text runs past the right rail ({b[2]:.3f} > {dn.MARGIN_R}): "
                             f"{t.get_text()[:60]!r}")
    footer_bottom = min(fig_box(fig, t, renderer)[1] for t in footer_texts)
    print(f"footer bottom (last line's descenders): {footer_bottom:.3f}")

    # ---- axes (bars only; the label column lives to the left in figure space) ----
    # No legend row: each row is one entity, named by its own row label, so a
    # legend would only repeat the three labels (the spec makes it optional).
    ax_left = dn.MARGIN_L + COL_W + COL_GAP
    ax_top = dek_bottom - AX_TOP_GAP
    ax = fig.add_axes([ax_left, AX_BOTTOM, AX_RIGHT - ax_left, ax_top - AX_BOTTOM])
    ax.set_xlim(0, 100)
    ax.set_ylim(len(GROUPS) - 0.5, -0.5)          # row 0 at the top
    ticks = [0, 25, 50, 75, 100]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t}%" for t in ticks])
    ax.set_yticks([])
    dn.style_axes(ax, fonts=fonts, grid_axis="x", show_bottom=True)
    slot_h = (ax_top - AX_BOTTOM) / len(GROUPS)
    print(f"axes top {ax_top:.3f}, bottom {AX_BOTTOM:.3f}, row slot {slot_h:.3f}")
    val_tf = blended_transform_factory(ax.transData, fig.transFigure)
    val_prop = dn.fp(fonts, "numeral", VALUE_PT)

    # ---- rows -------------------------------------------------------------------
    for i, (g, row_label) in enumerate(GROUPS):
        rec = pp[g]
        v = rec["at_least_one_pct"]
        yc = ax_top - (i + 0.5) * slot_h              # slot center, figure fraction
        grp = f"row{i}"

        # bar
        ax.barh(i, v, height=BAR_H, color=dn.SERIES[g], edgecolor="none", linewidth=0, zorder=2)

        # hero value at the bar tip: baseline chosen so the glyphs (not the font
        # box) are centered on the bar; Oswald numeral face, ink. A paper halo
        # (invisible on the white page) masks whichever gridline falls behind
        # the numeral, so every tick keeps its hairline and no chrome runs
        # through a number. The halo sits above the grid but BELOW the bars
        # (zorder 1.5 < 2), so its padding can never nick the bar tip beside it.
        ext = TextPath((0, 0), pct(v), prop=val_prop, size=VALUE_PT).get_extents()
        base_y = yc - ((ext.y0 + ext.y1) / 2) / (dn.FIG_H_IN * 72)
        ax.text(v + VALUE_OFFSET, base_y, pct(v), fontproperties=val_prop, color=dn.INK,
                ha="left", va="baseline", transform=val_tf, zorder=1.5,
                bbox=dict(boxstyle=f"square,pad={HALO_PAD}", facecolor=dn.PAPER, edgecolor="none"))
        x_anchor = fig.transFigure.inverted().transform(ax.transData.transform((v + VALUE_OFFSET, 0)))[0]
        boxes.append((grp, pct(v), (x_anchor + ext.x0 / (dn.FIG_W_IN * 72), base_y + ext.y0 / (dn.FIG_H_IN * 72),
                                    x_anchor + ext.x1 / (dn.FIG_W_IN * 72), base_y + ext.y1 / (dn.FIG_H_IN * 72))))

        # row label (left column)
        t = fig.text(dn.MARGIN_L, yc + LABEL_DY, row_label, fontproperties=dn.fp(fonts, "sans_semibold", LABEL_PT),
                     color=dn.INK, ha="left", va="center")
        boxes.append((grp, row_label, fig_box(fig, t, renderer)))

        # component mini table: muted label left, ink value right-aligned to the column edge
        for k, (key, comp_label) in enumerate(COMPONENTS):
            y = yc + COMP_DY0 - k * COMP_PITCH
            tl = fig.text(dn.MARGIN_L, y, comp_label, fontproperties=dn.fp(fonts, "sans", COMP_PT),
                          color=dn.MUTED, ha="left", va="center")
            tv = fig.text(dn.MARGIN_L + COL_W, y, pct(rec[key]), fontproperties=dn.fp(fonts, "sans_semibold", COMP_PT),
                          color=dn.INK, ha="right", va="center")
            # label and value share a line: check them against each other explicitly
            bl, bv = fig_box(fig, tl, renderer), fig_box(fig, tv, renderer)
            if bl[2] > bv[0] - 0.008:
                raise SystemExit(f"component label collides with its value: {comp_label!r}")
            boxes.append((grp, f"{comp_label} {pct(rec[key])}", (bl[0], bl[1], bv[2], bv[3])))

    # x tick labels
    fig.canvas.draw()
    for t in ax.get_xticklabels():
        boxes.append(("ticks", t.get_text(), fig_box(fig, t, renderer)))

    layout_check(boxes, x_max=0.96, y_min=0.0)

    written = dn.save(fig, STEM)
    for p in written:
        print("wrote", p)


if __name__ == "__main__":
    main()
