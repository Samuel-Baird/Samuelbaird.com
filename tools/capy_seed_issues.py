#!/usr/bin/env python3
"""Lint and apply `docs/saint-capybara/common-issues/proposals/<topic>.md` files.

See docs/saint-capybara/common-issues/README.md and
docs/saint-capybara/research-protocol.md sec 2 for the full contract. A
proposal file is written by `capy-lead-miner` (via `/capy-seed-issues`) or by
hand, in the shape:

    ---
    topic: <slug>
    generated: YYYY-MM-DD
    status: proposed | partial | applied
    leads: [<lead locators>]
    ---
    ### A1 — <one-sentence claim>
    ```yaml
    audience: general | catholic | protestant | exmo
    lead: "<GSA path p.N | url>"
    lead_note: 3
    upstream: {author: "...", title: "...", year: 1990, page: "..."}
    upstream_locator: "<GSA path+page | url>"
    upstream_in_gsa: true
    inspected_via: "GSA read_pages <vol> p.<n>"
    verification: {tool: cite_page, verdict: page-read, link: "https://corpus.noahairmet.com/b/..."}
    grade: fact | inference | disputed | apologetic-claim-unverified
    accept: false
    applied: null
    ```
    **Rewrite:** <one paragraph, rebuttal-first register>
    **Lead says / upstream says:** <one line each>

`lint` never touches a topic file. `apply` only ever touches the topic file for
items whose `accept: true` was set by the user (in chat or on the GitHub branch)
-- never by the miner. The FAIR/KnoWhy lead URL is recorded in the proposal for
provenance and is NEVER written into the topic file; only the upstream
locator/link is.

Usage:
    python tools/capy_seed_issues.py lint [--proposals DIR]
    python tools/capy_seed_issues.py apply --topic <slug> [--items A2,A4 | --all]
        [--proposals DIR] [--common-issues DIR] [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import capy_check_brand as brand_mod
import capy_merge_briefs as merge_mod

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROPOSALS_DIR = REPO_ROOT / "docs" / "saint-capybara" / "common-issues" / "proposals"
DEFAULT_COMMON_ISSUES_DIR = REPO_ROOT / "docs" / "saint-capybara" / "common-issues"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ITEM_HEADER_RE = re.compile(r"^### (?P<id>A\d+) — (?P<claim>.+)$", re.MULTILINE)
YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
REWRITE_RE = re.compile(r"\*\*Rewrite:\*\*\s*(.+?)(?=\n\*\*Lead says|\Z)", re.DOTALL)
LEAD_SAYS_RE = re.compile(r"\*\*Lead says / upstream says:\*\*\s*(.+?)(?=\n### |\Z)", re.DOTALL)

VALID_GRADES = {"fact", "inference", "disputed", "apologetic-claim-unverified"}
VALID_AUDIENCES = {"general", "catholic", "protestant", "exmo"}

# Combined-heading fallback map: audience -> the heading(s) to try, in order.
AUDIENCE_HEADING_CANDIDATES = {
    "general": ["## General response"],
    "catholic": ["## Catholic response", "## Catholic and Protestant response"],
    "protestant": ["## Protestant response", "## Catholic and Protestant response"],
    "exmo": ["## Exmo/atheist response"],
}


class Item:
    def __init__(self, item_id: str, claim: str, fields: dict, raw_block: str):
        self.item_id = item_id
        self.claim = claim
        self.fields = fields
        self.raw_block = raw_block

    @property
    def rewrite(self) -> str:
        m = REWRITE_RE.search(self.raw_block)
        return m.group(1).strip() if m else ""

    @property
    def lead_says(self) -> str:
        m = LEAD_SAYS_RE.search(self.raw_block)
        return m.group(1).strip() if m else ""


def parse_proposal(path: Path) -> tuple[dict, list[Item]]:
    text = path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.search(text)
    frontmatter = yaml.safe_load(fm_match.group(1)) if fm_match else {}
    body = text[fm_match.end():] if fm_match else text

    items: list[Item] = []
    headers = list(ITEM_HEADER_RE.finditer(body))
    for i, h in enumerate(headers):
        start = h.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        block = body[start:end]
        yaml_match = YAML_BLOCK_RE.search(block)
        fields = yaml.safe_load(yaml_match.group(1)) if yaml_match else {}
        items.append(Item(h.group("id"), h.group("claim").strip(), fields or {}, block))
    return frontmatter or {}, items


def lint_item(item: Item, topic: str) -> list[str]:
    problems = []
    f = item.fields
    prefix = f"{topic} {item.item_id}"

    for req in ("audience", "grade", "accept"):
        if req not in f:
            problems.append(f"{prefix}: missing required field '{req}'")

    audience = f.get("audience")
    if audience and audience not in VALID_AUDIENCES:
        problems.append(f"{prefix}: audience '{audience}' not one of {sorted(VALID_AUDIENCES)}")

    grade = f.get("grade")
    if grade and grade not in VALID_GRADES:
        problems.append(f"{prefix}: grade '{grade}' not one of {sorted(VALID_GRADES)}")

    verification = f.get("verification") or {}
    link = verification.get("link") if isinstance(verification, dict) else None
    inspected_via = f.get("inspected_via") or ""

    # A FAIR/KnoWhy/etc. host can never be the verification for a promoted claim --
    # same rule as capy_merge_briefs.py's apologetic-lead host check.
    if merge_mod._is_apologetic_lead_host(link):
        problems.append(f"{prefix}: verification.link is an apologetic-lead host ({link}) -- "
                         f"trace to the upstream source's own page/link instead")

    if grade == "fact":
        has_valid_link = bool(link) and merge_mod.looks_like_valid_link(link) and not merge_mod._is_apologetic_lead_host(link)
        has_tool_name = bool(merge_mod.VALID_INSPECTED_VIA.search(inspected_via))
        if not (has_valid_link and has_tool_name):
            problems.append(f"{prefix}: grade 'fact' requires both a traceable verification.link "
                             f"and an inspected_via naming a real tool call")

    if grade == "apologetic-claim-unverified" and f.get("accept") and not f.get("override"):
        problems.append(f"{prefix}: grade 'apologetic-claim-unverified' cannot be accept: true "
                         f"without an explicit override: true (the user must consciously override, "
                         f"not the miner)")

    if not item.rewrite:
        problems.append(f"{prefix}: missing **Rewrite:** paragraph")

    return problems


def lint(proposals_dir: Path) -> int:
    if not proposals_dir.exists():
        print(f"no proposals directory at {proposals_dir} -- nothing to lint")
        return 0

    proposal_paths = sorted(proposals_dir.glob("*.md"))
    if not proposal_paths:
        print(f"no proposal files found under {proposals_dir}")
        return 0

    all_problems: list[str] = []
    total_items = 0
    for p in proposal_paths:
        frontmatter, items = parse_proposal(p)
        topic = frontmatter.get("topic", p.stem)
        total_items += len(items)
        for item in items:
            all_problems += lint_item(item, topic)

    # Anonymity / brand scan over the whole proposals directory (reuses the same
    # scan capy_check_brand.py runs over research/**/*.md -- proposals can quote
    # narration-like rewrite text, so they get the same lint).
    phrases, warnings = brand_mod.load_banned_phrases(False)
    tokens = brand_mod.runtime_identity_tokens()
    for w in warnings:
        print(f"warning: {w}")
    for p in proposal_paths:
        all_problems += brand_mod.scan_text(str(p), p.read_text(encoding="utf-8"), phrases, tokens)

    print(f"Parsed {len(proposal_paths)} proposal file(s), {total_items} item(s).")
    if all_problems:
        print(f"\n{len(all_problems)} problem(s):")
        for prob in all_problems:
            print(f"  - {prob}")
    else:
        print("capy_seed_issues lint: clean.")
    return 1 if all_problems else 0


def find_heading_span(text: str, heading: str) -> tuple[int, int] | None:
    """Returns (start, end) character offsets of the section body belonging to
    `heading` (a '## ...' line), i.e. from just after the heading line to just
    before the next '## ' heading or end of file. None if the heading isn't found."""
    pattern = re.compile(r"^" + re.escape(heading) + r"\s*$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return None
    start = m.end()
    next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return start, end


def insert_bullet(topic_text: str, audience: str, bullet: str) -> str:
    for heading in AUDIENCE_HEADING_CANDIDATES.get(audience, []):
        span = find_heading_span(topic_text, heading)
        if span:
            start, end = span
            section = topic_text[start:end]
            # Insert at the end of the section, preserving a trailing blank line.
            section_stripped = section.rstrip("\n")
            new_section = section_stripped + "\n\n" + bullet + "\n\n"
            return topic_text[:start] + new_section + topic_text[end:]
    # No matching heading exists at all -- fall back to a dated Added section.
    today = date.today().isoformat()
    new_heading = f"\n## Added {today} — seeded from FAIR / Scripture Central leads\n\n{bullet}\n"
    return topic_text.rstrip("\n") + "\n" + new_heading


def apply_topic(topic: str, item_ids: list[str] | None, proposals_dir: Path,
                 common_issues_dir: Path, dry_run: bool) -> int:
    proposal_path = proposals_dir / f"{topic}.md"
    if not proposal_path.exists():
        print(f"error: no proposal file at {proposal_path}")
        return 2

    topic_path = common_issues_dir / f"{topic}.md"
    if not topic_path.exists():
        print(f"error: no topic file at {topic_path}")
        return 2

    frontmatter, items = parse_proposal(proposal_path)
    proposal_text = proposal_path.read_text(encoding="utf-8")
    topic_text = topic_path.read_text(encoding="utf-8")

    wanted = set(item_ids) if item_ids else None
    applied_any = []
    skipped = []

    for item in items:
        if wanted is not None and item.item_id not in wanted:
            continue
        if item.fields.get("applied"):
            skipped.append(f"{item.item_id}: already applied on {item.fields['applied']}")
            continue
        if not item.fields.get("accept"):
            skipped.append(f"{item.item_id}: accept is not true, skipped")
            continue

        problems = lint_item(item, topic)
        if problems:
            skipped.append(f"{item.item_id}: failed lint, not applied: {'; '.join(problems)}")
            continue

        audience = item.fields["audience"]
        rewrite = item.rewrite
        upstream = item.fields.get("upstream") or {}
        upstream_link = None
        verification = item.fields.get("verification") or {}
        if isinstance(verification, dict):
            upstream_link = verification.get("link")
        if not upstream_link:
            upstream_link = item.fields.get("upstream_locator")

        if upstream_link and not merge_mod._is_apologetic_lead_host(upstream_link):
            author_title = upstream.get("title") or upstream.get("author") or "source"
            bullet = f"- {rewrite} ([{author_title}]({upstream_link}))"
        else:
            # No safe upstream link to cite inline -- still apply the rewrite text
            # (it must already be upstream-sourced per lint), just without a link.
            bullet = f"- {rewrite}"

        topic_text = insert_bullet(topic_text, audience, bullet)
        item.fields["applied"] = date.today().isoformat()
        applied_any.append(item.item_id)

    if not applied_any:
        print(f"Nothing applied for topic '{topic}'.")
        for s in skipped:
            print(f"  - {s}")
        return 0

    # Rewrite the proposal file's per-item YAML blocks with the new `applied` date,
    # and update the frontmatter status.
    def _rewrite_yaml_block(match: re.Match) -> str:
        return match.group(0)  # placeholder, replaced per-item below

    new_proposal_text = proposal_text
    for item in items:
        if item.item_id not in applied_any:
            continue
        old_yaml = YAML_BLOCK_RE.search(item.raw_block).group(0)
        new_fields_text = yaml.safe_dump(item.fields, sort_keys=False, allow_unicode=True, width=100).strip()
        new_yaml = f"```yaml\n{new_fields_text}\n```"
        new_proposal_text = new_proposal_text.replace(old_yaml, new_yaml, 1)

    all_applied_now = all(it.fields.get("applied") for it in items)
    frontmatter["status"] = "applied" if all_applied_now else "partial"
    new_fm_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True, width=100).strip()
    new_proposal_text = FRONTMATTER_RE.sub(f"---\n{new_fm_text}\n---\n", new_proposal_text, count=1)

    print(f"Applied {len(applied_any)} item(s) to '{topic}': {', '.join(applied_any)}")
    for s in skipped:
        print(f"  - skipped: {s}")

    if dry_run:
        print("\n--dry-run: no files written.")
        return 0

    topic_path.write_text(topic_text, encoding="utf-8")
    proposal_path.write_text(new_proposal_text, encoding="utf-8")
    print(f"\nWrote {topic_path}")
    print(f"Wrote {proposal_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    lint_ap = sub.add_parser("lint")
    lint_ap.add_argument("--proposals", type=Path, default=DEFAULT_PROPOSALS_DIR)

    apply_ap = sub.add_parser("apply")
    apply_ap.add_argument("--topic", required=True)
    group = apply_ap.add_mutually_exclusive_group()
    group.add_argument("--items", help="comma-separated item ids, e.g. A2,A4")
    group.add_argument("--all", action="store_true")
    apply_ap.add_argument("--proposals", type=Path, default=DEFAULT_PROPOSALS_DIR)
    apply_ap.add_argument("--common-issues", type=Path, default=DEFAULT_COMMON_ISSUES_DIR)
    apply_ap.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    if args.command == "lint":
        return lint(args.proposals)
    elif args.command == "apply":
        item_ids = args.items.split(",") if args.items else None
        return apply_topic(args.topic, item_ids, args.proposals, args.common_issues, args.dry_run)
    return 1


if __name__ == "__main__":
    sys.exit(main())
