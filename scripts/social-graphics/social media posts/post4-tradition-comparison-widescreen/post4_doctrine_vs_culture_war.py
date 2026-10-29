#!/usr/bin/env python3
"""12_doctrine_vs_culture_war.png -- a two-column companion to post4's
"Still the beam" card (11_closing.png): the doctrine ranges from that card on
the left, the culture-war ranges on the right, 

Ranges are computed from the same per-tradition percentages the post4 charts
use (post4_tradition_comparison_widescreen.R / post2's data block), not typed
by hand, so they can't drift from the charts. If those percentages change,
change PCT below; the asserts check the doctrine side against the numbers
printed on 11_closing.png.

matplotlib rather than R for the same reason as post4_intro_cards.py (R not
installed on the authoring machine); same tokens, fonts, 1920x1080 canvas.
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
WINE = "#8C4A5F"
ACCENT = "#1f4f7a"
BORDER = "#D9D5CC"

FIG_W_IN, FIG_H_IN, DPI = 16, 9, 120

SCRIPT_DIR = Path(__file__).resolve().parent
FONTS_DIR = (SCRIPT_DIR.parents[2] / "state-of-theology-graphics" / "fonts").resolve()
OUT = SCRIPT_DIR / "png"
OUT.mkdir(parents=True, exist_ok=True)

# % of each tradition (Evangelical, Black Protestant, Mainline, Catholic) in
# the direction each statement is plotted in post4 -- State of Theology 2025,
# except Arianism (2022; dropped from the 2025 wave).
PCT = {
    "trinity":  [95, 92, 89, 89],  # agree
    "arian":    [61, 78, 61, 71],  # agree
    "spirit":   [52, 65, 73, 68],  # agree
    "teacher":  [34, 55, 52, 50],  # agree
    "abortion": [73, 63, 50, 55],  # agree it is a sin
    "sex":      [82, 73, 55, 49],  # agree it is a sin
    "homo":     [74, 52, 50, 41],  # DISagree that the condemnation no longer applies
    "gender":   [77, 65, 61, 53],  # DISagree with choosing gender regardless of sex
}


def rng(key: str) -> str:
    return f"{min(PCT[key])}–{max(PCT[key])}%"


def spread(keys: list[str]) -> tuple[int, int]:
    s = [max(PCT[k]) - min(PCT[k]) for k in keys]
    return min(s), max(s)


assert [rng(k) for k in ("trinity", "arian", "spirit", "teacher")] == [
    "89–95%", "61–78%", "52–73%", "34–55%"]  # = 11_closing.png

DOCTRINE = ["trinity", "arian", "spirit", "teacher"]
CULTURE = ["abortion", "sex", "homo", "gender"]
d_lo, d_hi = spread(DOCTRINE)
c_lo, c_hi = spread(CULTURE)

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

fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
fig.patch.set_facecolor(PAPER)
W_PX = FIG_W_IN * DPI


def width_px(text: str, fp: fm.FontProperties, fs: float) -> float:
    fig.canvas.draw()
    t = fig.text(0, 0, text, fontproperties=fp, fontsize=fs)
    fig.canvas.draw()
    w = t.get_window_extent(renderer=fig.canvas.get_renderer()).width
    t.remove()
    return w


def wrap(text: str, fs: float, first_px: float, rest_px: float) -> list[str]:
    lines, cur, limit = [], "", first_px
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if not cur or width_px(trial, fonts["regular"], fs) <= limit:
            cur = trial
        else:
            lines.append(cur)
            cur, limit = word, rest_px
    if cur:
        lines.append(cur)
    return lines


def step(fs: float, leading: float) -> float:
    return fs * leading / 72 / FIG_H_IN


LEFT, RIGHT = 0.045, 0.94
caption_top = draw_caption_bottom(
    fig, fonts, [], left=LEFT, fontsize=16, color=MUTED,
    handle="Data: The State of Theology survey  |  @ithinkisam", bottom=0.045,
)
fig.text(LEFT, 0.95, "Doctrine and culture war", fontproperties=fonts["title"], fontsize=52,
         color=INK, ha="left", va="top")

COL_W = 0.415
COL_X = [LEFT, 0.525]
fs_item, lead = 28, 1.2
body_px = COL_W * W_PX
y_head = 0.79

# (range, rest of sentence, range colour) per column
columns = [
    ("Doctrine", [
        (rng("trinity"), "confess the Trinity.", INK),
        (rng("arian"), "say Jesus was created.", WINE),
        (rng("spirit"), "say the Spirit is not a person.", WINE),
        (rng("teacher"), "say Jesus was not God.", WINE),
    ]),
    ("Culture war", [
        (rng("abortion"), "say abortion is a sin.", ACCENT),
        (rng("sex"), "say sex outside traditional marriage is a sin.", ACCENT),
        (rng("homo"), "say the Bible’s condemnation of homosexual behavior still applies.", ACCENT),
        (rng("gender"), "reject choosing a gender regardless of biological sex.", ACCENT),
    ]),
]

bottom = 1.0
for x, (head, items) in zip(COL_X, columns):
    fig.text(x, y_head, head, fontproperties=fonts["bold"], fontsize=36, color=INK, ha="left", va="top")
    fig.text(x, y_head - step(36, 1.25), "Range across the four traditions", fontproperties=fonts["regular"],
             fontsize=20, color=MUTED, ha="left", va="top")
    y = y_head - step(36, 1.25) - step(20, 1.25) - 0.03
    for num, text, color in items:
        num_w = width_px(num + " ", fonts["bold"], fs_item)
        lines = wrap(text, fs_item, body_px - num_w, body_px)
        fig.text(x, y, num, fontproperties=fonts["bold"], fontsize=fs_item, color=color, ha="left", va="top")
        fig.text(x + num_w / W_PX, y, lines[0], fontproperties=fonts["regular"], fontsize=fs_item,
                 color=INK, ha="left", va="top")
        y -= step(fs_item, lead)
        for ln in lines[1:]:
            fig.text(x, y, ln, fontproperties=fonts["regular"], fontsize=fs_item, color=INK, ha="left", va="top")
            y -= step(fs_item, lead)
        y -= 0.022
    bottom = min(bottom, y)

# Column divider
fig.add_artist(plt.Line2D([0.5, 0.5], [bottom + 0.02, y_head], color=BORDER, linewidth=2,
                          transform=fig.transFigure))

y = bottom

if y < caption_top:
    print(f"WARNING: body (bottom {y:.4f}) overlaps caption (top {caption_top:.4f})")

fig.savefig(OUT / "12_doctrine_vs_culture_war.png", facecolor=PAPER, dpi=DPI)
print("wrote 12_doctrine_vs_culture_war.png", f"doctrine gaps {d_lo}-{d_hi}, culture gaps {c_lo}-{c_hi}")
