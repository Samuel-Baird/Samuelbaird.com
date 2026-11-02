"""Brand-consistent thumbnails (YouTube 1280x720) and Reel covers (Instagram 1080x1920) from
a camera frame plus text, as specs in project.json "thumbnails".

    python tools/presentation/thumbs.py D:\\Videos\\<slug> [--only <out-name-substring>]

A spec:
  {"out": "exports/thumbnails/yt_19x_arians.jpg",  "size": [1280, 720],
   "frame": {"take": "1", "camera": "A", "t": 477.6},   mic time of a frame with eye contact
   "face_x": 0.70,          where the face sits across the canvas (text goes on the other side)
   "zoom_w": 2300,          landscape: width of the 4K crop (smaller = tighter on the face)
   "shade": "left",         darken behind the text: left | right | bottom | band:<y>
   "shift": 0,              portrait: push the speaker down by this many px (room for a photo)
   "top_photo": null,       portrait: a photo across the top that fades into the speaker
   "elements": [ ... drawn in order ... ]}
Elements (colors: orange, white, red, flag_red, blue, or [r,g,b]; fonts: black | bold):
  {"type": "text", "xy": [60, 50], "text": "19×", "size": 250, "color": "orange", "stroke": 4,
   "font": "black", "anchor": "la"}
  {"type": "pill", "xy": [72, 560], "text": "IN THE USA", "size": 44, "bg": "flag_red", "font": "black"}
  {"type": "bars", "xy": [60, 280], "width": 560, "rows": [{"label": "...", "value": "7.8M",
   "frac": 1.0, "color": "orange"}, ...]}
  {"type": "card", "image": "<path>", "xy": [70, 300], "width": 420, "angle": 3,
   "crop": [0, 0, 1, 0.56]}                 a tilted white card, e.g. one of the chart graphics
A soft drop shadow is added under everything drawn. Each output also gets a <name>_check.jpg
next to it in work/ showing a portrait cover at the Instagram grid crops (4:5 and 1:1) --
the headline must survive both.

Brand rules: docs/style-guide.md "Brand kit" -- Segoe UI Black for headlines, Segoe UI Bold for
secondary lines, orange for the number/key phrase, white for the rest, red for the negative,
and say where the data is from when it matters ("IN THE USA", "U.S. CHRISTIANS").
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

import brand
from common import FF, Project

COLORS = dict(orange=brand.ORANGE, white=brand.WHITE, red=brand.RED, flag_red=brand.FLAG_RED, blue=brand.BLUE,
              chip=brand.CHIP)
FONTS = dict(black=brand.FONT_BLACK, bold=brand.FONT_BOLD)


def col(c):
    return tuple(c) if isinstance(c, list) else COLORS[c]


def grab(pr: Project, take, cam, t) -> Path:
    out = pr.work / 'thumb_frames' / f'take{take}_{cam}_{t:.2f}.png'
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        path, off, _, _ = pr.camera(take, cam)
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t + off:.3f}', '-i', path, '-frames:v', '1', out], check=True)
    return out


def background(pr: Project, sp: dict) -> Image.Image:
    W, H = sp['size']
    fr = sp['frame']
    src = Image.open(grab(pr, str(fr['take']), fr['camera'], float(fr['t']))).convert('RGB')
    _, _, fx, fy = pr.camera(str(fr['take']), fr['camera'])
    FX, FY = fx * src.width, fy * src.height
    if W > H:
        zw = sp.get('zoom_w', 2300)
        zh = round(zw * H / W)
        x0 = max(0, min(src.width - zw, round(FX - sp.get('face_x', 0.7) * zw)))
        y0 = max(0, min(src.height - zh, round(FY - 0.42 * zh)))
        im = src.crop((x0, y0, x0 + zw, y0 + zh)).resize((W, H), Image.LANCZOS)
    else:
        cw = sp.get('crop_w', 1216 if sp.get('shift') else 1100)
        ch = min(src.height, round(cw * H / W))
        x0 = round(FX - cw / 2)
        y0 = 0 if sp.get('shift') else max(0, min(src.height - ch, round(FY - 0.30 * ch)))
        im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, round(W * ch / cw)), Image.LANCZOS)
        canvas = Image.new('RGB', (W, H), (8, 8, 9))
        canvas.paste(im, (0, sp.get('shift', 0)))
        im = canvas
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.10)).enhance(1.12)
    if sp.get('top_photo'):
        tab = Image.open(pr.p(sp['top_photo'])).convert('RGB')
        tw, th = W, round(H * 0.52)
        r = max(tw / tab.width, th / tab.height)
        tab = tab.resize((round(tab.width * r), round(tab.height * r)), Image.LANCZOS)
        tx, ty = (tab.width - tw) // 2, round((tab.height - th) * 0.15)
        tab = ImageEnhance.Contrast(tab.crop((tx, ty, tx + tw, ty + th))).enhance(1.15)
        fade = np.clip((np.arange(th) - th * 0.52) / (th * 0.42), 0, 1)
        im.paste(tab, (0, 0), Image.fromarray((255 * (1 - fade[:, None] * np.ones((1, tw)))).astype(np.uint8)))
    a = np.array(im).astype(float)
    shade = sp.get('shade', 'left')
    if shade in ('left', 'right'):
        ramp = np.linspace(0, 1, W)[::-1] if shade == 'right' else np.linspace(0, 1, W)
        g = (np.clip((0.62 - ramp) / 0.35, 0, 1) ** 1.2 * 0.90)[None, :, None]
    elif shade == 'bottom':
        g = (np.clip((np.linspace(0, 1, H) - 0.42) / 0.25, 0, 1) * 0.82)[:, None, None]
    elif shade.startswith('band:'):
        y = np.arange(H)
        g = (np.exp(-((y - float(shade[5:])) / (H * 0.135)) ** 2) * 0.70)[:, None, None]
    else:
        g = 0
    return Image.fromarray((a * (1 - g)).astype(np.uint8)).convert('RGBA')


def draw(layer: Image.Image, pr: Project, el: dict) -> None:
    d = ImageDraw.Draw(layer)
    t = el['type']
    if t == 'text':
        f = ImageFont.truetype(FONTS[el.get('font', 'black')], el['size'])
        d.text(tuple(el['xy']), el['text'], font=f, fill=col(el.get('color', 'white')),
               stroke_width=el.get('stroke', 0), stroke_fill=(0, 0, 0), anchor=el.get('anchor', 'la'))
    elif t == 'pill':
        f = ImageFont.truetype(FONTS[el.get('font', 'bold')], el['size'])
        anchor = el.get('anchor', 'la')
        x0, y0, x1, y1 = d.textbbox(tuple(el['xy']), el['text'], font=f, anchor=anchor)
        pad = el.get('pad', [22, 12])
        d.rounded_rectangle([x0 - pad[0], y0 - pad[1], x1 + pad[0], y1 + pad[1] + 4], 14, fill=col(el.get('bg', 'chip')))
        d.text(tuple(el['xy']), el['text'], font=f, fill=col(el.get('color', 'white')), anchor=anchor)
    elif t == 'bars':
        x, y = el['xy']
        for i, row in enumerate(el['rows']):
            yy = y + i * el.get('spacing', 175)
            d.text((x + 2, yy), row['label'].upper(), font=ImageFont.truetype(brand.FONT_BOLD, 34), fill=brand.WHITE,
                   stroke_width=2, stroke_fill=(0, 0, 0))
            L = round(el['width'] * row['frac'])
            d.rounded_rectangle([x, yy + 52, x + L, yy + 122], 10, fill=col(row['color']), outline=(0, 0, 0), width=3)
            d.text((x + L + 16, yy + 87), row['value'], font=ImageFont.truetype(brand.FONT_BLACK, 64), fill=brand.WHITE,
                   stroke_width=3, stroke_fill=(0, 0, 0), anchor='lm')
    elif t == 'card':
        g = Image.open(pr.p(el['image'])).convert('RGBA')
        if el.get('crop'):
            l, tp, r, b = el['crop']
            g = g.crop((int(g.width * l), int(g.height * tp), int(g.width * r), int(g.height * b)))
        g = g.resize((el['width'], round(el['width'] * g.height / g.width)), Image.LANCZOS)
        m = Image.new('L', g.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, g.width - 1, g.height - 1], 14, fill=255)
        g.putalpha(m)
        if el.get('angle'):
            g = g.rotate(el['angle'], resample=Image.BICUBIC, expand=True)
        layer.alpha_composite(g, tuple(el['xy']))
    else:
        raise SystemExit(f'unknown element type {t}')


def render(pr: Project, sp: dict) -> Path:
    im = background(pr, sp)
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for el in sp['elements']:
        draw(layer, pr, el)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    sh.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.8)))
    im = Image.alpha_composite(im, sh.transform(im.size, Image.AFFINE, (1, 0, -4, 0, 1, -6)))
    im = Image.alpha_composite(im, layer).convert('RGB')
    out = pr.p(sp['out'])
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=95)
    W, H = im.size
    if H > W:   # Instagram grid previews: 4:5 (current grid) and 1:1 (older grid)
        prev = Image.new('RGB', (3 * 360 + 40, 640), 'white')
        prev.paste(im.resize((360, 640)), (0, 0))
        prev.paste(im.crop((0, round(H * 0.1484), W, round(H * 0.8516))).resize((360, 450)), (380, 0))
        prev.paste(im.crop((0, (H - W) // 2, W, (H + W) // 2)).resize((360, 360)), (760, 0))
        prev.save(pr.work / f'{out.stem}_check.jpg', quality=85)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    pr = Project(a.project)
    for sp in pr.cfg.get('thumbnails', []):
        if a.only in sp['out']:
            print(render(pr, sp))


if __name__ == '__main__':
    main()
