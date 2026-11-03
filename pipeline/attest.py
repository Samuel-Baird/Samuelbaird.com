"""Count how Church-published translations render each concept.

Evidence is limited to: church_official + exact-alignment General Conference
paragraph pairs, and Church scripture verse pairs. ai_generated rows and
count_mismatch pairs are ignored.

Output: data/attestations/<slug>.json, data/provenance.json,
scratch/uncovered/<lang>/<slug>.jsonl + scratch/background-<lang>.jsonl (for mine_variants).
"""
import json
import random
import subprocess
import sys
from collections import defaultdict
from datetime import date

import yaml

from .config import CONCEPTS, CORPUS, DATA, EXCLUDE, LANGS, PULPIT, ROOT, SCRIPTURES
from .textutil import en_variants, fold, target_pattern, tokens, window

SNIP_POOL = 60        # reservoir size per candidate
UNCOVERED_CAP = 250
BACKGROUND_CAP = 4000
CHURCH_LANG = {"pt": "por", "es": "spa"}


class EnglishIndex:
    def __init__(self, concepts):
        self.bucket = defaultdict(list)  # first-token form -> [(allowed_sets, slug)]
        self.dupes = 0
        seen = {}
        for slug, c in concepts.items():
            for form in c["en"]["match"]:
                toks = [t for t, _ in tokens(fold(form))]
                if not toks:
                    continue
                key = tuple(toks)
                if key in seen and seen[key] != slug:
                    self.dupes += 1
                    continue
                seen[key] = slug
                sets = [en_variants(t) for t in toks]
                for f in sets[0]:
                    self.bucket[f].append((sets, slug))
        for b in self.bucket.values():
            b.sort(key=lambda x: -len(x[0]))

    def scan(self, text: str):
        """Return {slug: (char_start, char_end)} for the first non-overlapping hit of each concept."""
        toks = tokens(fold(text))
        hits = {}
        i = 0
        n = len(toks)
        while i < n:
            matched = 0
            for sets, slug in self.bucket.get(toks[i][0], ()):
                L = len(sets)
                if i + L <= n and all(toks[i + k][0] in sets[k] for k in range(L)):
                    if slug not in hits:
                        s = toks[i][1]
                        e = toks[i + L - 1][1] + len(toks[i + L - 1][0])
                        hits[slug] = (s, e)
                    matched = L
                    break
            i += matched or 1
        return hits


def load_concepts():
    return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(CONCEPTS.glob("*.yaml"))}


class Acc:
    """Per concept+lang accumulator."""

    def __init__(self, cands, rng):
        self.rng = rng
        stop = {"el", "la", "los", "las", "o", "a", "as", "os", "de", "del", "da", "do"}
        uniq = {}
        for c in cands:
            k = " ".join(t for t, _ in tokens(fold(c["term"])))
            if k and k not in stop and k not in uniq:   # accent/case duplicates count once
                uniq[k] = c
        self.cands = [{
            "term": c["term"], "hint": c["hint"], "pat": target_pattern(c["term"]),
            "pars": 0, "talks": set(), "verses": 0, "years": [], "pool": [], "seen": 0,
            "spool": [], "sseen": 0, "first": None,
        } for c in uniq.values()]
        self.en_pars = 0
        self.en_talks = set()
        self.en_verses = 0
        self.uncovered = 0
        self.unc_pool = []

    def reservoir(self, pool, seen, item, cap=SNIP_POOL):
        if len(pool) < cap:
            pool.append(item)
        else:
            j = self.rng.randint(0, seen - 1)
            if j < cap:
                pool[j] = item


def pick_snippets(pool, spool, lang):
    """Up to 3 snippets: one scripture verse, plus talk snippets spread across years."""
    out = []
    code = CHURCH_LANG[lang]
    if spool:
        ordered = sorted(spool, key=lambda x: len(x["tr"]))
        s = ordered[len(ordered) // 4]
        out.append({
            "kind": "scripture", "ref": f'{s["book_name"]} {s["chapter"]}:{s["verse"]}',
            "ref_en": f'{s["book_en"]} {s["chapter"]}:{s["verse"]}',
            "en": s["en"], "tr": s["tr"],
            "url": f'https://www.churchofjesuschrist.org/study/scriptures/{s["volume"]}/'
                   f'{s["book"]}/{s["chapter"]}?lang={code}&id=p{s["verse"]}',
        })
    if pool:
        ordered = sorted(pool, key=lambda x: x["year"])
        seen = set()
        for p in (ordered[0], ordered[len(ordered) // 2], ordered[-1]):
            if p["talk"] in seen:
                continue
            seen.add(p["talk"])
            out.append({"kind": "talk", "year": p["year"], "conference": p["conf"], "talk": p["talk"],
                        "para": p["para"], "en": p["en"], "tr": p["tr"]})
            if len(out) >= 3:
                break
    return out


def run():
    concepts = load_concepts()
    idx = EnglishIndex(concepts)
    print(f"concepts: {len(concepts)}, duplicate match forms skipped: {idx.dupes}")
    (DATA / "attestations").mkdir(parents=True, exist_ok=True)
    scratch = DATA.parent / "scratch" if EXCLUDE else ROOT / "scratch"
    results = {slug: {} for slug in concepts}
    stats = {}

    en_v = {}
    for line in open(SCRIPTURES["en"], encoding="utf-8"):
        v = json.loads(line)
        en_v[v["ref"]] = v

    for lang in LANGS:
        rng = random.Random(1830)
        accs = {slug: Acc(c["candidates"].get(lang, []), rng) for slug, c in concepts.items()}
        used = skipped_ai = skipped_mis = 0
        bg, bg_seen = [], 0

        # ---- General Conference pairs
        for k, line in enumerate(open(CORPUS[lang], encoding="utf-8")):
            r = json.loads(line)
            if EXCLUDE and r["source_id"].startswith(EXCLUDE):
                continue
            if r["translation_source"] != "church_official":
                skipped_ai += 1
                continue
            if r.get("alignment_confidence") != "exact":
                skipped_mis += 1
                continue
            used += 1
            src, tgt = r["source_text"], r["target_text"]
            year = int(r["source_id"][:4])
            tf = fold(tgt)
            bg_seen += 1
            if len(bg) < BACKGROUND_CAP:
                bg.append(tgt)
            else:
                j = rng.randint(0, bg_seen - 1)
                if j < BACKGROUND_CAP:
                    bg[j] = tgt
            for slug, (s, e) in idx.scan(src).items():
                a = accs[slug]
                a.en_pars += 1
                a.en_talks.add(r["target_id"])
                covered = False
                for c in a.cands:
                    m = c["pat"].search(tf)
                    if m:
                        covered = True
                        c["pars"] += 1
                        c["talks"].add(r["target_id"])
                        c["years"].append(year)
                        c["seen"] += 1
                        if c["first"] is None or r["source_id"] < c["first"]["sid"]:
                            c["first"] = {
                                "sid": r["source_id"], "year": year, "conference": r["source_conference"],
                                "talk": r["target_id"], "para": r["paragraph_index"],
                                "en": window(src, s, e), "tr": window(tgt, m.start(), m.end()),
                            }
                        a.reservoir(c["pool"], c["seen"], {
                            "year": year, "talk": r["target_id"], "para": r["paragraph_index"],
                            "conf": r["source_conference"],
                            "en": window(src, s, e), "tr": window(tgt, m.start(), m.end()),
                        })
                if not covered:
                    a.uncovered += 1
                    a.reservoir(a.unc_pool, a.uncovered,
                                {"year": year, "src": "talk", "id": r["target_id"], "tr": tgt}, UNCOVERED_CAP)
            if k % 20000 == 0:
                print(f"  {lang} talks: {k} rows", flush=True)

        # ---- Scriptures
        nverses = 0
        for line in open(SCRIPTURES[lang], encoding="utf-8"):
            tv = json.loads(line)
            ev = en_v.get(tv["ref"])
            if not ev:
                continue
            nverses += 1
            tf = fold(tv["text"])
            for slug, (s, e) in idx.scan(ev["text"]).items():
                a = accs[slug]
                a.en_verses += 1
                covered = False
                for c in a.cands:
                    if c["pat"].search(tf):
                        covered = True
                        c["verses"] += 1
                        c["sseen"] += 1
                        a.reservoir(c["spool"], c["sseen"], {
                            "volume": tv["volume"], "book": tv["book"], "chapter": tv["chapter"],
                            "verse": tv["verse"], "book_name": tv["book_name"], "book_en": ev["book_name"],
                            "en": ev["text"], "tr": tv["text"],
                        })
                if not covered:
                    a.uncovered += 1
                    a.reservoir(a.unc_pool, a.uncovered, {"src": "scripture", "id": tv["ref"], "tr": tv["text"]},
                                UNCOVERED_CAP)
        stats[lang] = {"talk_pairs_used": used, "skipped_ai_generated": skipped_ai,
                       "skipped_count_mismatch": skipped_mis, "scripture_verse_pairs": nverses}
        print(f"{lang}: {stats[lang]}", flush=True)

        # ---- finalize
        (scratch / "uncovered" / lang).mkdir(parents=True, exist_ok=True)
        with open(scratch / f"background-{lang}.jsonl", "w", encoding="utf-8") as fh:
            for t in bg:
                fh.write(json.dumps(t, ensure_ascii=False) + "\n")
        for slug, a in accs.items():
            if not (a.en_pars or a.en_verses):
                results[slug][lang] = {"en_paragraphs": 0, "en_talks": 0, "en_verses": 0,
                                       "uncovered_paragraphs": 0, "renderings": []}
                continue
            out = []
            for c in a.cands:
                approved = c["hint"] == "approved-terms"
                n = c["pars"] + c["verses"]
                if not n and not approved:
                    out.append({"term": c["term"], "evidence": [], "hint": c["hint"]})
                    continue
                years = c["years"]
                out.append({
                    "term": c["term"], "hint": c["hint"],
                    "evidence": (["approved_term"] if approved else []) + (["attested"] if n else []),
                    "paragraphs": c["pars"], "talks": len(c["talks"]), "verses": c["verses"],
                    "first_year": min(years) if years else None, "last_year": max(years) if years else None,
                    "snippets": pick_snippets(c["pool"], c["spool"], lang),
                    "earliest": ({k: v for k, v in c["first"].items() if k != "sid"} if c["first"] else None),
                })
            total = sum(x.get("paragraphs", 0) + x.get("verses", 0) for x in out)
            for x in out:
                if x["evidence"]:
                    x["share"] = round((x["paragraphs"] + x["verses"]) / total, 3) if total else 0
            out.sort(key=lambda x: -(x.get("paragraphs", 0) + x.get("verses", 0)))
            results[slug][lang] = {
                "en_paragraphs": a.en_pars, "en_talks": len(a.en_talks), "en_verses": a.en_verses,
                "uncovered_paragraphs": a.uncovered, "renderings": out,
            }
            if a.unc_pool:
                with open(scratch / "uncovered" / lang / f"{slug}.jsonl", "w", encoding="utf-8") as fh:
                    for it in a.unc_pool:
                        fh.write(json.dumps(it, ensure_ascii=False) + "\n")

    for slug, res in results.items():
        (DATA / "attestations" / f"{slug}.json").write_text(
            json.dumps({"id": concepts[slug]["id"], **res}, ensure_ascii=False, indent=1), encoding="utf-8")
    commit = subprocess.run(["git", "-C", str(PULPIT), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    (DATA / "provenance.json").write_text(json.dumps({
        "generated": date.today().isoformat(), "pulpit_commit": commit,
        "evidence": "church_official + exact alignment (talks); Church scripture verse pairs",
        "stats": stats,
    }, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(run())
