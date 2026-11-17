"""Per-language glossary: relevant-entry matching, user overrides, validation.

Only entries whose English side occurs in the text are ever surfaced, so the full
glossary never has to be put in a model prompt.
"""
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field

from . import config
from .textutil import en_variants, fold, target_pattern, tokens

ENFORCED = {"approved", "attested", "user"}   # "hint" entries are suggested, never enforced


@dataclass
class Entry:
    id: str
    en: list
    preferred: str
    confidence: str
    variants: list = field(default_factory=list)   # [{"term", "share"}]
    slug: str = ""
    note: str = ""

    def allowed(self):
        return [self.preferred] + [v["term"] for v in self.variants]

    def brief(self):
        d = {"en": self.en[0], "use": self.preferred, "confidence": self.confidence}
        if self.variants:
            d["also"] = [v["term"] for v in self.variants]
        if self.slug:
            d["url"] = f"https://urim.samuelbaird.com/c/{self.slug}"
        return d


@dataclass
class Match:
    entry: Entry
    start: int
    end: int
    text: str


class Glossary:
    def __init__(self, lang: str, store=None):
        self.lang = lang
        self.entries = []
        p = config.GLOSSARY_DIR / f"{lang}.json"
        if p.exists():
            for e in json.loads(p.read_text(encoding="utf-8"))["entries"]:
                self.entries.append(Entry(e["id"], e["en"], e["preferred"], e["confidence"],
                                          e.get("variants", []), e.get("slug", "")))
        if store is not None:
            for o in store.overrides(lang):
                self.entries.append(Entry(f"user.{fold(o['en'])}", [o["en"]], o["target"], "user", [], "", o["note"]))
        self._index()
        self.version = hashlib.sha1(json.dumps(
            [(e.id, e.preferred, e.confidence) for e in self.entries], ensure_ascii=False).encode()).hexdigest()[:8]

    def _index(self):
        self.bucket = defaultdict(list)
        # later entries (user overrides) win when the same English form appears twice
        seen = {}
        for e in self.entries:
            for form in e.en:
                toks = tuple(t for t, _ in tokens(fold(form)))
                if toks:
                    seen[toks] = e
        for toks, e in seen.items():
            sets = [en_variants(t) for t in toks]
            for f in sets[0]:
                self.bucket[f].append((sets, e))
        for b in self.bucket.values():
            b.sort(key=lambda x: -len(x[0]))
        self._pats = {}

    def match(self, text: str):
        """Non-overlapping, longest-first matches of glossary English terms in `text`."""
        toks = tokens(fold(text))
        out, i, n = [], 0, len(toks)
        while i < n:
            hit = 0
            for sets, e in self.bucket.get(toks[i][0], ()):
                L = len(sets)
                if i + L <= n and all(toks[i + k][0] in sets[k] for k in range(L)):
                    s = toks[i][1]
                    en_ = toks[i + L - 1][1] + len(toks[i + L - 1][0])
                    out.append(Match(e, s, en_, text[s:en_]))
                    hit = L
                    break
            i += hit or 1
        return out

    def _pat(self, term):
        if term not in self._pats:
            self._pats[term] = target_pattern(term)
        return self._pats[term]

    def missing(self, matches, target: str):
        """Enforced matches whose required rendering (or an allowed variant) is absent from `target`."""
        tf = fold(target)
        bad, seen = [], set()
        for m in matches:
            e = m.entry
            if e.confidence not in ENFORCED or e.id in seen:
                continue
            seen.add(e.id)
            if not any(self._pat(t).search(tf) for t in e.allowed()):
                bad.append(e)
        return bad

    def lookup(self, query: str, limit=8):
        """Forward (English) and reverse (rendering) lookup."""
        q = fold(query).strip()
        res = []
        for e in self.entries:
            en = [fold(x) for x in e.en]
            rend = [fold(t) for t in e.allowed()]
            if q in en or q in rend:
                res.append((0, e))
            elif any(q in x for x in en + rend):
                res.append((1, e))
        res.sort(key=lambda x: x[0])
        return [e for _, e in res[:limit]]
