"""
Shared render helper for the "U.S. Church membership by source" chart
family (charts 07-09+): reads a subset of
docs/datasets/lds-usa-membership-source-comparison/'s CSVs and plots each
as its own line/marker series, colored within the Deseret News brand
guide's five values. Factored out once a second zoomed variant (chart 08)
started duplicating chart 07's plotting logic almost line for line, and a
third (chart 09) needed the same thing again with a different start year
and source set.

Each chart script stays a thin, readable list of *what's different about
this one* (which sources, what year range, what title) - see
render_07_membership_by_source.py, render_08_membership_by_source_2000s.py,
and render_09_membership_by_source_since_almanac.py for the pattern.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

import dn_style as dn

DATA_DIR = Path(__file__).resolve().parent.parent / "docs/datasets/lds-usa-membership-source-comparison"

# name -> (csv filename, color, line style, marker size in points, "line" or "diamond")
ALL_SOURCES = {
    "Church Newsroom": ("church_newsroom_usa_membership.csv", dn.YELLOW, "-", 7, "line"),
    "Deseret News Church Almanac": ("church_almanac_usa_membership.csv", dn.GRAY1, "-", 6.5, "line"),
    "Yearbook of American & Canadian Churches": ("arda_yearbook_usa_membership.csv", dn.GRAY2, "--", 6, "line"),
    "U.S. Religion Census": ("us_religion_census_lds_membership.csv", dn.BLACK, "none", 8, "diamond"),
}


def read_series(filename: str, min_year: int) -> dict[int, int]:
    out: dict[int, int] = {}
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            year = int(row["year"])
            if year < min_year or year in out:
                continue  # one duplicate row in the Almanac file; keep the first
            out[year] = int(row["membership"])
    return out


def render(
    *,
    stem: str,
    title: str,
    dek: str | None,
    source_names: list[str],
    min_year: int,
    x_ticks: range,
    x_pad: tuple[float, float],
    footer_sources: str,
    zero_baseline: bool = False,
    label_source: str | None = None,
) -> None:
    """`source_names` selects from ALL_SOURCES, in legend order. `x_pad`
    widens the axis a bit past the first/last tick so end markers and
    labels have air. `label_source` (default: the first source name) gets
    a bold end-value callout on its last point; pass "" to skip labeling
    entirely."""
    fonts = dn.load_fonts()
    series = {name: read_series(ALL_SOURCES[name][0], min_year) for name in source_names}

    fig = dn.new_figure()
    y_hdr = dn.draw_header(fig, fonts, title, dek, title_wrap=46, dek_wrap=100)

    # Line-plotted sources get a plain line swatch (accurate: that's what's
    # on the chart). A source plotted as unconnected points (kind
    # "diamond" - currently only U.S. Religion Census) gets its own row
    # with a diamond marker swatch instead - a line swatch would imply a
    # connecting line that isn't actually drawn.
    line_names = [n for n in source_names if ALL_SOURCES[n][4] == "line"]
    diamond_names = [n for n in source_names if ALL_SOURCES[n][4] == "diamond"]

    assert len(diamond_names) <= 1, "only one diamond-marker legend row is currently supported"
    y_leg = y_hdr - 0.006
    if line_names:
        dn.legend_swatches(fig, fonts, [(n, ALL_SOURCES[n][1]) for n in line_names],
                           x=dn.MARGIN_L, y=y_leg, swatch="line", gap=0.02)
    if diamond_names:
        y_leg2 = y_leg - 0.032 if line_names else y_leg
        color = ALL_SOURCES[diamond_names[0]][1]
        fig.add_artist(plt.Line2D([dn.MARGIN_L + 0.006], [y_leg2], marker="D", markersize=7,
                                  color=color, linestyle="none", transform=fig.transFigure))
        fig.text(dn.MARGIN_L + 0.018, y_leg2, diamond_names[0],
                 fontproperties=dn.fp(fonts, "sans_medium", dn.SIZE["legend"]), color=dn.INK,
                 ha="left", va="center")
        y_leg = y_leg2

    dn.draw_footer(fig, fonts, [f"Source: {footer_sources}."])

    ax_left = 0.095 if zero_baseline else 0.11
    ax_top = y_leg - 0.075
    ax_bottom = dn.FOOTER_TOP + 0.10
    ax = fig.add_axes([ax_left, ax_bottom, dn.MARGIN_R - ax_left, ax_top - ax_bottom])

    all_vals = [v for s in series.values() for v in s.values()]
    # A 0-anchored full-history range spans ~7M and wants 1M gridline steps
    # (chart 07's original convention); a zoomed, non-zero-baseline range
    # spans 2-3M and reads better at 500K steps - both floor/ceil the data
    # to that step so the axis never clips a line's endpoint.
    y_step = 1_000_000 if zero_baseline else 500_000
    y_floor = 0 if zero_baseline else (min(all_vals) // y_step) * y_step
    y_ceil = (max(all_vals) // y_step + 1) * y_step

    ax.set_xlim(x_ticks[0] - x_pad[0], x_ticks[-1] + x_pad[1])
    ax.set_ylim(y_floor, y_ceil)
    ax.set_xticks(list(x_ticks))
    y_ticks = list(range(y_floor, y_ceil + 1, y_step))
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{t / 1_000_000:g}M" if t else "0" for t in y_ticks])
    dn.style_axes(ax, fonts=fonts, grid_axis="y")

    for name in source_names:
        _, color, style, msize, kind = ALL_SOURCES[name]
        pts = sorted(series[name].items())
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if kind == "line":
            ax.plot(xs, ys, color=color, linewidth=2.6, linestyle=style,
                     solid_capstyle="round", zorder=3)
            ax.scatter(xs, ys, s=msize ** 1.7, color=color, zorder=4,
                       edgecolor=dn.PAPER, linewidth=1.2)
        else:
            ax.scatter(xs, ys, s=msize ** 1.9, color=color, zorder=5,
                       edgecolor=dn.PAPER, linewidth=1.4, marker="D")

    label_source = source_names[0] if label_source is None else label_source
    if label_source:
        pts = sorted(series[label_source].items())
        x_last, y_last = pts[-1]
        ax.annotate(
            f"{y_last / 1_000_000:.2f}M", xy=(x_last, y_last), xytext=(6, 0),
            textcoords="offset points", ha="left", va="center",
            fontproperties=dn.fp(fonts, "sans_bold", dn.SIZE["label"]), color=dn.INK, zorder=6,
        )

    dn.save(fig, stem)
    print(f"wrote out/{stem}.png and .svg")
    for name in source_names:
        pts = sorted(series[name].items())
        print(f"{name:55} n={len(pts):3} {pts[0][0]}-{pts[-1][0]}")
