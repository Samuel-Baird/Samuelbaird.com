#!/usr/bin/env python3
"""Render slide 1 of a new social set: raw headcounts, not percentages.

post1/post2 (the sibling folders in this directory) chart *survey
percentages* -- share of a tradition's respondents who agree with a
statement. This post asks a different question: how many actual people
does that percentage represent? A survey share can look similar across
traditions while the traditions themselves are wildly different sizes, so
the raw headcount tells a story percentages alone don't.

This slide: "Jesus was a great teacher, but he was not God." Top half
converts each tradition's State of Theology agreement % into an estimated
number of American adults, then sums the four traditions surveyed. Bottom
half, below a black divider, plots The Church of Jesus Christ of
Latter-day Saints' own published total U.S. membership on the SAME x-axis
scale, so the size contrast is visual, not just verbal -- online apologetics
disproportionately singles out Latter-day Saints over this exact question,
despite the four largest other American Christian traditions combined
having a far larger population that answers the same way.

Methodology -- every input traceable to one public source, nothing hand-
guessed:
  1. U.S. adult population, 2025: U.S. Census Bureau QuickFacts national
     estimate, 341,784,857.
  2. Share of that population per tradition: Pew Research Center's 2023-24
     Religious Landscape Study ("Among all U.S. adults" column) --
     Evangelical Protestant 23.1%, Mainline Protestant 11.5%, Historically
     Black Protestant 5.4%; Roman Catholic ~19% is RLS's separately
     reported Catholic share (not on the Protestant sub-tradition table
     this repo already has as an image).
  3. Share of each tradition's adherents who strongly or somewhat agree
     "Jesus was a great teacher, but he was not God": State of Theology
     2025 survey (Lifeway Research / Ligonier Ministries), by tradition --
     already in this repo at
     scripts/social-graphics/social media posts/post2-tradition-comparison/post2_tradition_comparison.R.
  4. tradition population x agreement % = estimated headcount per
     tradition; the four are summed for the headline total. State of
     Theology only breaks this item out for these four traditions, so the
     total is a lower bound on all U.S. adults who'd agree, not a share of
     all U.S. Christians -- Orthodox Christians and other groups aren't in
     the source survey's breakout and aren't estimated here.
  5. Contrast bar: the Church's own published total U.S. membership,
     6,929,770, from churchofjesuschrist.org/learn/facts-statistics
     (as of Dec. 31, 2025).

Written in Python/matplotlib rather than R/ggplot2 like post1/post2's
scripts, matching the fallback path scripts/state-of-theology-graphics/
render_chart.py already established for this house style when no R
toolchain is available -- same palette, same fonts, same 1080x1350 canvas,
via chart_style.draw_caption_bottom.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from chart_style import draw_caption_bottom  # noqa: E402

# ---------------------------------------------------------------------------
# House-style tokens (scripts/state-of-theology-graphics/STYLE.md)
# ---------------------------------------------------------------------------
INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

AMBER = "#C9721C"  # Evangelical
MOSS = "#5B7553"  # Historically Black Protestant
SLATE = "#4E5D80"  # Mainline
WINE = "#8C4A5F"  # Roman Catholic
ACCENT = "#1f4f7a"  # site --accent, used only for the LDS contrast bar

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350, Instagram 4:5

SCRIPT_DIR = Path(__file__).resolve().parent
FONTS_DIR = (SCRIPT_DIR.parents[2] / "state-of-theology-graphics" / "fonts").resolve()
OUT = SCRIPT_DIR / "png"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Data -- see module docstring "Methodology" for source of every number.
# ---------------------------------------------------------------------------
POP_2025 = 341_784_857

TRADITION_SHARE = {  # Pew RLS 2023-24, share of all U.S. adults
    "Evangelical": 0.231,
    "Mainline": 0.115,
    "Black Protestant": 0.054,
    "Catholic": 0.19,
}
AGREE_PCT = {  # State of Theology 2025, "Jesus was a great teacher, but he
    # was not God" -- strongly + somewhat agree, by tradition
    "Evangelical": 0.34,
    "Mainline": 0.52,
    "Black Protestant": 0.55,
    "Catholic": 0.50,
}
COLOR = {
    "Evangelical": AMBER,
    "Mainline": SLATE,
    "Black Protestant": MOSS,
    "Catholic": WINE,
}
GROUPS = ["Catholic", "Black Protestant", "Mainline", "Evangelical"]

LDS_US_MEMBERS = 6_929_770

headcount = {g: POP_2025 * TRADITION_SHARE[g] * AGREE_PCT[g] for g in GROUPS}
total = sum(headcount.values())
ratio = total / LDS_US_MEMBERS

# "Total" is a summed aggregate, not a fifth tradition -- it sinks to the
# bottom of the chart per the site-wide row-order rule (an aggregate row
# always sits below every substantive row; see chart_style.sort_groups /
# BRANDING_AND_DESIGN.md's "Charts" section) and renders in MUTED, the same
# neutral non-identity color that rule uses for aggregate rows.
headcount["Total"] = total
COLOR["Total"] = MUTED
ORDER = ["Total", *GROUPS]  # bottom to top


def fmt_millions(n: float) -> str:
    return f"{n / 1_000_000:.1f}M"


def draw_mixed_line(fig, x: float, y: float, segments, fontsize: float, va: str = "top") -> float:
    """Draws a left-to-right line built from (text, fontproperties, color)
    segments -- e.g. a regular run, then one bold word, then more regular
    text -- so a single line can bold one word without the whole line being
    mathtext or a separate image. Widths are measured off the actual
    renderer (not estimated), so segments never overlap regardless of font
    metrics. Returns the figure-fraction x just past the last segment."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    cur_x = x
    for text, fp, color in segments:
        t = fig.text(cur_x, y, text, fontproperties=fp, fontsize=fontsize, color=color, ha="left", va=va)
        fig.canvas.draw()
        cur_x += t.get_window_extent(renderer=renderer).width / fig.bbox.width
    return cur_x


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
fonts: dict[str, fm.FontProperties] = {}
for key, filename in {
    "regular": "RobotoCondensed-Regular.ttf",
    "bold": "RobotoCondensed-Bold.ttf",
    "italic": "RobotoCondensed-Italic.ttf",
    "title": "RobotoSlab-Bold.ttf",
}.items():
    path = FONTS_DIR / filename
    if not path.exists():
        raise SystemExit(f"missing font file: {path}")
    fm.fontManager.addfont(str(path))
    fonts[key] = fm.FontProperties(fname=str(path))

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
fig.patch.set_facecolor(PAPER)

LEFT, RIGHT = 0.075, 0.94

caption_top = draw_caption_bottom(
    fig, fonts,
    [
        "Tradition shares: Pew Religious Landscape Study, 2023-24.   Population: U.S. Census Bureau, 2025 national estimate.   "
        "Agreement: State of Theology 2025 survey, by tradition.   LDS U.S. membership: Church-published statistics, Dec. 31, 2025.",
        "Estimated headcounts, not survey sample sizes.",
    ],
    left=LEFT,
    wrap_width=132,
    fontsize=11.5,
    color=MUTED,
    handle="@ithinkisam",
    handle_color=AMBER,
)

# ---- Title + subtitle (top half) ---------------------------------------
title_top = 0.965
title_lines = ["“Jesus was a great teacher,", "but he was not God”"]
line_step = 0.050
for i, line in enumerate(title_lines):
    fig.text(LEFT, title_top - i * line_step, line, fontproperties=fonts["title"],
              fontsize=34, color=INK, ha="left", va="top")

sub_y = title_top - len(title_lines) * line_step - 0.006
SUB_FONTSIZE = 18
draw_mixed_line(fig, LEFT, sub_y, [
    ("Estimated Americans who ", fonts["regular"], INK),
    ("agree", fonts["bold"], INK),
    (", by tradition", fonts["regular"], INK),
], fontsize=SUB_FONTSIZE)

# ---- Bar geometry: top chart (5 bars: Total + 4 traditions) and the LDS
# contrast bar (1 bar) share the SAME per-bar slot height in figure-fraction
# units, so a bar reads as literally the same size/thickness whether it's
# above or below the divider -- only its length differs, which is the only
# thing that should differ. Both axes use explicit ylim (-0.5, n-0.5) with
# zero margins so a "slot" is exactly 1 data unit tall, in both charts.
CHART_LEFT = 0.24  # moved in from 0.30 so bars run longer / labels sit tighter
BAR_HEIGHT_FRAC = 0.74
N_TOP = len(ORDER)  # Total + 4 traditions
SLOT_HEIGHT = 0.078  # figure-fraction per bar slot -- the one number that sets
# bar thickness (and, via BAR_HEIGHT_FRAC, the gaps between bars) everywhere.
# Chosen as the largest value that still lets the bottom section's fixed
# content (3-line title, subtitle, one bar, the gaps between them) fit
# above the caption once the divider is placed -- see "Divider" below.

top_band_top = sub_y - 0.028
top_band_height = SLOT_HEIGHT * N_TOP
top_band_bottom = top_band_top - top_band_height

ax = fig.add_axes([CHART_LEFT, top_band_bottom, RIGHT - CHART_LEFT, top_band_height])
ax.set_facecolor(PAPER)

xlim_top = total * 1.16  # Total is now the longest bar -- headroom for its own label
ax.barh(ORDER, [headcount[g] for g in ORDER], height=BAR_HEIGHT_FRAC,
         color=[COLOR[g] for g in ORDER], edgecolor=INK, linewidth=1.2, zorder=3)
ax.set_ylim(-0.5, N_TOP - 0.5)
ax.margins(y=0)
ax.set_xlim(0, xlim_top)
ax.set_xticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis="y", length=0, pad=10)
for label in ax.get_yticklabels():
    label.set_fontproperties(fonts["bold"])
    label.set_fontsize(20)
    label.set_color(INK)
    label.set_linespacing(1.05)

for g in ORDER:
    v = headcount[g]
    ax.text(v + xlim_top * 0.02, g, fmt_millions(v),
             va="center", ha="left", color=COLOR[g], fontproperties=fonts["bold"], fontsize=19)

# ---- Divider: placed right below the chart, not at a fixed 0.5. The LDS
# section below it needs far less content (a title, a subtitle, one bar)
# than the 5-bar chart above, so pinning it to an exact half would just
# leave that extra room as dead white space -- letting the chart's own
# height decide where the divider falls means the bottom section is only
# as tall as it actually needs to be.
DIVIDER_Y = top_band_bottom - 0.02
fig.add_artist(plt.Line2D([0.0, 1.0], [DIVIDER_Y, DIVIDER_Y], color=INK, linewidth=3.5,
                           transform=fig.transFigure, zorder=5))

# ---- Bottom section title, styled to match the top title exactly ------
# Deliberately the SAME size/weight as the survey-statement title above --
# this number isn't a fifth tradition answering the same survey question,
# it's a different metric (the Church's own reported membership count), and
# giving it equal visual weight (not a smaller subordinate label) is what
# signals that to the reader.
bottom_title_top = DIVIDER_Y - 0.035
bottom_title_lines = ["Total membership of The", "Church of Jesus Christ of", "Latter-day Saints"]
for i, line in enumerate(bottom_title_lines):
    fig.text(LEFT, bottom_title_top - i * line_step, line, fontproperties=fonts["title"],
              fontsize=34, color=INK, ha="left", va="top")
bottom_sub_y = bottom_title_top - len(bottom_title_lines) * line_step - 0.006
fig.text(LEFT, bottom_sub_y, "Total U.S. membership, 2025",
          fontproperties=fonts["regular"], fontsize=SUB_FONTSIZE, color=INK, ha="left", va="top")

# ---- LDS contrast bar: same x-scale AND same per-bar slot height as the
# chart above, so the size gap reads purely from bar length -- and, per the
# last revision, the same "6.9M" millions format the other bars use rather
# than the full "6,929,770" figure (still spelled out in the caption).
ax2_top = bottom_sub_y - 0.02
ax2_height = SLOT_HEIGHT  # identical slot height to one bar's worth above the divider
ax2_bottom = ax2_top - ax2_height
ax2 = fig.add_axes([CHART_LEFT, ax2_bottom, RIGHT - CHART_LEFT, ax2_height])
ax2.set_facecolor(PAPER)
ax2.barh([""], [LDS_US_MEMBERS], height=BAR_HEIGHT_FRAC, color=ACCENT, edgecolor=INK, linewidth=1.2, zorder=3)
ax2.set_ylim(-0.5, 0.5)
ax2.margins(y=0)
ax2.set_xlim(0, xlim_top)  # same scale as the chart above -- the point is the size gap
ax2.set_xticks([])
ax2.set_yticks([])
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.text(LDS_US_MEMBERS + xlim_top * 0.02, 0, fmt_millions(LDS_US_MEMBERS), va="center", ha="left",
          color=ACCENT, fontproperties=fonts["bold"], fontsize=20)

OUT_PATH = OUT / "1_teacher_headcount.png"
fig.savefig(OUT_PATH, facecolor=PAPER, dpi=DPI)
plt.close(fig)
print(f"wrote {OUT_PATH} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")
print(f"total (4 traditions): {total:,.0f}  |  LDS US: {LDS_US_MEMBERS:,}  |  ratio: {ratio:.2f}x")
