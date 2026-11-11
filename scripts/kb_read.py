"""Print cached textbook pages by PRINTED page range (local reading aid).

usage: python -I scripts/kb_read.py <slug> <first printed page> <last printed page>
Prints each page as '--- p.<printed> (pdf <n>) ---' followed by its text.
Output is book text: read it, paraphrase it, never commit it.
"""
import sys, json, pathlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
slug, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
root = pathlib.Path(__file__).resolve().parent.parent / "knowledge"
offset = json.loads((root / "learning" / "books" / f"{slug}.toc.json").read_text(encoding="utf-8"))["offset"]
for line in (root / "cache" / f"{slug}.pages.jsonl").open(encoding="utf-8"):
    p = json.loads(line)
    printed = p["pdf"] - offset
    if a <= printed <= b:
        print(f"--- p.{printed} (pdf {p['pdf']}) ---")
        print(p["text"].strip())
