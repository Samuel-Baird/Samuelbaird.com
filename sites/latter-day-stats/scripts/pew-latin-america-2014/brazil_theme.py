"""
Deliberate one-off exception to this site's locked chart palette
(BRANDING_AND_DESIGN.md's "Charts" section: every color traces to a token -
--accent, --oxblood, --border, --muted, or the single locked per-group
identity palette in chart_style.color_for_group). The three charts built
from this module are flag-themed for Brazil specifically, at the explicit,
one-time request of the site owner - not a new pipeline default, and not a
pattern to reuse for any other country or dataset. Do not import this module
from anywhere outside scripts/pew-latin-america-2014/'s own three Brazil
render scripts, and do not add a "themed" mode to
scripts/flagship-charts/common.py to generalize this - that module's whole
point is one shared, locked look across ~90 charts, which is exactly what
this one-off deliberately breaks.

Same canvas, fonts, and caption convention as every other chart in the Data
Explorer pipeline (scripts/chart_style.py) - only the color story differs:
a green/blue/yellow accent stripe under the title (sized 60/30/10, green
majority, blue second, yellow least, echoing the flag's own field-to-diamond-
to-globe proportions) and the same three colors used for the bars themselves
(context rows green, the single highlighted/subject row blue). Row labels,
value-label text, title, subtitle, and caption stay plain INK/MUTED - only
the bar fills and the title-accent stripe carry the theme, so the chart
stays legible rather than becoming a flag graphic that happens to have data
on it.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import MIN, draw_caption_bottom  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts  # noqa: E402

INK = "#1A1A1A"
PAPER = "#FFFFFF"

# Brazilian flag palette (Pantone-equivalent hex, not this site's own
# design tokens - see this module's docstring for why that's deliberate here).
BRAZIL_GREEN = "#009639"
BRAZIL_BLUE = "#002776"
BRAZIL_YELLOW = "#FEDF00"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120


def _draw_title(fig, fonts, title: str, subtitle: str, title_wrap_width: int = 42) -> float:
    """Same wrap-then-measure-then-rewrap technique as
    flagship-charts/common.py's _draw_title, plus a green/blue/yellow accent
    stripe (60/30/10 width split) drawn directly under the subtitle."""
    title_fontsize = 32
    subtitle_fontsize = 16
    line_spacing = title_fontsize / 650
    title_top = 0.965

    edge_margin_px = 0.045 * FIG_W_IN * DPI
    max_right_px = FIG_W_IN * DPI - edge_margin_px
    wrap_width = title_wrap_width
    while True:
        title_lines = textwrap.wrap(title, width=wrap_width)
        title_texts = [
            fig.text(
                0.065, title_top - i * line_spacing, line,
                fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
            )
            for i, line in enumerate(title_lines)
        ]
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        max_right_reached = max(
            (t.get_window_extent(renderer=renderer).x1 for t in title_texts), default=0,
        )
        if max_right_reached <= max_right_px or wrap_width <= 20:
            break
        for t in title_texts:
            t.remove()
        wrap_width -= 2

    subtitle_y = title_top - len(title_lines) * line_spacing - 0.015
    fig.text(
        0.065, subtitle_y, subtitle,
        fontproperties=fonts["regular"], fontsize=subtitle_fontsize, color=INK, ha="left", va="top",
    )
    subtitle_lines = subtitle.count("\n") + 1
    subtitle_line_height = subtitle_fontsize * 1.2 / 72 / FIG_H_IN
    stripe_y = subtitle_y - subtitle_lines * subtitle_line_height - 0.012

    stripe_left, stripe_right = 0.065, 0.94
    stripe_h = 0.011
    stripe_w = stripe_right - stripe_left
    splits = [stripe_left, stripe_left + 0.60 * stripe_w, stripe_left + 0.90 * stripe_w, stripe_right]
    for x0, x1, color in zip(splits[:-1], splits[1:], [BRAZIL_GREEN, BRAZIL_BLUE, BRAZIL_YELLOW]):
        fig.add_artist(
            plt.Rectangle((x0, stripe_y - stripe_h), x1 - x0, stripe_h,
                            transform=fig.transFigure, facecolor=color, edgecolor="none", zorder=5)
        )

    return stripe_y - stripe_h - 0.02


def render_brazil_bar(
    *,
    rows: list[str],
    values: dict[str, float],
    highlight_rows: set[str],
    title: str,
    subtitle: str,
    handle: str,
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
    axes_left: float = 0.36,
) -> None:
    """Horizontal magnitude bar, one row per `rows` entry (top-to-bottom
    display order). Rows in `highlight_rows` are drawn in BRAZIL_BLUE,
    everything else in BRAZIL_GREEN - see this module's docstring for why
    (a deliberate, one-time Brazil-flag theme, not this site's normal
    highlight-vs-gray convention). Row labels and value-label text stay
    plain INK regardless of bar color, for legibility."""
    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(
        fig, fonts, [], handle=handle, fontsize=16, color=INK,
    )
    ax_top = subtitle_bottom - 0.02
    ax_bottom = caption_top + 0.03

    n_rows = len(rows)
    AXES_LEFT, AXES_WIDTH = axes_left, 0.94 - axes_left
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    display_rows = rows[::-1]
    vals = [values[r] for r in display_rows]
    colors = [BRAZIL_BLUE if r in highlight_rows else BRAZIL_GREEN for r in display_rows]

    if n_rows > 8:
        bar_h, margin_frac = 0.68, 0.06
    elif n_rows >= 7:
        bar_h, margin_frac = 0.62, 0.11
    else:
        t = max(0.0, (n_rows - 1) / 6.0)
        bar_h = 0.85 - 0.23 * t
        margin_frac = 0.05 + 0.06 * t

    row_wrap_width = 30
    while True:
        wrapped_labels = {
            r: r if "\n" in r else "\n".join(textwrap.wrap(r, width=row_wrap_width))
            for r in display_rows
        }
        probes = [
            fig.text(0, 0, wrapped_labels[r], fontproperties=fonts["bold"], fontsize=MIN.LEGEND)
            for r in display_rows
        ]
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        AXES_LEFT_CAP = 0.46
        label_pad_px = 8 / 72 * DPI
        edge_margin_px = 0.045 * FIG_W_IN * DPI
        max_label_width_px = (AXES_LEFT_CAP * FIG_W_IN * DPI) - label_pad_px - edge_margin_px
        max_label_px = max((t.get_window_extent(renderer=renderer).width for t in probes), default=0)
        for t in probes:
            t.remove()
        if max_label_px <= max_label_width_px or row_wrap_width <= 12:
            break
        row_wrap_width -= 2

    required_left = min(0.46, (max_label_px + label_pad_px + edge_margin_px) / (FIG_W_IN * DPI))
    if required_left > AXES_LEFT:
        AXES_LEFT, AXES_WIDTH = required_left, 0.94 - required_left
        ax.set_position([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])

    lines_per_row = {r: wrapped_labels[r].count("\n") + 1 for r in display_rows}
    weights = [lines_per_row[r] for r in display_rows]
    row_positions = []
    running = 0.0
    for i, w in enumerate(weights):
        running += w / 2 if i == 0 else weights[i - 1] / 2 + w / 2
        row_positions.append(running)

    ax.barh(row_positions, vals, height=bar_h, color=colors, edgecolor=INK, linewidth=1, zorder=3)
    ax.set_xlim(0, max(vals) * 1.22)
    span = (row_positions[-1] + weights[-1] / 2) - (row_positions[0] - weights[0] / 2)
    pad = span * margin_frac
    ax.set_ylim(row_positions[0] - weights[0] / 2 - pad, row_positions[-1] + weights[-1] / 2 + pad)

    ax.set_yticks(row_positions)
    ax.set_yticklabels([wrapped_labels[r] for r in display_rows])
    for tick_label in ax.get_yticklabels():
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.LEGEND)
        tick_label.set_color(INK)

    data_label_fontsize = MIN.DATA_LABEL if n_rows > 8 else 15
    for r, v, y in zip(display_rows, vals, row_positions):
        ax.text(
            v + max(vals) * 0.02, y, f"{v:.0f}%", va="center", ha="left",
            color=INK, fontproperties=fonts["bold"],
            fontsize=data_label_fontsize, zorder=4,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")
