"""Copyright guardrail: flag verbatim runs of book text in committed knowledge notes.

usage: python -I scripts/kb_check.py [--run 10]
Scans knowledge/**/*.md (not the cache) and reports any run of >= N consecutive words
that also appears in a local textbook cache page. Exit code 1 if anything is found.
Needs the local cache (knowledge/cache/*.pages.jsonl); without it there is nothing to compare.
"""
import sys, re, json, glob, pathlib, argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("--run", type=int, default=10, help="consecutive words that count as copying (default 10)")
N = ap.parse_args().run
root = pathlib.Path(__file__).resolve().parent.parent / "knowledge"

def words(s):
    return re.findall(r"[a-z0-9']+", s.lower().replace("’", "'"))

grams = {}
caches = sorted((root / "cache").glob("*.pages.jsonl"))
if not caches:
    sys.exit("no cache found; run kb_extract.py first")
for c in caches:
    book = c.name.removesuffix(".pages.jsonl")
    prev = []
    for line in c.open(encoding="utf-8"):
        p = json.loads(line)
        w = prev[-(N - 1):] + words(p["text"])  # runs may cross a page break
        for i in range(len(w) - N + 1):
            grams.setdefault(tuple(w[i:i + N]), (book, p["pdf"]))
        prev = words(p["text"])

hits = 0
for md in sorted(root.rglob("*.md")):
    for ln, text in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if text.lstrip().startswith("#") or "Key terms" in text[:30] or text.startswith("**Citation"):
            continue  # headings mirror book contents; term lists are bare terms
        w = words(text)
        for i in range(len(w) - N + 1):
            g = tuple(w[i:i + N])
            if g in grams:
                book, pdf = grams[g]
                print(f"{md.relative_to(root.parent)}:{ln}: {N}+ words match {book} pdf {pdf}: \"{' '.join(g)}\"")
                hits += 1
                break
print(f"{hits} verbatim line(s) found at run length {N}")
sys.exit(1 if hits else 0)
