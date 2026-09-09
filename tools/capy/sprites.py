"""Render a pose's finalized sprite art into a full-canvas RGBA layer,
sized/positioned per a `capy.layout.SpriteSpec`, with a disk cache so the
25 finalized 1254x1254 (~1.5MB) PNGs aren't re-cropped/re-scaled on every
beat plate.

    from capy.sprites import render_sprite
    layer = render_sprite(theme, "reading", theme.sprite_spec("host"))
    img.alpha_composite(layer)

The finalized art's usable region is not uniform: most poses are
1254x1254 with the figure roughly filling ~0.9 of the canvas, but `quote`
is a 1448x1086 canvas and `researching`'s alpha bbox touches x=0 -- so
fitting is always by the alpha bounding box, bottom-aligned to
`theme.sprite_bottom`, never "resize the raw canvas to a square box".

`saint-capybara-deadpan.png` is a known art defect (flagged in
docs/saint-capybara/brand.md and the overhaul plan): it has no alpha
channel at all, so naively compositing it paints a solid black square
behind the figure. `render_sprite` detects this (a sprite whose corner
pixels, after RGBA conversion, are opaque) and raises rather than
silently shipping a black box -- see SpriteArtError below.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageFilter

from capy.layout import CaptionZone, SpriteSpec, Theme  # noqa: F401 (SpriteSpec/CaptionZone re-exported for callers)

_CORNER_MARGIN = 2


class SpriteArtError(RuntimeError):
    pass


def _alpha_bbox_crop(im: Image.Image) -> Image.Image:
    """Crop `im` (RGBA) to its alpha channel's bounding box. Raises
    SpriteArtError if the art has no usable transparency (the deadpan
    defect) or is fully transparent (a blank/broken file)."""
    if im.mode != "RGBA":
        raise SpriteArtError(
            f"sprite has no alpha channel (mode={im.mode}) -- known defect, see "
            "docs/saint-capybara/brand.md sec 4 quality checklist; regenerate from the master prompt."
        )
    alpha = im.split()[-1]
    corners = [
        alpha.getpixel((0, 0)),
        alpha.getpixel((im.width - 1, 0)),
        alpha.getpixel((0, im.height - 1)),
        alpha.getpixel((im.width - 1, im.height - 1)),
    ]
    if all(c > 250 for c in corners):
        raise SpriteArtError(
            "sprite's corners are opaque -- looks like a baked-in solid background rather than "
            "real transparency (the deadpan defect); regenerate from the master prompt before using this pose."
        )
    bbox = alpha.getbbox()
    if bbox is None:
        raise SpriteArtError("sprite is fully transparent -- broken or blank file")
    return im.crop(bbox)


def _cache_key(theme: Theme, pose: str, spec: SpriteSpec) -> str:
    shadow = spec.shadow or {}
    ground = spec.ground_shadow or {}
    parts = [
        pose,
        f"b{spec.box[0]}_{spec.box[1]}_{spec.box[2]}_{spec.box[3]}",
        f"o{spec.outline_px}",
        f"s{shadow.get('dx',0)}x{shadow.get('dy',0)}a{shadow.get('alpha',0)}",
        f"g{ground.get('rx',0)}x{ground.get('ry',0)}a{ground.get('alpha',0)}",
        theme.sprite_hash(pose)[:8],
        f"v{theme.layout_version}",
    ]
    return "__".join(parts)


def render_sprite(theme: Theme, pose: str, spec: SpriteSpec, *, use_cache: bool = True) -> Image.Image:
    """A full-canvas RGBA layer with `pose`'s sprite art fitted into
    `spec.box`, bottom-aligned (feet on theme.sprite_bottom), with the
    box's outline/shadow already composited. Cached on disk under
    theme.cache_dir('sprites')."""
    canvas_w, canvas_h = theme.canvas_size
    cache_key = _cache_key(theme, pose, spec)
    cache_path = None
    if use_cache:
        try:
            cache_path = theme.cache_dir("sprites") / f"{cache_key}.png"
            if cache_path.exists():
                return Image.open(cache_path).convert("RGBA")
        except Exception:
            cache_path = None  # cache unavailable (e.g. drive missing) -- render without it

    src_path = theme.finalized_sprite_path(pose)
    if not src_path.exists():
        src_path = theme.sprite_path(pose)
    src = Image.open(src_path).convert("RGBA")
    cropped = _alpha_bbox_crop(src)

    x0, y0, x1, y1 = spec.box
    box_size = x1 - x0
    ratio = box_size / max(cropped.width, cropped.height)
    new_w, new_h = max(1, round(cropped.width * ratio)), max(1, round(cropped.height * ratio))
    scaled = cropped.resize((new_w, new_h), Image.LANCZOS)

    # Bottom-align within the box; horizontally center within the box.
    px = x0 + (box_size - new_w) // 2
    py = y1 - new_h

    layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    if spec.ground_shadow:
        gs = spec.ground_shadow
        cx = x0 + box_size // 2
        shadow_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(shadow_img)
        d.ellipse(
            [cx - gs["rx"], y1 - gs["ry"], cx + gs["rx"], y1 + gs["ry"]],
            fill=(0, 0, 0, gs["alpha"]),
        )
        layer.alpha_composite(shadow_img)

    if spec.shadow:
        sh = spec.shadow
        alpha = scaled.split()[-1]
        silhouette = Image.new("RGBA", scaled.size, (0, 0, 0, 0))
        silhouette.putalpha(alpha.point(lambda a: sh["alpha"] if a > 0 else 0))
        layer.alpha_composite(silhouette, (px + sh["dx"], py + sh["dy"]))

    if spec.outline_px:
        r = spec.outline_px
        alpha = scaled.split()[-1]
        dilated = alpha.filter(ImageFilter.MaxFilter(2 * r + 1))
        outline_layer = Image.new("RGBA", scaled.size, (0, 0, 0, 0))
        ink = theme.color("ink")
        outline_layer.putalpha(dilated)
        outline_layer_rgb = Image.new("RGBA", scaled.size, ink + (0,))
        outline_layer_rgb.putalpha(dilated)
        layer.alpha_composite(outline_layer_rgb, (px, py))

    layer.alpha_composite(scaled, (px, py))

    if cache_path is not None:
        try:
            layer.save(cache_path)  # PIL default PNG save carries no text/metadata chunks
        except Exception:
            pass

    return layer
