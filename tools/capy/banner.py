"""The "RESPONSE INCOMING" banner (brand.md sec 8, 2026-09-20).

A big top-of-frame title over the opening clip only, until Saint Capybara
first speaks. The window is derived from beat order, never scripted:
it covers the leading run of `clip` beats and ends at the first beat of
any other kind. Rendered once as a transparent full-canvas PNG and
composited by capy_render_beat_clips.py (not baked into the plate PNGs).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from capy.layout import CaptionZone, Theme
from capy.text import _measure, draw_lines, fit_text

BANNER_FILENAME = "banner_response_incoming.png"


def banner_beat_ids(doc: dict) -> set[str]:
    """Ids of the leading run of `clip` beats. Empty when the script opens
    with anything other than a clip (no banner then)."""
    ids: set[str] = set()
    for beat in doc.get("beats", []):
        if beat.get("kind") != "clip":
            break
        ids.add(beat["id"])
    return ids


def render_banner(theme: Theme, out_path: Path) -> Path:
    spec = theme.response_banner()
    w, h = theme.canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    stroke = spec["stroke_px"]
    font, lines = fit_text(
        spec["text"], theme.font_path(spec["font"]),
        size=spec["size"], min_size=spec["min_size"], step=4,
        max_w=spec["max_width"], max_lines=1, stroke=stroke,
    )
    pill = spec.get("pill")
    zone = CaptionZone(y0=spec["y0"], y1=spec["y1"], max_width=spec["max_width"], x_center=w // 2)
    draw_lines(
        img, lines, font, zone,
        fill=theme.color_rgba(spec["primary"]), stroke_px=stroke,
        stroke_fill=theme.color_rgba(spec["outline"]),
        pill=pill, pill_color=theme.color_rgba(pill["color"], pill["alpha"]) if pill else None,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path
