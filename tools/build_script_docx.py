#!/usr/bin/env python3
"""Build the pre-production script .docx from a transcript, flags, and images.

Combines a Whisper transcript (word_timestamps json), a flags.json from
find_flags.py, and an optional image/quote-card manifest into
script/<slug>-script.docx per ../docs/script-doc-format.md:

  - Header table: slug, type, sources, model, date.
  - One paragraph per transcript segment, prefixed with [mm:ss].
    CUT flags: strikethrough + red highlight + trailing "<<CUT: reason>>".
    CHECK flags: yellow highlight (no strikethrough) + "<<CHECK: reason>>".
  - Image/quote-card blocks as bordered tables, inserted at the segment
    nearest their intended beat time.
  - Trailing tables: visual wish-list, music pick (solo-history only).

Usage:
    python build_script_docx.py \
        --transcript transcripts/mic.json \
        --flags transcripts/flags.json \
        --out script/my-video-script.docx \
        --slug my-video --type solo-history \
        --sources sources.json \
        --images images.json \
        --wishlist wishlist.json \
        --music music.json

sources.json / images.json / wishlist.json / music.json are small hand- or
script-authored JSON files; see the --help text on each field below and
../docs/script-doc-format.md for the exact shapes.
"""
from __future__ import annotations

import argparse
import io
import json
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.shared import Inches, Pt
from PIL import Image as PILImage, UnidentifiedImageError


def fmt_ts(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    return f"[{m:02d}:{s:02d}]"


def load_json(path: Path | None, default):
    if path is None:
        return default
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def flags_for_segment(seg: dict, flags: list[dict]) -> list[dict]:
    """Flags whose range overlaps this segment's [start, end)."""
    out = []
    for f in flags:
        if f["start"] < seg["end"] and f["end"] > seg["start"]:
            out.append(f)
    return out


def worst_tier(flags: list[dict]) -> str | None:
    if any(f["tier"] == "CUT" for f in flags):
        return "CUT"
    if any(f["tier"] == "CHECK" for f in flags):
        return "CHECK"
    return None


def add_header_table(doc: Document, slug: str, vtype: str, sources: list[dict], model: str):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    def row(label: str, value: str):
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = value

    row("Slug", slug)
    row("Type", vtype)
    src_text = "; ".join(
        f"{s.get('name', '?')} ({s.get('duration', '?')}, {s.get('role', '?')})"
        for s in sources
    ) or "(none listed)"
    row("Sources", src_text)
    row("Whisper model", model)
    row("Generated", date.today().isoformat())
    doc.add_paragraph()


def add_segment_paragraph(doc: Document, seg: dict, seg_flags: list[dict]):
    p = doc.add_paragraph()
    p.add_run(fmt_ts(seg["start"]) + " ").bold = True

    tier = worst_tier(seg_flags)
    run = p.add_run(seg["text"].strip())
    if tier == "CUT":
        run.font.strike = True
        run.font.highlight_color = WD_COLOR_INDEX.RED
    elif tier == "CHECK":
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW

    for f in seg_flags:
        note = p.add_run(f"  <<{f['tier']}: {f['reason']}>>")
        note.italic = True
        note.font.size = Pt(9)


def _docx_safe_image_stream(path: Path) -> io.BytesIO | None:
    """Re-encode via Pillow before handing to python-docx.

    python-docx ships its own minimal image-header parser (not Pillow) to
    read pixel dimensions without a full decode, and it rejects some
    perfectly valid JPEGs that Pillow opens fine (observed on a real
    Metropolitan Museum image with an unusual header shape). Images in this
    pipeline routinely come from arbitrary web sources, so normalize
    through Pillow -> JPEG bytes unconditionally rather than relying on
    python-docx's parser to accept whatever it's given.
    """
    try:
        im = PILImage.open(path)
        im.load()
    except (UnidentifiedImageError, OSError):
        return None
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf


def add_image_block(doc: Document, img: dict):
    """img: {path, caption, source_url, license, on_screen_seconds, is_quote_card?}"""
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.paragraphs[0].text = ""

    img_path = Path(img["path"])
    stream = _docx_safe_image_stream(img_path) if img_path.exists() else None
    if stream is not None:
        cell.paragraphs[0].add_run().add_picture(stream, width=Inches(4))
    elif img_path.exists():
        cell.paragraphs[0].add_run(f"[unreadable image: {img_path}]").italic = True
    else:
        cell.paragraphs[0].add_run(f"[missing image: {img_path}]").italic = True

    kind = "Quote card" if img.get("is_quote_card") else "Image"
    cell.add_paragraph(f"{kind}: {img.get('caption', '(no caption)')}")
    cell.add_paragraph(
        f"Source: {img.get('source_url', '(unsourced -- add to wish-list)')}   "
        f"License: {img.get('license', '?')}"
    )
    cell.add_paragraph(f"On screen: ~{img.get('on_screen_seconds', '?')}s")
    doc.add_paragraph()


def add_wishlist_table(doc: Document, wishlist: list[dict]):
    if not wishlist:
        return
    doc.add_heading("Visual wish-list", level=2)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = "Timestamp", "Needed", "Why"
    for item in wishlist:
        cells = table.add_row().cells
        cells[0].text = fmt_ts(item.get("beat_seconds", 0))
        cells[1].text = item.get("needed", "")
        cells[2].text = item.get("why", "")
    doc.add_paragraph()


def add_music_table(doc: Document, music: dict | None):
    if not music:
        return
    doc.add_heading("Music pick", level=2)
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    for label, key in [("Track", "track"), ("Source", "source"),
                        ("License", "license"), ("Attribution text", "attribution")]:
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = str(music.get(key, ""))
    doc.add_paragraph()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--flags", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--type", dest="vtype", required=True, choices=["response", "solo-history"])
    parser.add_argument("--model", default="small.en")
    parser.add_argument("--sources", type=Path, default=None, help="JSON list of {name,duration,role}")
    parser.add_argument("--images", type=Path, default=None,
                         help="JSON list of {beat_seconds,path,caption,source_url,license,on_screen_seconds,is_quote_card}")
    parser.add_argument("--wishlist", type=Path, default=None, help="JSON list of {beat_seconds,needed,why}")
    parser.add_argument("--music", type=Path, default=None, help="JSON {track,source,license,attribution}")
    args = parser.parse_args()

    transcript = json.loads(args.transcript.read_text(encoding="utf-8"))
    segments = transcript.get("segments", [])
    flags = load_json(args.flags, [])
    sources = load_json(args.sources, [])
    images = sorted(load_json(args.images, []), key=lambda i: i.get("beat_seconds", 0))
    wishlist = load_json(args.wishlist, [])
    music = load_json(args.music, None)

    doc = Document()
    doc.add_heading(f"{args.slug} -- pre-production script", level=1)
    add_header_table(doc, args.slug, args.vtype, sources, args.model)

    img_idx = 0
    for seg in segments:
        seg_flags = flags_for_segment(seg, flags)
        add_segment_paragraph(doc, seg, seg_flags)
        while img_idx < len(images) and images[img_idx].get("beat_seconds", 0) <= seg["end"]:
            add_image_block(doc, images[img_idx])
            img_idx += 1
    while img_idx < len(images):
        add_image_block(doc, images[img_idx])
        img_idx += 1

    add_wishlist_table(doc, wishlist)
    if args.vtype == "solo-history":
        add_music_table(doc, music)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(args.out))
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
