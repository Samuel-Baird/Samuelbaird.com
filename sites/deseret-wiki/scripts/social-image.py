"""Render the quote cards (src/pages/social/quote/[id].astro) to images, in both alphabets.

Run with the dev server up:  python scripts/social-image.py [http://localhost:4330] [id ...]
For every quote in src/data/quotes.json (or just the ids given) writes, into public/social/:
  <image>.png, <image>-dsrt.png          1200 x 630, for sharing and the download links
  (the og:image card, deseret-alphabet-quote, also keeps 2400 x 1260 @2x PNGs)
  <image>.webp, <image>-dsrt.webp, and @2x  lighter copies shown on the pages
Needs Playwright, Pillow and an installed Chrome.
"""
import json
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
BASE = (args.pop(0) if args and args[0].startswith('http') else 'http://localhost:4330').rstrip('/')
OUT = ROOT / 'public' / 'social'
OG = 'deseret-alphabet-quote'  # the site's og:image (src/layouts/Base.astro)
QUOTES = json.loads((ROOT / 'src' / 'data' / 'quotes.json').read_text(encoding='utf-8'))
if args:
    QUOTES = [q for q in QUOTES if q['id'] in args]

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome')
    for scale, suffix in ((1, ''), (2, '@2x')):
        page = browser.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=scale)
        for q in QUOTES:
            for script, tail in (('latn', ''), ('dsrt', '-dsrt')):
                page.goto(f"{BASE}/social/quote/{q['id']}/?script={script}", wait_until='networkidle')
                page.wait_for_function("document.documentElement.dataset.fit === 'done'")
                page.evaluate("document.querySelector('astro-dev-toolbar')?.remove()")  # dev server only
                page.wait_for_timeout(250)
                png = OUT / f"{q['image']}{tail}{suffix}.png"
                page.locator('#card').screenshot(path=str(png))
                webp = png.with_suffix('.webp')
                Image.open(png).save(webp, 'WEBP', quality=86, method=6)
                if scale == 2 and q['image'] != OG:
                    png.unlink()  # 1200 x 630 PNG is the share size; only the og:image keeps a 2x PNG too
                    print(webp.name, webp.stat().st_size // 1024, 'KB')
                    continue
                print(png.name, png.stat().st_size // 1024, 'KB /', webp.stat().st_size // 1024, 'KB webp')
        page.close()
    browser.close()
