"""Extract text and figures from Canvas handouts (docx/pdf) for local reading.

Usage: python -I scripts/extract_handouts.py <files_dir>
Writes <files_dir>/_extract/<stem>/{text.md, img/*} . Everything stays under the
gitignored canvas/files/ folder.
"""
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def docx(path: Path, out: Path):
    z = zipfile.ZipFile(path)
    rels = {}
    if "word/_rels/document.xml.rels" in z.namelist():
        for r in ET.fromstring(z.read("word/_rels/document.xml.rels")):
            rels[r.get("Id")] = r.get("Target")
    (out / "img").mkdir(parents=True, exist_ok=True)
    for n in z.namelist():
        if n.startswith("word/media/"):
            (out / "img" / Path(n).name).write_bytes(z.read(n))
    root = ET.fromstring(z.read("word/document.xml"))
    lines = []
    body = root.find(W + "body")
    for el in body:
        if el.tag == W + "p":
            lines.append(para(el, rels))
        elif el.tag == W + "tbl":
            for tr in el.iter(W + "tr"):
                cells = [" ".join(para(p, rels) for p in tc.iter(W + "p")).strip() for tc in tr.iter(W + "tc")]
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")
    (out / "text.md").write_text("\n".join(lines), encoding="utf-8")


def para(p, rels):
    parts = []
    for node in p.iter():
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag == A + "blip":
            rid = node.get(R + "embed")
            if rid in rels:
                parts.append(f" [IMG {Path(rels[rid]).name}] ")
        elif node.tag.endswith("}oMath"):
            pass
    return "".join(parts)


def pdf(path: Path, out: Path, dpi=110):
    doc = pymupdf.open(path)
    (out / "img").mkdir(parents=True, exist_ok=True)
    lines = []
    limit = min(len(doc), 40)
    for i in range(limit):
        pg = doc[i]
        lines.append(f"\n--- page {i + 1} ---\n" + pg.get_text())
        pg.get_pixmap(dpi=dpi).save(out / "img" / f"page{i + 1:02d}.png")
    (out / "text.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    d = Path(sys.argv[1])
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in (".docx", ".pdf"):
            continue
        stem = re.sub(r"[^A-Za-z0-9]+", "_", f.stem.split("__")[-1]).strip("_")
        out = d / "_extract" / stem
        out.mkdir(parents=True, exist_ok=True)
        (docx if f.suffix.lower() == ".docx" else pdf)(f, out)
        n = len(list((out / "img").glob("*")))
        print(f"{stem}: {len((out / 'text.md').read_text(encoding='utf-8'))} chars, {n} images")


if __name__ == "__main__":
    main()
