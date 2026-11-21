"""Smaller, searchable copy of a scanned book.

Pages are resampled to `dpi` (150 by default, from ~340 in a phone/BookChanger scan). Inside pages
become grayscale with the paper pushed to white (white point = the page's own paper colour, so blank
pages stay blank and show-through disappears); colour pages (the cover) stay colour. Each line of
Windows OCR text is laid over the page as invisible text, so the PDF can be searched and copied from.
"""
import io

import pymupdf as fitz
from PIL import Image

from winocr import page_image

FONTFILE = r'C:/Windows/Fonts/arial.ttf'


def clean_gray(img):
    g = img.convert('L')
    hist = g.histogram(); n = sum(hist); acc = 0
    for paper, c in enumerate(hist):           # 90th percentile = paper colour
        acc += c
        if acc >= 0.9 * n:
            break
    cut = max(120, paper * 0.88)
    return g.point(lambda v: 255 if v > cut else int(v * 255 / cut))


def make_small(src, out, ocr=None, dpi=150, quality=55, color_pages=(1,)):
    font = fitz.Font(fontfile=FONTFILE)
    doc = fitz.open(src)
    new = fitz.open()
    for i, page in enumerate(doc):
        pno = i + 1
        rect = page.rect
        img = page_image(doc, page)
        small = img.resize((round(rect.width / 72 * dpi), round(rect.height / 72 * dpi)), Image.LANCZOS)
        bio = io.BytesIO()
        if pno in color_pages:
            small.save(bio, 'JPEG', quality=70, optimize=True)
        else:
            clean_gray(small).save(bio, 'JPEG', quality=quality, optimize=True)
        np_ = new.new_page(width=rect.width, height=rect.height)
        np_.insert_image(np_.rect, stream=bio.getvalue())
        r = (ocr or {}).get(pno)
        if not r:
            continue
        sx, sy = rect.width / r['w'], rect.height / r['h']
        for ln in r['lines']:
            t = ln['t'].strip()
            box = fitz.Rect(ln['x'] * sx, ln['y'] * sy, ln['x2'] * sx, ln['y2'] * sy)
            if not t or box.width <= 0 or box.height <= 0:
                continue
            fs = box.height * 0.9
            tl = font.text_length(t, fontsize=fs)
            m = fitz.Matrix(box.width / tl if tl else 1, 0, 0, 1, 0, 0)   # stretch to the line's width
            np_.insert_text(fitz.Point(box.x0, box.y1 - box.height * 0.15), t, fontsize=fs, fontname='F0',
                            fontfile=FONTFILE, render_mode=3, morph=(fitz.Point(box.x0, box.y1), m))
    new.set_metadata(doc.metadata)
    new.subset_fonts()
    new.save(out, garbage=4, deflate=True)
    return new.page_count
