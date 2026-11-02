"""Discover renderings not yet in a concept's candidate list.

For each concept+language, takes the Church target paragraphs whose English side
contains the concept but which matched no known candidate (scratch/uncovered),
and ranks 1-3 word n-grams by how over-represented they are against a background
sample of Church paragraphs. Results are written into data/attestations/<slug>.json
under `inferred` (status: inferred, i.e. not yet reviewed). Never treated as attested.
"""
import json
import math
import re
import sys
from collections import Counter

from .config import DATA, LANGS, ROOT
from .textutil import fold, tokens

MIN_UNCOVERED = 3
MIN_FRAC = 0.2        # n-gram must appear in this share of uncovered paragraphs
MIN_RATIO = 6.0       # and be this many times more frequent than in the background
MAX_N = 3
TOP = 3


def grams(text):
    """{folded_ngram: surface_form} for distinct n-grams of one paragraph."""
    low = text.lower()
    toks = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\w+", low)]
    ft = tokens(fold(text))
    out = {}
    for n in range(1, MAX_N + 1):
        for i in range(len(toks) - n + 1):
            key = " ".join(t for t, _ in ft[i:i + n])
            out.setdefault(key, low[toks[i][1]:toks[i + n - 1][2]])
    return out


def usable(k, bg_df, nbg):
    """Letters only, no short tokens, no common function word at either edge."""
    ws = k.split()
    if not all(w.isalpha() and len(w) >= 3 for w in ws):
        return False
    return all(bg_df.get(w, 0) / nbg < 0.04 for w in (ws[0], ws[-1]))


def main():
    scratch = ROOT / "scratch"
    for lang in LANGS:
        bg_docs = [json.loads(l) for l in open(scratch / f"background-{lang}.jsonl", encoding="utf-8")]
        bg_df = Counter()
        for t in bg_docs:
            bg_df.update(grams(t).keys())
        nbg = len(bg_docs)
        done = 0
        for f in sorted((scratch / "uncovered" / lang).glob("*.jsonl")):
            slug = f.stem
            rows = [json.loads(l) for l in open(f, encoding="utf-8")]
            att_path = DATA / "attestations" / f"{slug}.json"
            att = json.loads(att_path.read_text(encoding="utf-8"))
            att[lang].pop("inferred", None)
            if len(rows) < MIN_UNCOVERED:
                att_path.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
                continue
            df, surf = Counter(), {}
            srcs = {}
            per = []
            for r in rows:
                g = grams(r["tr"])
                per.append(g)
                df.update(g.keys())
                for k, v in g.items():
                    surf.setdefault(k, v)
                    srcs.setdefault(k, set()).add(r.get("id"))
            n = len(rows)
            scored = []
            for k, c in df.items():
                frac = c / n
                if frac < MIN_FRAC or c < 2 or len(srcs[k]) < 2 or not usable(k, bg_df, nbg):
                    continue
                ratio = frac / ((bg_df.get(k, 0) + 1) / (nbg + 1))
                if ratio >= MIN_RATIO:
                    scored.append((frac * math.log(ratio), k, c, ratio))
            scored.sort(reverse=True)
            picked = []
            for _, k, c, ratio in scored:
                if any(k in p["_k"] or p["_k"] in k for p in picked):
                    continue
                ex = next(r for r, g in zip(rows, per) if k in g)
                low = ex["tr"].lower()
                pos = low.find(surf[k])
                picked.append({
                    "_k": k, "term": surf[k], "evidence": ["inferred"], "paragraphs": c,
                    "share_of_uncovered": round(c / n, 3), "ratio": round(ratio, 1),
                    "source": ex.get("id"), "kind": ex["src"],
                    "sample": ex["tr"][max(0, pos - 80): pos + len(surf[k]) + 80].strip(),
                })
                if len(picked) >= TOP:
                    break
            for p in picked:
                p.pop("_k")
            if picked:
                att[lang]["inferred"] = picked
                done += 1
            att_path.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{lang}: concepts with inferred variants: {done}")


if __name__ == "__main__":
    sys.exit(main())
