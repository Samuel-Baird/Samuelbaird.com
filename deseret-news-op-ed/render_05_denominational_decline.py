"""
Chart 05 - "Denominational decline" dumbbell, 2007 vs 2023-24.

Five rows (Evangelical Protestant, Mainline Protestant, Southern Baptist
Convention, United Methodist Church, Latter-day Saints). The YEAR is encoded
by marker shape, not by the set's entity grays: 2007 is a hollow ring and
2023-24 a filled dot. The ENTITY is encoded by color exactly as in the rest of
the set: Christian bodies in GRAY1, the Latter-day Saint row's connector and
2023-24 dot in Deseret yellow, with a small yellow tag after the row label so
the yellow needs no legend entry of its own. A right-hand "Relative change"
column is set in the numeral face.

Every number is read from data/oped_data.json at run time (the title's 1.7%
and 1.5% included). SBC/UMC 2023-24 come from Pew's published figures because
the public-use file withholds denomination detail; the footer says so.
"""
from __future__ import annotations

import json
import textwrap
from decimal import ROUND_HALF_UP, Decimal

import matplotlib.pyplot as plt
from matplotlib.ft2font import FT2Font

import dn_style as dn

STEM = "05_denominational_decline"

# Full-sentence, factual title (set rule). It wraps to exactly two lines at
# TITLE_WRAP; the assertion in main() guards against a break inside "2023-24"
# or "Latter-day" (textwrap breaks on hyphens by default).
TITLE_WRAP = 57
DEK = ("Share of U.S. adults identifying with each group in 2007 and 2023-24, "
       "Pew Research Center Religious Landscape Studies.")

ROWS = [
    "Evangelical Protestant",
    "Mainline Protestant",
    "Southern Baptist Convention",
    "United Methodist Church",
    "Latter-day Saints",
]
LDS = "Latter-day Saints"
PUBLISHED_2023 = {"Southern Baptist Convention", "United Methodist Church"}


def load_rows():
    with open(dn.DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)
    w07, w23 = data["waves"]["2007"], data["waves"]["2023-24"]
    pub = data["published"]["shares_rounded"]
    rows = []
    for name in ROWS:
        old = w07[name]
        new = w23[name]
        if new is None:  # PUF withholds denomination detail for 2023-24
            assert name in PUBLISHED_2023, name
            new = pub[name]["2023-24"]
        rows.append({"name": name, "old": float(old), "new": float(new),
                     "rel": (float(new) - float(old)) / float(old) * 100.0})
    rows.sort(key=lambda r: r["old"], reverse=True)
    return rows, w07["n_lds"], w23["n_lds"]


def round_half_up(v: float, places: int) -> Decimal:
    """Display rounding that matches Pew's published practice (5.05 -> 5.1),
    instead of binary-float rounding (5.05 -> 5.0)."""
    q = Decimal(1).scaleb(-places)  # 1, 0.1, ...
    return Decimal(str(v)).quantize(q, rounding=ROUND_HALF_UP)


def fmt_share(v: float) -> str:
    return f"{round_half_up(v, 0)}%" if v >= 10 else f"{round_half_up(v, 1)}%"


def has_glyph(fontprops, codepoint: int) -> bool:
    try:
        return FT2Font(fontprops.get_file()).get_char_index(codepoint) != 0
    except Exception:
        return False


# ---- marker vocabulary (shared by the plot and the legend) -------------------
DOT_PT = 8.2      # marker diameter in points (~23 px at 200 dpi, ~11 px at half scale)
RING_PT = 1.5     # paper ring around a filled dot
HOLLOW_PT = 1.9   # stroke of the hollow 2007 ring


def draw_hollow(artist_host, x, y, *, color, transform=None, zorder=4):
    kw = dict(linestyle="none", marker="o", markersize=DOT_PT, markerfacecolor="none",
              markeredgecolor=color, markeredgewidth=HOLLOW_PT, zorder=zorder)
    if transform is not None:
        artist_host.add_artist(plt.Line2D([x], [y], transform=transform, **kw))
    else:
        artist_host.plot([x], [y], **kw)


def draw_filled(artist_host, x, y, *, color, transform=None, zorder=3):
    kw = dict(linestyle="none", marker="o", markersize=DOT_PT, markerfacecolor=color,
              markeredgecolor=dn.PAPER, markeredgewidth=RING_PT, zorder=zorder)
    if transform is not None:
        artist_host.add_artist(plt.Line2D([x], [y], transform=transform, **kw))
    else:
        artist_host.plot([x], [y], **kw)


def legend_dots(fig, fonts, entries, *, x, y, gap=0.02):
    """Dot-swatch variant of dn.legend_swatches (same fonts, sizes, ink).
    `entries` is [(label, style, color), ...] with style 'hollow' or 'filled'."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    cx = x
    r_fig = 0.007  # half-width reserved for the dot, in figure fraction
    for label, style, color in entries:
        if style == "hollow":
            draw_hollow(fig, cx + r_fig, y, color=color, transform=fig.transFigure)
        else:
            draw_filled(fig, cx + r_fig, y, color=color, transform=fig.transFigure)
        cx += 2 * r_fig + 0.005
        t = fig.text(cx, y, label, fontproperties=dn.fp(fonts, "sans_medium", dn.SIZE["legend"]),
                     color=dn.INK, ha="left", va="center")
        bb = t.get_window_extent(renderer=renderer)
        cx += bb.width / (fig.get_figwidth() * fig.dpi) + gap


def main():
    rows, n_lds_07, n_lds_23 = load_rows()
    fonts = dn.load_fonts()
    minus = "−" if has_glyph(fonts["numeral"], 0x2212) else "-"
    lds_row = next(r for r in rows if r["name"] == LDS)

    title = ("Major Protestant bodies lost ground between 2007 and 2023-24, and "
             f"Latter-day Saints slipped from {fmt_share(lds_row['old'])} to {fmt_share(lds_row['new'])}")
    title_lines = textwrap.wrap(title, width=TITLE_WRAP)
    assert len(title_lines) == 2, title_lines
    assert not any(ln.endswith("-") for ln in title_lines), title_lines
    print("title lines:", title_lines)

    fig = dn.new_figure()
    y_head = dn.draw_header(fig, fonts, title, DEK, title_wrap=TITLE_WRAP)

    # ---- legend row (year = shape) + column header ------------------------
    y_leg = y_head - 0.008
    legend_dots(fig, fonts, [("2007", "hollow", dn.GRAY1), ("2023-24", "filled", dn.GRAY1)],
                x=dn.MARGIN_L, y=y_leg)
    fig.text(dn.MARGIN_R, y_leg, "Relative change", fontproperties=dn.fp(fonts, "sans_semibold", dn.SIZE["legend"]),
             color=dn.MUTED, ha="right", va="center")

    # ---- axes ----------------------------------------------------------------
    ax_left, ax_right = 0.285, 0.79
    ax_bottom, ax_top = 0.19, y_leg - 0.04
    ax = fig.add_axes([ax_left, ax_bottom, ax_right - ax_left, ax_top - ax_bottom])
    n = len(rows)
    x_max = 30
    ax.set_xlim(0, x_max)
    y_lo, y_hi = -0.5, n - 0.7          # a little less air above the top row
    ax.set_ylim(y_lo, y_hi)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_xticklabels([f"{t}%" for t in [0, 10, 20, 30]])
    ax.set_yticks([])
    dn.style_axes(ax, fonts=fonts, grid_axis="x", show_bottom=True)
    # the 0% gridline would run behind the small-share rows' left labels
    ax.xaxis.get_gridlines()[0].set_visible(False)

    label_fp = dn.fp(fonts, "sans_medium", 14)
    label_off = DOT_PT / 2 + HOLLOW_PT + 5.5   # points from marker centre to label edge
    # outer radius of the hollow ring, in data units, so connectors stop at its edge
    ax_w_px = (ax_right - ax_left) * fig.get_figwidth() * fig.dpi
    ring_r_data = (DOT_PT / 2 + HOLLOW_PT / 2) * fig.dpi / 72 / ax_w_px * x_max

    def row_y_fig(i):
        return ax_bottom + (i - y_lo) / (y_hi - y_lo) * (ax_top - ax_bottom)

    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    row_label_fp = dn.fp(fonts, "sans_medium", 13.5)

    for k, r in enumerate(rows):
        yi = n - 1 - k                      # top row first
        is_lds = r["name"] == LDS
        c_row = dn.YELLOW if is_lds else dn.GRAY1
        # connector: from the filled 2023-24 dot to the edge of the hollow 2007 ring
        if r["old"] - r["new"] > ring_r_data:
            ax.plot([r["new"], r["old"] - ring_r_data], [yi, yi], color=c_row, linewidth=3.0,
                    solid_capstyle="butt", zorder=2)
        # 2023-24 filled dot in the entity color; 2007 hollow ring on top so it
        # stays visible even where the two values nearly coincide
        draw_filled(ax, r["new"], yi, color=c_row, zorder=3)
        draw_hollow(ax, r["old"], yi, color=dn.GRAY1, zorder=4)
        # value labels: newer (lower) value to the left, 2007 value to the right
        ax.annotate(fmt_share(r["new"]), xy=(r["new"], yi), xytext=(-label_off, 0),
                    textcoords="offset points", ha="right", va="center",
                    fontproperties=label_fp, color=dn.INK, zorder=5)
        ax.annotate(fmt_share(r["old"]), xy=(r["old"], yi), xytext=(label_off, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontproperties=label_fp, color=dn.INK, zorder=5)
        # row label on the left rail (+ a small yellow tag on the Latter-day Saint row)
        t = fig.text(dn.MARGIN_L, row_y_fig(yi), r["name"], fontproperties=row_label_fp,
                     color=dn.INK, ha="left", va="center")
        if is_lds:
            bb = t.get_window_extent(renderer=rend)
            x_tag = bb.x1 / (fig.get_figwidth() * fig.dpi) + 0.008
            fig.patches.append(plt.Rectangle((x_tag, row_y_fig(yi) - 0.0075), 0.010, 0.015,
                                             transform=fig.transFigure, facecolor=dn.YELLOW,
                                             edgecolor="none"))
        # relative change column
        rel = int(round_half_up(r["rel"], 0))
        sign = minus if rel < 0 else ("+" if rel > 0 else "")
        fig.text(dn.MARGIN_R, row_y_fig(yi), f"{sign}{abs(rel)}%", fontproperties=dn.fp(fonts, "numeral", 24),
                 color=dn.MUTED, ha="right", va="center")

    # ---- footer (two lines; the module's geometry cannot fit a third) ------
    rail_px = (dn.MARGIN_R - dn.MARGIN_L) * fig.get_figwidth() * fig.dpi

    def fits(line: str, frac: float = 0.995) -> bool:
        t = fig.text(0, 0, line, fontproperties=dn.fp(fonts, "sans", dn.SIZE["source"]))
        w = t.get_window_extent(renderer=rend).width
        t.remove()
        return w <= frac * rail_px

    # Set-wide template: "Source: Pew Research Center, Religious Landscape
    # Study, <waves>; public-use microdata, weighted." + the smallest group's n.
    src = "Source: Pew Research Center, Religious Landscape Study, 2007 and 2023-24; public-use microdata, weighted."
    source_candidates = [
        f"{src} Latter-day Saints n={n_lds_07:,} (2007), {n_lds_23:,} (2023-24), unweighted.",
        f"{src} Latter-day Saints n={n_lds_07:,} (2007) and {n_lds_23:,} (2023-24).",
        f"{src} Latter-day Saints n={n_lds_07:,} (2007), {n_lds_23:,} (2023-24).",
        f"{src} Latter-day Saints n={n_lds_07:,} and {n_lds_23:,}, unweighted.",
        f"{src} Latter-day Saints n={n_lds_07:,} and {n_lds_23:,}.",
    ]
    method_candidates = [
        "Southern Baptist Convention and United Methodist Church shares for 2023-24 are Pew's published figures; "
        "the public-use file withholds denomination detail.",
        "Southern Baptist Convention and United Methodist Church 2023-24 shares are Pew's published figures; "
        "the public-use file withholds denomination detail.",
        "Southern Baptist and United Methodist shares for 2023-24 are Pew's published figures; "
        "the public-use file withholds denomination detail.",
    ]
    source = next((c for c in source_candidates if fits(c)), None)
    method = next((c for c in method_candidates if fits(c)), None)
    if source is None or method is None:
        raise SystemExit("no footer candidate fits the text rail at 10.5pt")
    print("footer line 1 (candidate", source_candidates.index(source) + 1, "):", source)
    print("footer line 2 (candidate", method_candidates.index(method) + 1, "):", method)
    dn.draw_footer(fig, fonts, [source, method])

    # ---- self-check: every text artist inside the canvas and the rail --------
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    W, H = fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi
    problems = []
    for t in list(fig.texts) + list(ax.texts) + ax.get_xticklabels():
        if not t.get_text():
            continue
        bb = t.get_window_extent(renderer=rend)
        x0, x1, y0, y1 = bb.x0 / W, bb.x1 / W, bb.y0 / H, bb.y1 / H
        if x0 < 0.02 or x1 > 0.98 or y0 < 0.01 or y1 > 0.99:
            problems.append((t.get_text()[:40], round(x0, 3), round(x1, 3), round(y0, 3), round(y1, 3)))
        if x1 > dn.MARGIN_R + 0.002:
            problems.append(("beyond rail: " + t.get_text()[:40], round(x1, 3)))
    print("header y:", round(y_head, 3), "| axes top:", round(ax_top, 3))
    for r in rows:
        print(f"{r['name']:<28} {r['old']:>6.2f} -> {r['new']:>6.2f}  rel {r['rel']:+.1f}%")
    print("layout problems:", problems or "none")
    written = dn.save(fig, STEM)
    for p in written:
        print("wrote", p)


if __name__ == "__main__":
    main()
