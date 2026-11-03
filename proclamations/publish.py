"""Copy generated PDFs into the Urim site and write previews and a manifest.

    python -m proclamations.publish

Writes site/posters/<edition>/<doc>-<edition>-<size>.pdf (one flat folder per edition: english, spanish,
deseret), a JPEG preview of each document per edition, and site/posters/manifest.json, which
pipeline/build.py turns into the /proclamations page.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import pymupdf

from . import scripts, sizes
from .generate import DOCS, HERE, load_text, output_path

ROOT = HERE.parent
SITE = ROOT / "site" / "posters"
PREVIEW_SIZE = "18x24"
PREVIEW_WIDTH = 520


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args(argv)
    if SITE.exists():
        shutil.rmtree(SITE)          # old layouts must not linger
    manifest = []
    for slug in DOCS:
        en, es = load_text(slug, "en"), load_text(slug, "es")
        entry = {"slug": slug, "title": en["title"], "subtitle": en.get("subtitle", ""),
                 "titles": {"english": en["title"], "spanish": es["title"]},
                 "source_url": {"english": en["source_url"], "spanish": es["source_url"]}, "editions": {}}
        for name in scripts.EDITIONS:
            script = scripts.get(name)
            dest = SITE / name
            dest.mkdir(parents=True, exist_ok=True)
            files = {}
            for size, (w, h) in sizes.SIZES.items():
                f = output_path(a.out, name, slug, size)
                if not f.exists():
                    raise SystemExit(f"missing {f}; run `python -m proclamations.generate` first")
                shutil.copyfile(f, dest / f.name)
                files[size] = {"file": f.name, "kb": round(f.stat().st_size / 1024), "label": sizes.LABELS[size],
                               "w_in": round(w / 72, 1), "h_in": round(h / 72, 1)}
            page = pymupdf.open(output_path(a.out, name, slug, PREVIEW_SIZE))[0]
            z = PREVIEW_WIDTH / page.rect.width
            preview = f"{slug}-{name}-preview.jpg"
            page.get_pixmap(matrix=pymupdf.Matrix(z, z)).save(dest / preview, jpg_quality=82)
            entry["editions"][name] = {"label": script.label, "files": files, "preview": preview}
            if name == "deseret":
                entry["title_deseret"] = script.convert([en["title"]])[0]
        manifest.append(entry)
    (SITE / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    n = sum(len(e["files"]) for m in manifest for e in m["editions"].values())
    print(f"published {n} PDFs and {len(manifest) * len(scripts.EDITIONS)} previews to {SITE.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
