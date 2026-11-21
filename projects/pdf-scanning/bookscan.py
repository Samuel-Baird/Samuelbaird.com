"""Check, clean up and assemble book scans (image-only PDFs).

  python bookscan.py check    scan.pdf            OCR every page, write a report of pages to rescan and duplicates
  python bookscan.py drop     scan.pdf 59 60 ...  copy the PDF without the given pages (1-based)
  python bookscan.py assemble scan.pdf --front cover.pdf [--back back.pdf] --title "Book Title" [--author "..."]

`check` caches OCR in <scan>.bookscan/ocr.jsonl and resumes if interrupted.
Every write goes to a new file; the input PDFs are never changed.
See README.md for the workflow and how to read the report.
"""
import argparse, hashlib, io, json, os, re, statistics as st, sys

import pymupdf as fitz


# ---------- OCR ----------

def page_image(doc, page):
    """The page's embedded scan if it has exactly one, else a 200 dpi render."""
    from PIL import Image
    imgs = page.get_images()
    if len(imgs) == 1:
        data = doc.extract_image(imgs[0][0])['image']
        return Image.open(io.BytesIO(data)).convert('RGB')
    pix = page.get_pixmap(dpi=200)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def ocr_pdf(pdf, cache, limit=None):
    import numpy as np, cv2
    from rapidocr_onnxruntime import RapidOCR
    done = set()
    if os.path.exists(cache):
        done = {json.loads(l)['page'] for l in open(cache, encoding='utf-8')}
    doc = fitz.open(pdf)
    n = doc.page_count if limit is None else min(limit, doc.page_count)
    todo = [i for i in range(n) if i + 1 not in done]
    if not todo:
        return
    ocr = RapidOCR()
    with open(cache, 'a', encoding='utf-8') as f:
        for k, i in enumerate(todo, 1):
            pil = page_image(doc, doc[i])
            arr = np.array(pil)
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            res, _ = ocr(arr)
            res = res or []
            confs = [float(r[2]) for r in res]
            rec = dict(page=i + 1, w=pil.width, h=pil.height,
                       lap=float(cv2.Laplacian(gray, cv2.CV_64F).var()),
                       mean_bright=float(gray.mean()),
                       n_lines=len(res),
                       conf_mean=float(np.mean(confs)) if confs else 0.0,
                       conf_low_frac=float(np.mean([c < 0.8 for c in confs])) if confs else 1.0,
                       text='\n'.join(r[1] for r in res))
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            f.flush()
            print(f'\rOCR {k}/{len(todo)} (page {i + 1})', end='', file=sys.stderr, flush=True)
    print(file=sys.stderr)


# ---------- analysis ----------

# Running-header page numbers: "84 MORMONISM IN FIVE MINUTES" (verso) or
# "AUTHOR-CHAPTER TITLE? 65" (recto). Chapter numbers alone on a line don't match.
VERSO = re.compile(r'^(\d{1,4})\s*[A-Z][A-Z]')
RECTO = re.compile(r'[A-Za-z?!.)"”]\s*(\d{1,4})$')


def printed_number(text, header_re=None):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return None
    head = lines[0]
    if header_re:
        m = re.search(header_re, head)
        return int(m.group(1)) if m else None
    m = VERSO.match(head)
    if m:
        return int(m.group(1))
    letters = re.sub(r'[^A-Za-z]', '', head)
    m = RECTO.search(head)
    if m and len(letters) >= 8 and letters.upper() == letters:
        return int(m.group(1))
    return None


def shingles(text):
    w = re.findall(r'[a-z]+', text.lower())
    return set(zip(w, w[1:], w[2:], w[3:]))


def analyze(recs, header_re=None):
    recs = sorted(recs, key=lambda r: r['page'])
    by = {r['page']: r for r in recs}
    text_pages = [r for r in recs if r['n_lines'] > 10]
    med_lap = st.median(r['lap'] for r in text_pages) if text_pages else 0
    med_conf = st.median(r['conf_mean'] for r in text_pages) if text_pages else 0

    quality = []
    for r in recs:
        why = []
        if r['n_lines'] > 5 and r['conf_mean'] < 0.93:
            why.append(f"low OCR confidence {r['conf_mean']:.2f}")
        if r['n_lines'] > 5 and r['conf_low_frac'] > 0.15:
            why.append(f"{r['conf_low_frac']:.0%} of lines unsure")
        if r['n_lines'] > 5 and r['lap'] < 0.3 * med_lap:
            why.append(f"soft image (sharpness {r['lap']:.0f} vs median {med_lap:.0f})")
        if r['mean_bright'] < 140:
            why.append(f"dark (brightness {r['mean_bright']:.0f})")
        if why:
            quality.append((r['page'], why))
    blank = [r['page'] for r in recs if r['n_lines'] <= 1]

    # printed page numbers -> breaks in the pdf-to-printed offset
    nums = [(r['page'], printed_number(r['text'], header_re)) for r in recs]
    nums = [(p, n) for p, n in nums if n is not None]
    # drop isolated misreads: a number whose offset matches neither neighbour
    clean = []
    for i, (p, n) in enumerate(nums):
        off = p - n
        nb = [nums[j][0] - nums[j][1] for j in (i - 1, i + 1) if 0 <= j < len(nums)]
        if off in nb or len(nums) == 1:
            clean.append((p, n))
    breaks = []
    for (p0, n0), (p1, n1) in zip(clean, clean[1:]):
        d = (p1 - n1) - (p0 - n0)
        if d > 0:
            breaks.append((p0, n0, p1, n1, f'{d} extra scan(s) between'))
        elif d < 0:
            breaks.append((p0, n0, p1, n1, f'{-d} printed page(s) missing between'))
    seen = {}
    for p, n in clean:
        seen.setdefault(n, []).append(p)
    repeats = {n: ps for n, ps in seen.items() if len(ps) > 1}

    # duplicate text
    S = [(r['page'], shingles(r['text'])) for r in recs]
    dups = []
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            a, b = S[i][1], S[j][1]
            if len(a) < 15 or len(b) < 15:
                continue
            inter = len(a & b)
            jac = inter / len(a | b)
            ov = inter / min(len(a), len(b))
            if jac > 0.6 or ov > 0.85:
                dups.append((S[i][0], S[j][0], jac, ov))

    return dict(pages=len(recs), med_lap=med_lap, med_conf=med_conf, quality=quality,
                blank=blank, numbered=len(clean), first=clean[0] if clean else None,
                last=clean[-1] if clean else None, breaks=breaks, repeats=repeats,
                dups=dups, by=by)


def overlap(a, b):
    if len(a) < 5 or len(b) < 5:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def rescanned_blocks(a):
    """Each 'extra scan' break means a run of d pages was scanned twice in a row.
    Find the run (block A immediately followed by its copy B) and keep the copy with
    better OCR confidence. Returns [(block_a, block_b, similarity, drop)]."""
    by, n = a['by'], a['pages']
    sh = {p: shingles(r['text']) for p, r in by.items()}
    out = []
    for p0, n0, p1, n1, msg in a['breaks']:
        d = (p1 - n1) - (p0 - n0)
        if d <= 0:
            continue
        best = None
        for s in range(max(1, p0 - 2 * d + 1), p1 - d + 1):
            A = list(range(s, s + d)); B = list(range(s + d, s + 2 * d))
            if B[-1] > n:
                continue
            sim = sum(overlap(sh[x], sh[y]) for x, y in zip(A, B)) / d
            if best is None or sim > best[2]:
                best = (A, B, sim)
        if not best or best[2] < 0.4:
            out.append((None, None, 0.0, []))
            continue
        A, B, sim = best
        conf = lambda blk: sum(by[p]['conf_mean'] for p in blk) / len(blk)
        out.append((A, B, sim, B if conf(A) >= conf(B) else A))
    return out


def suggest_drops(a):
    return sorted({p for *_, drop in rescanned_blocks(a) for p in drop})


def report(pdf, a, outdir):
    L = [f'# Scan check: {os.path.basename(pdf)}', '',
         f"{a['pages']} pages. Median OCR confidence on text pages {a['med_conf']:.3f}.", '']
    L += ['## Page order', '']
    if a['first']:
        L.append(f"Running-header page numbers found on {a['numbered']} pages, "
                 f"pdf {a['first'][0]} = p.{a['first'][1]} to pdf {a['last'][0]} = p.{a['last'][1]}.")
    else:
        L.append('No running-header page numbers recognised (try --header-regex).')
    if a['breaks']:
        L.append('')
        for p0, n0, p1, n1, msg in a['breaks']:
            L.append(f'- pdf {p0} (p.{n0}) -> pdf {p1} (p.{n1}): {msg}')
    else:
        L.append('No gaps or extra scans inside that range.')
    if a['repeats']:
        L += ['', 'Printed page numbers that appear more than once: ' +
              ', '.join(f'p.{n} at pdf {ps}' for n, ps in sorted(a['repeats'].items()))]
    blocks = rescanned_blocks(a)
    drops = []
    if blocks:
        L += ['', '## Rescanned pages', '']
        for A, B, sim, drop in blocks:
            if A is None:
                L.append('- one extra-scan break could not be matched to a repeated block; check it by eye')
            else:
                L.append(f'- pdf {A} scanned again as pdf {B} (text match {sim:.0%}); '
                         f'suggest dropping {drop} (lower OCR confidence)')
        drops = suggest_drops(a)
        if drops:
            L += ['', 'Compare both copies in `review/` first (OCR cannot see fingers or tabs), then:', '',
                  f"    python bookscan.py drop \"{pdf}\" {' '.join(map(str, drops))}"]
    L += ['', '## Pages with matching text', '',
          'Includes the rescans above; other pairs are usually repeated bios or cross-reference lists.', '']
    if a['dups']:
        for p, q, jac, ov in a['dups']:
            L.append(f'- pdf {p} and {q}: shared phrases {ov:.0%} (jaccard {jac:.2f})')
    else:
        L.append('None found.')
    L += ['', '## Pages to look at', '',
          'Thumbnails are in `review/`. Look before rescanning: short pages (end of chapter, '
          'reading lists) often score soft only because they are mostly blank.', '']
    if a['quality']:
        for p, why in a['quality']:
            L.append(f"- pdf {p}: {'; '.join(why)}")
    else:
        L.append('None flagged.')
    L += ['', f"Blank or near-blank pages (usually dividers): {a['blank'] or 'none'}"]
    path = os.path.join(outdir, 'report.md')
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return path, drops


def thumbnails(pdf, pages, outdir):
    os.makedirs(os.path.join(outdir, 'review'), exist_ok=True)
    doc = fitz.open(pdf)
    for p in pages:
        doc[p - 1].get_pixmap(dpi=90).save(os.path.join(outdir, 'review', f'p{p:04d}.png'))


# ---------- PDF writing ----------

def image_digests(doc):
    out = []
    for p in doc:
        imgs = p.get_images()
        out.append(hashlib.md5(doc.extract_image(imgs[0][0])['image']).hexdigest() if imgs else None)
    return out


def save_new(doc, path):
    if os.path.exists(path):
        sys.exit(f'{path} already exists; not overwriting.')
    doc.save(path, garbage=3, deflate=True)


def cmd_check(args):
    outdir = args.out or os.path.splitext(args.pdf)[0] + '.bookscan'
    os.makedirs(outdir, exist_ok=True)
    cache = os.path.join(outdir, 'ocr.jsonl')
    ocr_pdf(args.pdf, cache, args.limit)
    recs = [json.loads(l) for l in open(cache, encoding='utf-8')]
    a = analyze(recs, args.header_regex)
    rescans = {p for A, B, *_ in rescanned_blocks(a) if A for p in A + B}
    flagged = sorted({p for p, _ in a['quality']} | {p for d in a['dups'] for p in d[:2]} | rescans)
    thumbnails(args.pdf, flagged, outdir)
    path, drops = report(args.pdf, a, outdir)
    print(open(path, encoding='utf-8').read())
    print(f'Report: {path}')


def cmd_drop(args):
    src = fitz.open(args.pdf)
    drop = sorted(set(args.pages))
    out = args.out or os.path.splitext(args.pdf)[0] + '_deduped.pdf'
    before = image_digests(src)
    src.delete_pages([p - 1 for p in drop])
    save_new(src, out)
    want = [d for i, d in enumerate(before, 1) if i not in drop]
    ok = image_digests(fitz.open(out)) == want
    print(f'{out}: {len(want)} pages, dropped {drop}. Page images match original: {ok}')


def cmd_assemble(args):
    parts = ([args.front] if args.front else []) + [args.pdf] + ([args.back] if args.back else [])
    doc = fitz.open()
    for p in parts:
        doc.insert_pdf(fitz.open(p))
    meta = {'title': args.title}
    if args.author:
        meta['author'] = args.author
    doc.set_metadata(meta)
    safe = re.sub(r'[<>:"/\\|?*]', '', args.title).strip()
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.pdf)), safe + '.pdf')
    save_new(doc, out)
    want = sum((image_digests(fitz.open(p)) for p in parts), [])
    ok = image_digests(fitz.open(out)) == want
    print(f'{out}: {len(want)} pages. Page images match sources: {ok}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check')
    c.add_argument('pdf')
    c.add_argument('--out', help='output folder (default <pdf>.bookscan)')
    c.add_argument('--limit', type=int, help='only OCR the first N pages (quick test)')
    c.add_argument('--header-regex', help='regex with one group capturing the page number in the first OCR line')
    c.set_defaults(fn=cmd_check)
    d = sub.add_parser('drop')
    d.add_argument('pdf')
    d.add_argument('pages', type=int, nargs='+')
    d.add_argument('--out')
    d.set_defaults(fn=cmd_drop)
    s = sub.add_parser('assemble')
    s.add_argument('pdf')
    s.add_argument('--front')
    s.add_argument('--back')
    s.add_argument('--title', required=True)
    s.add_argument('--author')
    s.add_argument('--out')
    s.set_defaults(fn=cmd_assemble)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
