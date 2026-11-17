"""Index textbook problem numbers by section heading (private cache only; never published).

usage: python -I scripts/problem_index.py "<textbook.pdf>" courses/me3320/textbook/toc.json courses/me3320/textbook/cache/problem_index.json
"""
import sys, json, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pymupdf
pdf, tocf, out = sys.argv[1:4]
doc = pymupdf.open(pdf)
toc = json.load(open(tocf))
chs = {c["ch"]: c for c in toc["chapters"]}
res = {}
for ch, c in chs.items():
    if not c["problems_pdf"]: continue
    start = c["problems_pdf"]
    end = (chs[ch + 1]["pdf"] - 1) if ch + 1 in chs else start + 20
    lines = []
    for p in range(start, end + 1):
        lines += [l.strip() for l in doc[p - 1].get_text().split("\n") if l.strip()]
    entries, head, seen = [], None, set()
    small = {"and", "of", "in", "with", "for", "the", "a", "to", "on", "by", "from", "at", "or", "over", "across", "within"}
    pat = re.compile(r"^" + str(ch) + r"\.(\d+)\s+(\S.*)$")
    for i, l in enumerate(lines):
        m = pat.match(l)
        if m and int(m[1]) not in seen:
            seen.add(int(m[1]))
            entries.append({"n": int(m[1]), "head": head, "text": m[2][:100]})
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        words = l.replace("–", "-").split()
        if (pat.match(nxt) and 1 <= len(words) <= 7 and len(l) < 60 and not re.search(r"[0-9=.,;:]", l)
                and all(w[0].isupper() or w.lower() in small for w in words)):
            head = l
    res[ch] = entries
json.dump(res, open(out, "w"), indent=1)
print({k: len(v) for k, v in res.items()})
