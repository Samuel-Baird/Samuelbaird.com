"""
Chart 08 - "Membership by source, since 2000": the same four unreconciled
sources as chart 07 (render_07_membership_by_source.py), zoomed to
2000-2025. A companion chart, NOT a replacement - chart 07's full 1925-2025
view stays as it is. Reads the four CSVs directly, same as chart 07.

The zoom tells a different story than the full-history chart: in this
window the sources mostly agree (three land on the exact same 2010 figure),
except the U.S. Religion Census's "adherents" methodology starts nearly a
million below the Church's own 2000 membership count before converging.

Usage: python render_08_membership_by_source_2000s.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

import dn_style as dn

STEM = "08_membership_by_source_2000s"
DATA_DIR = Path(__file__).resolve().parent.parent / "docs/datasets/lds-usa-membership-source-comparison"

# (csv filename, legend label, color, line style, show connecting line,
#  marker size in points)
SOURCES = [
    ("church_newsroom_usa_membership.csv", "Church Newsroom", dn.YELLOW, "-", True, 7),
    ("church_almanac_usa_membership.csv", "Deseret News Church Almanac", dn.GRAY1, "-", True, 6.5),
    ("arda_yearbook_usa_membership.csv", "Yearbook of American & Canadian Churches", dn.GRAY2, "--", True, 6),
    ("us_religion_census_lds_membership.csv", "U.S. Religion Census", dn.BLACK, "none", False, 8),
]

DATA_MIN_YEAR = 2000
X_MIN, X_MAX = 1999, 2026.6  # axis padding only - one year of air before the first 2000 point

TITLE = "The Religion Census and the Church's own counts converge by 2010, after starting apart in 2000"
DEK = ("The same four sources as the full 1925-2025 chart, zoomed to 2000-2025. The U.S. "
       "Religion Census's “adherents” estimate started nearly a million below the Church's "
       "own membership count in 2000, then matched every other source almost exactly by "
       "2010 and again in 2020. The Almanac and the Yearbook stopped reporting a U.S. total "
       "after 2010; only Church Newsroom continues.")


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
    y_hdr = dn.draw_header(fig, fonts, TITLE, DEK, title_wrap=46, dek_wrap=100)

    # Two legend rows: the three connected-line sources on row 1, then U.S.
    # Religion Census alone on row 2 with a diamond marker swatch - it's
    # plotted as unconnected points (see below), so a line swatch would
    # misrepresent it. Same layout as chart 07 for family consistency.
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

    ax_left = 0.11
    ax_top = y_leg2 - 0.075
    ax_bottom = dn.FOOTER_TOP + 0.10
    ax = fig.add_axes([ax_left, ax_bottom, dn.MARGIN_R - ax_left, ax_top - ax_bottom])

    all_vals = [v for s in series.values() for v in s.values()]
    # Non-zero baseline, matching this pipeline's own timeseries convention
    # (a line's slope carries the trend; truncating to the data's own range
    # isn't misleading as long as the gridlines are labeled plainly, which
    # they are here) - the companion full-history chart already shows the
    # 0-anchored long view.
    y_floor = (min(all_vals) // 500_000) * 500_000
    y_ceil = (max(all_vals) // 500_000 + 1) * 500_000

    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(y_floor, y_ceil)
    ax.set_xticks(range(2000, 2026, 5))
    y_ticks = list(range(y_floor, y_ceil + 1, 500_000))
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{t / 1_000_000:g}M" for t in y_ticks])
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

    # End/start labels: Newsroom's latest figure, and the Census's 2000
    # start - the two numbers the dek's narrative references directly.
    newsroom_pts = sorted(series["Church Newsroom"].items())
    x_last, y_last = newsroom_pts[-1]
    ax.annotate(
        f"{y_last / 1_000_000:.2f}M", xy=(x_last, y_last), xytext=(6, 0),
        textcoords="offset points", ha="left", va="center",
        fontproperties=dn.fp(fonts, "sans_bold", dn.SIZE["label"]), color=dn.INK, zorder=6,
    )
    # Offset to the right, not below - this point sits close to the x-axis
    # (the lowest value on the chart), so a below-offset label would
    # collide with the "2000" tick label directly under it.
    census_pts = sorted(series["U.S. Religion Census"].items())
    x0, y0 = census_pts[0]
    ax.annotate(
        f"{y0 / 1_000_000:.2f}M", xy=(x0, y0), xytext=(9, 0),
        textcoords="offset points", ha="left", va="center",
        fontproperties=dn.fp(fonts, "sans_bold", dn.SIZE["label"] - 1), color=dn.INK, zorder=6,
    )

    dn.save(fig, STEM)
    print(f"wrote out/{STEM}.png and .svg")
    for fn, label, *_ in SOURCES:
        pts = sorted(series[label].items())
        print(f"{label:55} n={len(pts):3} {pts[0][0]}-{pts[-1][0]}")


if __name__ == "__main__":
    main()
