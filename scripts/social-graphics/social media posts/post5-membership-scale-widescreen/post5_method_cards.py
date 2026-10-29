#!/usr/bin/env python3
"""Two methodology cards for post5 (raw numbers, widescreen): how a survey
percentage becomes an estimated headcount. Meant to lead the carousel ahead of
1_trinity_headcount.png, in the same style as post4_intro_cards.py.

  m1_how_it_works.png   the three inputs and the formula, with one example
  m2_worked_example.png the same math for all four traditions on one statement

Every input is the same one post5_membership_scale_widescreen.py uses (they
are imported from it conceptually -- kept as literals here so this file runs
standalone; if the main script's inputs change, change them here too, and the
asserts below will catch a mismatch with the published 124.6M total).

Same tokens, fonts and 1920x1080 canvas as post5 / post4_intro_cards.py.
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
AMBER = "#C9721C"
MOSS = "#5B7553"
SLATE = "#4E5D80"
WINE = "#8C4A5F"
ACCENT = "#1f4f7a"

FIG_W_IN, FIG_H_IN, DPI = 16, 9, 120

SCRIPT_DIR = Path(__file__).resolve().parent
FONTS_DIR = (SCRIPT_DIR.parents[2] / "state-of-theology-graphics" / "fonts").resolve()
OUT = SCRIPT_DIR / "png"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Inputs -- identical to post5_membership_scale_widescreen.py
# ---------------------------------------------------------------------------
POP_2025 = 341_784_857  # U.S. Census Bureau QuickFacts, 2025 national estimate
SHARE = {  # Pew Religious Landscape Study 2023-24, share of all U.S. adults
    "Evangelical": 0.231,
    "Mainline": 0.115,
    "Black Protestant": 0.054,
    "Catholic": 0.19,
}
# "Abortion is a sin." -- % who agree, State of Theology 2025
EXAMPLE_PCT = {"Evangelical": 73, "Mainline": 50, "Black Protestant": 63, "Catholic": 55}
COLOR = {"Evangelical": AMBER, "Mainline": SLATE, "Black Protestant": MOSS, "Catholic": WINE}
ROWS = ["Evangelical", "Mainline", "Black Protestant", "Catholic"]  # same top-to-bottom order as the charts
LDS_US_MEMBERS = 6_929_770

people = {g: POP_2025 * SHARE[g] for g in ROWS}
estimate = {g: people[g] * EXAMPLE_PCT[g] / 100 for g in ROWS}
total = sum(estimate.values())
assert f"{estimate['Evangelical'] / 1e6:.1f}" == "57.6", estimate  # matches 7_abortion_headcount.png
assert f"{total / 1e6:.1f}" == "124.6", total

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
    lines: list[str] = []
    cur = ""
    for word in text.split(" "):
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
W_PX = FIG_W_IN * DPI
TITLE_FS = 48


def line_step_for(fontsize_pt: float, leading: float = 1.4) -> float:
    return fontsize_pt * leading / 72 / FIG_H_IN


def new_card(title: str):
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    caption_top = draw_caption_bottom(
        fig, fonts, [], left=LEFT, fontsize=16, color=MUTED,
        handle="Estimates built from the sources shown  |  @ithinkisam", bottom=0.045,
    )
    fig.text(LEFT, 0.90, title, fontproperties=fonts["title"], fontsize=TITLE_FS,
             color=INK, ha="left", va="top")
    return fig, caption_top


def draw_lines(fig, x, y, lines, fs, fp, color, step=None):
    step = step or line_step_for(fs)
    for ln in lines:
        fig.text(x, y, ln, fontproperties=fp, fontsize=fs, color=color, ha="left", va="top")
        y -= step
    return y


def save(fig, name: str, caption_top: float, y_bottom: float) -> None:
    if y_bottom < caption_top:
        print(f"  WARNING: {name} -- body (bottom {y_bottom:.4f}) overlaps caption (top {caption_top:.4f})")
    fig.savefig(OUT / name, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {name}")


def millions(n: float) -> str:
    return f"{n / 1e6:.1f}M"


# ---------------------------------------------------------------------------
# m1 -- the three inputs and the formula
# ---------------------------------------------------------------------------
fig, cap = new_card("How the raw numbers are estimated")
fig.text(LEFT, 0.775, "Example: Evangelicals who agree “Abortion is a sin.”",
         fontproperties=fonts["regular"], fontsize=28, color=MUTED, ha="left", va="top")

COL_W = 0.19
GAP = (RIGHT - LEFT - 4 * COL_W) / 3
cols = [
    dict(label="U.S. POPULATION", value=f"{POP_2025 / 1e6:.1f}M", color=INK,
         src="U.S. Census Bureau, 2025 national estimate"),
    dict(label="SHARE IN THE TRADITION", value="23.1%", color=AMBER,
         src="Pew Research Center, 2023–24 Religious Landscape Study: Evangelical Protestants as a share of U.S. adults"),
    dict(label="SHARE WHO AGREE", value="73%", color=AMBER,
         src="State of Theology survey, 2025: Evangelicals who strongly or somewhat agree"),
    dict(label="ESTIMATED PEOPLE", value=millions(estimate["Evangelical"]), color=AMBER,
         src="Population × share in tradition × share who agree"),
]
ops = ["×", "×", "="]
y_label, y_value, y_src = 0.62, 0.55, 0.40
bottom = y_src
for i, c in enumerate(cols):
    x = LEFT + i * (COL_W + GAP)
    fig.text(x, y_label, c["label"], fontproperties=fonts["bold"], fontsize=20, color=MUTED, ha="left", va="top")
    fig.text(x, y_value, c["value"], fontproperties=fonts["title"], fontsize=54, color=c["color"], ha="left", va="top")
    src_lines = wrap_to_width(c["src"], fonts["regular"], 22, COL_W * W_PX)
    bottom = min(bottom, draw_lines(fig, x, y_src, src_lines, 22, fonts["regular"], INK))
    if i < 3:
        fig.text(x + COL_W + GAP / 2, y_value - 0.012, ops[i], fontproperties=fonts["title"], fontsize=54,
                 color=INK, ha="center", va="top")
save(fig, "m1_how_it_works.png", cap, bottom)

# ---------------------------------------------------------------------------
# m2 -- worked example, every tradition
# ---------------------------------------------------------------------------
fig, cap = new_card("The same math, four traditions")
fig.text(LEFT, 0.775, "“Abortion is a sin.” — estimated Americans who agree",
         fontproperties=fonts["regular"], fontsize=28, color=MUTED, ha="left", va="top")

xs = [LEFT, 0.275, 0.445, 0.635, 0.795]  # tradition | share | people | agree | estimate
heads = ["", "Pew share", "People", "Agree", "Estimate"]
y = 0.66
for x, h in zip(xs, heads):
    fig.text(x, y, h, fontproperties=fonts["bold"], fontsize=22, color=MUTED, ha="left", va="top")
y -= 0.075
for g in ROWS:
    c = COLOR[g]
    cells = [g, f"{SHARE[g] * 100:g}%", millions(people[g]), f"{EXAMPLE_PCT[g]}%", millions(estimate[g])]
    for j, (x, t) in enumerate(zip(xs, cells)):
        fig.text(x, y, t, fontproperties=fonts["bold"], fontsize=34, color=c if j in (0, 4) else INK,
                 ha="left", va="top")
    y -= 0.075
fig.add_artist(plt.Line2D([LEFT, RIGHT], [y + 0.02] * 2, color=INK, linewidth=3, transform=fig.transFigure))
y -= 0.02
fig.text(xs[0], y, "Total", fontproperties=fonts["bold"], fontsize=34, color=MUTED, ha="left", va="top")
fig.text(xs[4], y, millions(total), fontproperties=fonts["bold"], fontsize=34, color=MUTED, ha="left", va="top")
y -= 0.08
note = (f"People = {POP_2025 / 1e6:.1f}M × Pew share. Estimate = People × Agree. "
        "Every statement in this set uses the same first two columns; only the Agree column changes.")
y = draw_lines(fig, LEFT, y, wrap_to_width(note, fonts["regular"], 22, (RIGHT - LEFT) * W_PX),
               22, fonts["regular"], INK)
save(fig, "m2_worked_example.png", cap, y)

plt.close(_measure_fig)
print("done")
