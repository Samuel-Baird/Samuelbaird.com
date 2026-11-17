#!/usr/bin/env python3
"""Render on-screen meme text as a transparent full-frame PNG overlay for
the meme/edit video type (docs/types/meme-edit.md).

    python tools/meme_text.py "when the bishop says 'quick announcement'" --out overlays/t01.png
    python tools/meme_text.py "..." --out overlays/t02.png --position bottom --brand saint-capybara
    python tools/meme_text.py "..." --out overlays/t03.png --width 1920 --height 1080 --font C:\\Windows\\Fonts\\arialbd.ttf

Classic meme treatment: white fill, thick black stroke, wrapped by measured
pixel width (capy.text.fit_text -- never a character-count guess) inside a
platform-UI-safe zone, shrinking toward --min-size before allowing an extra
line. The PNG is placed as a still on its own Resolve video track over the
footage, the same way quote cards are (docs/pipeline.md sec 3).

Fonts are brand-specific and must not cross over (docs/types/meme-edit.md
"Brand"): `--brand saint-capybara` uses that brand's own body font from
assets/saint-capybara/theme.yaml; `--brand standard` (the default) uses
Impact from the Windows font folder unless --font is given. Saves with no
PNG metadata chunks either way (brand.md sec 10's image rule).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capy.text import fit_text, _measure  # noqa: E402

STANDARD_FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\impact.ttf"),
    Path("/usr/share/fonts/truetype/msttcorefonts/Impact.ttf"),
    Path("/Library/Fonts/Impact.ttf"),
]

# Vertical safe zones as fractions of frame height. On 9:16 the top ~13%
# and bottom ~18% sit under Reels/Shorts/TikTok UI chrome (the same
# assumption theme.yaml's layout block documents); landscape has no
# overlay chrome, so a plain 6% margin is enough.
ZONES_VERTICAL = {"top": (0.14, 0.32), "center": (0.40, 0.60), "bottom": (0.62, 0.80)}
ZONES_LANDSCAPE = {"top": (0.06, 0.30), "center": (0.38, 0.62), "bottom": (0.70, 0.94)}


def resolve_font(brand: str, font: str | None) -> Path:
    if font:
        p = Path(font)
        if not p.exists():
            raise SystemExit(f"--font not found: {p}")
        return p
    if brand == "saint-capybara":
        from capy.palette import font_path, load_theme
        return font_path(load_theme(), "body")
    for p in STANDARD_FONT_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit("Impact not found -- pass --font <path to a bold .ttf>")


def render(text: str, out: Path, *, width: int, height: int, position: str, font_file: Path,
           size: int, min_size: int, max_lines: int, upper: bool) -> None:
    if upper:
        text = text.upper()
    zones = ZONES_VERTICAL if height > width else ZONES_LANDSCAPE
    f0, f1 = zones[position]
    y0, y1 = int(height * f0), int(height * f1)
    max_w = int(width * 0.88)
    stroke = max(3, size // 12)
    font, lines = fit_text(text, font_file, size=size, min_size=min_size, step=4,
                           max_w=max_w, max_lines=max_lines, stroke=stroke)
    stroke = max(3, font.size // 12)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    line_h = int(font.size * 1.1)
    ty = (y0 + y1) // 2 - line_h * len(lines) // 2
    for line in lines:
        tx = width // 2 - int(_measure(draw, line, font, stroke)) // 2
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255),
                  stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
        ty += line_h

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", pnginfo=None)
    print(f"Wrote {out} ({width}x{height}, {position}, {font.size}px, {len(lines)} line(s))")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--position", choices=["top", "center", "bottom"], default="top")
    ap.add_argument("--brand", choices=["standard", "saint-capybara"], default="standard")
    ap.add_argument("--font", help="override the brand's default font (.ttf path)")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--size", type=int, default=96)
    ap.add_argument("--min-size", type=int, default=60)
    ap.add_argument("--max-lines", type=int, default=3)
    ap.add_argument("--no-upper", dest="upper", action="store_false",
                    help="keep the text's own casing (default: ALL CAPS)")
    args = ap.parse_args()

    render(args.text, args.out, width=args.width, height=args.height, position=args.position,
           font_file=resolve_font(args.brand, args.font), size=args.size, min_size=args.min_size,
           max_lines=args.max_lines, upper=args.upper)
    return 0


if __name__ == "__main__":
    sys.exit(main())
