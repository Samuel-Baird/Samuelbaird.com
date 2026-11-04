"""Frame a website screenshot as a browser window (dark tab bar + address pill with the URL), so a
viewer knows it's a live site and can read the address. Screenshots are taken at 1400x788 CSS px,
device scale 2 (2800x1576), so they fill the long-form split layout's slide card exactly.

    python tools/interview/browser_frame.py <shot.png> <url> <out.png>            # static slide
    python tools/interview/browser_frame.py --bar <url> <out.bar.png> [width]       # bar only, for a
                                                                                    # scrolling page

A static slide keeps the top of the page and loses the bottom 7 % under the bar. A scrolling page
(build.py "scroll:<stem>") gets the bar as a separate <stem>.bar.png laid over the moving page.
"""
from __future__ import annotations

import sys

from PIL import Image, ImageDraw, ImageFont

FONT = 'C:/Windows/Fonts/segoeui.ttf'
BAR_FRAC = 0.071          # bar height as a fraction of the 16:9 card (56 px of 788)
BG, PILL, TEXT, DIM = (32, 33, 36), (48, 49, 53), (232, 234, 237), (154, 160, 166)


def bar(url: str, width: int) -> Image.Image:
    h = round(width * 9 / 16 * BAR_FRAC)
    s = width / 1400            # 1.0 at card size, 2.0 at capture size
    im = Image.new('RGB', (width, h), BG)
    d = ImageDraw.Draw(im)
    for i, c in enumerate(((237, 106, 94), (245, 191, 79), (98, 197, 84))):
        cx, cy, r = round((26 + 22 * i) * s), h // 2, round(6.5 * s)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    x0, x1 = round(112 * s), width - round(112 * s)
    d.rounded_rectangle([x0, round(11 * s), x1, h - round(11 * s)], radius=(h - round(22 * s)) // 2, fill=PILL)
    # padlock
    lx, ly = x0 + round(20 * s), h // 2
    d.rounded_rectangle([lx, ly - round(2 * s), lx + round(11 * s), ly + round(8 * s)], radius=round(2 * s), fill=DIM)
    d.arc([lx + round(2 * s), ly - round(9 * s), lx + round(9 * s), ly + round(3 * s)], 180, 360, fill=DIM,
          width=max(1, round(2 * s)))
    f = ImageFont.truetype(FONT, round(17 * s))
    host, _, path = url.partition('/')
    tx = lx + round(24 * s)
    d.text((tx, h // 2), host, font=f, fill=TEXT, anchor='lm')
    if path:
        d.text((tx + d.textlength(host, font=f), h // 2), '/' + path, font=f, fill=DIM, anchor='lm')
    return im


def frame(shot: str, url: str, out: str) -> None:
    im = Image.open(shot).convert('RGB')
    w, h = im.size
    b = bar(url, w)
    page = im.crop((0, 0, w, h - b.height))
    o = Image.new('RGB', (w, h))
    o.paste(b, (0, 0))
    o.paste(page, (0, b.height))
    o.save(out)


if __name__ == '__main__':
    if sys.argv[1] == '--bar':
        bar(sys.argv[2], int(sys.argv[4]) if len(sys.argv) > 4 else 1400).save(sys.argv[3])
    else:
        frame(*sys.argv[1:4])
