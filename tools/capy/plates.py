"""Render one 1080x1920 RGBA "plate" (a single frame representing a beat)
for the storyboard contact sheet and capy_render_beat_clips.py's per-beat
video composition.

    from capy.plates import render_plate
    img = render_plate(beat, theme, project_dir=Path(...))

Everything about *where* things go comes from capy.layout.Theme (which
reads assets/saint-capybara/theme.yaml) -- nothing here hardcodes a zone's
pixel coordinates. Character position/size comes from
capy.layout.Theme.sprite_spec(mode) (see capy.sprites.render_sprite).

layout.version 2 (2026-09-09): three frame modes (CLIP/HOST/CARD), no
chips, no wordmark, no hook-on-screen -- see docs/saint-capybara/brand.md
sec 8. In CLIP mode the plate is a *pure overlay*: fully transparent
except the sprite layer, with the real source video composited
underneath by ffmpeg (capy_render_beat_clips.py) or, for the storyboard
preview only, by this module when `preview_video_frame` is given.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from capy.beats import resolve_pose
from capy.layout import Theme
from capy.poses import SENSITIVE_FORBIDDEN
from capy.sprites import render_sprite
from capy.text import fit_text, draw_lines as _draw_text_lines


def _font(theme: Theme, which: str, size: int) -> ImageFont.FreeTypeFont:
    """Loads a theme font at `size`. Raises rather than silently falling
    back to PIL's tiny default bitmap font -- a missing font file should
    fail loudly during development, not ship an unreadable frame."""
    return ImageFont.truetype(str(theme.font_path(which)), size)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Simple measured-width wrap for short chart/evidence labels that
    don't need the shrink-to-fit behavior of capy.text.fit_text (those
    are always short strings drawn at a fixed size)."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _background(theme: Theme) -> Image.Image:
    w, h = theme.canvas_size
    parchment = theme.color_rgba("parchment")
    img = Image.new("RGBA", (w, h), parchment)
    # Subtle pixel-dither vignette: darken toward the edges.
    vignette = Image.new("L", (w, h), 0)
    vdraw = ImageDraw.Draw(vignette)
    max_r = ((w / 2) ** 2 + (h / 2) ** 2) ** 0.5
    steps = 24
    for i in range(steps):
        t = i / steps
        radius = max_r * (1 - t * 0.5)
        alpha = int(40 * t)
        cx, cy = w / 2, h / 2
        vdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=alpha)
    vignette = ImageOps.invert(vignette)
    dark = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    img = Image.composite(dark, img, vignette.point(lambda p: int(p * 0.35)))
    return img


def _clip_preview_frame(theme: Theme, frame: Image.Image) -> Image.Image:
    """Storyboard-only preview of the CLIP-mode full-bleed compositing:
    9:16-or-narrower sources cover-crop the whole canvas; 16:9-or-wider
    sources fit inside the letterbox band over a blurred, darkened cover
    copy -- mirrors capy_render_beat_clips.py's ffmpeg filter graph so the
    contact sheet doesn't lie about the real look."""
    w, h = theme.canvas_size
    cf = frame.convert("RGBA")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if cf.width <= cf.height:
        ratio = max(w / cf.width, h / cf.height)
        cf = cf.resize((max(1, round(cf.width * ratio)), max(1, round(cf.height * ratio))), Image.LANCZOS)
        ox, oy = (cf.width - w) // 2, (cf.height - h) // 2
        out.alpha_composite(cf.crop((ox, oy, ox + w, oy + h)))
        return out

    band_y0, band_y1 = theme.letterbox_band()
    band_h = band_y1 - band_y0
    bg = theme.letterbox_bg()
    bg_ratio = max(w / cf.width, h / cf.height)
    bg_img = cf.resize((max(1, round(cf.width * bg_ratio)), max(1, round(cf.height * bg_ratio))), Image.LANCZOS)
    bx, by = (bg_img.width - w) // 2, (bg_img.height - h) // 2
    blur_radius = float(bg["boxblur"].split(":")[0])
    bg_img = bg_img.crop((bx, by, bx + w, by + h)).filter(ImageFilter.GaussianBlur(blur_radius))
    dim = Image.new("RGBA", (w, h), (0, 0, 0, int(255 * bg["dim"])))
    bg_img = Image.alpha_composite(bg_img, dim)
    out.alpha_composite(bg_img)

    fit_ratio = min(w / cf.width, band_h / cf.height)
    fw, fh = max(1, round(cf.width * fit_ratio)), max(1, round(cf.height * fit_ratio))
    fg = cf.resize((fw, fh), Image.LANCZOS)
    fx, fy = (w - fw) // 2, band_y0 + (band_h - fh) // 2
    out.alpha_composite(fg, (fx, fy))
    return out


def _background_photo(theme: Theme, photo: Image.Image) -> Image.Image:
    """Full-bleed cover-crop of `photo`, blurred and dimmed per
    theme.layout.host.freeze -- shared by HOST mode's `stage: freeze`
    (the last clip's final frame) and `stage: image` (an arbitrary
    project image, e.g. a historical painting/photo/sketch supplied via
    `background:`). Same treatment either way -- a backdrop the sprite
    reads clearly against, not a full-detail photo."""
    w, h = theme.canvas_size
    spec = theme.freeze_spec()
    cf = photo.convert("RGBA")
    ratio = max(w / cf.width, h / cf.height)
    cf = cf.resize((max(1, round(cf.width * ratio)), max(1, round(cf.height * ratio))), Image.LANCZOS)
    ox = (cf.width - w) // 2
    oy = (cf.height - h) // 2
    cf = cf.crop((ox, oy, ox + w, oy + h))
    cf = cf.filter(ImageFilter.GaussianBlur(spec["blur_sigma"]))
    dim = Image.new("RGBA", (w, h), (0, 0, 0, int(255 * spec["dim"])))
    return Image.alpha_composite(cf, dim)


def draw_card(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], quote: str, attribution: str, *, beat_id: str | None = None) -> None:
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(img)
    draw.rectangle(box, fill=theme.color_rgba("parchment"), outline=theme.color_rgba("ink"), width=4)
    pad = theme.card_pad
    inner_w = (x1 - x0) - pad * 2

    qs = theme.text_style("card_text.quote")
    q_font, q_lines = fit_text(
        f"“{quote}”", theme.font_path(qs["font"]),
        size=qs["size"], min_size=qs["min_size"], step=4, max_w=inner_w,
        max_lines=8, stroke=0, beat_id=beat_id,
    )
    line_h = int(q_font.size * qs["line_height"])
    q_total_h = len(q_lines) * line_h

    ats = theme.text_style("card_text.attribution")
    a_font, a_lines = fit_text(
        attribution, theme.font_path(ats["font"]),
        size=ats["size"], min_size=ats["min_size"], step=2, max_w=inner_w,
        max_lines=3, stroke=0, beat_id=beat_id,
    )
    a_line_h = int(a_font.size * ats["line_height"])
    a_total_h = len(a_lines) * a_line_h

    avail_h = (y1 - y0) - pad * 2
    ty = y0 + pad + max(0, (avail_h - q_total_h - a_total_h - 20) // 2)
    for line in q_lines:
        bbox = draw.textbbox((0, 0), line, font=q_font)
        tw = bbox[2] - bbox[0]
        draw.text((x0 + ((x1 - x0) - tw) // 2, ty), line, font=q_font, fill=theme.color_rgba(qs["color"]))
        ty += line_h

    ay = y1 - pad - a_total_h
    for line in a_lines:
        bbox = draw.textbbox((0, 0), line, font=a_font)
        tw = bbox[2] - bbox[0]
        draw.text((x0 + ((x1 - x0) - tw) // 2, ay), line, font=a_font, fill=theme.color_rgba(ats["color"]))
        ay += a_line_h


def draw_excerpt_card(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], text: str, attribution: str, *, beat_id: str | None = None) -> None:
    """The article-mode analog of draw_card: a pull-quote from the
    source's own words. `text` may contain literal '[...]' ellipsis
    markers (shown as-is -- see capy.excerpts). Visually identical to
    draw_card apart from calling it out as a direct quotation is already
    handled by the smart quotes + attribution; kept as a separate
    function per the excerpt-beat design (see the overhaul plan Part 4)."""
    draw_card(img, theme, box, text, attribution, beat_id=beat_id)


def draw_bar_chart(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], title: str, data: list[list], credit: str = "") -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=theme.color_rgba("parchment"), outline=theme.color_rgba("ink"), width=4)
    cs = theme.data["card_text"]["chart"]
    title_font = _font(theme, cs["title"]["font"], cs["title"]["size"])
    label_font = _font(theme, cs["label"]["font"], cs["label"]["size"])
    pad = theme.card_pad
    draw.text((x0 + pad, y0 + pad), title, font=title_font, fill=theme.color_rgba("ink"))
    chart_top = y0 + pad + 50
    chart_bottom = y1 - pad - 40
    chart_left = x0 + pad
    chart_right = x1 - pad
    if not data:
        return
    max_val = max(float(v) for _, v in data) or 1.0
    n = len(data)
    gap = 20
    bar_w = (chart_right - chart_left - gap * (n - 1)) / n
    for i, (label, val) in enumerate(data):
        bar_h = (chart_bottom - chart_top) * (float(val) / max_val)
        bx0 = chart_left + i * (bar_w + gap)
        by0 = chart_bottom - bar_h
        draw.rectangle([bx0, by0, bx0 + bar_w, chart_bottom], fill=theme.color_rgba("highlight_brick"))
        draw.text((bx0, chart_bottom + 6), str(label), font=label_font, fill=theme.color_rgba("ink"))
        draw.text((bx0, by0 - 30), str(val), font=label_font, fill=theme.color_rgba("ink"))
    if credit:
        cfont = _font(theme, cs["credit"]["font"], cs["credit"]["size"])
        draw.text((x0 + pad, y1 - 28), credit, font=cfont, fill=theme.color_rgba("source_teal"))


def _paste_evidence(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], project_dir: Path, evidence: dict, *, bake_image: bool = True) -> None:
    """Evidence-photo layout (2026-09-13 user direction, superseding the
    original boxed-card look): no border/parchment box drawn around the
    photo -- it sits directly in the mode's own background ("blank
    space") -- and the citation is never drawn here at all (see
    `_draw_citation`, always pinned to the fixed bottom-of-canvas zone
    regardless of where/how large the photo ends up).

    `bake_image=True` (the storyboard/mock-preview path only) still
    pastes the photo into the flat plate so a human reviewer sees roughly
    what's intended. `bake_image=False` (capy_beat_plates.py's real
    build path) never pastes it -- the real photo becomes its own live,
    independently resizable clip on a separate Resolve track instead (see
    docs/saint-capybara/hybrid-resolve-pipeline.md, "Raw evidence photos
    on their own timeline layer"), composited by the Resolve build step,
    not baked in here. `box` is now only a *default fit/position hint*
    for that preview and for the Resolve overlay's starting placement --
    not a drawn boundary."""
    if not bake_image:
        return
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    image_rel = evidence.get("image")
    if image_rel:
        img_path = project_dir / image_rel
        if img_path.exists():
            ev = Image.open(img_path).convert("RGBA")
            crop = evidence.get("crop")
            if crop and any(crop):
                ev = ev.crop(tuple(crop))
            pad = theme.card_pad
            avail_w, avail_h = (x1 - x0 - pad * 2), (y1 - y0 - pad * 2)
            ratio = min(avail_w / ev.width, avail_h / ev.height, 1.0)
            ev = ev.resize((max(1, int(ev.width * ratio)), max(1, int(ev.height * ratio))), Image.LANCZOS)
            paste_x = x0 + pad + (avail_w - ev.width) // 2
            paste_y = y0 + pad + (avail_h - ev.height) // 2
            img.alpha_composite(ev, (paste_x, paste_y))
        else:
            ec = theme.data["card_text"]["evidence_credit"]
            draw.text((x0 + 12, y0 + 12), "[missing evidence image]", font=_font(theme, ec["font"], ec["size"]), fill=theme.color_rgba("highlight_brick"))


def _draw_citation(img: Image.Image, theme: Theme, credit: str) -> None:
    """Citation/credit line for an evidence or chart beat, always pinned
    to the fixed bottom-of-canvas zone (`theme.layout['citation']`) --
    2026-09-13 user direction: previously this was drawn at the bottom of
    the (now-removed) evidence box, which meant it moved around with the
    photo's own size/position. It now has a single, predictable location
    regardless of what the photo does."""
    if not credit:
        return
    draw = ImageDraw.Draw(img)
    w, _h = theme.canvas_size
    zone = theme.data["layout"]["citation"]
    ec = theme.data["card_text"]["evidence_credit"]
    cfont = _font(theme, ec["font"], ec["size"])
    max_width = zone["max_width"]
    lines = _wrap_text(draw, credit, cfont, max_width)
    line_h = ec["size"] + 4
    total_h = len(lines) * line_h
    cy = zone["y1"] - total_h
    for line in lines:
        lw = draw.textlength(line, font=cfont)
        cx = (w - lw) / 2
        draw.text((cx, cy), line, font=cfont, fill=theme.color_rgba("source_teal"))
        cy += line_h


def render_plate(
    beat: dict,
    theme: Theme,
    *,
    project_dir: Path,
    freeze_frame: Image.Image | None = None,
    sensitive: bool = False,
    preview_video_frame: Image.Image | None = None,
    bake_evidence_image: bool = True,
) -> Image.Image:
    """Render one beat's plate. `freeze_frame`: the last clip's final
    frame, used only when `beat.stage == "freeze"` in HOST mode.
    `preview_video_frame`: storyboard-only -- a real extracted frame of
    the CLIP beat's own source video, composited under the transparent
    plate so the contact sheet previews the real full-bleed look (never
    used by capy_render_beat_clips.py, which composites the real video
    with ffmpeg instead).

    HOST-mode `stage:` values (brand.md sec 8, script-format.md):
    `blank` (parchment+vignette), `freeze` (last clip's final frame,
    blurred/dimmed), `image` (an arbitrary project image -- a historical
    painting/photo/sketch -- via `beat.background`, same blur/dim
    treatment), `video` (the source video playing continuously, not
    frozen, behind the sprite -- rendered as a transparent plate here;
    the real compositing happens in capy_render_beat_clips.py, same as
    CLIP mode's live video).

    `bake_evidence_image`: whether an `evidence` beat's photo gets pasted
    into this plate at all (2026-09-13). Storyboard/mock preview calls
    leave this `True` so the contact sheet still shows the photo; the
    real build (`capy_beat_plates.py`) passes `False` -- the photo is a
    live, separately-resizable Resolve overlay clip instead, never baked
    in. Either way the citation is drawn at the fixed bottom-of-canvas
    zone, independent of the photo."""
    kind = beat.get("kind")
    mode = theme.mode_for(beat)
    w, h = theme.canvas_size

    if mode == "clip":
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if preview_video_frame is not None:
            img.alpha_composite(_clip_preview_frame(theme, preview_video_frame))
    elif mode == "host":
        stage_mode = beat.get("stage", "blank")
        if stage_mode == "freeze" and freeze_frame is not None:
            img = _background_photo(theme, freeze_frame)
        elif stage_mode == "image" and beat.get("background"):
            bg_path = project_dir / beat["background"]
            try:
                img = _background_photo(theme, Image.open(bg_path))
            except Exception as e:
                import sys
                print(f"warning: could not load background image {bg_path} for beat {beat.get('id')}: {e}", file=sys.stderr)
                img = _background(theme)
        elif stage_mode == "video":
            # Transparent plate -- capy_render_beat_clips.py composites the
            # live, blurred/dimmed source video underneath, matching CLIP
            # mode's approach rather than baking a still into the PNG.
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            if preview_video_frame is not None:
                img.alpha_composite(_background_photo(theme, preview_video_frame))
        else:
            img = _background(theme)
    else:  # card
        img = _background(theme)
        box = theme.card_box()
        if kind == "card":
            card = beat.get("card", {})
            draw_card(img, theme, box, card.get("quote", ""), card.get("attribution", ""), beat_id=beat.get("id"))
        elif kind == "chart":
            chart = beat.get("chart", {})
            draw_bar_chart(img, theme, box, chart.get("title", ""), chart.get("data", []), chart.get("credit", ""))
        elif kind == "evidence":
            evidence = beat.get("evidence", {})
            _paste_evidence(img, theme, box, project_dir, evidence, bake_image=bake_evidence_image)
            _draw_citation(img, theme, evidence.get("credit", ""))
        elif kind == "excerpt":
            attribution = beat.get("_excerpt_attribution", "")
            draw_excerpt_card(img, theme, box, beat.get("text", ""), attribution, beat_id=beat.get("id"))

    # --- Sprite ---
    pose = resolve_pose(beat, sensitive=sensitive)
    if pose:
        if sensitive and pose in SENSITIVE_FORBIDDEN:
            pose = "solemn"  # safe fallback; capy_check_sources.py should have already errored on this
        spec = theme.sprite_spec(mode)
        try:
            sprite_layer = render_sprite(theme, pose, spec)
            img.alpha_composite(sprite_layer)
        except Exception as e:  # SpriteArtError or a missing file -- never silently ship a blank frame
            import sys
            print(f"warning: sprite render failed for pose {pose!r} on beat {beat.get('id')}: {e}", file=sys.stderr)

    return img
