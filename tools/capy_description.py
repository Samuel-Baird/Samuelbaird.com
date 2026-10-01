#!/usr/bin/env python3
"""Generate the Saint Capybara export description package.

Was "not yet built" (`docs/types/saint-capybara.md` step 7); previously
written by hand every time. Assembles `exports/<slug>-description.txt` from
data the pipeline already has -- no new input format:

  - `script/beats.yaml` -- title, hook, summary, tags
  - `research/sources.yaml` -- every source cited by >=1 beat, grouped by
    `type` (the same tier field `capy_check_sources.py` already enforces)
  - `source/source_info.json` (via `capy.source.load_source_info`) -- the
    source-video credit (uploader, canonical url) -- this is the "source
    visible on screen" clip-fairness requirement, which `brand.md` §1 says
    now lives in the description instead of an on-screen chip
  - the brand-required disclaimer sentence, quoted verbatim from
    `brand.md` §1 ("Independent project. Not affiliated with or endorsed
    by The Church of Jesus Christ of Latter-day Saints.")

Run `tools/capy_check_brand.py --project <dir>` afterward (it already
globs `exports/*-description.txt` on its own, no extra flag needed) --
this tool does not scan its own output for banned phrases/identity tokens.

Usage:
    python tools/capy_description.py --project D:\\Videos\\<slug> [--force]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy import beats as beats_mod
from capy import source as source_mod
from capy_check_sources import load_sources

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DISCLAIMER_LINE = (
    "Independent project. Not affiliated with or endorsed by The Church "
    "of Jesus Christ of Latter-day Saints."
)

FAIR_USE_LINE = (
    "Brief excerpts of the source video are used for the purposes of "
    "criticism, comment, and analysis, consistent with fair use principles."
)

# Display order and heading for each sources.yaml `type` -- mirrors the
# tier vocabulary capy_check_sources.py / capy_merge_briefs.py already use
# (UPSTREAM_TRACE_TYPES plus critic/apologetic-lead). "critic" entries that
# just restate the SOURCE VIDEO/SOURCE ARTICLE credit above (same url) are
# dropped from this list in build_description() to avoid double-printing
# the same credit twice; a genuinely separate critic source still appears
# here under "Also referenced."
TYPE_ORDER = [
    ("critic", "Also referenced"),
    ("primary", "Primary"),
    ("official", "Official (General Conference)"),
    ("scripture", "Scripture"),
    ("scholarly", "Scholarly"),
    ("dataset", "Dataset"),
    ("apologetic-lead", "Apologetic sources (traced to primary/scholarly sources above)"),
]


def _format_source_line(src: dict) -> str:
    parts = []
    if src.get("author"):
        parts.append(str(src["author"]))
    if src.get("title"):
        parts.append(f"\"{src['title']}\"" if not str(src["title"]).startswith('"') else str(src["title"]))
    if src.get("date"):
        parts.append(str(src["date"]))
    line = ", ".join(parts) if parts else src.get("id", "?")
    url = src.get("url") or (src.get("locator") if str(src.get("locator", "")).startswith("http") else None)
    if url:
        return f"- {line}.\n  {url}"
    return f"- {line}."


def build_description(project: Path) -> str:
    beats_path = project / "script" / "beats.yaml"
    doc = beats_mod.load_beats(beats_path)
    sources = load_sources(project / "research" / "sources.yaml")
    info = source_mod.load_source_info(project)

    used_ids: set[str] = set()
    for beat in doc.get("beats", []):
        used_ids.update(beat.get("sources") or [])

    credit_urls = {u for u in (info.canonical_url, info.url) if u}

    lines: list[str] = []
    title = doc.get("title") or doc.get("slug", "")
    lines.append(title)
    lines.append("")
    if doc.get("hook"):
        lines.append(doc["hook"])
        lines.append("")
    if doc.get("summary"):
        lines.append(doc["summary"])
        lines.append("")

    if info.kind == "article":
        lines.append("SOURCE ARTICLE")
        credit_bits = [b for b in (info.byline, info.publication) if b]
        if credit_bits:
            lines.append(", ".join(credit_bits))
        if info.url:
            lines.append(info.url)
    else:
        lines.append("SOURCE VIDEO")
        credit_bits = [b for b in (info.title, info.uploader) if b]
        if credit_bits:
            lines.append(" -- ".join(credit_bits))
        if info.canonical_url:
            lines.append(info.canonical_url)
    lines.append("")

    lines.append("SOURCES")
    lines.append("")
    any_grouped = False
    for src_type, heading in TYPE_ORDER:
        entries = [sources[sid] for sid in sorted(used_ids) if sources.get(sid, {}).get("type") == src_type]
        if src_type == "critic":
            entries = [s for s in entries if s.get("url") not in credit_urls and s.get("locator") not in credit_urls]
        if not entries:
            continue
        any_grouped = True
        lines.append(f"{heading}:")
        for src in entries:
            lines.append(_format_source_line(src))
        lines.append("")
    if not any_grouped:
        lines.append("(none cited)")
        lines.append("")

    lines.append("DISCLAIMER")
    lines.append("")
    lines.append(DISCLAIMER_LINE)
    lines.append("")
    lines.append(
        "This video responds to a publicly available video using brief "
        "excerpts, independently researched facts, and citations linked above."
    )
    lines.append("")

    lines.append("FAIR USE")
    lines.append("")
    lines.append(FAIR_USE_LINE)
    lines.append("")

    tags = doc.get("tags") or []
    if tags:
        lines.append("TAGS")
        lines.append(" ".join(f"#{t}" for t in tags))

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--force", action="store_true", help="overwrite an existing description file")
    args = ap.parse_args()

    beats_path = args.project / "script" / "beats.yaml"
    if not beats_path.exists():
        print(f"error: {beats_path} not found", file=sys.stderr)
        return 2

    out_dir = args.project / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = beats_mod.load_beats(beats_path)
    out_path = out_dir / f"{doc.get('slug', args.project.name)}-description.txt"
    if out_path.exists() and not args.force:
        print(f"error: {out_path} already exists (use --force to overwrite)", file=sys.stderr)
        return 2

    text = build_description(args.project)
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path}")
    print("Run tools/capy_check_brand.py --project <dir> next -- it scans exports/*-description.txt automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
