"""Unit tests for capy_seed_issues.py (2026-09-13).

    python -m pytest tools/tests/test_seed_issues.py
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import capy_seed_issues as s  # noqa: E402


def _write_proposal(dir_: Path, topic: str, item_yaml: str, rewrite: str = "Rewrite text here.",
                     lead_says: str = "Lead says X. Upstream says Y.") -> Path:
    text = f"""---
topic: {topic}
generated: "2026-09-13"
status: proposed
leads: ["https://scripturecentral.org/knowhy/example"]
---
### A1 — a one-sentence claim
```yaml
{item_yaml}
```
**Rewrite:** {rewrite}

**Lead says / upstream says:** {lead_says}
"""
    p = dir_ / f"{topic}.md"
    p.write_text(text, encoding="utf-8")
    return p


def _write_topic(dir_: Path, topic: str, body: str) -> Path:
    p = dir_ / f"{topic}.md"
    p.write_text(body, encoding="utf-8")
    return p


FACT_ITEM = """audience: general
lead: "https://scripturecentral.org/knowhy/example"
lead_note: null
upstream: {author: "Some Scholar", title: "Some Book", year: 2015, page: "8"}
upstream_locator: "Read/Some/Path.pdf p.8"
upstream_in_gsa: true
inspected_via: "GSA read_pages some-path p.8"
verification: {tool: read_pages, verdict: page-read, link: "https://corpus.noahairmet.com/b/some-path/8"}
grade: fact
accept: false
applied: null"""


# --- parsing ---

def test_parse_proposal_reads_frontmatter_and_item(tmp_path):
    p = _write_proposal(tmp_path, "topic-a", FACT_ITEM)
    frontmatter, items = s.parse_proposal(p)
    assert frontmatter["topic"] == "topic-a"
    assert len(items) == 1
    assert items[0].item_id == "A1"
    assert items[0].fields["grade"] == "fact"
    assert "Rewrite text here." in items[0].rewrite


# --- lint rules ---

def test_lint_fact_requires_valid_link_and_inspected_via(tmp_path):
    bad_item = FACT_ITEM.replace('inspected_via: "GSA read_pages some-path p.8"', 'inspected_via: "the agent looked it up"')
    p = _write_proposal(tmp_path, "topic-b", bad_item)
    rc = s.lint(tmp_path)
    assert rc == 1


def test_lint_rejects_fair_host_as_verification_link(tmp_path):
    bad_item = FACT_ITEM.replace(
        'verification: {tool: read_pages, verdict: page-read, link: "https://corpus.noahairmet.com/b/some-path/8"}',
        'verification: {tool: WebFetch, verdict: direct-read, link: "https://www.fairlatterdaysaints.org/answers/Foo"}',
    )
    p = _write_proposal(tmp_path, "topic-c", bad_item)
    frontmatter, items = s.parse_proposal(p)
    problems = s.lint_item(items[0], "topic-c")
    assert any("apologetic-lead host" in prob for prob in problems)


def test_lint_apologetic_claim_unverified_cannot_be_accepted_without_override(tmp_path):
    item = FACT_ITEM.replace("grade: fact", "grade: apologetic-claim-unverified").replace("accept: false", "accept: true")
    p = _write_proposal(tmp_path, "topic-d", item)
    frontmatter, items = s.parse_proposal(p)
    problems = s.lint_item(items[0], "topic-d")
    assert any("override" in prob for prob in problems)


def test_lint_apologetic_claim_unverified_accepted_with_override_is_clean(tmp_path):
    item = FACT_ITEM.replace("grade: fact", "grade: apologetic-claim-unverified").replace(
        "accept: false", "accept: true\noverride: true"
    )
    p = _write_proposal(tmp_path, "topic-e", item)
    frontmatter, items = s.parse_proposal(p)
    problems = s.lint_item(items[0], "topic-e")
    assert problems == []


# --- heading resolution ---

def test_find_heading_span_finds_section_body():
    text = "# T\n\n## General response\n\nSome text.\n\n## Catholic and Protestant response\n\nOther text.\n"
    span = s.find_heading_span(text, "## General response")
    assert span is not None
    start, end = span
    assert "Some text." in text[start:end]
    assert "Other text." not in text[start:end]


def test_insert_bullet_combined_heading_when_split_absent():
    text = "# T\n\n## General response\n\nGeneral text.\n\n## Catholic and Protestant response\n\nShared text.\n\n## Exmo/atheist response\n\nExmo text.\n"
    out = s.insert_bullet(text, "catholic", "- new catholic bullet")
    assert "- new catholic bullet" in out
    span = s.find_heading_span(out, "## Catholic and Protestant response")
    start, end = span
    assert "- new catholic bullet" in out[start:end]


def test_insert_bullet_prefers_split_heading_when_present():
    text = "# T\n\n## General response\n\nG.\n\n## Catholic response\n\nC.\n\n## Protestant response\n\nP.\n\n## Exmo/atheist response\n\nE.\n"
    out = s.insert_bullet(text, "protestant", "- protestant-only bullet")
    span = s.find_heading_span(out, "## Protestant response")
    start, end = span
    assert "- protestant-only bullet" in out[start:end]
    cath_span = s.find_heading_span(out, "## Catholic response")
    cstart, cend = cath_span
    assert "- protestant-only bullet" not in out[cstart:cend]


def test_insert_bullet_falls_back_to_added_section_when_no_heading_matches():
    text = "# T\n\n## Some Other Heading\n\nirrelevant\n"
    out = s.insert_bullet(text, "general", "- fallback bullet")
    assert "## Added" in out
    assert "- fallback bullet" in out
    assert "seeded from FAIR / Scripture Central leads" in out


# --- apply end-to-end ---

def test_apply_inserts_bullet_and_never_writes_fair_url_to_topic_file(tmp_path):
    proposals = tmp_path / "proposals"
    common_issues = tmp_path / "common-issues"
    proposals.mkdir()
    common_issues.mkdir()

    accepted_item = FACT_ITEM.replace("accept: false", "accept: true")
    _write_proposal(proposals, "some-topic", accepted_item, rewrite="X shows Y, which answers the objection.")
    _write_topic(common_issues, "some-topic",
                 "# Some Topic\n\n## General response\n\nExisting text.\n\n## Catholic and Protestant response\n\nC/P text.\n\n## Exmo/atheist response\n\nExmo text.\n")

    rc = s.apply_topic("some-topic", None, proposals, common_issues, dry_run=False)
    assert rc == 0

    topic_text = (common_issues / "some-topic.md").read_text(encoding="utf-8")
    assert "X shows Y, which answers the objection." in topic_text
    assert "fairlatterdaysaints" not in topic_text
    assert "scripturecentral" not in topic_text
    assert "corpus.noahairmet.com" in topic_text  # the upstream link IS allowed

    proposal_text = (proposals / "some-topic.md").read_text(encoding="utf-8")
    assert "status: applied" in proposal_text
    assert "applied:" in proposal_text
    assert "applied: null" not in proposal_text


def test_apply_skips_items_not_accepted(tmp_path):
    proposals = tmp_path / "proposals"
    common_issues = tmp_path / "common-issues"
    proposals.mkdir()
    common_issues.mkdir()

    _write_proposal(proposals, "no-accept-topic", FACT_ITEM)  # accept: false
    _write_topic(common_issues, "no-accept-topic", "# T\n\n## General response\n\nText.\n")

    rc = s.apply_topic("no-accept-topic", None, proposals, common_issues, dry_run=False)
    assert rc == 0
    topic_text = (common_issues / "no-accept-topic.md").read_text(encoding="utf-8")
    assert "Rewrite text here." not in topic_text


def test_apply_items_filter_only_applies_named_ids(tmp_path):
    proposals = tmp_path / "proposals"
    common_issues = tmp_path / "common-issues"
    proposals.mkdir()
    common_issues.mkdir()

    text = f"""---
topic: two-item-topic
generated: "2026-09-13"
status: proposed
leads: []
---
### A1 — first claim
```yaml
{FACT_ITEM.replace("accept: false", "accept: true")}
```
**Rewrite:** First rewrite.

### A2 — second claim
```yaml
{FACT_ITEM.replace("accept: false", "accept: true")}
```
**Rewrite:** Second rewrite.
"""
    (proposals / "two-item-topic.md").write_text(text, encoding="utf-8")
    _write_topic(common_issues, "two-item-topic", "# T\n\n## General response\n\nText.\n")

    rc = s.apply_topic("two-item-topic", ["A1"], proposals, common_issues, dry_run=False)
    assert rc == 0
    topic_text = (common_issues / "two-item-topic.md").read_text(encoding="utf-8")
    assert "First rewrite." in topic_text
    assert "Second rewrite." not in topic_text

    proposal_text = (proposals / "two-item-topic.md").read_text(encoding="utf-8")
    assert "status: partial" in proposal_text
