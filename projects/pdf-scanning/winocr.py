"""OCR with the engine built into Windows (Windows.Media.Ocr).

Used for the searchable text layer and the EPUB: it keeps word spacing and line positions,
and is fast (under a second a page). Output: JSONL, one record per page:
  {"page": n, "w": image width, "h": image height, "lines": [{"t", "x", "y", "x2", "y2"}, ...]}
Resumable: pages already in the cache are skipped.
"""
import asyncio, io, json, os, sys

import pymupdf as fitz
from PIL import Image


def _engine():
    import winrt.windows.media.ocr as ocr
    eng = ocr.OcrEngine.try_create_from_user_profile_languages()
    if eng is None:
        sys.exit('Windows OCR has no language pack for your user languages (Settings > Time & language).')
    return ocr, eng


async def _recognize(eng, ocr, pil):
    import winrt.windows.graphics.imaging as gi
    import winrt.windows.storage.streams as ss
    w, h = pil.size
    s = min(1.0, ocr.OcrEngine.max_image_dimension / max(w, h))
    if s < 1:
        pil = pil.resize((int(w * s), int(h * s)))
    rgba = pil.convert('RGBA')
    buf = ss.DataWriter()
    buf.write_bytes(rgba.tobytes())
    bmp = gi.SoftwareBitmap.create_copy_from_buffer(buf.detach_buffer(), gi.BitmapPixelFormat.RGBA8,
                                                    rgba.width, rgba.height)
    res = await eng.recognize_async(bmp)
    lines = []
    for ln in res.lines:
        ws = [wd.bounding_rect for wd in ln.words]
        lines.append(dict(t=ln.text, x=min(b.x for b in ws), y=min(b.y for b in ws),
                          x2=max(b.x + b.width for b in ws), y2=max(b.y + b.height for b in ws)))
    return lines, rgba.width, rgba.height


def page_image(doc, page):
    imgs = page.get_images()
    if len(imgs) == 1:
        return Image.open(io.BytesIO(doc.extract_image(imgs[0][0])['image'])).convert('RGB')
    pix = page.get_pixmap(dpi=300)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def ocr_pdf_windows(pdf, cache):
    ocr, eng = _engine()
    done = set()
    if os.path.exists(cache):
        done = {json.loads(l)['page'] for l in open(cache, encoding='utf-8')}
    doc = fitz.open(pdf)
    todo = [i for i in range(doc.page_count) if i + 1 not in done]
    with open(cache, 'a', encoding='utf-8') as f:
        for k, i in enumerate(todo, 1):
            lines, w, h = asyncio.run(_recognize(eng, ocr, page_image(doc, doc[i])))
            f.write(json.dumps(dict(page=i + 1, w=w, h=h, lines=lines), ensure_ascii=False) + '\n')
            f.flush()
            print(f'\rWindows OCR {k}/{len(todo)}', end='', file=sys.stderr, flush=True)
    if todo:
        print(file=sys.stderr)
    return {r['page']: r for r in map(json.loads, open(cache, encoding='utf-8'))}
