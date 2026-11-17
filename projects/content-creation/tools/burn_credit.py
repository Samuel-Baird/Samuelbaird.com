#!/usr/bin/env python3
"""Burn a small bottom-left source credit into an image.

Per ../docs/style-guide.md: small text on a low-opacity chip in the
bottom-left corner -- never a full-width caption bar. Writes a new file by
default so the original stays untouched; pass --in-place to overwrite.

Usage:
    python burn_credit.py --image images/roman_domus.jpg \
        --credit "Wikimedia Commons / public domain" \
        --out images/roman_domus_credited.jpg
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
TEXT_COLOR = (240, 240, 240)
CHIP_COLOR = (0, 0, 0, 140)
MARGIN = 24
PADDING = 10
FONT_SIZE_FRACTION = 0.018  # of image width, so the credit scales with resolution


def find_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--credit", required=True, help='e.g. "Wikimedia Commons / public domain"')
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    if not args.in_place and args.out is None:
        parser.error("pass --out PATH or --in-place")

    base = Image.open(args.image).convert("RGB")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    font_size = max(14, int(base.width * FONT_SIZE_FRACTION))
    font = find_font(font_size)
    label = f"Source: {args.credit}"

    text_bbox = draw.textbbox((0, 0), label, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    chip_x0 = MARGIN
    chip_y0 = base.height - MARGIN - text_h - 2 * PADDING
    chip_x1 = chip_x0 + text_w + 2 * PADDING
    chip_y1 = base.height - MARGIN

    draw.rectangle([chip_x0, chip_y0, chip_x1, chip_y1], fill=CHIP_COLOR)
    draw.text((chip_x0 + PADDING, chip_y0 + PADDING - text_bbox[1]), label, font=font, fill=TEXT_COLOR)

    result = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

    out_path = args.image if args.in_place else args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(str(out_path))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
