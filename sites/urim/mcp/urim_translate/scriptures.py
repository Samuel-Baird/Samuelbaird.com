"""The Church's own scripture text (en, es, pt) with the Church's book names.

Data lives in `data/scriptures/{en,es,pt}.tsv.gz` (book slug, chapter, verse, text) plus `books.json` (slug -> book
name per language). It is derived, read-only, from pulpit-vault's ingested Church verse files by
`python -m urim_translate build-scriptures`, and committed so the tool works without that repo.
"""
import gzip
import json
import re
from difflib import SequenceMatcher

from . import config
from .textutil import fold

DIR = config.REPO / "data" / "scriptures"
LANGS = ("en", "es", "pt")
_DASH = re.compile(r"[–—\-]")
_cache = {}


def build(pulpit=None):
    """(Re)build data/scriptures from pulpit-vault's indexes/scriptures/<lang>.jsonl (read-only)."""
    src = (pulpit or config.PULPIT) / "indexes" / "scriptures"
    DIR.mkdir(parents=True, exist_ok=True)
    names = {}
    for lang in LANGS:
        rows, names[lang] = [], {}
        for line in open(src / f"{lang}.jsonl", encoding="utf-8"):
            r = json.loads(line)
            names[lang].setdefault(r["book"], r["book_name"])
            text = " ".join(r["text"].split())
            rows.append(f'{r["book"]}\t{r["chapter"]}\t{r["verse"]}\t{text}')
        with gzip.open(DIR / f"{lang}.tsv.gz", "wt", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(rows) + "\n")
        print(f"{lang}: {len(rows)} verses")
    (DIR / "books.json").write_text(json.dumps(names, ensure_ascii=False, indent=0), encoding="utf-8")


def available() -> bool:
    return all((DIR / f"{l}.tsv.gz").exists() for l in LANGS) and (DIR / "books.json").exists()


def _load(lang):
    if lang not in _cache:
        verses = {}
        with gzip.open(DIR / f"{lang}.tsv.gz", "rt", encoding="utf-8") as f:
            for line in f:
                b, c, v, t = line.rstrip("\n").split("\t", 3)
                verses[(b, int(c), int(v))] = t
        _cache[lang] = verses
    return _cache[lang]


def _names():
    if "names" not in _cache:
        _cache["names"] = json.loads((DIR / "books.json").read_text(encoding="utf-8"))
    return _cache["names"]


def _slugs():
    """English book name (as in data/scripture_books.json, any spacing) -> slug."""
    if "slugs" not in _cache:
        s = {fold(n).replace("\xa0", " "): k for k, n in _names()["en"].items()}
        s["d&c"] = "dc"
        _cache["slugs"] = s
    return _cache["slugs"]


def slug_of(english_name: str):
    return _slugs().get(fold(english_name).replace("\xa0", " "))


def book_name(lang: str, slug: str) -> str:
    return _names()[lang][slug]


def parse_spec(spec: str):
    """':21', ':21-23', ':1, 3' -> [(from, to)]; '' (whole chapter) -> []."""
    out = []
    for part in spec.lstrip(":").split(","):
        part = part.strip()
        if not part:
            continue
        a, *b = [x.strip() for x in _DASH.split(part) if x.strip()]
        try:
            out.append((int(a), int(b[0]) if b else int(a)))
        except ValueError:
            continue
    return out


def verses(lang: str, slug: str, chapter: int, v_from: int, v_to: int):
    """[(verse, text)] for the range, skipping verses the language file does not have."""
    data = _load(lang)
    out = []
    for v in range(v_from, v_to + 1):
        t = data.get((slug, chapter, v))
        if t is not None:
            out.append((v, t))
    return out


def passage(lang, slug, chapter, v_from, v_to) -> str:
    return " ".join(t for _, t in verses(lang, slug, chapter, v_from, v_to))


def _words(s):
    return re.findall(r"\w+", fold(re.sub(r"\[[^\]]*\]", " ", s)))


def match_quote(quote: str, en_passage: str):
    """(contained, ratio, full): how much of the quotation lies inside the English passage (0-1), how similar the two
    are overall, and whether it reproduces the whole passage word for word (no ellipsis or editorial brackets), so the
    Church's text can stand in for it."""
    q, p = _words(quote), _words(en_passage)
    if not q or not p:
        return 0.0, 0.0, False
    sm = SequenceMatcher(None, q, p, autojunk=False)
    contained = sum(b.size for b in sm.get_matching_blocks()) / len(q)
    ratio = sm.ratio()
    full = ratio >= 0.9 and abs(len(q) - len(p)) <= max(1, len(p) // 10) and "…" not in quote and "[" not in quote
    return contained, ratio, full
