"""Checks that generated proclamations match the Church's own format and are complete.

    python -m proclamations.check              # format parity: English output at letter size vs the originals
    python -m proclamations.check --outputs    # integrity of every PDF under out/ (size, clipping, no lost words)

Format parity compares what can be compared across different typefaces: rule and frame positions,
colours and weights, column edges, title placement. Line breaks are not compared, because the
originals use proprietary fonts. Exit status is non-zero if anything fails.
"""
import re
import unicodedata
import sys
import tempfile
from pathlib import Path

import pymupdf
import yaml

from . import fonts, reference, scripts, sizes
from .generate import DOCS, HERE, load_text, localize, render

POS_TOL, END_TOL, COLOR_TOL = 2.0, 4.0, 0.08


def _rule_matches(ref, rules):
    for g in rules:
        if g["o"] != ref["o"] or abs(g["pos"] - ref["pos"]) > POS_TOL:
            continue
        if abs(g["a"] - ref["a"]) > END_TOL or abs(g["b"] - ref["b"]) > END_TOL:
            continue
        if max(abs(x - y) for x, y in zip(g["c"], ref["c"])) > COLOR_TOL:
            continue
        if ref["w"] and not (0.5 <= g["w"] / ref["w"] <= 1.6):
            continue
        return True
    return False


def format_check(slug, ref, out_dir):
    path = render(slug, scripts.get("english"), "letter", out_dir, with_credit=True)
    got = reference.measure(path)
    results = []
    results.append(("page size", abs(got["page"][0] - ref["page"][0]) <= 1.5 and abs(got["page"][1] - ref["page"][1]) <= 1.5,
                    f"{got['page']} vs {ref['page']}"))
    for r in ref["rules"]:
        label = f"{'horizontal' if r['o'] == 'h' else 'vertical'} rule at {r['pos']} ({r['a']}-{r['b']}, {r['w']}pt)"
        results.append((label, _rule_matches(r, got["rules"]), ""))
    for key, tol in (("col1_left", 6), ("col2_left", 6), ("body_top", 12), ("title_center_x", 6), ("title_top", 12)):
        a, b = got.get(key), ref.get(key)
        results.append((key, a is not None and b is not None and abs(a - b) <= tol, f"{a} vs {b} (tol {tol})"))
    ratio = got["body_size"] / ref["body_size"]
    results.append(("body type size within 30%", 0.7 <= ratio <= 1.3, f"{got['body_size']} vs {ref['body_size']}"))
    return results


# ------------------------------------------------------------------ output integrity
def _norm(text):
    out = []
    for ch in text:
        cp = ord(ch)
        out.append(chr(cp + 0x28) if 0x10400 <= cp <= 0x10427 else ch.casefold().replace("ı", "i"))   # Turkish dotless i is capitalized as I
    return re.findall(r"[\U00010428-\U0001044f\w]+", unicodedata.normalize("NFC", "".join(out)).replace("i̇", "i"))


def _split_dropcap(text):
    """The decorative initial is drawn as its own glyph, so extraction sees it as a separate token
    (the Church's own PDFs behave the same way)."""
    first, _, rest = text.partition(" ")
    head, tail = fonts.initial_split(first)
    return (head + " " + tail + " " + rest) if tail else text


TRACKED = {"restoration"}      # letter-spaced subtitle: extractors (and the Church's own PDF) return it letter by letter


def _expected_words(L, d):
    paras = list(L.paragraphs)
    verses = [t for _, t in L.verses]
    if paras:
        paras[0] = _split_dropcap(paras[0])
    if verses:
        verses[0] = _split_dropcap(verses[0])
    subtitle = "" if L.slug in TRACKED else L.subtitle
    parts = [L.title, subtitle, L.author, L.note, L.signature, L.date] + paras + verses
    parts += list(L.groups) + [n for names in L.names.values() for n in names]
    return _norm(" ".join(p for p in parts if p))


def _overlaps(spans, scale=1.0):
    """True when two text spans cover each other (a heading running into its neighbor). Only the middle band of each
    span's box is compared: tall scripts have line boxes taller than their line spacing, which is not a collision."""
    boxes = []
    for s in spans:
        t = s["text"].strip()
        if len(t) > 1 and not t.isdigit():
            x0, y0, x1, y1 = s["bbox"]
            mid, h = (y0 + y1) / 2, (y1 - y0) * 0.2
            boxes.append((x0, mid - h, x1, mid + h))
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            w = min(a[2], b[2]) - max(a[0], b[0])
            h = min(a[3], b[3]) - max(a[1], b[1])
            if w > 4 * scale and h > 0.5 * min(a[3] - a[1], b[3] - b[1]):
                return True
    return False


def output_check(path):
    slug, script_name, size = path.stem.rsplit("-", 2)       # <doc>-<edition>-<size>.pdf
    script = scripts.get(script_name)
    L, d = localize(slug, script)
    doc = pymupdf.open(path)
    page = doc[0]
    results = []
    w, h = sizes.get(size)
    results.append(("page size", len(doc) == 1 and abs(page.rect.width - w) < 0.7 and abs(page.rect.height - h) < 0.7,
                    f"{page.rect.width:.1f}x{page.rect.height:.1f}"))
    spans = [s for b in page.get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"] if s["text"].strip()]
    inside = all(-0.5 <= s["bbox"][0] and s["bbox"][2] <= page.rect.width + 0.5 and -0.5 <= s["bbox"][1]
                 and s["bbox"][3] <= page.rect.height + 0.5 for s in spans)
    results.append(("all text inside the page", inside, ""))
    results.append(("no overlapping text", not _overlaps(spans, page.rect.width / 612), ""))
    raw = page.get_text()
    # a word split across lines extracts as "pri-" / "mavera": accept the rejoined word as well
    rejoined = [a + b for a, b in re.findall(r"(\w+)-\n(\w+)", raw)]
    got = _norm(raw) + _norm(" ".join(rejoined))
    want = _expected_words(L, d)
    if not script.spaced or script.rtl:
        # no spaces between words (or a right-to-left text layer whose word gaps readers guess): compare the letters
        from collections import Counter
        have, need = Counter("".join(got)), Counter("".join(want))
        lost = need - have
        results.append(("no source letters lost", not lost, f"{sum(need.values())} expected, missing {dict(list(lost.items())[:8])}"))
    else:
        missing, remaining = [], list(got)
        for wd in want:
            if wd in remaining:
                remaining.remove(wd)
            else:
                missing.append(wd)
        results.append(("no source words lost", not missing, f"{len(want)} expected, missing {missing[:8]}"))
    if slug in TRACKED:
        letters = "".join(_norm(L.subtitle))
        stream = "".join(_norm(raw))                      # letters only, so tracked spacing and split diacritics do not matter
        as_words = all(w in got for w in _norm(L.subtitle))      # some fonts extract tracked text as words
        results.append(("letter-spaced subtitle present", letters in stream or as_words, letters[:30]))
    return results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    failures = 0
    if "--outputs" in argv:
        only = argv[argv.index("--sizes") + 1].split(",") if "--sizes" in argv else None
        root = Path(argv[argv.index("--dir") + 1]) if "--dir" in argv else HERE / "out"
        pdfs = [p for p in sorted(root.glob("*/*.pdf")) if not only or p.stem.rsplit("-", 1)[1] in only]
        if not pdfs:
            print("no PDFs under proclamations/out; run proclamations.generate first")
            return 1
        bad = 0
        for p in pdfs:
            res = output_check(p)
            fails = [r for r in res if not r[1]]
            bad += bool(fails)
            if fails:
                print(f"FAIL {p.relative_to(root.parent) if root.parent in p.parents else p}: " + "; ".join(f"{a} ({c})" for a, _, c in fails))
        print(f"{len(pdfs)} PDFs checked, {bad} with problems")
        return 1 if bad else 0

    ref = reference.load()
    with tempfile.TemporaryDirectory() as tmp:
        for slug in DOCS:
            res = format_check(slug, ref[slug], tmp)
            n_ok = sum(ok for _, ok, _ in res)
            print(f"{slug}: {n_ok}/{len(res)} checks match the original")
            for label, ok, detail in res:
                if not ok:
                    failures += 1
                    print(f"   MISMATCH {label} {detail}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
