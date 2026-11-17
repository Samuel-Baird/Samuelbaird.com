"""Render the social card (src/pages/social/quote.astro) to PNG, in both alphabets.

Run with the dev server up:  python scripts/social-image.py [http://localhost:4330]
Writes public/social/deseret-alphabet-quote.png (Latin) and ...-dsrt.png (Deseret), 1200 x 630,
plus 2x versions for crisp display on the home page. Needs Playwright and an installed Chrome.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:4330').rstrip('/')
OUT = Path(__file__).resolve().parent.parent / 'public' / 'social'

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome')
    for scale, suffix in ((1, ''), (2, '@2x')):
        page = browser.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=scale)
        for script, name in (('latn', 'deseret-alphabet-quote'), ('dsrt', 'deseret-alphabet-quote-dsrt')):
            page.goto(f'{BASE}/social/quote/?script={script}', wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            page.evaluate("document.querySelector('astro-dev-toolbar')?.remove()")  # dev server only
            page.wait_for_timeout(400)
            out = OUT / f'{name}{suffix}.png'
            page.locator('#card').screenshot(path=str(out))
            print(out.relative_to(OUT.parent.parent), out.stat().st_size // 1024, 'KB')
        page.close()
    browser.close()
