"""
Chart 07 - "Membership by source": U.S. Latter-day Saint membership as
reported by four different, unreconciled sources since 1925. Modeled on the
site's own us-membership-growth-2000-2025 "U.S. Church membership,
2000-2025" chart (a single merged line), but this one deliberately does NOT
merge the sources - docs/datasets/lds-usa-membership-source-comparison/'s
whole point is that these four sources disagree by definition, not just by
data-entry error, so collapsing them into one line would misrepresent the
underlying data. Four lines instead, one per source, colored within the
Deseret News brand guide's own five values (no color invented beyond
YELLOW/GRAY1/GRAY2/BLACK).

Reads the four CSVs directly - no separate compute step, since no
aggregation happens beyond picking one row per (source, year).

Usage: python render_07_membership_by_source.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

import dn_style as dn

STEM = "07_membership_by_source"
DATA_DIR = Path(__file__).resolve().parent.parent / "docs/datasets/lds-usa-membership-source-comparison"

# (csv filename, legend label, color, line style, show connecting line,
#  marker size in points)
SOURCES = [
    ("church_newsroom_usa_membership.csv", "Church Newsroom", dn.YELLOW, "-", True, 7),
    ("church_almanac_usa_membership.csv", "Deseret News Church Almanac", dn.GRAY1, "-", True, 6.5),
    ("arda_yearbook_usa_membership.csv", "Yearbook of American & Canadian Churches", dn.GRAY2, "--", True, 6),
    ("us_religion_census_lds_membership.csv", "U.S. Religion Census", dn.BLACK, "none", False, 8),
]

TITLE = "How many Latter-day Saints live in the U.S.? It depends which source you ask"
DEK = ("U.S. membership as reported by four separate sources since 1925: the Church's own "
       "membership rolls (Newsroom and the Almanac), the Yearbook of American and Canadian "
       "Churches' count of “inclusive membership,” and the U.S. Religion Census's "
       "survey-based “adherents” estimate. The definitions are not interchangeable, and the "
       "sources are not reconciled here.")


def read_series(filename: str) -> dict[int, int]:
    path = DATA_DIR / filename
    out: dict[int, int] = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            year = int(row["year"])
            if year in out:
                continue  # one duplicate row in the Almanac file; keep the first
            out[year] = int(row["membership"])
    return out


def main() -> None:
    series = {label: read_series(fn) for fn, label, *_ in SOURCES}

    fonts = dn.load_fonts()
    fig = dn.new_figure()
    y_hdr = dn.draw_header(fig, fonts, TITLE, DEK, title_wrap=48, dek_wrap=100)

    # Two legend rows: the three connected-line sources on row 1 (a plain
    # line swatch is accurate for all three), then U.S. Religion Census
    # alone on row 2 with a diamond marker swatch - it's plotted as
    # unconnected points (see below), so a line swatch would misrepresent it.
    y_leg = y_hdr - 0.006
    dn.legend_swatches(fig, fonts, [(label, color) for _, label, color, *_ in SOURCES[:3]],
                       x=dn.MARGIN_L, y=y_leg, swatch="line", gap=0.02)
    y_leg2 = y_leg - 0.032
    _, census_label, census_color, *_ = SOURCES[3]
    fig.add_artist(plt.Line2D([dn.MARGIN_L + 0.006], [y_leg2], marker="D", markersize=7,
                              color=census_color, linestyle="none", transform=fig.transFigure))
    fig.text(dn.MARGIN_L + 0.018, y_leg2, census_label,
             fontproperties=dn.fp(fonts, "sans_medium", dn.SIZE["legend"]), color=dn.INK,
             ha="left", va="center")

    dn.draw_footer(fig, fonts, [
        "Source: Church Newsroom; Deseret News Church Almanac; Yearbook of American and "
        "Canadian Churches via ARDA; U.S. Religion Census.",
    ])

    ax_left = 0.095
    ax_top = y_leg2 - 0.075
    ax_bottom = dn.FOOTER_TOP + 0.10
    ax = fig.add_axes([ax_left, ax_bottom, dn.MARGIN_R - ax_left, ax_top - ax_bottom])

    all_years = [y for s in series.values() for y in s]
    all_vals = [v for s in series.values() for v in s.values()]
    x_min, x_max = 1920, 2028
    y_max = (max(all_vals) // 1_000_000 + 1) * 1_000_000

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xticks(range(1925, 2026, 10))
    ax.set_yticks(range(0, y_max + 1, 1_000_000))
    ax.set_yticklabels([f"{t // 1_000_000}M" if t else "0" for t in range(0, y_max + 1, 1_000_000)])
    dn.style_axes(ax, fonts=fonts, grid_axis="y")

    for fn, label, color, style, show_line, msize in SOURCES:
        pts = sorted(series[label].items())
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if show_line:
            ax.plot(xs, ys, color=color, linewidth=2.6, linestyle=style,
                     solid_capstyle="round", zorder=3)
            ax.scatter(xs, ys, s=msize ** 1.7, color=color, zorder=4,
                       edgecolor=dn.PAPER, linewidth=1.2)
        else:
            ax.scatter(xs, ys, s=msize ** 1.9, color=color, zorder=5,
                       edgecolor=dn.PAPER, linewidth=1.4, marker="D")

    # Single end-label: Church Newsroom's current figure, the number a
    # reader is most likely to already have in mind. A second label at
    # Almanac's 2010 endpoint would sit on top of the Census/Newsroom
    # points that also land on 2010, so it's left off rather than crowded in.
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
