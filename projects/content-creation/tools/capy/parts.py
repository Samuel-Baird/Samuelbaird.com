"""Saint Capybara sprite parts (v3 -- true curves, drawn hard-edged at 128px).

v1 drew a person-shaped monk (robed body, held Bible) that read as a bear
in a robe. v2 fixed the anatomy (continuous body+head, two-tone muzzle,
tucked ears) but built every shape from `rounded_rectangle`, which reads
as boxy/"gumdrop" regardless of anatomy. There is no text-to-image
generation tool available in this environment (checked: Adobe's MCP only
edits existing images -- it says so explicitly on its selection tools --
and Canva's generator produces whole marketing documents, not isolated
transparent sprite frames with pose-to-pose consistency), so getting a
properly round, plush silhouette has to come from a better drawing
technique within PIL, not a different tool.

v3's fix: every part is drawn with true ellipses (not rounded rectangles)
directly on the CANVAS x CANVAS logical grid. An early version of this
fix supersampled at 8x and downsampled with a quality filter (LANCZOS)
for smoother curves, but that produced soft anti-aliased edges that read
as flat vector art, not pixel art -- it lost the hard-edged "stair-step"
look the brief explicitly asks for (8/16-bit, clean pixel shapes, dark
outlines, icon-like retro sprite). PIL's plain ImageDraw does not
anti-alias, so drawing true ellipses directly at 128px keeps genuine
hard pixel edges while still tracing a correctly round capybara
silhouette -- the boxiness in v2 came from the rounded-rectangle
primitive, not from insufficient resolution. SUPERSAMPLE stays as a
no-op passthrough (kept for API stability / in case a supersampled path
is wanted for some other asset later); every part-drawing function below
works directly in CANVAS-space.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from capy.palette import rgba

CANVAS = 128        # logical pixel grid -- this IS the sprite resolution, no downsampling
SUPERSAMPLE = 1      # no-op; see module docstring for why this isn't 8

DEFAULT_VARIANT = {
    "body_rx": 46, "body_ry": 42,     # body ellipse half-width/-height
    "body_cy": 76,                     # body ellipse vertical center
    "snout_rx": 22, "snout_ry": 15,
    "snout_style": "round",             # "round" | "flat" (flatter bottom)
    "ear_r": 9,
    "ear_style": "small",               # "small" | "round" (bigger, rounder)
    "outline": 2,                        # outline width in LOGICAL px
    "fur": "fur",
    "fur_shade": "fur_shade",
    "snout_tone": "snout",
    "eye_style": "dot",                  # "dot" | "bead"
}


def _v(variant: dict, key: str):
    return variant.get(key, DEFAULT_VARIANT[key])


def _s(v):
    """Scale a single logical coordinate/length up to internal (supersample) space."""
    return v * SUPERSAMPLE


def _sbox(box):
    return [c * SUPERSAMPLE for c in box]


def _ellipse(draw, box, fill, outline=None, width=1):
    draw.ellipse(_sbox(box), fill=fill, outline=outline, width=_s(width) if width else 0)


def _rect(draw, box, fill, outline=None, width=0):
    draw.rectangle(_sbox(box), fill=fill, outline=outline, width=_s(width) if width else 0)


def _line(draw, points, fill, width=1):
    draw.line([(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points], fill=fill, width=_s(width))


def _arc(draw, box, start, end, fill, width=1):
    draw.arc(_sbox(box), start=start, end=end, fill=fill, width=_s(width))


# ---------------------------------------------------------------------------
# Fixed elements
# ---------------------------------------------------------------------------

def _body_geometry(variant: dict):
    """Central geometry so every part agrees on where the body actually is."""
    rx = _v(variant, "body_rx")
    ry = _v(variant, "body_ry")
    cy = _v(variant, "body_cy")
    cx = CANVAS / 2
    return cx, cy, rx, ry


def draw_halo(draw, theme, variant):
    gold = rgba(theme, "halo")
    shade = rgba(theme, "halo_shade")
    cx, cy, rx, ry = _body_geometry(variant)
    top = cy - ry  # approx top of the head, halo floats just above it
    _ellipse(draw, [cx - 32, top - 22, cx + 32, top - 6], None, outline=shade, width=4)
    _ellipse(draw, [cx - 30, top - 20, cx + 30, top - 8], None, outline=gold, width=2)


def draw_ears(draw, theme, variant):
    """Drawn BEFORE the body so the body ellipse buries the lower half of
    each ear -- what makes them read as attached tips, not floating
    shapes with a visible gap/seam."""
    fur = rgba(theme, _v(variant, "fur_shade"))
    outline = rgba(theme, "outline")
    ow = _v(variant, "outline")
    cx, cy, rx, ry = _body_geometry(variant)
    r = _v(variant, "ear_r")
    big = _v(variant, "ear_style") == "round"
    if big:
        r = int(r * 1.25)
    spread = rx * 0.52
    # Ear vertical center sits ON the body ellipse's own edge at that x
    # offset, so half is always buried regardless of body proportions.
    import math
    frac = min(0.98, spread / rx)
    edge_y = cy - ry * math.sqrt(max(0.0, 1 - frac * frac))
    for sign in (-1, 1):
        ex = cx + sign * spread
        _ellipse(draw, [ex - r, edge_y - r, ex + r, edge_y + r], fill=fur, outline=outline, width=ow)


def draw_body(draw, theme, variant):
    """The single continuous body+head mass -- a true ellipse (a real
    capybara has no neck and a rounded-oval silhouette), not a rounded
    rectangle. Returns (x0, y0, x1, y1) bounding box for other parts to
    anchor off of."""
    fur = rgba(theme, _v(variant, "fur"))
    shade = rgba(theme, _v(variant, "fur_shade"))
    outline = rgba(theme, "outline")
    ow = _v(variant, "outline")
    cx, cy, rx, ry = _body_geometry(variant)

    draw_ears(draw, theme, variant)
    box = [cx - rx, cy - ry, cx + rx, cy + ry]
    _ellipse(draw, box, fill=fur, outline=outline, width=ow)
    # A soft underside shading crescent for volume, capybara-loaf style.
    shade_box = [cx - rx * 0.75, cy + ry * 0.35, cx + rx * 0.75, cy + ry * 1.05]
    _ellipse(draw, shade_box, fill=shade)
    # Re-stroke the outline so the shading crescent never covers it.
    _ellipse(draw, box, fill=None, outline=outline, width=ow)
    return (cx - rx, cy - ry, cx + rx, cy + ry)


def draw_snout(draw, theme, variant, body_box):
    """The dominant 'reads as capybara' shape: a wide, low, two-tone
    muzzle patch across the lower-middle of the face -- an ellipse, not
    a rounded rectangle, so it blends into the round face instead of
    looking like a sticker applied on top."""
    x0, y0, x1, y1 = body_box
    tone = rgba(theme, _v(variant, "snout_tone"))
    outline = rgba(theme, "outline")
    cx = (x0 + x1) / 2
    srx = _v(variant, "snout_rx")
    sry = _v(variant, "snout_ry")
    scy = y1 - sry - 8  # bottom of muzzle stays clear of the body's own bottom edge
    box = [cx - srx, scy - sry, cx + srx, scy + sry]
    _ellipse(draw, box, fill=tone, outline=outline, width=1)
    return box


def draw_crucifix(draw, theme, variant, body_box):
    x0, y0, x1, y1 = body_box
    gold = rgba(theme, "crucifix")
    outline = rgba(theme, "outline")
    cx = (x0 + x1) / 2
    y = y1 - 16
    _rect(draw, [cx - 2, y, cx + 2, y + 14], fill=gold, outline=outline, width=1)
    _rect(draw, [cx - 6, y + 4, cx + 6, y + 8], fill=gold, outline=outline, width=1)


# ---------------------------------------------------------------------------
# Pose-specific held props -- NOT part of the fixed identity. Used only
# by the evidence-adjacent poses (reading, reading_source, researching)
# that need something in-frame for the show's format.
# ---------------------------------------------------------------------------

def draw_book(draw, theme, variant, cx, cy, open_book=False):
    cover = rgba(theme, "book_cover")
    pages = rgba(theme, "book_pages")
    outline = rgba(theme, "outline")
    if open_book:
        _rect(draw, [cx - 16, cy - 8, cx + 16, cy + 8], fill=pages, outline=outline, width=1)
        _line(draw, [(cx, cy - 8), (cx, cy + 8)], fill=outline, width=1)
    else:
        _rect(draw, [cx - 12, cy - 8, cx + 12, cy + 10], fill=cover, outline=outline, width=1)


def draw_scroll(draw, theme, variant, cx, cy):
    scroll = rgba(theme, "scroll")
    outline = rgba(theme, "outline")
    _ellipse(draw, [cx - 14, cy - 6, cx + 14, cy + 6], fill=scroll, outline=outline, width=1)
    _line(draw, [(cx - 8, cy - 6), (cx - 8, cy + 6)], fill=outline, width=1)
    _line(draw, [(cx + 8, cy - 6), (cx + 8, cy + 6)], fill=outline, width=1)


def draw_books_pile(draw, theme, variant, body_box, side="left"):
    x0, y0, x1, y1 = body_box
    outline = rgba(theme, "outline")
    colors = [rgba(theme, "book_cover"), rgba(theme, "fur_shade"), rgba(theme, "scroll")]
    bx = x0 - 6 if side == "left" else x1 + 6
    for i, c in enumerate(colors):
        y = y1 - 4 - i * 9
        box = [bx - 15, y - 8, bx + 1, y] if side == "left" else [bx - 1, y - 8, bx + 15, y]
        _rect(draw, box, fill=c, outline=outline, width=1)


def draw_papers(draw, theme, variant, body_box):
    x0, y0, x1, y1 = body_box
    paper = rgba(theme, "paper")
    outline = rgba(theme, "outline")
    _rect(draw, [x0 - 22, y1 - 26, x0 - 4, y1 - 4], fill=paper, outline=outline, width=1)
    _line(draw, [(x0 - 18, y1 - 18), (x0 - 8, y1 - 18)], fill=outline, width=1)
    _line(draw, [(x0 - 18, y1 - 12), (x0 - 8, y1 - 12)], fill=outline, width=1)


# ---------------------------------------------------------------------------
# Expression parts (vary by pose)
# ---------------------------------------------------------------------------

def draw_eyes(draw, theme, variant, body_box, style="open"):
    eye = rgba(theme, "eye")
    white = rgba(theme, "eye_white")
    x0, y0, x1, y1 = body_box
    cx = (x0 + x1) / 2
    y = y0 + (y1 - y0) * 0.42
    lx, rx = cx - 15, cx + 15
    if style in ("closed", "prayer_closed"):
        _line(draw, [(lx - 4, y), (lx + 4, y)], fill=eye, width=2)
        _line(draw, [(rx - 4, y), (rx + 4, y)], fill=eye, width=2)
        return
    if style == "half":
        _rect(draw, [lx - 4, y, lx + 4, y + 3], fill=eye)
        _rect(draw, [rx - 4, y, rx + 4, y + 3], fill=eye)
        return
    if style == "wide":
        for cxi in (lx, rx):
            _ellipse(draw, [cxi - 6, y - 6, cxi + 6, y + 6], fill=white, outline=eye, width=1)
            _ellipse(draw, [cxi - 2, y - 2, cxi + 2, y + 2], fill=eye)
        return
    if style == "narrow":
        _line(draw, [(lx - 5, y), (lx + 5, y)], fill=eye, width=3)
        _line(draw, [(rx - 5, y), (rx + 5, y)], fill=eye, width=3)
        return
    if style == "side":
        _rect(draw, [lx - 5, y - 2, lx - 1, y + 2], fill=eye)
        _rect(draw, [rx - 5, y - 2, rx - 1, y + 2], fill=eye)
        return
    # "open" default -- small close-set dot eyes (or bead style variant)
    if _v(variant, "eye_style") == "dot":
        for cxi in (lx, rx):
            _rect(draw, [cxi - 2, y - 2, cxi + 2, y + 2], fill=eye)
    else:
        r = 4
        for cxi in (lx, rx):
            _ellipse(draw, [cxi - r, y - r, cxi + r, y + r], fill=eye)


def draw_brows(draw, theme, variant, body_box, style="neutral"):
    if style == "neutral":
        return
    brow = rgba(theme, "brow")
    x0, y0, x1, y1 = body_box
    cx = (x0 + x1) / 2
    y = y0 + (y1 - y0) * 0.30
    lx, rx = cx - 15, cx + 15
    if style == "raised":
        _line(draw, [(lx - 6, y - 2), (lx + 6, y - 4)], fill=brow, width=2)
        _line(draw, [(rx - 6, y - 4), (rx + 6, y - 2)], fill=brow, width=2)
    elif style == "furrowed":
        _line(draw, [(lx - 6, y + 2), (lx + 6, y - 2)], fill=brow, width=2)
        _line(draw, [(rx - 6, y - 2), (rx + 6, y + 2)], fill=brow, width=2)
    elif style == "asym":
        _line(draw, [(lx - 6, y - 4), (lx + 6, y)], fill=brow, width=2)
        _line(draw, [(rx - 6, y), (rx + 6, y)], fill=brow, width=2)


def draw_nose_mouth(draw, theme, variant, snout_box, style="closed"):
    """Small dark nose+mouth glyph centered in the snout patch -- the
    stubby vertical mark with a base tick that reads as a rodent
    nose/mouth in reference capybara icons."""
    sx0, sy0, sx1, sy1 = snout_box
    outline = rgba(theme, "outline")
    cx = (sx0 + sx1) / 2
    top = sy0 + (sy1 - sy0) * 0.32
    _ellipse(draw, [cx - 4, top - 4, cx + 4, top + 4], fill=outline)
    bottom = top + 16
    if style == "open":
        _rect(draw, [cx - 4, top + 4, cx + 4, bottom], fill=outline)
    elif style == "small_o":
        _ellipse(draw, [cx - 4, top + 4, cx + 4, bottom + 4], fill=outline)
    elif style == "smile":
        _line(draw, [(cx, top + 4), (cx, bottom - 4)], fill=outline, width=2)
        _arc(draw, [cx - 8, bottom - 10, cx + 8, bottom + 6], start=20, end=160, fill=outline, width=2)
    elif style == "frown":
        _line(draw, [(cx, top + 4), (cx, bottom - 4)], fill=outline, width=2)
        _arc(draw, [cx - 8, bottom - 6, cx + 8, bottom + 10], start=200, end=340, fill=outline, width=2)
    else:  # "closed" / "flat" default -- straight vertical tick, no lip shape
        _line(draw, [(cx, top + 4), (cx, bottom)], fill=outline, width=2)
        _line(draw, [(cx - 4, bottom), (cx + 4, bottom)], fill=outline, width=2)


# ---------------------------------------------------------------------------
# Paws (vary by pose) -- small stubby ellipses, drawn in fur-shade tone
# so they read as part of the capybara, not a foreign limb.
# ---------------------------------------------------------------------------

def draw_paws(draw, theme, variant, body_box, style="rest"):
    fur = rgba(theme, _v(variant, "fur_shade"))
    outline = rgba(theme, "outline")
    ow = _v(variant, "outline")
    x0, y0, x1, y1 = body_box

    def paw(cx, cy, r=10):
        _ellipse(draw, [cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=fur, outline=outline, width=ow)

    if style == "rest":
        paw(x0 + 22, y1 - 12)
        paw(x1 - 22, y1 - 12)
    elif style == "hold_book":
        paw(x0 + 26, y1 - 26)
        paw(x1 - 26, y1 - 26)
        draw_book(draw, theme, variant, (x0 + x1) / 2, y1 - 22)
    elif style == "hold_book_open":
        paw(x0 + 20, y1 - 26)
        paw(x1 - 20, y1 - 26)
        draw_book(draw, theme, variant, (x0 + x1) / 2, y1 - 22, open_book=True)
    elif style == "hold_scroll":
        paw(x0 + 22, y1 - 14)
        draw_book(draw, theme, variant, x0 + 22, y1 - 24)
        paw(x1 - 26, y1 - 26)
        draw_scroll(draw, theme, variant, x1 - 22, y1 - 30)
    elif style == "point_side":
        paw(x0 + 22, y1 - 14)
        paw(x1 - 6, y0 + (y1 - y0) * 0.62, r=9)
    elif style == "point_up":
        paw(x0 + 22, y1 - 14)
        paw(x1 - 22, y0 + (y1 - y0) * 0.12, r=9)
    elif style == "paw_forehead":
        paw(x0 + 22, y1 - 14)
        cx = (x0 + x1) / 2
        paw(cx, y0 + (y1 - y0) * 0.22, r=9)
    elif style == "open_palms":
        paw(x0 + 6, y1 - 30, r=9)
        paw(x1 - 6, y1 - 30, r=9)
    elif style == "prayer":
        cx = (x0 + x1) / 2
        paw(cx, y1 - 16, r=9)
    else:
        paw(x0 + 22, y1 - 12)
        paw(x1 - 22, y1 - 12)


# ---------------------------------------------------------------------------
# Extras (small overlays for a handful of poses)
# ---------------------------------------------------------------------------

def draw_extra(draw, theme, variant, body_box, kind):
    outline = rgba(theme, "outline")
    x0, y0, x1, y1 = body_box
    if kind == "question":
        _ellipse(draw, [x1 - 10, y0 - 4, x1 + 2, y0 + 8], fill=None, outline=outline, width=2)
    elif kind == "sweat":
        _ellipse(draw, [x1 - 2, y0 + 14, x1 + 10, y0 + 28], fill=rgba(theme, "eye_white"), outline=outline, width=1)
