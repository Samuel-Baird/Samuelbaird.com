"""Search the local textbook index.

usage: python -I scripts/kb_search.py "spacing effect" [--book chance] [-n 10]
Prints book, chapter, printed page and a short snippet. Output is for in-session
lookup only; paraphrase it, never paste it into committed files.
"""
import sys, sqlite3, argparse, pathlib

ap = argparse.ArgumentParser()
ap.add_argument("query")
ap.add_argument("--book")
ap.add_argument("-n", type=int, default=10)
a = ap.parse_args()

db = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "knowledge" / "cache" / "kb.sqlite")
q = '"' + a.query.replace('"', '') + '"' if " " in a.query and not any(w in a.query for w in (" OR ", " AND ", "*")) else a.query
sql = "SELECT book, chapter, title, pdf, printed, snippet(pages, 0, '[', ']', ' ... ', 24) FROM pages WHERE pages MATCH ?"
args = [q]
if a.book:
    sql += " AND book = ?"
    args.append(a.book)
sql += " ORDER BY rank LIMIT ?"
args.append(a.n)
rows = db.execute(sql, args).fetchall()
if not rows:
    print("no hits")
for book, ch, title, pdf, printed, snip in rows:
    print(f"{book} | ch {ch} {title or ''} | p.{printed} (pdf {pdf})\n    {' '.join(snip.split())}")
