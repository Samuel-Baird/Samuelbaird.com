#!/usr/bin/env python3
"""Render the full post5 set -- post3's exact data, copy, and styling,
reformatted 1920x1080 (16:9) instead of 1080x1350 (4:5), the same way
post4 is post2 reformatted widescreen. See post4's own module-level
comment in post4_tradition_comparison_widescreen.R for the rationale
(platforms that want landscape rather than an Instagram-portrait
carousel). If post3's data or copy ever changes, mirror the change here
too. Everything below through the ITEMS/COMPANIONS lists is copied
verbatim from post3_membership_scale.py; only the canvas dimensions and
the layout constants that depend on them (SLOT_HEIGHT, the inter-section
gaps, CHART_LEFT, title wrap width) changed -- search "16:9" for those.

Render the full post3 set: raw headcounts, not percentages, one slide per
State of Theology statement post2 already covers (post2's own
"comparison by tradition" set -- see post2_tradition_comparison.R in the
sibling folder).

post1/post2 chart *survey percentages* -- share of a tradition's
respondents who agree (or disagree) with a statement. This post asks a
different question for the same ten statements: how many actual people
does that percentage represent? A survey share can look similar across
traditions while the traditions themselves are wildly different sizes, so
the raw headcount tells a story percentages alone don't.

Each slide: the survey statement itself as the title (verbatim, in quotes
-- no editorial headline, unlike post2's own titles for the same items),
converts each tradition's State of Theology agreement/disagreement % into
an estimated number of American adults, sums the four traditions surveyed
into a "Total" bar, then -- below a black divider placed right under the
chart, not at a fixed half -- plots The Church of Jesus Christ of
Latter-day Saints' own published total U.S. membership on the SAME x-axis
scale and at the SAME per-bar thickness, so the size contrast is visual,
not just verbal.

Methodology -- every input traceable to one public source, nothing hand-
guessed:
  1. U.S. adult population, 2025: U.S. Census Bureau QuickFacts national
     estimate, 341,784,857.
  2. Share of that population per tradition: Pew Research Center's 2023-24
     Religious Landscape Study ("Among all U.S. adults" column) --
     Evangelical Protestant 23.1%, Mainline Protestant 11.5%, Historically
     Black Protestant 5.4%; Roman Catholic ~19% is RLS's separately
     reported Catholic share (not on the Protestant sub-tradition table
     this repo already has as an image). Fixed across every slide.
  3. Share of each tradition's adherents who strongly or somewhat
     agree/disagree with each statement: State of Theology survey, by
     tradition -- the same ten items and per-tradition percentages already
     in this repo at
     scripts/social-graphics/social media posts/post2-tradition-comparison/post2_tradition_comparison.R,
     2025 wave unless noted per item (Arianism is 2022, dropped from the
     2025 wave).
  4. tradition population x agreement/disagreement % = estimated headcount
     per tradition; the four are summed for the "Total" bar. State of
     Theology only breaks each item out for these four traditions, so the
     total is a lower bound on all U.S. adults who'd answer that way, not a
     share of all U.S. Christians -- Orthodox Christians and other groups
     aren't in the source survey's breakout and aren't estimated here.
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
MOSS = "#5B7553"  # Black Protestant
SLATE = "#4E5D80"  # Mainline
WINE = "#8C4A5F"  # Catholic
ACCENT = "#1f4f7a"  # site --accent, used only for the LDS contrast bar

FIG_W_IN, FIG_H_IN, DPI = 16, 9, 120  # 1920x1080, 16:9 -- see "16:9" comments below

SCRIPT_DIR = Path(__file__).resolve().parent
FONTS_DIR = (SCRIPT_DIR.parents[2] / "state-of-theology-graphics" / "fonts").resolve()
OUT = SCRIPT_DIR / "png"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Data fixed across every slide -- see module docstring "Methodology".
# ---------------------------------------------------------------------------
POP_2025 = 341_784_857
TRADITION_SHARE = {  # Pew RLS 2023-24, share of all U.S. adults
    "Evangelical": 0.231,
    "Mainline": 0.115,
    "Black Protestant": 0.054,
    "Catholic": 0.19,
}
COLOR = {
    "Evangelical": AMBER,
    "Mainline": SLATE,
    "Black Protestant": MOSS,
    "Catholic": WINE,
    "Total": MUTED,
}
GROUPS = ["Catholic", "Black Protestant", "Mainline", "Evangelical"]  # bottom to top
ORDER = ["Total", *GROUPS]

LDS_US_MEMBERS = 6_929_770

# One row per post2 statement, same ten items/percentages as
# post2_tradition_comparison.R -- quote verbatim (this slide's title),
# direction ("agree" or "disagree" -- some items, like "homo" and
# "gender", are plotted as % disagree because that's the traditional/
# conservative-reading direction the item is about), survey year, and each
# tradition's %.
ITEMS = [
    dict(n=1, key="trinity", file="1_trinity_headcount.png", direction="agree", year="2025",
         quote="There is one true God in three persons: God the Father, God the Son, and God the Holy Spirit.",
         pct={"Evangelical": 95, "Black Protestant": 92, "Mainline": 89, "Catholic": 89}),
    dict(n=2, key="arian", file="2_arian_headcount.png", direction="agree", year="2022",
         quote="Jesus is the first and greatest being created by God.",
         pct={"Evangelical": 61, "Black Protestant": 78, "Mainline": 61, "Catholic": 71}),
    dict(n=3, key="teacher", file="3_teacher_headcount.png", direction="agree", year="2025",
         quote="Jesus was a great teacher, but he was not God.",
         pct={"Evangelical": 34, "Black Protestant": 55, "Mainline": 52, "Catholic": 50}),
    dict(n=4, key="spirit", file="4_spirit_headcount.png", direction="agree", year="2025",
         quote="The Holy Spirit is a force but is not a personal being.",
         pct={"Evangelical": 52, "Black Protestant": 65, "Mainline": 73, "Catholic": 68}),
    dict(n=5, key="relig", file="5_relig_headcount.png", direction="agree", year="2025",
         quote="God accepts the worship of all religions, including Christianity, Judaism, and Islam.",
         pct={"Evangelical": 49, "Black Protestant": 81, "Mainline": 80, "Catholic": 88}),
    dict(n=6, key="nature", file="6_nature_headcount.png", direction="agree", year="2025",
         quote="Everyone sins a little, but most people are good by nature.",
         pct={"Evangelical": 55, "Black Protestant": 71, "Mainline": 81, "Catholic": 82}),
    dict(n=7, key="abortion", file="7_abortion_headcount.png", direction="agree", year="2025",
         quote="Abortion is a sin.",
         pct={"Evangelical": 73, "Black Protestant": 63, "Mainline": 50, "Catholic": 55}),
    dict(n=8, key="sex", file="8_sex_headcount.png", direction="agree", year="2025",
         quote="Sex outside of traditional marriage is a sin.",
         pct={"Evangelical": 82, "Black Protestant": 73, "Mainline": 55, "Catholic": 49}),
    dict(n=9, key="homo", file="9_homo_headcount.png", direction="disagree", year="2025",
         quote="The Bible's condemnation of homosexual behavior doesn't apply today.",
         pct={"Evangelical": 74, "Black Protestant": 52, "Mainline": 50, "Catholic": 41}),
    dict(n=10, key="gender", file="10_gender_headcount.png", direction="disagree", year="2025",
         quote="People should be able to choose their gender regardless of their biological sex.",
         pct={"Evangelical": 77, "Black Protestant": 65, "Mainline": 61, "Catholic": 53}),
]

# Companion slides for six of the above statements, plotting the OPPOSITE
# direction from the original slide (e.g. trinity's original is "% who
# agree"; this is "% who disagree"). These percentages are NOT simply
# 100 - the original % -- State of Theology is a 5-point scale (strongly/
# somewhat disagree, not sure, somewhat/strongly agree), so "100 - agree%"
# would silently fold "not sure" into "disagree" and overstate it. Instead
# each value here is strongly+somewhat on the OTHER end of the same
# question, read directly from src/lib/evangelical-quiz/data.json's
# per-tradition raw_pct (the quiz's own full 5-point breakdown, built by
# scripts/evangelical-quiz/build_data.py -- the same source render_chart.py
# reads from) rather than derived. That file's agree-side numbers for
# these six items already match post2's hardcoded percentages above
# (spot-checked while pulling these), confirming both sides come from the
# same underlying State of Theology tradition-level breakout.
COMPANIONS = [
    dict(n=1, key="trinity_disagree", file="1b_trinity_disagree_headcount.png", direction="disagree", year="2025",
         quote="There is one true God in three persons: God the Father, God the Son, and God the Holy Spirit.",
         pct={"Evangelical": 3, "Black Protestant": 2, "Mainline": 3, "Catholic": 6}),
    dict(n=6, key="nature_disagree", file="6b_nature_disagree_headcount.png", direction="disagree", year="2025",
         quote="Everyone sins a little, but most people are good by nature.",
         pct={"Evangelical": 42, "Black Protestant": 22, "Mainline": 17, "Catholic": 15}),
    dict(n=7, key="abortion_disagree", file="7b_abortion_disagree_headcount.png", direction="disagree", year="2025",
         quote="Abortion is a sin.",
         pct={"Evangelical": 19, "Black Protestant": 24, "Mainline": 41, "Catholic": 36}),
    dict(n=8, key="sex_disagree", file="8b_sex_disagree_headcount.png", direction="disagree", year="2025",
         quote="Sex outside of traditional marriage is a sin.",
         pct={"Evangelical": 15, "Black Protestant": 23, "Mainline": 38, "Catholic": 45}),
    dict(n=9, key="homo_agree", file="9b_homo_agree_headcount.png", direction="agree", year="2025",
         quote="The Bible's condemnation of homosexual behavior doesn't apply today.",
         pct={"Evangelical": 20, "Black Protestant": 29, "Mainline": 38, "Catholic": 44}),
    dict(n=10, key="gender_agree", file="10b_gender_agree_headcount.png", direction="agree", year="2025",
         quote="People should be able to choose their gender regardless of their biological sex.",
         pct={"Evangelical": 17, "Black Protestant": 26, "Mainline": 28, "Catholic": 38}),
]


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

# Scratch figure used only to measure text widths (wrapping, mixed-bold
# segments) via the real renderer -- never saved itself.
_measure_fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)


def text_width_px(text: str, fp: fm.FontProperties, fontsize: float) -> float:
    _measure_fig.canvas.draw()
    renderer = _measure_fig.canvas.get_renderer()
    t = _measure_fig.text(0, 0, text, fontproperties=fp, fontsize=fontsize)
    _measure_fig.canvas.draw()
    w = t.get_window_extent(renderer=renderer).width
    t.remove()
    return w


def wrap_to_width(text: str, fp: fm.FontProperties, fontsize: float, max_width_px: float) -> list[str]:
    """Greedy word-wrap using ACTUAL measured glyph widths (not an assumed
    character count), so a line never overflows regardless of how wide the
    font's characters happen to be."""
    words = text.split(" ")
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if not cur or text_width_px(trial, fp, fontsize) <= max_width_px:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


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
# Shared layout constants -- fixed across every slide so the whole set
# reads as one consistent series (same bar thickness, same margins).
# ---------------------------------------------------------------------------
# post3's LEFT/RIGHT/CHART_LEFT margins were all tuned for a 9in-wide
# canvas; carried over unchanged they left a wide, unused gutter on this
# 16in-wide one (CHART_LEFT=0.30 alone reserved 4.8in for a label column
# that only needs ~2.2in even at "Black Protestant"'s width) - explicit
# whitespace the bars should get instead. LEFT: 0.075 -> 0.045 (title/
# caption/subtitle's own left margin - was 1.2in, now 0.72in, still a
# real margin, just not an oversized one). CHART_LEFT: 0.30 -> 0.19,
# measured (`text_width_px`) against "Black Protestant" bold 24pt (the
# widest row label, ~2.20in / 0.138 of 16in) plus the axis tick padding
# and a small buffer - so labels still clear the left edge with room to
# spare. The freed-up width (RIGHT - CHART_LEFT grows from 0.64 to 0.75)
# goes straight to the bars: same `xlim_top` formula below, but now
# mapped across a wider pixel span, so every bar draws longer.
LEFT, RIGHT = 0.045, 0.94
CHART_LEFT = 0.19
BAR_HEIGHT_FRAC = 0.74
N_TOP = len(ORDER)  # Total + 4 traditions
TITLE_FONTSIZE = 34
# All the figure-fraction constants below (line spacing, section gaps,
# SLOT_HEIGHT) were tuned for post3's 11.25in-tall canvas. Point sizes
# (fonts) don't scale with canvas height, but a figure-fraction distance
# does - at this post's shorter 9in canvas, the same fraction is less
# absolute space, which is exactly backwards for anything that has to
# clear a fixed-size line of text (most visibly: stacked title lines
# butting into each other with too little leading). VSCALE undoes that -
# multiply any *_STEP or gap constant that exists to clear text by VSCALE
# so it holds its ABSOLUTE (inch) size across both canvas heights. Pure
# whitespace/bar-thickness constants (the divider/section gaps, SLOT_HEIGHT)
# don't need this - there's no minimum absolute size they have to clear.
VSCALE = 11.25 / FIG_H_IN
LINE_STEP = 0.050 * VSCALE
# 18 -> 22pt, matching post1/post2's round-four subtitle bump (see those
# scripts' own `plot.subtitle` size) so this post's type reads consistently
# with the rest of the State of Theology social series.
SUB_FONTSIZE = 22
TITLE_MAX_WIDTH_PX = (RIGHT - LEFT) * FIG_W_IN * DPI

# The one number that sets bar thickness (and, via BAR_HEIGHT_FRAC, the
# gaps between bars) everywhere. Sized to the WORST case in this set -- a
# 3-line title (the longest quotes, e.g. "trinity"/"relig") -- so every
# slide in the series shares the same bar size instead of it drifting
# slide to slide with quote length; see the vertical-budget arithmetic in
# this folder's git history / PR description for how this value was
# derived (max S that still clears the caption for a 3-line title).
SLOT_HEIGHT = 0.072


def render_item(item: dict) -> None:
    headcount = {g: POP_2025 * TRADITION_SHARE[g] * item["pct"][g] / 100 for g in GROUPS}
    total = sum(headcount.values())
    headcount["Total"] = total

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    caption_top = draw_caption_bottom(
        fig, fonts,
        [
            # One flowing paragraph, methodology note leading straight into
            # the sources inline (was two separate hard-broken lines) - the
            # sentence order matters: "estimated headcounts" first sets up
            # what the numbers even are before naming where they came from.
            "Estimated headcounts, not survey sample sizes. Tradition shares: Pew Religious "
            "Landscape Study, 2023-24. Population: U.S. Census Bureau, 2025 national estimate. "
            f"{item['direction'].capitalize()}: State of Theology {item['year']} survey, by "
            "tradition. LDS U.S. membership: Church-published statistics, Dec. 31, 2025.",
        ],
        left=LEFT,
        # 95 -> 85 chars: 95 still let a couple of the widest-character
        # lines in this merged paragraph run past the canvas's right edge
        # (checked with a pixel-level scan, not just a visual read - see
        # this rollout's own note on how easy that clipping is to miss by
        # eye). 85 clears every regenerated line with margin to spare at
        # post3's 9in-wide canvas. This canvas is 16in wide, ~1.78x more
        # room on the same LEFT-to-RIGHT span, so the wrap width scales up
        # too (85 * 16/9 ~ 151) - otherwise the caption wraps into more
        # (needlessly short) lines than the width actually requires, eating
        # into the vertical budget below the LDS bar for no reason.
        wrap_width=round(85 * FIG_W_IN / 9),
        # Gray (MUTED), not ink - this caption (methodology note + sources
        # + the @ithinkisam credit) is fine print, not a second subtitle.
        fontsize=16,
        color=MUTED,
        handle="@ithinkisam",
        # draw_caption_bottom's own defaults (line_step=0.0165, bottom=0.030)
        # are figure-fraction constants tuned for post3's 11.25in canvas -
        # scaled by VSCALE here for the same reason LINE_STEP is above.
        line_step=0.0165 * VSCALE,
        bottom=0.030 * VSCALE,
    )

    # ---- Title: the survey statement itself, verbatim, in quotes -------
    title_top = 1 - (1 - 0.965) * VSCALE
    title_lines = wrap_to_width(f"“{item['quote']}”", fonts["title"], TITLE_FONTSIZE, TITLE_MAX_WIDTH_PX)
    title_fontsize = TITLE_FONTSIZE
    if len(title_lines) > 4:  # matches render_chart.py's own long-statement fallback
        title_fontsize = 27
        title_lines = wrap_to_width(f"“{item['quote']}”", fonts["title"], title_fontsize, TITLE_MAX_WIDTH_PX)
    line_step = LINE_STEP * (title_fontsize / TITLE_FONTSIZE)
    for i, line in enumerate(title_lines):
        fig.text(LEFT, title_top - i * line_step, line, fontproperties=fonts["title"],
                  fontsize=title_fontsize, color=INK, ha="left", va="top")

    sub_y = title_top - len(title_lines) * line_step - 0.006
    draw_mixed_line(fig, LEFT, sub_y, [
        ("Estimated Americans who ", fonts["regular"], INK),
        (item["direction"], fonts["bold"], INK),
        (", by tradition", fonts["regular"], INK),
    ], fontsize=SUB_FONTSIZE)

    # ---- Top chart: Total + 4 traditions --------------------------------
    # 0.028 -> 0.048: spacing widened (here and at the three other gap
    # points below - divider, bottom title, bottom bar) to use up the
    # canvas's own leftover whitespace between the LDS bar and the caption,
    # without touching any font size or the bar-thickness constant
    # (SLOT_HEIGHT) that's shared with the chart above.
    top_band_top = sub_y - 0.048
    top_band_height = SLOT_HEIGHT * N_TOP
    top_band_bottom = top_band_top - top_band_height

    ax = fig.add_axes([CHART_LEFT, top_band_bottom, RIGHT - CHART_LEFT, top_band_height])
    ax.set_facecolor(PAPER)

    xlim_top = total * 1.16  # Total is always the longest bar -- headroom for its own label
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
        # 20 -> 24pt (MIN.LEGEND): matches post2's y-axis group/identity
        # labels, same site-wide convention (state-of-theology-graphics/
        # STYLE.md's "At-a-glance legibility and mobile floors").
        label.set_fontsize(24)
        label.set_color(INK)
        label.set_linespacing(1.05)

    for g in ORDER:
        v = headcount[g]
        ax.text(v + xlim_top * 0.02, g, fmt_millions(v),
                 va="center", ha="left", color=COLOR[g], fontproperties=fonts["bold"], fontsize=19)

    # ---- Divider: right below the chart, not at a fixed half -----------
    divider_y = top_band_bottom - 0.035
    fig.add_artist(plt.Line2D([0.0, 1.0], [divider_y, divider_y], color=INK, linewidth=3.5,
                               transform=fig.transFigure, zorder=5))

    # ---- Bottom section: LDS total, same visual weight as the title ----
    # One line, all caps, replacing the old three-line "Total membership of
    # The Church of Jesus Christ of Latter-day Saints" + separate "Total
    # U.S. membership, 2025" subtitle -- shorter and reads at a glance.
    # Same fontsize as the top title's own `title_fontsize` (not the fixed
    # TITLE_FONTSIZE) so the two titles always match, even on a slide where
    # a long quoted statement dropped the top title to the 27pt fallback.
    bottom_title_top = divider_y - 0.055
    fig.text(LEFT, bottom_title_top, "U.S. LDS membership, 2025", fontproperties=fonts["title"],
              fontsize=title_fontsize, color=INK, ha="left", va="top")

    ax2_top = bottom_title_top - line_step - 0.04
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
    ax2.text(LDS_US_MEMBERS + xlim_top * 0.02, 0, f"{fmt_millions(LDS_US_MEMBERS)} LDS", va="center", ha="left",
              color=ACCENT, fontproperties=fonts["bold"], fontsize=20)

    if ax2_bottom < caption_top:
        print(f"  WARNING: {item['file']} -- LDS bar (bottom {ax2_bottom:.4f}) overlaps caption (top {caption_top:.4f})")

    out_path = OUT / item["file"]
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    ratio = total / LDS_US_MEMBERS
    print(f"wrote {out_path.name}: {len(title_lines)} title line(s), total={total:,.0f}, ratio={ratio:.1f}x")


for item in [*ITEMS, *COMPANIONS]:
    render_item(item)
plt.close(_measure_fig)
print("done")
