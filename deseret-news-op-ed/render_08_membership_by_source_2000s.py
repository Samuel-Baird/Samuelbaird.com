"""
Chart 08 - "Membership by source, since 2000": three of chart 07's four
unreconciled sources (render_07_membership_by_source.py) - Church
Newsroom, the Deseret News Church Almanac, and the Yearbook of American
and Canadian Churches - zoomed to 2000-2025. U.S. Religion Census is
excluded here (its three sparse, decade-apart points don't add much at
this narrower time scale and its low 2000 figure was pulling the y-axis
down over 1M below the other three sources' range). A companion chart,
NOT a replacement - chart 07's full 1925-2025, four-source view stays as
it is. Reads the three CSVs directly, same as chart 07.

No dek/subtitle - title only, so the chart reads at a glance.

Usage: python render_08_membership_by_source_2000s.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import dn_style as dn

STEM = "08_membership_by_source_2000s"
DATA_DIR = Path(__file__).resolve().parent.parent / "docs/datasets/lds-usa-membership-source-comparison"

# (csv filename, legend label, color, line style, marker size in points)
SOURCES = [
    ("church_newsroom_usa_membership.csv", "Church Newsroom", dn.YELLOW, "-", 7),
    ("church_almanac_usa_membership.csv", "Deseret News Church Almanac", dn.GRAY1, "-", 6.5),
    ("arda_yearbook_usa_membership.csv", "Yearbook of American & Canadian Churches", dn.GRAY2, "--", 6),
]

DATA_MIN_YEAR = 2000
X_MIN, X_MAX = 1999, 2026.6  # axis padding only - one year of air before the first 2000 point

TITLE = "U.S. Church Membership by Source, 2000-2025"


def read_series(filename: str) -> dict[int, int]:
    path = DATA_DIR / filename
    out: dict[int, int] = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            year = int(row["year"])
            if year < DATA_MIN_YEAR or year in out:
                continue  # one duplicate row in the Almanac file; keep the first
            out[year] = int(row["membership"])
    return out


def main() -> None:
    series = {label: read_series(fn) for fn, label, *_ in SOURCES}

    fonts = dn.load_fonts()
    fig = dn.new_figure()
    y_hdr = dn.draw_header(fig, fonts, TITLE, None, title_wrap=46)

    y_leg = y_hdr - 0.006
    dn.legend_swatches(fig, fonts, [(label, color) for _, label, color, *_ in SOURCES],
                       x=dn.MARGIN_L, y=y_leg, swatch="line", gap=0.02)

    dn.draw_footer(fig, fonts, [
        "Source: Church Newsroom; Deseret News Church Almanac; Yearbook of American and "
        "Canadian Churches via ARDA.",
    ])

    ax_left = 0.11
    ax_top = y_leg - 0.075
    ax_bottom = dn.FOOTER_TOP + 0.10
    ax = fig.add_axes([ax_left, ax_bottom, dn.MARGIN_R - ax_left, ax_top - ax_bottom])

    all_vals = [v for s in series.values() for v in s.values()]
    # Non-zero baseline, matching this pipeline's own timeseries convention
    # (a line's slope carries the trend; truncating to the data's own range
    # isn't misleading as long as the gridlines are labeled plainly, which
    # they are here) - the companion full-history chart already shows the
    # 0-anchored long view. With Census removed, the three remaining
    # sources all start around 5.2M in 2000, so the floor sits there
    # instead of down at Census's 4.22M - a tighter, more legible scale.
    y_floor = (min(all_vals) // 500_000) * 500_000
    y_ceil = (max(all_vals) // 500_000 + 1) * 500_000

    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(y_floor, y_ceil)
    ax.set_xticks(range(2000, 2026, 5))
    y_ticks = list(range(y_floor, y_ceil + 1, 500_000))
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{t / 1_000_000:g}M" for t in y_ticks])
    dn.style_axes(ax, fonts=fonts, grid_axis="y")

    for fn, label, color, style, msize in SOURCES:
        pts = sorted(series[label].items())
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, color=color, linewidth=2.6, linestyle=style,
                 solid_capstyle="round", zorder=3)
        ax.scatter(xs, ys, s=msize ** 1.7, color=color, zorder=4,
                   edgecolor=dn.PAPER, linewidth=1.2)

    # Single end-label: Church Newsroom's current figure.
    newsroom_pts = sorted(series["Church Newsroom"].items())
    x_last, y_last = newsroom_pts[-1]
    ax.annotate(
        f"{y_last / 1_000_000:.2f}M", xy=(x_last, y_last), xytext=(6, 0),
        textcoords="offset points", ha="left", va="center",
        fontproperties=dn.fp(fonts, "sans_bold", dn.SIZE["label"]), color=dn.INK, zorder=6,
    )

    dn.save(fig, STEM)
    print(f"wrote out/{STEM}.png and .svg")
    for fn, label, *_ in SOURCES:
        pts = sorted(series[label].items())
        print(f"{label:55} n={len(pts):3} {pts[0][0]}-{pts[-1][0]}")


if __name__ == "__main__":
    main()
