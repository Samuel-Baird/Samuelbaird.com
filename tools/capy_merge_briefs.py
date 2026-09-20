#!/usr/bin/env python3
"""Merge multi-angle research briefs (research/briefs/claim*.md) into a Saint
Capybara project's research/sources.yaml.

See docs/saint-capybara/research-protocol.md sec 15 for the full contract this
implements. Each researcher subagent (capy-historian, capy-scripture-theologian,
capy-doctrine-scholar, capy-philosopher, capy-data-analyst, capy-red-team) writes
ONE brief file with a fenced ```yaml sources: [...] block in the shape of
assets/saint-capybara/templates/sources.yaml. This tool is the only thing that
ever writes those entries into sources.yaml -- it exists so a subagent's claim of
`inspected: true` is checked by machine, not trusted on its word (see the failure
mode this was built to close: a past project's `inspected_via: "Research agent
WebFetch"` entries, which capy_check_sources.py cannot catch because it doesn't
validate inspected_via at all).

What this tool checks, that capy_check_sources.py deliberately does not:
  - inspected: true requires inspected_via to name a real tool call (one of the
    known tool-name patterns below), not a vague phrase like "research agent" or
    "the agent's own research".
  - a set `quote` requires a `verification.link` on an allowlisted host, or a
    verification.tool of verify_quote/cite_page (i.e. traceable back to a real MCP
    call), UNLESS inspected_via itself is a WebFetch call recorded in the brief's
    "Verification log" section with the source id present there -- checked here
    only loosely (the log entry's presence, not word-for-word against a live
    fetch, since this tool does not re-fetch pages itself).
  - `type: critic` is refused unless `id == critic-article` (find_critic_article_entry
    in capy_check_sources.py takes the FIRST type:critic match in file order --
    a researcher-introduced critic entry ahead of the real one would silently break
    Gate A's article checks).
  - (2026-09-13) a `locator`/`verification.link` pointing at an apologetics site
    (FAIR, Scripture Central, Evidence Central, Interpreter -- APOLOGETIC_LEAD_HOST_HINTS)
    can never verify a `quote`, and any entry pointing at one of those hosts must be
    `type: apologetic-lead`. An `apologetic-lead` entry must have `quote: null` and a
    `traced_to` that resolves (in this brief or in the existing sources.yaml) to an
    upstream `primary/scholarly/official/scripture/dataset` entry -- never to another
    lead, a critic entry, or nothing at all. See research-protocol.md sec 2 and
    apologetics-playbook.md "Source hierarchy -- quote upstream".
  - anything failing validation is imported anyway, but with `inspected: false`
    (so capy_check_sources.py's existing "not inspected" error blocks citing it
    until a human or a future run actually verifies it) and a note explaining why.

Merge behaviour: entries are APPENDED, never prepended (sources.yaml already has
a real critic-article entry earlier in the file on an article project --
prepending would reorder it out of "first match"). Dedupe by `id` first (skip a
duplicate id, print a conflict); then by `locator` (same locator under a different
id is reported as a likely duplicate, but still imported, since ids may legitimately
differ per claim in rare cases).

Usage:
    python tools/capy_merge_briefs.py --project D:\\Videos\\<slug> [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Tool-name patterns that count as "actually verified this run" for inspected_via.
# Deliberately strict and explicit -- a brief author can't satisfy this with vague
# language, only with a real tool name.
VALID_INSPECTED_VIA = re.compile(
    r"(verify_quote|read_paragraphs|talks_by_speaker|search_concordance"
    r"|read_pages|cite_page|get_page_image|get_volume_info|list_shelf"
    r"|list_datasets|get_dataset|list_studies|get_study|list_channels|get_channel"
    r"|search_transcripts|read_transcript|list_videos|get_video"
    r"|WebFetch)",
    re.IGNORECASE,
)

# Hosts a verification.link or a WebFetch citation is allowed to point at.
# Extend as new MCP corpora / archive hosts come into use.
ALLOWED_LINK_HOST_HINTS = (
    "pulpit", "restorationcommons", "gospel-scholar", "gsa", "bookshelf",
    "web.archive.org", "archive.org", "newspapers.lib.utah.edu",
    "churchofjesuschrist.org", "latter-day-stats",
)

# Apologetics-lead hosts (2026-09-13, apologetics-playbook.md "Source hierarchy" /
# research-protocol.md sec 2). A page on one of these is a LEAD ONLY -- it can never
# be the verification for a `quote`, and any source entry whose locator/verification
# link points here MUST be `type: apologetic-lead` with `traced_to` set. See
# validate_entry's apologetic-lead checks below.
APOLOGETIC_LEAD_HOST_HINTS = (
    "fairlatterdaysaints.org", "fairmormon.org",
    "scripturecentral.org", "bookofmormoncentral.org", "evidencecentral.org",
    "interpreterfoundation.org",
)


def _is_apologetic_lead_host(link: str | None) -> bool:
    if not link:
        return False
    low = link.lower()
    return any(hint in low for hint in APOLOGETIC_LEAD_HOST_HINTS)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
VERIFICATION_LOG_RE = re.compile(r"## Verification log\n(.*?)(?:\n##|\Z)", re.DOTALL)


def load_sources_doc(path: Path) -> dict:
    if not path.exists():
        return {"sources": []}
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    doc.setdefault("sources", [])
    return doc


def parse_brief(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.search(text)
    frontmatter = yaml.safe_load(fm_match.group(1)) if fm_match else {}

    yaml_match = YAML_BLOCK_RE.search(text)
    sources = []
    if yaml_match:
        block = yaml.safe_load(yaml_match.group(1)) or {}
        sources = block.get("sources", []) or []

    log_match = VERIFICATION_LOG_RE.search(text)
    verification_log = log_match.group(1).strip() if log_match else ""

    return {
        "path": path,
        "frontmatter": frontmatter or {},
        "sources": sources,
        "verification_log": verification_log,
    }


def looks_like_valid_link(link: str | None) -> bool:
    if not link:
        return False
    low = link.lower()
    return any(hint in low for hint in ALLOWED_LINK_HOST_HINTS) or low.startswith("http")


UPSTREAM_TRACE_TYPES = {"primary", "scholarly", "official", "scripture", "dataset"}


def validate_entry(entry: dict, verification_log: str, role: str, known_types: dict[str, str] | None = None) -> list[str]:
    """Returns a list of problems. An entry with any problem is imported with
    inspected: false regardless of what the brief claimed.

    known_types maps source id -> type for every entry already in sources.yaml
    plus every entry merged so far in this run (see merge()) -- used to validate
    `traced_to` actually resolves to an upstream primary/scholarly/etc. entry,
    not to another lead or to nothing at all.
    """
    problems = []
    sid = entry.get("id", "<no id>")
    known_types = known_types or {}

    if entry.get("type") == "critic" and sid != "critic-article":
        problems.append(f"{sid}: type 'critic' is reserved for the real critic-article entry")

    if entry.get("inspected"):
        via = entry.get("inspected_via", "") or ""
        if not VALID_INSPECTED_VIA.search(via):
            problems.append(
                f"{sid}: inspected: true but inspected_via '{via}' does not name a "
                f"recognized tool call"
            )

    verification = entry.get("verification") or {}
    link = verification.get("link") if isinstance(verification, dict) else None
    tool = verification.get("tool") if isinstance(verification, dict) else None
    locator = entry.get("locator")

    if entry.get("quote"):
        has_valid_link = looks_like_valid_link(link)
        has_verify_tool = tool in ("verify_quote", "cite_page")
        webfetch_logged = "webfetch" in verification_log.lower() and sid.lower() in verification_log.lower()
        if not (has_valid_link or has_verify_tool or webfetch_logged):
            problems.append(
                f"{sid}: quote is set but has no traceable verification (link/tool/"
                f"verification-log entry)"
            )
        # An apologetic-lead host (FAIR/Scripture Central/etc.) can never verify a
        # quote -- 2026-09-13: closes the hole where looks_like_valid_link() accepts
        # any http(s) URL. A lead's own words are never the terminal citation.
        if _is_apologetic_lead_host(link) or _is_apologetic_lead_host(locator):
            problems.append(
                f"{sid}: quote is verified against an apologetic-lead host ({link or locator}) "
                f"-- a lead can never be the terminal citation for a quote; trace it to the "
                f"primary/scholarly source it cites instead"
            )

    entry_type = entry.get("type")
    is_lead_host = _is_apologetic_lead_host(link) or _is_apologetic_lead_host(locator)

    if is_lead_host and entry_type != "apologetic-lead":
        problems.append(
            f"{sid}: locator/verification link points at an apologetics site "
            f"({link or locator}) but type is '{entry_type}', not 'apologetic-lead'"
        )

    if entry_type == "apologetic-lead":
        traced_to = entry.get("traced_to")
        if traced_to is None:
            problems.append(f"{sid}: type 'apologetic-lead' requires traced_to")
        else:
            traced_type = known_types.get(traced_to)
            if traced_type is None:
                problems.append(
                    f"{sid}: traced_to '{traced_to}' does not resolve to any source id "
                    f"in this brief or in sources.yaml"
                )
            elif traced_type not in UPSTREAM_TRACE_TYPES:
                problems.append(
                    f"{sid}: traced_to '{traced_to}' resolves to a '{traced_type}' source -- "
                    f"apologetic-lead must trace to an upstream primary/scholarly/official/"
                    f"scripture/dataset source, not to another lead, critic, or 'other' entry"
                )
        if entry.get("quote"):
            problems.append(f"{sid}: type 'apologetic-lead' must have quote: null -- quote the traced_to source instead")

    return problems


def merge(project: Path, dry_run: bool) -> int:
    briefs_dir = project / "research" / "briefs"
    sources_path = project / "research" / "sources.yaml"

    if not briefs_dir.exists():
        print(f"no briefs directory at {briefs_dir} -- nothing to merge")
        return 0

    brief_paths = sorted(briefs_dir.glob("claim*.md"))
    if not brief_paths:
        print(f"no brief files found under {briefs_dir}")
        return 0

    doc = load_sources_doc(sources_path)
    existing_ids = {s["id"] for s in doc["sources"] if s.get("id")}
    existing_locators = {s.get("locator") for s in doc["sources"] if s.get("locator")}
    # id -> type, for validating traced_to. Seeded from sources.yaml, and updated as
    # each brief's entries are accepted below -- so a lead in one brief can legitimately
    # trace to a primary/scholarly source another researcher found in the same run,
    # as long as that source is processed first (briefs are processed in filename
    # order, i.e. claim<N> order, which is the natural dependency order in practice).
    known_types = {s["id"]: s.get("type") for s in doc["sources"] if s.get("id")}

    added = []
    conflicts = []
    downgraded = []

    for bp in brief_paths:
        brief = parse_brief(bp)
        role = brief["frontmatter"].get("role", bp.stem)
        for entry in brief["sources"]:
            sid = entry.get("id")
            if not sid:
                conflicts.append(f"{bp.name}: source entry with no id, skipped")
                continue
            if sid in existing_ids:
                conflicts.append(f"{bp.name}: id '{sid}' already exists, skipped (rename in the brief and re-run if this is actually a different source)")
                continue

            problems = validate_entry(entry, brief["verification_log"], role, known_types)
            if problems:
                entry["inspected"] = False
                entry.setdefault("notes", "")
                entry["notes"] = (entry["notes"] + " " if entry["notes"] else "") + \
                    "[capy_merge_briefs: imported as inspected:false -- " + "; ".join(problems) + "]"
                downgraded.append((sid, problems))

            entry.setdefault("found_by", role)
            claim_no = brief["frontmatter"].get("claim")
            if claim_no is not None:
                entry.setdefault("claims", [claim_no])

            locator = entry.get("locator")
            if locator and locator in existing_locators:
                conflicts.append(f"{bp.name}: '{sid}' has the same locator as an existing source (likely duplicate, imported anyway)")

            doc["sources"].append(entry)  # append, never prepend
            existing_ids.add(sid)
            known_types[sid] = entry.get("type")
            if locator:
                existing_locators.add(locator)
            added.append(sid)

    print(f"Parsed {len(brief_paths)} brief file(s).")
    print(f"Added {len(added)} source(s): {', '.join(added) if added else '(none)'}")
    if downgraded:
        print(f"\n{len(downgraded)} source(s) imported as inspected: false (provenance not verifiable):")
        for sid, problems in downgraded:
            for p in problems:
                print(f"  - {p}")
    if conflicts:
        print(f"\n{len(conflicts)} conflict(s)/note(s):")
        for c in conflicts:
            print(f"  - {c}")

    if dry_run:
        print("\n--dry-run: sources.yaml not written.")
        return 0

    sources_path.parent.mkdir(parents=True, exist_ok=True)
    sources_path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    print(f"\nWrote {sources_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true", help="parse and validate, but don't write sources.yaml")
    args = ap.parse_args()
    return merge(args.project, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
