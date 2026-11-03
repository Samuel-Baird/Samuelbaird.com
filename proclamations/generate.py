"""Generate proclamation PDFs in the Church's own formats, for every edition in languages.yaml,
at standard and poster sizes.

    python -m proclamations.generate                          # every edition, all four documents, every size
    python -m proclamations.generate --edition deseret --doc family --size 24x36
    python -m proclamations.generate --edition portugues --jobs 4
    python -m proclamations.generate --edition english --size letter --out scratch/qa

Output: <out>/<edition>/<doc>-<edition>-<size>.pdf, one flat folder per edition (english, espanol, portugues,
deseret, ...). Text is converted once per document and rendered at every size; documents run in parallel.
"""
import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import yaml

from . import fonts
from . import languages
from . import layout
from . import scripts as scripts_mod
from . import sizes as sizes_mod
from .render import Page
from .templates import TEMPLATES, Loc, credit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS = ["family", "living-christ", "restoration", "articles-of-faith"]

# The Living Christ (2000) is signed by the First Presidency and Quorum of the Twelve of that date.
# The original prints facsimile signatures; these editions set the names in type instead.
SIGNERS = [
    ["Gordon B. Hinckley", "Thomas S. Monson", "James E. Faust"],
    ["Boyd K. Packer", "L. Tom Perry", "David B. Haight", "Neal A. Maxwell", "Russell M. Nelson", "Dallin H. Oaks",
     "M. Russell Ballard", "Joseph B. Wirthlin", "Richard G. Scott", "Robert D. Hales", "Jeffrey R. Holland",
     "Henry B. Eyring"],
]


def load_text(slug, lang="en"):
    return yaml.safe_load((HERE / "texts" / lang / f"{slug}.yaml").read_text(encoding="utf-8"))


def available(edition, slug):
    """True if the edition has the source text for this document."""
    return (HERE / "texts" / scripts_mod.get(edition).source / f"{slug}.yaml").exists()


def output_path(out_dir, edition, slug, size):
    return Path(out_dir) / edition / f"{slug}-{edition}-{size}.pdf"


def localize(slug, script):
    """Load the edition's source text, convert it to the edition's script, and return (Loc, source dict)."""
    d = load_text(slug, script.source)
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
    out = [fonts.sanitize(t, script.latin_family) for t in script.convert(strings)]
    L = Loc(slug=slug, script=script, title="", lang=script.source, hints=script.hints)
    L.names = {0: [], 1: []}
    L.paragraphs, L.groups = [None] * len(d.get("paragraphs", [])), [None] * len(d.get("signature_groups", []))
    verses = [None] * len(d.get("verses", []))
    for key, text in zip(keys, out):
        if key[0] == "p":
            L.paragraphs[key[1]] = text
        elif key[0] == "v":
            verses[key[1]] = (d["verses"][key[1]].get("label") or d["verses"][key[1]]["n"], text)
        elif key[0] == "g":
            L.groups[key[1]] = text
        elif key[0] == "n":
            L.names[key[1]].append(text)
        else:
            setattr(L, key[0], text)
    L.verses = verses
    L.credit = script.credit
    return L, d


def render(slug, script, size_name, out_dir, with_credit=True, loc=None):
    """Render one PDF. Pass `loc` (from localize) to avoid converting the text again."""
    fonts.set_family(script.latin_family)
    layout.set_hyphenation(script.hyphenation)
    layout.set_justify(script.justify)
    L, d = loc or localize(slug, script)
    w, h = sizes_mod.get(size_name)
    path = output_path(out_dir, script.name, slug, size_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    title = d["title"] + (": " + d["subtitle"] if slug in ("family", "living-christ") and d.get("subtitle") else "")
    pg = Page(path, w, h, meta={
        "title": f"{title} ({script.label})",
        "author": "Unofficial layout; not an official publication of The Church of Jesus Christ of Latter-day Saints",
        "subject": f"Source text: {d['source_url']}",
    })
    TEMPLATES[slug](pg, L)
    if with_credit:
        credit(pg, L)
    pg.finish()
    return path


def run_task(edition, slug, size_names, out_dir, with_credit):
    """One document of one edition at every requested size. Top-level so it can run in a worker process."""
    script = scripts_mod.get(edition)
    loc = localize(slug, script)
    paths = [render(slug, script, n, out_dir, with_credit, loc) for n in size_names]
    return edition, slug, [str(p) for p in paths], script.report()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", default="all", help="family, living-christ, restoration, articles-of-faith, or all")
    ap.add_argument("--edition", "--script", dest="edition", default="all",
                    help="comma list of edition folders from languages.yaml, or all (default)")
    ap.add_argument("--size", default="all", help="comma list of sizes, or all")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--jobs", type=int, default=1, help="documents to render in parallel")
    ap.add_argument("--no-credit", action="store_true", help="omit the unofficial-edition line in the bottom margin")
    a = ap.parse_args(argv)

    docs = DOCS if a.doc == "all" else a.doc.split(",")
    names = list(sizes_mod.SIZES) if a.size == "all" else a.size.split(",")
    editions = languages.slugs() if a.edition == "all" else a.edition.split(",")
    tasks = []
    for ed in editions:
        for slug in docs:
            if available(ed, slug):
                tasks.append((ed, slug, names, a.out, not a.no_credit))
            else:
                print(f"[{ed}] no source text for {slug}; skipped")
    left = {}
    if a.jobs > 1 and len(tasks) > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            results = list(ex.map(run_task, *zip(*tasks)))
    else:
        results = [run_task(*t) for t in tasks]
    for ed, slug, paths, rep in results:
        for p in paths:
            pp = Path(p)
            print(f"{pp.relative_to(Path(a.out)) if str(pp).startswith(str(a.out)) else pp}  {pp.stat().st_size // 1024} KB")
        left.setdefault(ed, set()).update(rep.get("left_in_latin", []))
    for ed, words in left.items():
        if words:
            print(f"[{ed}] words left in Latin script (no Deseret spelling):", ", ".join(sorted(words)))


if __name__ == "__main__":
    sys.exit(main())
