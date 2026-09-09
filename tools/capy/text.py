"""Fit-to-width text layout for captions and card text.

Replaces the old character-count wrap (`plates._wrap_text`,
`capy_caption_cards._render_phrase_png`'s char-count split), which is what
produced the shipped clipping bug: a 34-char line at 68px is ~1100px wide
on a 1080px canvas and gets cut off at both edges. Everything here wraps
by measured pixel width (`font.getlength`) and shrinks the font size as a
last resort instead of ever emitting an unmeasured line.

    from capy.text import fit_text, draw_lines

    font, lines = fit_text(text, font_path, size=84, min_size=60, step=4,
                            max_width=960, max_lines=2, stroke=6)
    draw_lines(img, lines, font, zone, fill=..., stroke_px=6, stroke_fill=...)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke: int) -> float:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    return bbox[2] - bbox[0]


def wrap_by_width(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_w: int,
    stroke: int = 0,
    *,
    draw: ImageDraw.ImageDraw | None = None,
) -> list[str]:
    """Greedy word-wrap: a line grows while it measures within max_w. A
    single word wider than max_w on its own becomes its own (overflowing)
    line -- the caller's shrink loop (fit_text) is what actually prevents
    that in practice."""
    if draw is None:
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if cur and _measure(draw, trial, font, stroke) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def fit_text(
    text: str,
    font_path: Path,
    *,
    size: int,
    min_size: int,
    step: int,
    max_w: int,
    max_lines: int,
    stroke: int = 0,
    beat_id: str | None = None,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Shrink `size` down to `min_size` (in steps of `step`) looking for the
    largest size at which `text` wraps into <= max_lines lines that each
    measure within max_w. If even `min_size` overflows, return the
    min_size wrap allowing one extra line (never silently clip) and print
    a warning naming the beat/phrase so it doesn't ship unnoticed."""
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    last_font = None
    last_lines: list[str] = []
    for s in range(size, min_size - 1, -step):
        font = ImageFont.truetype(str(font_path), s)
        lines = wrap_by_width(text, font, max_w, stroke, draw=draw)
        last_font, last_lines = font, lines
        if len(lines) <= max_lines and all(_measure(draw, ln, font, stroke) <= max_w for ln in lines):
            return font, lines
    # Last resort at min_size: allow one extra line rather than clip.
    font = ImageFont.truetype(str(font_path), min_size)
    lines = wrap_by_width(text, font, max_w, stroke, draw=draw)
    overflow = [ln for ln in lines if _measure(draw, ln, font, stroke) > max_w]
    if len(lines) > max_lines or overflow:
        loc = f" [{beat_id}]" if beat_id else ""
        print(
            f"warning: text still overflows at min_size={min_size}{loc}: "
            f"{len(lines)} lines (max {max_lines}), {len(overflow)} line(s) over {max_w}px -- {text!r}",
            file=sys.stderr,
        )
    return font, lines


def draw_lines(
    img: Image.Image,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    zone,  # capy.layout.CaptionZone
    *,
    fill: tuple[int, int, int, int],
    stroke_px: int,
    stroke_fill: tuple[int, int, int, int],
    line_height_mult: float = 1.15,
    highlight_words: set[str] | None = None,
    highlight_color: tuple[int, int, int, int] | None = None,
    pill: dict | None = None,
    pill_color: tuple[int, int, int, int] | None = None,
) -> None:
    """Draw `lines`, vertically centred in `zone`, each line horizontally
    centred at `zone.x_center`. Draws per-word so a highlighted word can
    get its own fill color. An optional pill (single rounded-corner-free
    rectangle sized to the widest line) is drawn behind the whole block
    first, e.g. for source captions over busy video."""
    draw = ImageDraw.Draw(img)
    highlight_words = highlight_words or set()
    line_h = int(font.size * line_height_mult)
    total_h = line_h * len(lines)
    cy = (zone.y0 + zone.y1) // 2
    ty0 = cy - total_h // 2

    if pill and lines:
        widest = max(_measure(draw, ln, font, stroke_px) for ln in lines)
        pad_x, pad_y = pill.get("pad_x", 24), pill.get("pad_y", 16)
        draw.rectangle(
            [
                zone.x_center - widest // 2 - pad_x,
                ty0 - pad_y,
                zone.x_center + widest // 2 + pad_x,
                ty0 + total_h + pad_y,
            ],
            fill=pill_color,
        )

    ty = ty0
    for line in lines:
        tw = _measure(draw, line, font, stroke_px)
        tx = zone.x_center - int(tw) // 2
        cursor_x = tx
        for word in line.split():
            is_hl = highlight_color is not None and word.strip(",.!?’'\"") in highlight_words
            color = highlight_color if is_hl else fill
            draw.text((cursor_x, ty), word, font=font, fill=color, stroke_width=stroke_px, stroke_fill=stroke_fill)
            word_w = _measure(draw, word + " ", font, stroke_px)
            cursor_x += word_w
        ty += line_h
