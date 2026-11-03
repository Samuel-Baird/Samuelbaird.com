"""Fetch the English proclamation texts from churchofjesuschrist.org into texts/<slug>.yaml.

The pages are server-rendered; this parses the headline, subtitle, author line, body
paragraphs, numbered verses and closing note. Only text is taken: no images, logos or
signature facsimiles. Re-run to refresh; the YAML records the URL and retrieval date.

    python -m proclamations.fetch_texts            # all four
    python -m proclamations.fetch_texts family
"""
import datetime
import html
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import yaml

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

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.stack.append((tag, a.get("class", "")))
        in_body = any("body-block" in c for _, c in self.stack)
        wanted = tag == "h1" or (tag == "p" and (in_body or a.get("class") in ("subtitle", "author-name")))
        if wanted and self.cur is None:
            self.cur = [tag, a.get("class", ""), ""]

    def handle_endtag(self, tag):
        if self.cur and self.cur[0] == tag:
            text = re.sub(r"\s+", " ", html.unescape(self.cur[2])).strip()
            if text:
                self.out.append((self.cur[0], self.cur[1], text))
            self.cur = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.cur is not None:
            self.cur[2] += data


def fetch(slug):
    url = BASE + PAGES[slug] + "?lang=eng"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    p = Blocks()
    p.feed(raw)
    return url, p.out


def build(slug):
    url, blocks = fetch(slug)
    doc = {"slug": slug, "language": "en", "source_url": url, "retrieved": datetime.date.today().isoformat()}
    h1 = next(t for tag, c, t in blocks if tag == "h1")
    doc["title"] = h1
    doc["subtitle"] = next((t for tag, c, t in blocks if c == "subtitle"), "")
    doc["author"] = next((t for tag, c, t in blocks if c == "author-name"), "")
    body = [(c, t) for tag, c, t in blocks if tag == "p" and c not in ("subtitle", "author-name")]
    if slug == "articles-of-faith":
        m = re.match(r"(The Articles of Faith)\s+(of .*)", h1)
        doc["title"], doc["subtitle"] = m.group(1), m.group(2)
        doc["verses"] = [{"n": int(t.split(" ", 1)[0]), "text": t.split(" ", 1)[1]} for c, t in body if c == "verse"]
        doc["signature"] = next(t for c, t in body if c == "signature")
        return doc
    paras = []
    for c, t in body:
        if c == "title":   # start of the signature block (The Living Christ)
            break
        paras.append(t)
    if slug == "living-christ":
        doc["paragraphs"] = paras[:-1] if paras[-1].startswith("January") else paras
        doc["date"] = "January 1, 2000"
        doc["signature_groups"] = [t for c, t in body if c == "title"]
    else:
        doc["note"] = paras[-1]
        doc["paragraphs"] = paras[:-1]
    return doc


def main(argv):
    slugs = argv or list(PAGES)
    (HERE / "texts").mkdir(exist_ok=True)
    for slug in slugs:
        doc = build(slug)
        (HERE / "texts" / f"{slug}.yaml").write_text(
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8", newline="\n")
        n = len(doc.get("paragraphs", doc.get("verses", [])))
        print(f"{slug}: {n} blocks")


if __name__ == "__main__":
    main(sys.argv[1:])
