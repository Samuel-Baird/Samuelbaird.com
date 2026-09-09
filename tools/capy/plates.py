"""Render one 1080x1920 RGBA "plate" (a single frame representing a beat)
for the storyboard contact sheet and, later, capy_render.py's per-segment
video composition.

    from capy.plates import render_plate
    img = render_plate(beat, theme, project_dir=Path(...), clip_frame=None)

Everything about *where* things go comes from capy.layout.Theme (which
reads assets/saint-capybara/theme.yaml) -- nothing here hardcodes a zone's
pixel coordinates. Character position is always the theme's `sprite`
zone (bottom-left corner, per docs/saint-capybara/brand.md sec 8).
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from capy.layout import Theme
from capy.poses import SENSITIVE_FORBIDDEN
from capy.beats import resolve_pose, OUTRO_POSES


def _font(theme: Theme, which: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(theme.font_path(which)), size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
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


def _draw_label_chip(draw: ImageDraw.ImageDraw, theme: Theme, text: str, xy: tuple[int, int]) -> None:
    font = _font(theme, "display", 22)
    pad = 10
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0] + pad * 2
    h = bbox[3] - bbox[1] + pad * 2
    x, y = xy
    draw.rectangle([x, y, x + w, y + h], fill=theme.color_rgba("ink", 210), outline=theme.color_rgba("halo_gold_hex"))
    draw.text((x + pad, y + pad), text, font=font, fill=theme.color_rgba("parchment"))


def draw_card(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], quote: str, attribution: str) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=theme.color_rgba("parchment"), outline=theme.color_rgba("ink"), width=4)
    body_font = _font(theme, "body", 40)
    attr_font = _font(theme, "display", 22)
    pad = 40
    lines = _wrap_text(draw, f"“{quote}”", body_font, (x1 - x0) - pad * 2)
    total_h = len(lines) * (body_font.size + 10)
    ty = y0 + ((y1 - y0) - total_h) // 2 - 30
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=body_font)
        tw = bbox[2] - bbox[0]
        draw.text((x0 + ((x1 - x0) - tw) // 2, ty), line, font=body_font, fill=theme.color_rgba("ink"))
        ty += body_font.size + 10
    attr_lines = _wrap_text(draw, attribution, attr_font, (x1 - x0) - pad * 2)
    ay = y1 - pad - len(attr_lines) * (attr_font.size + 6)
    for line in attr_lines:
        bbox = draw.textbbox((0, 0), line, font=attr_font)
        tw = bbox[2] - bbox[0]
        draw.text((x0 + ((x1 - x0) - tw) // 2, ay), line, font=attr_font, fill=theme.color_rgba("source_teal"))
        ay += attr_font.size + 6


def draw_bar_chart(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], title: str, data: list[list], credit: str = "") -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=theme.color_rgba("parchment"), outline=theme.color_rgba("ink"), width=4)
    title_font = _font(theme, "display", 26)
    label_font = _font(theme, "body", 24)
    pad = 40
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
        cfont = _font(theme, "body", 18)
        draw.text((x0 + pad, y1 - 28), credit, font=cfont, fill=theme.color_rgba("source_teal"))


def _paste_evidence(img: Image.Image, theme: Theme, box: tuple[int, int, int, int], project_dir: Path, evidence: dict) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=theme.color_rgba("parchment"), outline=theme.color_rgba("ink"), width=3)
    image_rel = evidence.get("image")
    if image_rel:
        img_path = project_dir / image_rel
        if img_path.exists():
            ev = Image.open(img_path).convert("RGBA")
            crop = evidence.get("crop")
            if crop and any(crop):
                ev = ev.crop(tuple(crop))
            pad = 12
            avail_w, avail_h = (x1 - x0 - pad * 2), (y1 - y0 - pad * 2 - 40)
            ratio = min(avail_w / ev.width, avail_h / ev.height, 1.0)
            ev = ev.resize((max(1, int(ev.width * ratio)), max(1, int(ev.height * ratio))), Image.LANCZOS)
            img.alpha_composite(ev, (x0 + pad, y0 + pad))
        else:
            draw.text((x0 + 12, y0 + 12), "[missing evidence image]", font=_font(theme, "body", 20), fill=theme.color_rgba("highlight_brick"))
    credit = evidence.get("credit")
    if credit:
        cfont = _font(theme, "body", 18)
        lines = _wrap_text(draw, credit, cfont, (x1 - x0) - 24)
        cy = y1 - 12 - len(lines) * 22
        for line in lines:
            draw.text((x0 + 12, cy), line, font=cfont, fill=theme.color_rgba("source_teal"))
            cy += 22


def render_plate(
    beat: dict,
    theme: Theme,
    *,
    project_dir: Path,
    clip_frame: Image.Image | None = None,
    sensitive: bool = False,
    punch_stage_hole: bool = False,
) -> Image.Image:
    """`punch_stage_hole` (TEST/EXPERIMENTAL, hybrid Resolve pipeline only,
    see docs/saint-capybara/hybrid-resolve-pipeline.md): for a `clip` beat,
    cut the stage rectangle's alpha to 0 instead of drawing a placeholder
    or a composited frame, so the real source clip -- placed on a Resolve
    video track *below* this plate -- shows through. Unused by the
    ffmpeg-compositor path (capy_storyboard.py's contact sheet / any future
    capy_render.py still want an actual `clip_frame` preview instead)."""
    img = _background(theme)
    draw = ImageDraw.Draw(img)
    kind = beat.get("kind")
    stage_box = theme.stage_box()

    # --- Stage content ---
    if kind == "clip" and punch_stage_hole:
        x0, y0, x1, y1 = stage_box
        img.paste((0, 0, 0, 0), (x0, y0, x1, y1))
        _draw_label_chip(draw, theme, beat.get("speaker", "Source video"), (stage_box[0] + 16, stage_box[1] + 16))
    elif kind == "clip":
        if clip_frame is not None:
            cf = clip_frame.convert("RGBA")
            sw, sh = stage_box[2] - stage_box[0], stage_box[3] - stage_box[1]
            ratio = max(sw / cf.width, sh / cf.height)
            cf = cf.resize((int(cf.width * ratio), int(cf.height * ratio)), Image.LANCZOS)
            ox = (cf.width - sw) // 2
            oy = (cf.height - sh) // 2
            cf = cf.crop((ox, oy, ox + sw, oy + sh))
            img.alpha_composite(cf, (stage_box[0], stage_box[1]))
        else:
            draw.rectangle(stage_box, fill=theme.color_rgba("outline"))
            draw.text((stage_box[0] + 20, stage_box[1] + 20), "[source clip]", font=_font(theme, "display", 20), fill=theme.color_rgba("parchment"))
        _draw_label_chip(draw, theme, beat.get("speaker", "Source video"), (stage_box[0] + 16, stage_box[1] + 16))
    elif kind == "card":
        card = beat.get("card", {})
        draw_card(img, theme, stage_box, card.get("quote", ""), card.get("attribution", ""))
        _draw_label_chip(draw, theme, "SOURCE", (stage_box[0] + 16, stage_box[1] + 16))
    elif kind == "chart":
        chart = beat.get("chart", {})
        draw_bar_chart(img, theme, stage_box, chart.get("title", ""), chart.get("data", []), chart.get("credit", ""))
    elif kind == "evidence" and beat.get("evidence", {}).get("placement") == "stage":
        _paste_evidence(img, theme, stage_box, project_dir, beat.get("evidence", {}))
        _draw_label_chip(draw, theme, "SOURCE", (stage_box[0] + 16, stage_box[1] + 16))
    else:
        # narration/outro/evidence-in-panel: freeze (dimmed) or blank stage
        stage_mode = beat.get("stage", "blank")
        if stage_mode == "freeze" and clip_frame is not None:
            cf = clip_frame.convert("RGBA")
            sw, sh = stage_box[2] - stage_box[0], stage_box[3] - stage_box[1]
            cf = cf.resize((sw, sh), Image.LANCZOS)
            dim = Image.new("RGBA", cf.size, (0, 0, 0, int(255 * 0.45)))
            cf = Image.alpha_composite(cf, dim)
            img.alpha_composite(cf, (stage_box[0], stage_box[1]))
        else:
            draw.rectangle(stage_box, fill=theme.color_rgba("parchment"), outline=theme.color_rgba("ink"), width=2)

    # --- Panel (inline evidence beside the sprite), when applicable ---
    if kind == "evidence" and beat.get("evidence", {}).get("placement", "panel") == "panel":
        _paste_evidence(img, theme, theme.panel_box(), project_dir, beat.get("evidence", {}))

    # --- Sprite (bottom-left corner, per theme.yaml) ---
    pose = resolve_pose(beat, sensitive=sensitive)
    if pose:
        if sensitive and pose in SENSITIVE_FORBIDDEN:
            pose = "solemn"  # safe fallback; capy_check_sources.py should have already errored on this
        sprite_path = theme.finalized_sprite_path(pose)
        if not sprite_path.exists():
            sprite_path = theme.sprite_path(pose)  # retired code-drawn fallback, see layout.py
        if sprite_path.exists():
            sprite = Image.open(sprite_path).convert("RGBA")
            x0, y0, x1, y1 = theme.sprite_box()
            size = x1 - x0
            sprite = sprite.resize((size, size), Image.LANCZOS)
            img.alpha_composite(sprite, (x0, y0))

    # --- Hook chip (beat 1 only, in reserved_top) ---
    if beat.get("_is_first") and beat.get("_hook"):
        rz = theme.zone("reserved_top")
        w, _ = theme.canvas_size
        text = beat["_hook"]
        max_w = w - 80
        size = 30
        while size > 16:
            hook_font = _font(theme, "display", size)
            bbox = draw.textbbox((0, 0), text, font=hook_font)
            if bbox[2] - bbox[0] <= max_w:
                break
            size -= 2
        else:
            hook_font = _font(theme, "display", size)
        lines = _wrap_text(draw, text, hook_font, max_w) if draw.textbbox((0, 0), text, font=hook_font)[2] > max_w else [text]
        line_h = hook_font.size + 8
        total_h = len(lines) * line_h
        cx = w // 2
        cy = (rz["y0"] + rz["y1"]) // 2
        max_tw = max(draw.textbbox((0, 0), line, font=hook_font)[2] for line in lines)
        draw.rectangle(
            [cx - max_tw // 2 - 20, cy - total_h // 2 - 12, cx + max_tw // 2 + 20, cy + total_h // 2 + 12],
            fill=theme.color_rgba("ink", 220), outline=theme.color_rgba("halo_gold_hex"),
        )
        ty = cy - total_h // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=hook_font)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw // 2, ty), line, font=hook_font, fill=theme.color_rgba("parchment"))
            ty += line_h

    # --- Wordmark, bottom-right in reserved_bottom ---
    wm = theme.wordmark_box()
    wm_font = _font(theme, "display", 16)
    text = "SAINT CAPYBARA"
    bbox = draw.textbbox((0, 0), text, font=wm_font)
    tw = bbox[2] - bbox[0]
    draw.text((wm["x1"] - tw, wm["y0"]), text, font=wm_font, fill=theme.color_rgba("ink", 140))

    return img
