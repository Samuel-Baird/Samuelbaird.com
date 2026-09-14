#!/usr/bin/env python3
"""Two new lead-in text cards for post4 (State of Theology, widescreen
carousel): "What this survey is" (methodology) and "Before we start" (two
disclaimers), prepended ahead of 0_intro.png.

R wasn't used here (unlike the rest of post4) because R isn't installed on
this machine right now -- these two cards are plain text, no chart, so the
matplotlib fallback path scripts/state-of-theology-graphics/render_chart.py
already established for this house style covers them fine. Same tokens,
same fonts, same 1920x1080 canvas as post4_tradition_comparison_widescreen.R's
own card() function.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from chart_style import draw_caption_bottom  # noqa: E402

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

FIG_W_IN, FIG_H_IN, DPI = 16, 9, 120

SCRIPT_DIR = Path(__file__).resolve().parent
FONTS_DIR = (SCRIPT_DIR.parents[2] / "state-of-theology-graphics" / "fonts").resolve()
OUT = SCRIPT_DIR / "png"
OUT.mkdir(parents=True, exist_ok=True)

fonts: dict[str, fm.FontProperties] = {}
for key, filename in {
    "regular": "RobotoCondensed-Regular.ttf",
    "bold": "RobotoCondensed-Bold.ttf",
    "title": "RobotoSlab-Bold.ttf",
}.items():
    path = FONTS_DIR / filename
    if not path.exists():
        raise SystemExit(f"missing font file: {path}")
    fm.fontManager.addfont(str(path))
    fonts[key] = fm.FontProperties(fname=str(path))

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


LEFT, RIGHT = 0.045, 0.94
BODY_MAX_WIDTH_PX = (RIGHT - LEFT) * FIG_W_IN * DPI
TITLE_FONTSIZE = 48


def line_step_for(fontsize_pt: float, leading: float = 1.4) -> float:
    """Figure-fraction distance between two stacked baselines at this point
    size -- fontsize (pt) * leading / 72 (pt/in) / canvas height (in)."""
    return fontsize_pt * leading / 72 / FIG_H_IN


def draw_block(fig, y: float, lines: list[str], fontsize: float, fp: fm.FontProperties,
                color: str, line_step: float, indent: float = 0.0) -> float:
    for line in lines:
        if line == "":
            # A blank separator between wrapped paragraphs only needs a
            # partial line's worth of breathing room, not a whole extra
            # line -- a full blank line reads as double-spaced.
            y -= line_step * 0.5
            continue
        fig.text(LEFT + indent, y, line, fontproperties=fp, fontsize=fontsize,
                  color=color, ha="left", va="top")
        y -= line_step
    return y


def render_card(file: str, title: str, sections: list[dict]) -> None:
    """sections: list of {lines: [str,...] pre-split paragraphs (each item
    wrapped to BODY_MAX_WIDTH_PX already), fontsize, fp, color, line_step,
    gap_after} drawn top to bottom below the title."""
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    caption_top = draw_caption_bottom(
        fig, fonts, [], left=LEFT, fontsize=16, color=MUTED,
        handle="Data: The State of Theology survey  |  @ithinkisam",
        bottom=0.045,
    )

    y = 0.90
    fig.text(LEFT, y, title, fontproperties=fonts["title"], fontsize=TITLE_FONTSIZE,
              color=INK, ha="left", va="top")
    y -= 0.115

    for section in sections:
        y = draw_block(fig, y, section["lines"], section["fontsize"], section["fp"],
                        section["color"], section["line_step"], section.get("indent", 0.0))
        y -= section.get("gap_after", 0.02)

    if y < caption_top:
        print(f"  WARNING: {file} -- body (bottom {y:.4f}) overlaps caption (top {caption_top:.4f})")

    fig.savefig(OUT / file, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {file}")


# ---------------------------------------------------------------------------
# Slide A -- what this survey is
# ---------------------------------------------------------------------------
BULLET_FS = 28
BULLET_STEP = line_step_for(BULLET_FS)
NOTE_FS = 22
NOTE_STEP = line_step_for(NOTE_FS)

bullets = [
    "Commissioned by Ligonier Ministries, R.C. Sproul's Reformed teaching "
    "ministry. Fielded by Lifeway Research, the Southern Baptist "
    "Convention's research arm.",
    "Run every two years since 2014.",
    "A demographically balanced online panel was used for interviewing "
    "American adults.",
]
bullet_lines: list[str] = []
for b in bullets:
    wrapped = wrap_to_width(b, fonts["regular"], BULLET_FS, BODY_MAX_WIDTH_PX - 0.03 * FIG_W_IN * DPI)
    bullet_lines.append("— " + wrapped[0])
    for cont in wrapped[1:]:
        bullet_lines.append("   " + cont)
    bullet_lines.append("")
if bullet_lines and bullet_lines[-1] == "":
    bullet_lines.pop()

notes = [
    "3,001 surveys were completed January 6–15, 2025.",
    "The sample provides 95% confidence that the sampling error from the "
    "online panel does not exceed ±1.9%.",
    "Margins of error are higher in sub-groups.",
    "Slight weights were used to balance gender, age, ethnicity, income, "
    "region, and religion.",
]
note_lines: list[str] = []
for n in notes:
    wrapped = wrap_to_width(n, fonts["regular"], NOTE_FS, BODY_MAX_WIDTH_PX - 0.03 * FIG_W_IN * DPI)
    note_lines.append("• " + wrapped[0])
    for cont in wrapped[1:]:
        note_lines.append("   " + cont)
    note_lines.append("")
if note_lines and note_lines[-1] == "":
    note_lines.pop()

render_card("a_survey.png", "The State of Theology", [
    dict(lines=bullet_lines, fontsize=BULLET_FS, fp=fonts["regular"], color=INK,
         line_step=BULLET_STEP, gap_after=BULLET_STEP * 0.6),
    dict(lines=note_lines, fontsize=NOTE_FS, fp=fonts["regular"], color=MUTED,
         line_step=NOTE_STEP, gap_after=0.0),
])

# ---------------------------------------------------------------------------
# Slide B -- before we start
# ---------------------------------------------------------------------------
INTRO_FS = 30
ITEM_FS = 26
INTRO_STEP = line_step_for(INTRO_FS)
ITEM_STEP = line_step_for(ITEM_FS)

item1 = (
    "I'm not saying anyone is a heretic. I just want to point out that it "
    "may be better to spend more energy on catechesis than evangelizing to "
    "Latter-day Saints. Nothing here is a claim about anyone's standing "
    "before God. By Latter-day Saint teaching these are Christians in good "
    "faith."
)
item2 = (
    "If I've gotten something wrong, in the data or the reading of it, "
    "tell me and I'll correct it publicly."
)

item1_lines = wrap_to_width(item1, fonts["regular"], ITEM_FS, BODY_MAX_WIDTH_PX - 0.05 * FIG_W_IN * DPI)
item2_lines = wrap_to_width(item2, fonts["regular"], ITEM_FS, BODY_MAX_WIDTH_PX - 0.05 * FIG_W_IN * DPI)

item1_block = ["1. " + item1_lines[0]] + ["   " + l for l in item1_lines[1:]]
item2_block = ["2. " + item2_lines[0]] + ["   " + l for l in item2_lines[1:]]

render_card("b_before_we_start.png", "Before we start", [
    dict(lines=["Two things:"], fontsize=INTRO_FS, fp=fonts["bold"], color=INK,
         line_step=INTRO_STEP, gap_after=INTRO_STEP * 0.8),
    dict(lines=item1_block, fontsize=ITEM_FS, fp=fonts["regular"], color=INK,
         line_step=ITEM_STEP, gap_after=ITEM_STEP * 0.8),
    dict(lines=item2_block, fontsize=ITEM_FS, fp=fonts["regular"], color=INK,
         line_step=ITEM_STEP, gap_after=0.0),
])

plt.close(_measure_fig)
print("done")
