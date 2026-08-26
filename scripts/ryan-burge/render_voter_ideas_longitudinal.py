#!/usr/bin/env python3
"""Renders the six VOTER Panel "longitudinal panel" idea graphics
(docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md, ideas 1/2/3/5/20) - four
line charts (retention, religious importance, daily prayer, government
trust, each tracking a fixed baseline-religion cohort across waves) and
two paired bars (R vote share 2012 vs. 2016; gay-marriage support baseline
vs. 2016).

Reads only docs/datasets/ryan-burge/voter-ideas-longitudinal.json
(produced by scripts/ryan-burge/voter_ideas_longitudinal.py) - no number
here is hand-typed. The line-chart shape generalizes
render_pid_over_time_chart.py's own conventions (donut markers, dashed gap
connector, end-of-line labels, highlight-vs-gray) to a percentage y-axis
and an uneven wave-year x-axis (baseline ~2011, 2016, 2017 - not evenly
spaced, per the real survey calendar); the paired-bar shape reuses
render_beliefs_charts.py's own two-bars-per-row convention.

Usage: see the six --*-out flags below; run with --help for the full list.
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
GRID = "#D9D5CC"

ACCENT = "#1f4f7a"
HONEY = "#8a5a06"
CONTEXT_GRAY = "#6E6A63"
CONTEXT_ALPHA = 0.55
HIGHLIGHT_GROUP = "Mormon"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120
CAPTION_TOP = 0.155

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "voter-ideas-longitudinal.json"
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


def draw_title(fig, fonts, title: str, subtitle: str, width: int = 27,
                title_fontsize: float = 27, subtitle_fontsize: float = 14) -> float:
    """Returns the y-fraction where the subtitle block actually ends - see
    scripts/pew-rls/STYLE.md's "Vertical layout" section."""
    title_lines = textwrap.wrap(title, width=width)
    line_spacing = title_fontsize / 650
    title_top = 0.965
    for i, line in enumerate(title_lines):
        fig.text(
            0.065, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
        )
    subtitle_y = title_top - len(title_lines) * line_spacing - 0.015
    fig.text(
        0.065, subtitle_y, subtitle,
        fontproperties=fonts["regular"], fontsize=subtitle_fontsize, color=MUTED, ha="left", va="top",
    )
    subtitle_lines = subtitle.count("\n") + 1
    subtitle_line_height = subtitle_fontsize * 1.2 / 72 / FIG_H_IN
    return subtitle_y - subtitle_lines * subtitle_line_height


def draw_caption(fig, fonts, note: str) -> None:
    source_paragraphs = [
        note,
        "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, via Ryan Burge "
        "(github.com/ryanburge).",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    for i, line in enumerate(caption_lines):
        fig.text(
            0.065, CAPTION_TOP - i * 0.0165, line, fontproperties=fonts["regular"],
            fontsize=10, color=MUTED, ha="left", va="top",
        )


def render_line_chart(
    waves: list[int], series: dict, group_order: list[str], title: str, subtitle: str, note: str,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering: size the axes to the real gap between the
    # subtitle and the caption, not a fixed guess - see STYLE.md. Reserve
    # a fixed slice at the bottom of that band for the wave-year tick
    # labels, drawn as their own fig.text() row rather than inside the
    # axes' data coordinates (keeps them out of the axes' own y-limits).
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    tick_row_h = 0.045
    ax_top = subtitle_bottom - 0.03
    ax_bottom = CAPTION_TOP + 0.03 + tick_row_h

    AXES_LEFT, AXES_WIDTH = 0.09, 0.62
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    for spine in ax.spines.values():
        spine.set_visible(False)

    span = waves[-1] - waves[0]
    xmin, xmax = waves[0] - span * 0.04, waves[-1] + span * 0.55
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, 100)

    yticks = [0, 25, 50, 75, 100]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{t}%" for t in yticks])
    for label in ax.get_yticklabels():
        label.set_fontproperties(fonts["regular"])
        label.set_fontsize(11)
        label.set_color(MUTED)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.set_xticks([])

    for t in yticks:
        ax.axhline(t, color=GRID, linewidth=1.2 if t == 0 else 0.8,
                    linestyle="-" if t == 0 else (0, (4, 2)), zorder=1)

    plot_order = [g for g in group_order if g != HIGHLIGHT_GROUP] + [HIGHLIGHT_GROUP]
    end_labels: list[dict] = []

    for group in plot_order:
        values = series[group]["values"]
        highlight = group == HIGHLIGHT_GROUP
        paint = ACCENT if highlight else CONTEXT_GRAY
        alpha = 1.0 if highlight else CONTEXT_ALPHA

        pts = [(yr, v) for yr, v in zip(waves, values) if v is not None]
        if not pts:
            continue

        idx_by_year = {yr: i for i, yr in enumerate(waves)}
        runs = [[pts[0]]]
        for prev, cur in zip(pts, pts[1:]):
            if idx_by_year[cur[0]] == idx_by_year[prev[0]] + 1:
                runs[-1].append(cur)
            else:
                runs.append([cur])

        for run in runs:
            xs, ys = zip(*run)
            ax.plot(xs, ys, color=paint, alpha=alpha, linewidth=2.2,
                     solid_capstyle="round", zorder=3 if highlight else 2)

        xs, ys = zip(*pts)
        ax.scatter(xs, ys, s=46, facecolor=PAPER, edgecolor=paint, linewidth=1.4, alpha=alpha, zorder=4)
        ax.scatter(xs, ys, s=7, facecolor=paint, edgecolor="none", alpha=alpha, zorder=5)

        last_year, last_val = pts[-1]
        end_labels.append({
            "text": group, "year": last_year, "value": last_val,
            "color": paint if highlight else INK, "alpha": 1.0 if highlight else 0.85,
        })

    MIN_GAP = 4.2
    end_labels.sort(key=lambda d: d["value"], reverse=True)
    end_labels[0]["label_y"] = end_labels[0]["value"]
    for i in range(1, len(end_labels)):
        end_labels[i]["label_y"] = min(end_labels[i]["value"], end_labels[i - 1]["label_y"] - MIN_GAP)

    label_x = waves[-1] + span * 0.06
    for d in end_labels:
        ax.annotate(
            d["text"], xy=(d["year"], d["value"]), xytext=(label_x, d["label_y"]),
            textcoords="data", va="center", ha="left",
            color=d["color"], alpha=d["alpha"],
            fontproperties=fonts["bold"], fontsize=11.5, zorder=6,
        )
        if abs(d["label_y"] - d["value"]) > 1e-6:
            ax.plot([d["year"] + span * 0.015, label_x - span * 0.01], [d["value"], d["label_y"]],
                     color=d["color"], alpha=d["alpha"] * 0.5, linewidth=0.9, zorder=3)

    # Explicit wave-year tick labels below the axes, as their own fig.text()
    # row (percent-positioned in figure fraction) rather than inside the
    # axes' data coordinates - the house "HTML overlay" text rule.
    tick_labels = {waves[0]: "Baseline (~2011)"} if waves[0] not in (2016, 2017) else {}
    tick_y = ax_bottom - 0.012
    for yr in waves:
        label_text = tick_labels.get(yr, str(yr))
        xfrac = AXES_LEFT + (yr - xmin) / (xmax - xmin) * AXES_WIDTH
        fig.text(xfrac, tick_y, label_text, ha="center", va="top",
                 fontproperties=fonts["regular"], fontsize=10.5, color=MUTED)

    draw_caption(fig, fonts, note)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_paired_bar(
    series_a: dict, series_b: dict, label_a: str, label_b: str, group_order: list[str],
    title: str, subtitle: str, note: str, out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    ax_top = subtitle_bottom - 0.04
    ax_bottom = CAPTION_TOP + 0.03
    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    rows = group_order[::-1]
    y_positions = list(range(len(rows)))
    ax.set_ylim(-0.7, len(rows) - 0.3)
    all_vals = [series_a[g] for g in rows if series_a[g] is not None] + \
               [series_b[g] for g in rows if series_b[g] is not None]
    max_val = max(all_vals) if all_vals else 100

    ax.set_xlim(0, max_val * 1.22)
    bar_h = 0.34
    for y, g in zip(y_positions, rows):
        av, bv = series_a[g], series_b[g]
        if av is not None:
            ax.barh(y + bar_h / 2 + 0.02, av, height=bar_h, color=ACCENT, zorder=3)
            ax.text(av + max_val * 0.02, y + bar_h / 2 + 0.02, f"{av:.0f}%", va="center", ha="left",
                     color=ACCENT, fontproperties=fonts["bold"], fontsize=10.5, zorder=4)
        if bv is not None:
            ax.barh(y - bar_h / 2 - 0.02, bv, height=bar_h, color=HONEY, zorder=3)
            ax.text(bv + max_val * 0.02, y - bar_h / 2 - 0.02, f"{bv:.0f}%", va="center", ha="left",
                     color=HONEY, fontproperties=fonts["bold"], fontsize=10.5, zorder=4)
        label_color = ACCENT if g == HIGHLIGHT_GROUP else INK
        ax.text(-max_val * 0.02, y, g, va="center", ha="right",
                 color=label_color, fontproperties=fonts["bold"], fontsize=12, zorder=4)

    handles = [mpatches.Patch(facecolor=ACCENT, edgecolor=PAPER, label=label_a),
               mpatches.Patch(facecolor=HONEY, edgecolor=PAPER, label=label_b)]
    legend = ax.legend(
        handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.05),
        ncol=2, frameon=False, handlelength=1.2, handleheight=1.2,
        fontsize=12, prop=fonts["bold"], columnspacing=1.5,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    draw_caption(fig, fonts, note)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--retention-out", type=Path, required=True)
    ap.add_argument("--religimp-out", type=Path, required=True)
    ap.add_argument("--prayer-out", type=Path, required=True)
    ap.add_argument("--trustgovt-out", type=Path, required=True)
    ap.add_argument("--vote-out", type=Path, required=True)
    ap.add_argument("--gaymar-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    waves = data["wave_years"]
    group_order = data["group_order"]
    cohort_note = "Population: religpew_baseline cohort (~2011), tracked forward regardless " \
                  "of later religious identification. Unweighted."

    render_line_chart(
        waves, data["retention"], group_order,
        title="Religious retention, by tradition",
        subtitle="Of each tradition's baseline (~2011) members, share who\nstill identify with it at each later wave.",
        note="Population: religpew_baseline cohort (~2011). Unweighted.",
        out_path=args.retention_out, fonts=fonts,
    )
    render_line_chart(
        waves, data["religimp_very_important"], group_order,
        title="Religion \"very important,\" by tradition",
        subtitle="Of each tradition's baseline cohort, share who say\nreligion is very important in their life.",
        note=cohort_note, out_path=args.religimp_out, fonts=fonts,
    )
    render_line_chart(
        waves, data["prayer_daily"], group_order,
        title="Pray daily, by tradition",
        subtitle="Of each tradition's baseline cohort, share who pray\nat least once a day.",
        note=cohort_note, out_path=args.prayer_out, fonts=fonts,
    )
    render_line_chart(
        waves, data["trustgovt_top_two"], group_order,
        title="Trust the government, by tradition",
        subtitle="Of each tradition's baseline cohort, share who trust\nthe government to do right most of the time or always.",
        note=cohort_note, out_path=args.trustgovt_out, fonts=fonts,
    )

    vote = data["vote_r_share_2012_2016"]
    render_paired_bar(
        {g: vote[g]["2012"] for g in group_order}, {g: vote[g]["2016"] for g in group_order},
        "2012 (Romney)", "2016 (Trump)", group_order,
        title="Republican presidential vote share, 2012 vs. 2016",
        subtitle="Of each tradition's baseline cohort, share who voted\nfor the Republican candidate.",
        note=cohort_note, out_path=args.vote_out, fonts=fonts,
    )
    gaymar = data["gaymar_favor_baseline_2016"]
    render_paired_bar(
        {g: gaymar[g]["baseline"] for g in group_order}, {g: gaymar[g]["2016"] for g in group_order},
        "Baseline (~2011)", "2016", group_order,
        title="Favor gay marriage, baseline vs. 2016",
        subtitle="Of each tradition's baseline cohort, share who favor\nallowing gays and lesbians to marry legally.",
        note=cohort_note, out_path=args.gaymar_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
