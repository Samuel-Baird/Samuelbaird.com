#!/usr/bin/env python3
"""Lint a Saint Capybara project's beats.yaml against research/sources.yaml.

Rules (see docs/saint-capybara/research-protocol.md and script-format.md):
  - every factual beat cites >=1 source id, unless opinion: true
  - every cited source id resolves in sources.yaml and is inspected: true
  - a card beat's quote is a normalized-substring of its source's recorded quote
  - a source whose type is apologetic-lead must have traced_to set, and any
    beat relying ONLY on apologetic-lead sources (no traced primary/scholarly
    backing among its other cited sources) is a warning (--strict: error)
  - sensitive: true forbids amused/happy poses anywhere in the video
  - the beats.yaml must end with the exact mandatory outro sequence
  - unused sources (declared but never cited by any beat) are reported as info

Usage:
    python tools/capy_check_sources.py --project D:\\Videos\\<slug> [--strict]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml
from capy import beats as beats_mod
from capy.poses import SENSITIVE_FORBIDDEN


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def load_sources(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {s["id"]: s for s in data.get("sources", []) if s.get("id")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--strict", action="store_true", help="upgrade apologetic-only-support warnings to errors")
    ap.add_argument("--draft", action="store_true", help="downgrade duration-budget errors to warnings")
    args = ap.parse_args()

    beats_path = args.project / "script" / "beats.yaml"
    sources_path = args.project / "research" / "sources.yaml"
    escalation_path = args.project / "research" / "ESCALATION.md"

    if not beats_path.exists():
        print(f"error: {beats_path} not found")
        return 2

    doc = beats_mod.load_beats(beats_path)
    sources = load_sources(sources_path)

    issues: list[beats_mod.Issue] = list(beats_mod.validate(doc))

    total, per_beat = beats_mod.resolve_durations(doc)
    issues += beats_mod.check_duration_budget(doc, total, draft=args.draft)

    used_ids: set[str] = set()
    for beat in doc.get("beats", []):
        bid = beat["id"]
        cited = beat.get("sources") or []
        used_ids.update(cited)

        for sid in cited:
            src = sources.get(sid)
            if src is None:
                issues.append(beats_mod.Issue("error", bid, f"cites unknown source id '{sid}' (not in sources.yaml)"))
                continue
            if not src.get("inspected"):
                issues.append(beats_mod.Issue("error", bid, f"source '{sid}' is not marked inspected: true"))
            if src.get("type") == "apologetic-lead" and not src.get("traced_to"):
                issues.append(beats_mod.Issue("error", bid, f"apologetic-lead source '{sid}' has no traced_to (must trace to a primary/scholarly source)"))

        if cited:
            non_apologetic = [sources[s]["type"] for s in cited if s in sources and sources[s].get("type") != "apologetic-lead"]
            all_apologetic = cited and all(sources.get(s, {}).get("type") == "apologetic-lead" for s in cited)
            if all_apologetic:
                level = "error" if args.strict else "warning"
                issues.append(beats_mod.Issue(level, bid, "relies only on apologetic-lead source(s) with no traced primary/scholarly backing among its citations"))

        if beat.get("kind") == "card":
            quote = beat.get("card", {}).get("quote", "")
            src_ids = cited
            if quote and src_ids:
                matched = False
                for sid in src_ids:
                    src = sources.get(sid)
                    if src and src.get("quote") and normalize(quote) in normalize(src["quote"]):
                        matched = True
                        break
                if not matched:
                    issues.append(beats_mod.Issue("error", bid, "card quote is not a substring of any cited source's recorded quote"))

    # unused sources -> info
    for sid in sources:
        if sid not in used_ids:
            issues.append(beats_mod.Issue("info", None, f"source '{sid}' is declared but not cited by any beat (fine if researched-but-unused)"))

    if escalation_path.exists():
        issues.append(beats_mod.Issue("error", None, f"unresolved {escalation_path.name} present -- blocks Gate A until addressed"))

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    infos = [i for i in issues if i.level == "info"]

    for i in issues:
        print(i)

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info. Total runtime estimate: {total:.1f}s")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
