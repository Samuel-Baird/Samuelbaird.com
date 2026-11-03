"""Generate proclamation PDFs in the Church's own formats, in a chosen script, at poster sizes.

    python -m proclamations.generate                         # all four, Deseret, all nine poster sizes
    python -m proclamations.generate --doc family --size 24x36
    python -m proclamations.generate --script latin --size letter --out scratch/qa   # format check only

Output: <out>/<script>/<doc>/<doc>-<script>-<size>.pdf
"""
import argparse
import sys
from pathlib import Path

import yaml

from . import scripts as scripts_mod
from . import sizes as sizes_mod
from .templates import CREDIT_TEXT, TEMPLATES, Loc, credit
from .render import Page

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS = ["family", "living-christ", "restoration", "articles-of-faith"]

# The Living Christ (2000) is signed by the First Presidency and Quorum of the Twelve of that date.
# The original prints facsimile signatures; this edition sets the names in type instead.
SIGNERS = [
    ["Gordon B. Hinckley", "Thomas S. Monson", "James E. Faust"],
    ["Boyd K. Packer", "L. Tom Perry", "David B. Haight", "Neal A. Maxwell", "Russell M. Nelson", "Dallin H. Oaks",
     "M. Russell Ballard", "Joseph B. Wirthlin", "Richard G. Scott", "Robert D. Hales", "Jeffrey R. Holland",
     "Henry B. Eyring"],
]


def load_text(slug):
    return yaml.safe_load((HERE / "texts" / f"{slug}.yaml").read_text(encoding="utf-8"))


def localize(slug, script):
    """Convert one document's English text into `script` and return a Loc."""
    d = load_text(slug)
    keys, strings = [], []

    def add(key, value):
        keys.append(key)
        strings.append(value)

    for f in ("title", "subtitle", "author", "note", "signature", "date"):
        if d.get(f):
            add((f,), d[f])
    for i, p in enumerate(d.get("paragraphs", [])):
        add(("p", i), p)
    for i, v in enumerate(d.get("verses", [])):
        add(("v", i), v["text"])
    for i, g in enumerate(d.get("signature_groups", [])):
        add(("g", i), g)
    if slug == "living-christ":
        for gi, names in enumerate(SIGNERS):
            for ni, n in enumerate(names):
                add(("n", gi, ni), n)
    out = script.convert(strings)
    L = Loc(slug=slug, script=script, title="")
    L.names = {0: [], 1: []}
    L.paragraphs, L.groups = [None] * len(d.get("paragraphs", [])), [None] * len(d.get("signature_groups", []))
    verses = [None] * len(d.get("verses", []))
    for key, text in zip(keys, out):
        if key[0] == "p":
            L.paragraphs[key[1]] = text
        elif key[0] == "v":
            verses[key[1]] = (d["verses"][key[1]]["n"], text)
        elif key[0] == "g":
            L.groups[key[1]] = text
        elif key[0] == "n":
            L.names[key[1]].append(text)
        else:
            setattr(L, key[0], text)
    L.verses = verses
    L.credit = CREDIT_TEXT.format(label=script.label)
    return L, d


def render(slug, script, size_name, out_dir, with_credit=True):
    L, d = localize(slug, script)
    w, h = sizes_mod.get(size_name)
    path = Path(out_dir) / script.name / slug / f"{slug}-{script.name}-{size_name}.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    pg = Page(path, w, h, meta={
        "title": f"{d['title']}: {d.get('subtitle', '')} ({script.label} edition)".replace(": )", ")").replace(": (", " ("),
        "author": "Unofficial transliteration; not an official publication of The Church of Jesus Christ of Latter-day Saints",
        "subject": f"Source text: {d['source_url']}",
    })
    TEMPLATES[slug](pg, L)
    if with_credit:
        credit(pg, L)
    pg.finish()
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", default="all", help="family, living-christ, restoration, articles-of-faith, or all")
    ap.add_argument("--script", default="deseret", help="deseret (default) or latin (format check)")
    ap.add_argument("--size", default="all", help="comma list of sizes, or all (the nine poster sizes)")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--no-credit", action="store_true", help="omit the unofficial-edition line in the bottom margin")
    a = ap.parse_args(argv)

    docs = DOCS if a.doc == "all" else a.doc.split(",")
    names = list(sizes_mod.SIZES) if a.size == "all" else a.size.split(",")
    script = scripts_mod.get(a.script)
    for slug in docs:
        for n in names:
            p = render(slug, script, n, a.out, with_credit=not a.no_credit)
            print(f"{p.relative_to(Path(a.out)) if str(p).startswith(a.out) else p}  {p.stat().st_size // 1024} KB")
    rep = script.report()
    if rep.get("left_in_latin"):
        print("words left in Latin script (no Deseret spelling):", ", ".join(rep["left_in_latin"]))


if __name__ == "__main__":
    sys.exit(main())
