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
import textwrap
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
ORDER = ["Catholic", "Black Protestant", "Mainline", "Evangelical"]  # bottom to top

LDS_US_MEMBERS = 6_929_770

headcount = {g: POP_2025 * TRADITION_SHARE[g] * AGREE_PCT[g] for g in ORDER}
total = sum(headcount.values())
ratio = total / LDS_US_MEMBERS


def fmt_millions(n: float) -> str:
    return f"{n / 1_000_000:.1f}M"


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
        "Tradition shares: Pew Religious Landscape Study, 2023-24. Population: U.S. "
        "Census Bureau, 2025 national estimate. Agreement: State of Theology 2025 survey, "
        "by tradition. LDS U.S. membership: Church-published statistics, Dec. 31, 2025.",
    ],
    left=LEFT,
    handle="Estimated headcounts, not survey sample sizes",
    fontsize=11.5,
    color=MUTED,
    handle_color=INK,
)

# ---- Title + subtitle -------------------------------------------------
title_top = 0.965
title_lines = ["“Jesus was a great teacher,", "but he was not God”"]
line_step = 0.050
for i, line in enumerate(title_lines):
    fig.text(LEFT, title_top - i * line_step, line, fontproperties=fonts["title"],
              fontsize=34, color=INK, ha="left", va="top")

sub_y = title_top - len(title_lines) * line_step - 0.006
fig.text(LEFT, sub_y, "Estimated Americans who agree, by tradition — not survey percentages",
          fontproperties=fonts["regular"], fontsize=15.5, color=MUTED, ha="left", va="top")
sub2_y = sub_y - 0.032
fig.text(LEFT, sub2_y,
          "State of Theology 2025 agreement % × each tradition's 2025 U.S. population (Pew RLS 2023-24 share × Census 2025 total)",
          fontproperties=fonts["italic"], fontsize=11.5, color=MUTED, ha="left", va="top")

# ---- Divider: splits the canvas into a top and bottom half ------------
DIVIDER_Y = 0.535
fig.add_artist(plt.Line2D([0.0, 1.0], [DIVIDER_Y, DIVIDER_Y], color=INK, linewidth=3.5,
                           transform=fig.transFigure, zorder=5))

# ---- Top half: bar chart, 4 traditions ---------------------------------
CHART_LEFT = 0.30
chart_top = sub2_y - 0.055
chart_bottom = DIVIDER_Y + 0.155
ax = fig.add_axes([CHART_LEFT, chart_bottom, RIGHT - CHART_LEFT, chart_top - chart_bottom])
ax.set_facecolor(PAPER)

xmax = max(headcount.values())
xlim_top = xmax * 1.42
ax.barh(ORDER, [headcount[g] for g in ORDER], height=0.62,
         color=[COLOR[g] for g in ORDER], edgecolor=INK, linewidth=1.2, zorder=3)
ax.set_xlim(0, xlim_top)
ax.margins(y=0.10)
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

total_y = chart_bottom - 0.045
fig.text(LEFT, total_y,
          f"≈ {total/1_000_000:,.0f} million Americans across just these four traditions",
          fontproperties=fonts["bold"], fontsize=19, color=INK, ha="left", va="top")

# ---- Bottom half: LDS contrast bar, same x-scale as the chart above ----
label_y = DIVIDER_Y - 0.075
fig.text(LEFT, label_y, "The Church of Jesus Christ of Latter-day Saints", fontproperties=fonts["bold"],
          fontsize=19, color=INK, ha="left", va="top")
fig.text(LEFT, label_y - 0.040, "Total U.S. membership, 2025", fontproperties=fonts["regular"],
          fontsize=15.5, color=MUTED, ha="left", va="top")

ax2_top = label_y - 0.095
ax2_bottom = ax2_top - 0.075
ax2 = fig.add_axes([CHART_LEFT, ax2_bottom, RIGHT - CHART_LEFT, ax2_top - ax2_bottom])
ax2.set_facecolor(PAPER)
ax2.barh([""], [LDS_US_MEMBERS], height=0.62, color=ACCENT, edgecolor=INK, linewidth=1.2, zorder=3)
ax2.set_xlim(0, xlim_top)  # same scale as the chart above -- the point is the size gap
ax2.set_xticks([])
ax2.set_yticks([])
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.text(LDS_US_MEMBERS + xlim_top * 0.02, 0, f"{LDS_US_MEMBERS:,}", va="center", ha="left",
          color=ACCENT, fontproperties=fonts["bold"], fontsize=20)

note_y = ax2_bottom - 0.045
note = (f"That’s {ratio:,.0f} people who say Jesus wasn’t God, in just these four "
        f"traditions, for every one Latter-day Saint in the country — a tradition "
        f"whose divinity-of-Christ doctrine is routinely singled out instead.")
wrapped = textwrap.wrap(note, width=52)
for i, line in enumerate(wrapped):
    fig.text(LEFT, note_y - i * 0.028, line, fontproperties=fonts["italic"], fontsize=14.5,
              color=INK, ha="left", va="top")

OUT_PATH = OUT / "1_teacher_headcount.png"
fig.savefig(OUT_PATH, facecolor=PAPER, dpi=DPI)
plt.close(fig)
print(f"wrote {OUT_PATH} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")
print(f"total (4 traditions): {total:,.0f}  |  LDS US: {LDS_US_MEMBERS:,}  |  ratio: {ratio:.2f}x")
