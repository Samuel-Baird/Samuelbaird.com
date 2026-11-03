"""Checks that generated proclamations match the Church's own format and are complete.

    python -m proclamations.check              # format parity: English output at letter size vs the originals
    python -m proclamations.check --outputs    # integrity of every PDF under out/ (size, clipping, no lost words)

Format parity compares what can be compared across different typefaces: rule and frame positions,
colours and weights, column edges, title placement. Line breaks are not compared, because the
originals use proprietary fonts. Exit status is non-zero if anything fails.
"""
import re
import sys
import tempfile
from pathlib import Path

import pymupdf
import yaml

from . import reference, scripts, sizes
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
    path = render(slug, scripts.get("latin"), "letter", out_dir, with_credit=True)
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
        out.append(chr(cp + 0x28) if 0x10400 <= cp <= 0x10427 else ch.casefold())
    return re.findall(r"[\U00010428-\U0001044f\w]+", "".join(out))


def _split_dropcap(text):
    """The decorative initial is drawn as its own glyph, so extraction sees it as a separate token
    (the Church's own PDFs behave the same way)."""
    first, _, rest = text.partition(" ")
    return (first[0] + " " + first[1:] + " " + rest) if len(first) > 1 else text


def _expected_words(L, d):
    paras = list(L.paragraphs)
    verses = [t for _, t in L.verses]
    if paras:
        paras[0] = _split_dropcap(paras[0])
    if verses:
        verses[0] = _split_dropcap(verses[0])
    parts = [L.title, L.subtitle, L.author, L.note, L.signature, L.date] + paras + verses
    parts += list(L.groups) + [n for names in L.names.values() for n in names]
    return _norm(" ".join(p for p in parts if p))


def output_check(path):
    slug = path.parent.name
    script_name = path.name.split("-")[-2]
    size = path.stem.rsplit("-", 1)[1]
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
    got = _norm(page.get_text())
    want = _expected_words(L, d)
    missing, remaining = [], list(got)
    for wd in want:
        if wd in remaining:
            remaining.remove(wd)
        else:
            missing.append(wd)
    results.append(("no source words lost", not missing, f"{len(want)} expected, missing {missing[:8]}"))
    return results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    failures = 0
    if "--outputs" in argv:
        pdfs = sorted((HERE / "out").glob("*/*/*.pdf"))
        if not pdfs:
            print("no PDFs under proclamations/out; run proclamations.generate first")
            return 1
        bad = 0
        for p in pdfs:
            res = output_check(p)
            fails = [r for r in res if not r[1]]
            bad += bool(fails)
            if fails:
                print(f"FAIL {p.relative_to(HERE)}: " + "; ".join(f"{a} ({c})" for a, _, c in fails))
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
