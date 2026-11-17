"""Extract per-page text from a textbook PDF into a local, gitignored cache.

usage: python -I scripts/kb_extract.py <pdf> <slug>
out:   knowledge/cache/<slug>.pages.jsonl   one JSON object per PDF page:
       {"pdf": n, "printed": m|null, "text": "..."}

Printed page numbers are guessed from a bare number in the first/last few lines
of each page; the most common (pdf - printed) offset is then used to fill gaps.
The cache holds book text, so it must never be committed (see .gitignore).
"""
import sys, json, re, collections, pathlib
import pymupdf

pdf, slug = sys.argv[1], sys.argv[2]
out = pathlib.Path(__file__).resolve().parent.parent / "knowledge" / "cache" / f"{slug}.pages.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)

doc = pymupdf.open(pdf)
pages = [doc[i].get_text() for i in range(doc.page_count)]

def guess_printed(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines[:3] + lines[-3:]:
        if re.fullmatch(r"\d{1,4}", l):
            return int(l)
    return None

guesses = [guess_printed(t) for t in pages]
offsets = collections.Counter(i + 1 - g for i, g in enumerate(guesses) if g is not None and 0 < g < doc.page_count)
offset = offsets.most_common(1)[0][0] if offsets else None

with open(out, "w", encoding="utf-8") as f:
    for i, (t, g) in enumerate(zip(pages, guesses)):
        printed = g if (g is not None and offset is not None and i + 1 - g == offset) else (i + 1 - offset if offset is not None and i + 1 - offset > 0 else None)
        f.write(json.dumps({"pdf": i + 1, "printed": printed, "text": t}, ensure_ascii=False) + "\n")

print(f"{slug}: {len(pages)} pages, offset={offset} (votes {offsets.most_common(1)}), -> {out}")
