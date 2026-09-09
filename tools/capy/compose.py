"""Compose a Saint Capybara sprite frame from parts + a pose recipe.

    from capy.compose import compose, upscale, contact_sheet
    img = compose("neutral", variant)          # 128x128 RGBA (logical grid)
    img_b = compose("talking", variant, mouth_open=True)  # 2nd talking frame
    big = upscale(img, 4)                       # 512x512, nearest-neighbor

Every part in parts.py draws true curves (ellipses, not rounded
rectangles) directly on the CANVASxCANVAS logical grid, hard-edged (PIL's
plain ImageDraw does not anti-alias) -- see parts.py's module docstring
for why that, not a supersample-then-blur pass, is what fixes the
"boxy"/"gumdrop" look while keeping a genuine pixel-art edge instead of
sliding into smooth flat-vector art. capy.parts.SUPERSAMPLE is a no-op
kept only for API stability.

See parts.py for the individual part-drawing functions and poses.py for
the pose recipes / rhetorical-function mapping.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from capy import parts
from capy.poses import POSES
from capy.palette import font_path


def compose(pose_name: str, variant: dict, *, mouth_open: bool = False) -> Image.Image:
    """Render one CANVASxCANVAS (128x128) RGBA frame for `pose_name`
    using `variant`.

    If mouth_open is True and the pose defines a `mouth_open` alternate
    mouth style, that style is used instead of the pose's resting mouth
    (this is the 2nd frame of the talking flicker; see
    poses.TALKING_CAPABLE and capy_render.py).
    """
    pose = POSES[pose_name]
    internal = parts.CANVAS * parts.SUPERSAMPLE
    canvas = Image.new("RGBA", (internal, internal), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    theme = _theme_cache()

    dy = pose.get("head_dy", 0)

    parts.draw_halo(draw, theme, variant)
    body_box = parts.draw_body(draw, theme, variant)  # draws ears internally, behind the body outline
    snout_box = parts.draw_snout(draw, theme, variant, body_box)

    # Face parts (eyes, brows, nose/mouth) share a small vertical offset
    # so a "looking down/up" pose (reading, disappointed, ...) reads
    # clearly, without moving the body/ears/snout outline itself.
    face_layer = Image.new("RGBA", (internal, internal), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(face_layer)
    parts.draw_eyes(fdraw, theme, variant, body_box, style=pose.get("eyes", "open"))
    parts.draw_brows(fdraw, theme, variant, body_box, style=pose.get("brows", "neutral"))
    mouth_style = pose.get("mouth_open") if (mouth_open and pose.get("mouth_open")) else pose.get("mouth", "closed")
    parts.draw_nose_mouth(fdraw, theme, variant, snout_box, style=mouth_style)
    canvas.alpha_composite(face_layer, (0, dy * parts.SUPERSAMPLE))

    for prop in pose.get("props", []):
        if prop == "books_left":
            parts.draw_books_pile(draw, theme, variant, body_box, side="left")
        elif prop == "books_right":
            parts.draw_books_pile(draw, theme, variant, body_box, side="right")
        elif prop == "papers":
            parts.draw_papers(draw, theme, variant, body_box)

    parts.draw_paws(draw, theme, variant, body_box, style=pose.get("paws", "rest"))
    parts.draw_crucifix(draw, theme, variant, body_box)

    for extra in pose.get("extras", []):
        parts.draw_extra(draw, theme, variant, body_box, extra)

    if internal != parts.CANVAS:
        # Only relevant if SUPERSAMPLE is ever set above 1 again; kept
        # as NEAREST (not LANCZOS) so it would never introduce the
        # anti-aliased "flat vector" look described in parts.py.
        canvas = canvas.resize((parts.CANVAS, parts.CANVAS), resample=Image.NEAREST)
    return canvas


_THEME_SINGLETON = None


def _theme_cache():
    global _THEME_SINGLETON
    if _THEME_SINGLETON is None:
        from capy.palette import load_theme

        _THEME_SINGLETON = load_theme()
    return _THEME_SINGLETON


def upscale(img: Image.Image, factor: int = 4) -> Image.Image:
    """Nearest-neighbor upscale from the logical grid -- the only
    resampling used at THIS stage, to keep hard pixel edges once the
    frame has already been pixelated by compose()."""
    w, h = img.size
    return img.resize((w * factor, h * factor), resample=Image.NEAREST)


def save_png(img: Image.Image, path) -> None:
    """Save with no text/metadata chunks (anonymity requirement -- see
    docs/saint-capybara/brand.md 'Operational anonymity checklist')."""
    img.save(path, format="PNG")


def contact_sheet(
    labeled_images: list[tuple[str, Image.Image]],
    *,
    cols: int = 4,
    cell: int = 260,
    pad: int = 16,
    label_h: int = 28,
) -> Image.Image:
    """Lay out (label, image) pairs on a plain white contact sheet with
    a label under each cell. Images are pasted centered, already at
    whatever scale the caller passed in."""
    n = len(labeled_images)
    rows = (n + cols - 1) // cols
    sheet_w = cols * (cell + pad) + pad
    sheet_h = rows * (cell + label_h + pad) + pad
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        theme = _theme_cache()
        font = ImageFont.truetype(str(font_path(theme, "display")), 14)
    except Exception:
        font = ImageFont.load_default()

    for i, (label, img) in enumerate(labeled_images):
        row, col = divmod(i, cols)
        cx = pad + col * (cell + pad)
        cy = pad + row * (cell + label_h + pad)
        thumb = img
        if thumb.width > cell or thumb.height > cell:
            ratio = min(cell / thumb.width, cell / thumb.height)
            thumb = thumb.resize(
                (max(1, int(thumb.width * ratio)), max(1, int(thumb.height * ratio))),
                resample=Image.NEAREST,
            )
        ox = cx + (cell - thumb.width) // 2
        oy = cy + (cell - thumb.height) // 2
        checker = Image.new("RGBA", (cell, cell), (235, 235, 235, 255))
        sheet.paste(checker, (cx, cy))
        sheet.paste(thumb, (ox, oy), thumb if thumb.mode == "RGBA" else None)
        draw.rectangle([cx, cy, cx + cell, cy + cell], outline=(180, 180, 180, 255))
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((cx + (cell - tw) // 2, cy + cell + 6), label, fill=(20, 20, 20, 255), font=font)

    return sheet
