"""Build the local SQLite FTS5 search index over every knowledge/cache/*.pages.jsonl.

usage: python -I scripts/kb_index.py
Chapter labels come from knowledge/learning/books/<slug>.toc.json when it exists
(each chapter spans from its pdf start page to the next chapter's start).
"""
import json, sqlite3, pathlib

root = pathlib.Path(__file__).resolve().parent.parent / "knowledge"
cache = root / "cache"
db_path = cache / "kb.sqlite"
if db_path.exists():
    db_path.unlink()
db = sqlite3.connect(db_path)
db.execute("CREATE VIRTUAL TABLE pages USING fts5(text, book UNINDEXED, chapter UNINDEXED, title UNINDEXED, pdf UNINDEXED, printed UNINDEXED, tokenize='porter unicode61')")

total = 0
for jl in sorted(cache.glob("*.pages.jsonl")):
    slug = jl.name.removesuffix(".pages.jsonl")
    toc_file = root / "learning" / "books" / f"{slug}.toc.json"
    chapters = json.loads(toc_file.read_text(encoding="utf-8"))["chapters"] if toc_file.exists() else []
    starts = sorted(chapters, key=lambda c: c["pdf"])
    for line in jl.open(encoding="utf-8"):
        p = json.loads(line)
        ch = [c for c in starts if c["pdf"] <= p["pdf"]]
        c = ch[-1] if ch else None
        db.execute("INSERT INTO pages VALUES (?,?,?,?,?,?)",
                   (p["text"], slug, c["ch"] if c else None, c["title"] if c else None, p["pdf"], p["printed"]))
        total += 1
db.commit()
print(total, "pages indexed ->", db_path)
