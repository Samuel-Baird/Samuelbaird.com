"""Copy generated PDFs into the Urim site and write previews and a manifest.

    python -m proclamations.publish

Writes site/posters/<edition>/<doc>-<edition>-<size>.pdf (one flat folder per language or alphabet), a small
JPEG preview of each document, and site/posters/manifest.json, which pipeline/build.py turns into the
/proclamations index and one page per language.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import pymupdf

from . import languages, scripts, sizes
from .generate import DOCS, HERE, available, load_text, output_path

ROOT = HERE.parent
SITE = ROOT / "site" / "posters"
PREVIEW_SIZE = "18x24"
PREVIEW_WIDTH = 420


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args(argv)
    if SITE.exists():
        shutil.rmtree(SITE)          # old layouts must not linger
    entries = []
    for slug in languages.slugs():
        reg = languages.get(slug)
        script = scripts.get(slug)
        docs = {}
        dest = SITE / slug
        for doc in DOCS:
            if not available(slug, doc):
                continue
            src = load_text(doc, script.source)
            files = {}
            for size, (w, h) in sizes.SIZES.items():
                f = output_path(a.out, slug, doc, size)
                if not f.exists():
                    raise SystemExit(f"missing {f}; run `python -m proclamations.generate` first")
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, dest / f.name)
                files[size] = {"file": f.name, "kb": round(f.stat().st_size / 1024), "label": sizes.LABELS[size],
                               "w_in": round(w / 72, 1), "h_in": round(h / 72, 1)}
            page = pymupdf.open(output_path(a.out, slug, doc, PREVIEW_SIZE))[0]
            z = PREVIEW_WIDTH / page.rect.width
            preview = f"{doc}-{slug}-preview.jpg"
            page.get_pixmap(matrix=pymupdf.Matrix(z, z)).save(dest / preview, jpg_quality=78)
            title = src["title"] if reg["kind"] == "language" else script.convert([src["title"]])[0]
            docs[doc] = {"title": title, "subtitle": src.get("subtitle", "") if reg["kind"] == "language" else "",
                         "source_url": src["source_url"], "files": files, "preview": preview}
        if docs:
            entries.append({"slug": slug, "kind": reg["kind"], "code": reg["code"], "native": reg["native"],
                            "english": reg["english"], "docs": docs})
    (SITE / "manifest.json").write_text(json.dumps(entries, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    n = sum(len(d["files"]) for e in entries for d in e["docs"].values())
    print(f"published {n} PDFs for {len(entries)} editions to {SITE.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
