#!/usr/bin/env python3
"""Renders the "Party ID over time, by tradition" line-chart PNG for the CES
stacked 2006-2018 Data Explorer page.

Reads only docs/datasets/ryan-burge/pid-over-time.json (produced by
scripts/ryan-burge/pid_over_time.py) - no number here is hand-typed. Same
canvas/fonts/palette as scripts/pew-rls/render_switching_chart.py (see that
folder's STYLE.md); this is the first PNG line chart in that pipeline, so it
translates the in-app WaveLineChart's own conventions (donut markers,
dashed connector across a gap, end-of-line labels instead of a legend,
highlight-vs-gray) onto the static-canvas house style rather than
inventing a new one.

Usage:
    python render_pid_over_time_chart.py \
        --out ../../public/data-explorer/ces-stacked-2006-2018/pid-over-time.png
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import MIN, draw_caption_bottom  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see scripts/pew-rls/STYLE.md. Keep this block in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
GRID = "#D9D5CC"

ACCENT = "#1f4f7a"  # --accent - the one highlighted series (Latter-day Saint)
CONTEXT_GRAY = "#6E6A63"  # --muted, used for every non-highlighted series
CONTEXT_ALPHA = 0.55  # lighter than the in-app CONTEXT_OPACITY (0.45) since
                       # this has to hold up printed at 1080px with no hover
                       # to fall back on if a gray line reads too faint

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

HIGHLIGHT_GROUP = "Latter-day Saint"

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "pid-over-time.json"
).resolve()
DEFAULT_FONTS_DIR = (
    Path(__file__).parent / ".." / "state-of-theology-graphics" / "fonts"
).resolve()


def load_fonts(fonts_dir: Path) -> dict[str, fm.FontProperties]:
    files = {
        "regular": "RobotoCondensed-Regular.ttf",
        "bold": "RobotoCondensed-Bold.ttf",
        "title": "RobotoSlab-Bold.ttf",
    }
    props = {}
    for key, filename in files.items():
        path = fonts_dir / filename
        if not path.exists():
            raise SystemExit(f"missing font file: {path}")
        fm.fontManager.addfont(str(path))
        props[key] = fm.FontProperties(fname=str(path))
    return props


def render(data: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    waves: list[int] = data["waves"]
    series: dict[str, dict] = data["series"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Caption drawn first (bottom-anchored) - see STYLE.md's "Footnotes:
    # bottom-anchored" section - so the axes can reclaim whatever space the
    # caption doesn't use.
    caption_top = draw_caption_bottom(fig, fonts, [], handle="@ithinkisam | data: Ryan Burge, CES 2006-2018")
    ax_bottom = caption_top + 0.03 + 0.045  # + a wave-year tick-label row

    AXES_LEFT, AXES_WIDTH = 0.115, 0.62
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, 0.36 + 0.42 - ax_bottom])
    ax.set_facecolor(PAPER)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Padding to the right of the last wave reserves room inside the axes'
    # own data coordinates for the end-of-line labels, so they're never
    # clipped by the axes box - simpler than juggling annotation_clip.
    xmin, xmax = waves[0] - 0.5, waves[-1] + 3.4
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-3, 3)

    yticks = [-3, -1.5, 0, 1.5, 3]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{t:+g}" if t != 0 else "0" for t in yticks])
    for label in ax.get_yticklabels():
        label.set_fontproperties(fonts["regular"])
        label.set_fontsize(MIN.AXIS_LABEL)
        label.set_color(MUTED)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.set_xticks([])

    for t in yticks:
        ax.axhline(t, color=GRID, linewidth=1.2 if t == 0 else 0.8,
                    linestyle="-" if t == 0 else (0, (4, 2)), zorder=1)

    # Draw context (gray) series first, highlight series last, so the
    # highlighted line always sits on top at any crossing.
    group_order = [g for g in series if g != HIGHLIGHT_GROUP] + [HIGHLIGHT_GROUP]

    end_labels: list[dict] = []  # collision-resolved separately below, once
                                  # every series's real endpoint is known

    for group in group_order:
        values = series[group]["values"]
        highlight = group == HIGHLIGHT_GROUP
        paint = ACCENT if highlight else CONTEXT_GRAY
        alpha = 1.0 if highlight else CONTEXT_ALPHA

        pts = [(yr, v) for yr, v in zip(waves, values) if v is not None]
        if not pts:
            continue

        # Split into contiguous runs so a missing wave draws a dashed
        # connector rather than a silently interpolated solid line, per
        # WaveLineChart's own convention.
        idx_by_year = {yr: i for i, yr in enumerate(waves)}
        runs: list[list[tuple[int, float]]] = [[pts[0]]]
        for prev, cur in zip(pts, pts[1:]):
            if idx_by_year[cur[0]] == idx_by_year[prev[0]] + 1:
                runs[-1].append(cur)
            else:
                runs.append([cur])

        for run in runs:
            xs, ys = zip(*run)
            ax.plot(xs, ys, color=paint, alpha=alpha, linewidth=2.2,
                     solid_capstyle="round", zorder=3 if highlight else 2)
        for (py, pv), (cy, cv) in zip(pts, pts[1:]):
            if idx_by_year[cy] != idx_by_year[py] + 1:
                ax.plot([py, cy], [pv, cv], color=paint, alpha=alpha * 0.8,
                         linewidth=1.5, linestyle=(0, (4, 3)), zorder=2)

        # Donut markers at every plotted wave: paper-colored core, a ring in
        # the series color, a small filled center.
        xs, ys = zip(*pts)
        ax.scatter(xs, ys, s=46, facecolor=PAPER, edgecolor=paint,
                    linewidth=1.4, alpha=alpha, zorder=4)
        ax.scatter(xs, ys, s=7, facecolor=paint, edgecolor="none", alpha=alpha, zorder=5)

        # End-of-line label, not a legend - position resolved below, once
        # every series's real endpoint is collected.
        last_year, last_val = pts[-1]
        end_labels.append({
            "text": group, "year": last_year, "value": last_val,
            "color": paint if highlight else INK,
            "alpha": 1.0 if highlight else 0.85,
        })

    # Collision-resolved label y-positions: greedy top-down pass enforcing a
    # minimum gap in data units, since several traditions land within a few
    # tenths of each other at the last wave (Latter-day Saint vs. Southern
    # Baptist, 2018: 0.99 vs. 0.85) and would otherwise overlap. The marker
    # itself always stays at the real value - only the printed label moves.
    MIN_GAP = 0.38  # widened slightly for the larger end-of-line label font size
    end_labels.sort(key=lambda d: d["value"], reverse=True)
    end_labels[0]["label_y"] = end_labels[0]["value"]
    for i in range(1, len(end_labels)):
        end_labels[i]["label_y"] = min(end_labels[i]["value"], end_labels[i - 1]["label_y"] - MIN_GAP)

    for d in end_labels:
        label_x = d["year"] + 0.35
        ax.annotate(
            d["text"], xy=(d["year"], d["value"]), xytext=(label_x, d["label_y"]),
            textcoords="data", va="center", ha="left",
            color=d["color"], alpha=d["alpha"],
            fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=6,
        )
        # Thin leader from the real endpoint to the (possibly nudged) label,
        # only drawn when the label actually moved - an unmoved label needs
        # no leader, it's already right at its own point.
        if abs(d["label_y"] - d["value"]) > 1e-6:
            ax.plot([d["year"] + 0.08, label_x - 0.05], [d["value"], d["label_y"]],
                     color=d["color"], alpha=d["alpha"] * 0.5, linewidth=0.9, zorder=3)

    # Explicit wave-year x ticks below the plot, not interpolated dates.
    tick_y = -3 - 0.16
    for yr in waves:
        ax.text(yr, tick_y, str(yr), ha="center", va="top",
                 fontproperties=fonts["regular"], fontsize=MIN.AXIS_LABEL, color=MUTED)

    # --- Title / subtitle -------------------------------------------------
    title_fontsize = 28
    fig.text(
        0.065, 0.965, "Party ID over time, by tradition",
        fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
    )
    fig.text(
        0.065, 0.912,
        "Mean 7-point party ID (-3 = strong Democrat, +3 = strong Republican)\n"
        "across seven federal election cycles.",
        fontproperties=fonts["regular"], fontsize=14, color=MUTED, ha="left", va="top",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True, help="output PNG path")
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    render(data, args.out, fonts)


if __name__ == "__main__":
    main()
