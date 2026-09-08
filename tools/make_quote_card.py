#!/usr/bin/env python3
"""Render the one quote-card template used across every video.

See ../docs/style-guide.md for the spec this implements: 1920x1080, dark
charcoal background, cream serif quote text auto-shrunk to fit within a
line cap, a thin accent rule, and a smaller attribution line bottom-right.

Usage:
    python make_quote_card.py \
        --quote "Let a man examine himself, and so let him eat of that bread." \
        --attribution "1 Corinthians 11:28" \
        --out cards/1-corinthians-11-28.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1920, 1080)
BACKGROUND = (26, 26, 26)          # #1a1a1a
TEXT_COLOR = (240, 235, 220)       # cream
RULE_COLOR = (240, 235, 220, 110)  # cream, reduced opacity
MARGIN_FRACTION = 0.12             # 12% of width each side
MAX_LINES = 6
MAX_QUOTE_PT = 90
MIN_QUOTE_PT = 32
ATTRIBUTION_PT = 30

SERIF_CANDIDATES = [
    r"C:\Windows\Fonts\georgia.ttf",
    r"C:\Windows\Fonts\georgiab.ttf",
    r"C:\Windows\Fonts\times.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = SERIF_CANDIDATES
    if bold:
        candidates = [c for c in candidates if "b.ttf" in c.lower()] + candidates
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_quote(draw: ImageDraw.ImageDraw, quote: str, max_width: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for pt in range(MAX_QUOTE_PT, MIN_QUOTE_PT - 1, -2):
        font = find_font(pt)
        lines = wrap_text(draw, quote, font, max_width)
        if len(lines) <= MAX_LINES:
            return font, lines
    # Fall through: smallest size, however many lines it takes.
    font = find_font(MIN_QUOTE_PT)
    return font, wrap_text(draw, quote, font, max_width)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quote", required=True)
    parser.add_argument("--attribution", required=True,
                         help='e.g. "-- Justin Martyr, First Apology, c. 155 AD" '
                              '(a leading "-- " is added automatically if missing)')
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    img = Image.new("RGB", CANVAS_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(img, "RGBA")

    width, height = CANVAS_SIZE
    margin = int(width * MARGIN_FRACTION)
    max_text_width = width - 2 * margin

    quote_font, lines = fit_quote(draw, args.quote.strip(), max_text_width)
    line_height = int(quote_font.size * 1.35)
    block_height = line_height * len(lines)

    attribution = args.attribution.strip()
    if not attribution.startswith("--") and not attribution.startswith("\u2014"):
        attribution = f"\u2014 {attribution}"
    attribution_font = find_font(ATTRIBUTION_PT)

    rule_gap_above = 40
    rule_gap_below = 30
    attribution_h = int(attribution_font.size * 1.3)
    total_h = block_height + rule_gap_above + 2 + rule_gap_below + attribution_h
    top = (height - total_h) // 2

    y = top
    for line in lines:
        line_width = draw.textlength(line, font=quote_font)
        x = (width - line_width) / 2
        draw.text((x, y), line, font=quote_font, fill=TEXT_COLOR)
        y += line_height

    rule_y = y + rule_gap_above
    rule_width = int(width * 0.22)
    rule_x0 = (width - rule_width) / 2
    draw.line([(rule_x0, rule_y), (rule_x0 + rule_width, rule_y)], fill=RULE_COLOR, width=2)

    attr_y = rule_y + rule_gap_below
    attr_width = draw.textlength(attribution, font=attribution_font)
    draw.text((width - margin - attr_width, attr_y), attribution, font=attribution_font, fill=TEXT_COLOR)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(args.out))
    print(f"Wrote {args.out} ({quote_font.size}pt, {len(lines)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
