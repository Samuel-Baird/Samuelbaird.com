"""Fetch the proclamation texts from churchofjesuschrist.org into texts/<code>/<doc>.yaml.

    python -m proclamations.fetch_texts                    # every language in languages.yaml
    python -m proclamations.fetch_texts --all              # every language the survey found (text-only ones too)
    python -m proclamations.fetch_texts --lang rus,jpn family

<code> is the Church's own ?lang= code. Each language is the Church's published version of the document
(nothing is translated here). A page the Church has not published in a language is skipped.

The headline, subtitle and author come from the page structure. The Articles of Faith page has one heading
("Articles of Faith of The Church of Jesus Christ ..."); it is split into title and subtitle at the Church's
name, which is read from that language's Living Christ page (or set `aof_split` in languages.yaml).
"""
import datetime
import html
import re
import sys
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

import yaml

from . import languages

HERE = Path(__file__).resolve().parent
BASE = "https://www.churchofjesuschrist.org/study/scriptures/"
PAGES = {
    "family": "the-family-a-proclamation-to-the-world/the-family-a-proclamation-to-the-world",
    "living-christ": "the-living-christ-the-testimony-of-the-apostles/the-living-christ-the-testimony-of-the-apostles",
    "restoration": "the-restoration-of-the-fulness-of-the-gospel-of-jesus-christ/the-restoration-of-the-fulness-of-the-gospel-of-jesus-christ",
    "articles-of-faith": "af-poster",
}


class Blocks(HTMLParser):
    """Collects (tag, class, text) for headings and paragraphs inside the article body."""

    def __init__(self):
        super().__init__()
        self.stack, self.out, self.cur = [], [], None
        self.ruby = 0           # inside <rt>/<rp> (Japanese furigana): readings are not part of the text

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("rt", "rp"):
            self.ruby += 1
        self.stack.append((tag, a.get("class", "")))
        in_body = any("body-block" in c for _, c in self.stack)
        wanted = tag == "h1" or (tag == "p" and (in_body or a.get("class") in ("subtitle", "author-name")))
        if wanted and self.cur is None:
            self.cur = [tag, a.get("class", ""), ""]

    def handle_endtag(self, tag):
        if tag in ("rt", "rp") and self.ruby:
            self.ruby -= 1
        if self.cur and self.cur[0] == tag:
            text = re.sub(r"\s+", " ", html.unescape(self.cur[2])).strip()
            if text:
                self.out.append((self.cur[0], self.cur[1], text))
            self.cur = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.cur is not None and not self.ruby:
            self.cur[2] += data


def fetch(slug, code):
    url = BASE + PAGES[slug] + f"?lang={code}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    p = Blocks()
    p.feed(raw)
    return url, p.out


def _score(tokens, name_tokens):
    names = {w.lower().strip(".,") for w in name_tokens}
    return sum(w.lower().strip(".,") in names for w in tokens) / max(len(name_tokens), len(tokens))


def _fuzzy_match(h1, name):
    """Find the Church's name in the heading even if its words are inflected (Russian, Polish, Finnish...).
    Returns ("suffix", k) or ("prefix", k): the name is the last/first k words of the heading."""
    hw, nw = h1.split(" "), name.split(" ")
    if len(nw) < 3 or len(hw) <= len(nw) - 1:
        return None
    best = None
    for side in ("suffix", "prefix"):
        for k in (len(nw), len(nw) + 1, len(nw) - 1):          # prefer the exact length on ties
            if k >= len(hw) or k < 2:
                continue
            tokens = hw[-k:] if side == "suffix" else hw[:k]
            sc = _score(tokens, nw)
            if sc >= 0.5 and (best is None or sc > best[0]):
                best = (sc, side, k)
    return best[1:] if best else None


def split_aof_heading(h1, church_name, marker=None):
    """Split "Articles of Faith of The Church of ..." into (title, subtitle)."""
    h1 = unicodedata.normalize("NFC", h1)
    if marker:
        i = h1.find(marker)
        if i > 0:
            return h1[:i].strip(), h1[i:].strip()
    name = unicodedata.normalize("NFC", church_name or "")
    i = h1.lower().find(name.lower()) if name else -1
    if i < 0 and name:
        m = _fuzzy_match(h1, name)
        if m:
            side, k = m
            hw = h1.split(" ")
            if side == "prefix":                                 # the Church's name comes first in this language
                return " ".join(hw[k:]), " ".join(hw[:k])
            i = len(" ".join(hw[:-k])) + 1
    if i < 0:
        return h1, ""                                            # heading kept whole; the layout copes with no subtitle
    if i == 0:
        return h1[len(name):].strip(), h1[:len(name)].strip()
    prefix = h1[:i].rstrip()
    words = prefix.split(" ")
    if len(words) > 1 and len(words[-1]) <= 3 and words[-1].islower():   # a connector ("of", "de", "na") goes with the name
        return " ".join(words[:-1]), words[-1] + " " + h1[i:]
    return prefix, h1[i:]


def build(slug, code, church_name=None):
    url, blocks = fetch(slug, code)
    doc = {"slug": slug, "language": code, "source_url": url, "retrieved": datetime.date.today().isoformat()}
    h1 = next((t for tag, c, t in blocks if tag == "h1"), None)
    if h1 is None:
        raise ValueError("page has no heading")
    doc["title"] = h1
    doc["subtitle"] = next((t for tag, c, t in blocks if c == "subtitle"), "")
    doc["author"] = next((t for tag, c, t in blocks if c == "author-name"), "")
    body = [(c, t) for tag, c, t in blocks if tag == "p" and c not in ("subtitle", "author-name")]
    if slug == "articles-of-faith":
        reg = languages.load()
        marker = next((e.get("aof_split") for e in reg.values() if e.get("code") == code), None)
        doc["title"], doc["subtitle"] = split_aof_heading(h1, church_name, marker)
        doc["verses"] = []
        for c, t in body:
            if c == "verse":
                num, _, rest = t.partition(" ")
                numeral = bool(rest) and len(num) <= 4 and all(ch.isdigit() or unicodedata.category(ch) == "No"
                                                                or unicodedata.numeric(ch, None) is not None for ch in num)
                v = {"n": len(doc["verses"]) + 1, "text": rest if numeral else t}
                if numeral and not num.isascii():
                    v["label"] = num                          # the language's own numerals, printed as the verse number
                doc["verses"].append(v)
        sig = next((t for c, t in body if c == "signature"), "")
        doc["signature"] = sig
        return doc
    paras = []
    for c, t in body:
        if c == "title":   # start of the signature block (The Living Christ)
            break
        paras.append(t)
    if slug == "living-christ":
        titles = [i for i, (c, t) in enumerate(body) if c == "title"]
        doc["paragraphs"] = paras
        doc["date"] = next((t for c, t in body[titles[0] + 1:] if c != "title"), "") if titles else ""
        doc["signature_groups"] = [t for c, t in body if c == "title"]
    else:
        doc["note"] = paras[-1]
        doc["paragraphs"] = paras[:-1]
    return doc


def fetch_language(code, only=None):
    """Fetch every document for one language. Returns {slug: doc or error string}."""
    out, church_name = {}, None
    order = [s for s in ("living-christ", "family", "restoration", "articles-of-faith") if not only or s in only]
    if "articles-of-faith" in order and "living-christ" not in order:
        order.insert(0, "living-christ")               # needed for the Church's name in that language
        fetch_only_for_name = True
    else:
        fetch_only_for_name = False
    for slug in order:
        try:
            doc = build(slug, code, church_name)
            out[slug] = doc
            if slug == "living-christ":
                church_name = doc.get("author")
        except urllib.error.HTTPError as e:
            out[slug] = f"HTTP {e.code}"
        except Exception as e:                       # a page may be structured differently in some language
            out[slug] = f"{type(e).__name__}: {str(e)[:70]}"
    if fetch_only_for_name:
        out.pop("living-christ", None)                  # looked up for its Church name only; not requested
    return out


def write(code, slug, doc):
    d = HERE / "texts" / code
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.yaml").write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
                                    encoding="utf-8", newline="\n")


def main(argv):
    only = [a for a in argv if a in PAGES]
    argv = [a for a in argv if a not in PAGES]
    if "--all" in argv:
        import json
        codes = [e["code"] for e in json.loads((HERE / "language-survey.json").read_text(encoding="utf-8")) if e["documents"]]
    elif "--lang" in argv:
        codes = argv[argv.index("--lang") + 1].split(",")
    else:
        codes = [e["code"] for e in languages.load().values() if e["kind"] == "language"]
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda c: fetch_language(c, only), codes))
    problems = 0
    for code, res in zip(codes, results):
        got = [s for s, d in res.items() if isinstance(d, dict)]
        for slug in got:
            write(code, slug, res[slug])
        bad = {s: d for s, d in res.items() if isinstance(d, str) and not d.startswith("HTTP 404")}
        problems += len(bad)
        print(f"{code}: {len(got)}/4" + (f"  PROBLEMS {bad}" if bad else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
