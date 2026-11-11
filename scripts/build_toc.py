"""Build courses/<course>/textbook/toc.json from the textbook PDF's bookmarks.

usage: python -I scripts/build_toc.py "<path to textbook.pdf>" courses/me3320/textbook/toc.json

printed page = PDF page - OFFSET (24 for Bergman 8e). Only refs are stored, never book text.
"""
import sys, json, re
import pymupdf

OFFSET = 24
pdf_path, out = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf_path)
chapters, cur = [], None
for lvl, title, page in doc.get_toc():
    m = re.match(r"^(\d+)\.\s+(.*)$", title)
    if lvl == 1 and m:
        cur = {"ch": int(m[1]), "title": m[2], "pdf": page, "printed": page - OFFSET, "sections": [], "problems_pdf": None}
        chapters.append(cur)
    elif lvl == 2 and cur:
        s = re.match(r"^(\d+\.\d+)\s+(.*)$", title)
        if s:
            cur["sections"].append({"sec": s[1], "title": s[2].replace("\ufffd", "-"), "pdf": page, "printed": page - OFFSET})
        elif title == "Problems":
            cur["problems_pdf"] = page
        # references are skipped
json.dump({"offset": OFFSET, "chapters": chapters}, open(out, "w"), indent=1)
print(len(chapters), "chapters ->", out)

# ---- worked-example index: only number + printed page are stored (no book text) ----
ex = {}
sec_pages = {c["ch"]: [(s["sec"], s["pdf"]) for s in c["sections"]] for c in chapters}
for c in chapters:
    end = next((d["pdf"] for d in chapters if d["ch"] == c["ch"] + 1), c["pdf"] + 80)
    for p in range(c["pdf"], end):
        for m in re.finditer(r"(?im)^\s*example\s+(\d+\.\d+)\s*$", doc[p - 1].get_text()):
            n = m[1]
            if n.split(".")[0] == str(c["ch"]) and n not in ex:
                sec = max((s for s in sec_pages[c["ch"]] if s[1] <= p), key=lambda s: s[1], default=(None, 0))[0]
                ex[n] = {"ex": n, "printed": p - OFFSET, "pdf": p, "sec": sec}
json.dump({"offset": OFFSET, "chapters": chapters, "examples": sorted(ex.values(), key=lambda e: [int(x) for x in e["ex"].split(".")])},
          open(out, "w"), indent=1)
print(len(ex), "examples indexed")
