"""Copy generated PDFs into the Urim site and write previews and a manifest.

    python -m proclamations.publish [--script deseret]

Writes site/posters/<doc>/<doc>-<script>-<size>.pdf, a JPEG preview of each, and
site/posters/manifest.json, which pipeline/build.py turns into the /proclamations page.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import pymupdf

from . import scripts, sizes
from .generate import DOCS, HERE, load_text

ROOT = HERE.parent
SITE = ROOT / "site" / "posters"
PREVIEW_SIZE = "18x24"
PREVIEW_WIDTH = 760


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="deseret")
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args(argv)
    script = scripts.get(a.script)
    SITE.mkdir(parents=True, exist_ok=True)
    manifest = []
    for slug in DOCS:
        d = load_text(slug)
        src = Path(a.out) / script.name / slug
        dest = SITE / slug
        dest.mkdir(parents=True, exist_ok=True)
        files = {}
        for size in sizes.SIZES:
            f = src / f"{slug}-{script.name}-{size}.pdf"
            if not f.exists():
                raise SystemExit(f"missing {f}; run `python -m proclamations.generate` first")
            shutil.copyfile(f, dest / f.name)
            w, h = sizes.SIZES[size]
            files[size] = {"file": f.name, "kb": round(f.stat().st_size / 1024), "label": sizes.LABELS[size],
                           "w_in": round(w / 72, 1), "h_in": round(h / 72, 1)}
        page = pymupdf.open(src / f"{slug}-{script.name}-{PREVIEW_SIZE}.pdf")[0]
        z = PREVIEW_WIDTH / page.rect.width
        preview = f"{slug}-{script.name}-preview.jpg"
        page.get_pixmap(matrix=pymupdf.Matrix(z, z)).save(dest / preview, jpg_quality=82)
        title = d["title"] + (": " + d["subtitle"] if slug in ("family", "living-christ") and d.get("subtitle") else "")
        dsrt = script.convert([d["title"]])[0] if script.name == "deseret" else ""
        manifest.append({"slug": slug, "title": d["title"], "subtitle": d.get("subtitle", ""), "title_native": dsrt,
                         "source_url": d["source_url"], "files": files, "preview": preview, "script": script.name,
                         "label": script.label})
    (SITE / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    n = sum(len(m["files"]) for m in manifest)
    print(f"published {n} PDFs and {len(manifest)} previews to {SITE.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
