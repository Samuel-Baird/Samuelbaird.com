"""Unit tests for capy_merge_briefs.py's apologetic-lead validation (2026-09-13).

    python -m pytest tools/tests/test_merge_briefs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import capy_merge_briefs as m  # noqa: E402


def _entry(**kw):
    base = {
        "id": "x", "type": "primary", "title": "t", "author": "a", "date": "2020",
        "locator": "https://example.org/x", "accessed": "2026-09-13",
        "inspected": True, "inspected_via": "WebFetch https://example.org/x",
        "quote": None, "verification": None, "grade_supports": "fact",
        "traced_to": None, "used_on_screen": False, "counter": False, "notes": "",
    }
    base.update(kw)
    return base


# --- (a) an apologetic-lead host can never verify a quote ---------------------

def test_quote_verified_against_fair_link_is_rejected():
    entry = _entry(
        id="fair-quote", type="critic", quote="something quoted",
        verification={"tool": "WebFetch", "link": "https://www.fairlatterdaysaints.org/answers/Foo"},
    )
    problems = m.validate_entry(entry, verification_log="", role="capy-historian")
    assert any("apologetic-lead host" in p for p in problems)


def test_quote_verified_against_gsa_link_is_fine():
    entry = _entry(
        id="gsa-quote", type="scholarly", quote="something quoted",
        verification={"tool": "cite_page", "link": "https://corpus.noahairmet.com/b/vol-1/12"},
    )
    problems = m.validate_entry(entry, verification_log="", role="capy-historian")
    assert problems == []


# --- (b) a source pointing at a FAIR/KnoWhy host must be type apologetic-lead --

def test_fair_locator_wrong_type_is_rejected():
    entry = _entry(id="fair-lead", type="scholarly", locator="https://scripturecentral.org/knowhy/foo", traced_to=None)
    problems = m.validate_entry(entry, verification_log="", role="capy-historian")
    assert any("apologetic-lead" in p and "not 'apologetic-lead'" in p for p in problems)


def test_fair_locator_correct_type_with_traced_to_is_fine():
    known_types = {"upstream-1": "scholarly"}
    entry = _entry(id="fair-lead", type="apologetic-lead", locator="https://www.fairlatterdaysaints.org/answers/Foo",
                    inspected=True, inspected_via="WebFetch https://www.fairlatterdaysaints.org/answers/Foo",
                    traced_to="upstream-1", quote=None)
    problems = m.validate_entry(entry, verification_log="", role="capy-historian", known_types=known_types)
    assert problems == []


# --- (c) traced_to must resolve to an upstream primary/scholarly/etc. entry ---

def test_apologetic_lead_requires_traced_to():
    entry = _entry(id="lead-no-trace", type="apologetic-lead", traced_to=None)
    problems = m.validate_entry(entry, verification_log="", role="capy-historian")
    assert any("requires traced_to" in p for p in problems)


def test_traced_to_unresolved_is_rejected():
    entry = _entry(id="lead-bad-trace", type="apologetic-lead", traced_to="does-not-exist")
    problems = m.validate_entry(entry, verification_log="", role="capy-historian", known_types={})
    assert any("does not resolve" in p for p in problems)


def test_traced_to_pointing_at_another_lead_is_rejected():
    known_types = {"other-lead": "apologetic-lead"}
    entry = _entry(id="lead-chain", type="apologetic-lead", traced_to="other-lead")
    problems = m.validate_entry(entry, verification_log="", role="capy-historian", known_types=known_types)
    assert any("must trace to an upstream" in p for p in problems)


def test_traced_to_pointing_at_critic_is_rejected():
    known_types = {"critic-article": "critic"}
    entry = _entry(id="lead-to-critic", type="apologetic-lead", traced_to="critic-article")
    problems = m.validate_entry(entry, verification_log="", role="capy-historian", known_types=known_types)
    assert any("must trace to an upstream" in p for p in problems)


def test_apologetic_lead_with_quote_is_rejected():
    known_types = {"upstream-1": "primary"}
    entry = _entry(id="lead-with-quote", type="apologetic-lead", traced_to="upstream-1", quote="verbatim text")
    problems = m.validate_entry(entry, verification_log="", role="capy-historian", known_types=known_types)
    assert any("quote: null" in p for p in problems)


# --- end-to-end: merge() downgrades a bad brief entry to inspected: false -----

def test_merge_downgrades_fair_quote_entry(tmp_path):
    project = tmp_path / "proj"
    briefs = project / "research" / "briefs"
    briefs.mkdir(parents=True)

    brief_text = """---
role: capy-historian
claim: 1
---
```yaml
sources:
  - id: fair-bad-quote
    type: critic
    title: "FAIR page"
    author: null
    date: "2024"
    locator: "https://www.fairlatterdaysaints.org/answers/Foo"
    accessed: "2026-09-13"
    inspected: true
    inspected_via: "WebFetch https://www.fairlatterdaysaints.org/answers/Foo"
    quote: "a quoted line"
    verification: {tool: WebFetch, link: "https://www.fairlatterdaysaints.org/answers/Foo"}
    grade_supports: fact
    traced_to: null
    used_on_screen: false
    counter: false
    notes: ""
```

## Verification log
none
"""
    (briefs / "claim1-capy-historian.md").write_text(brief_text, encoding="utf-8")

    rc = m.merge(project, dry_run=False)
    assert rc == 0

    doc = yaml.safe_load((project / "research" / "sources.yaml").read_text(encoding="utf-8"))
    entry = next(s for s in doc["sources"] if s["id"] == "fair-bad-quote")
    assert entry["inspected"] is False
    assert "apologetic-lead host" in entry["notes"]


def test_merge_accepts_lead_traced_to_source_found_earlier_same_run(tmp_path):
    """A lead in one brief can trace to a primary/scholarly source another
    researcher found in the same run, as long as it's processed first (briefs
    are merged in claim<N> filename order)."""
    project = tmp_path / "proj"
    briefs = project / "research" / "briefs"
    briefs.mkdir(parents=True)

    (briefs / "claim1-capy-historian.md").write_text("""---
role: capy-historian
claim: 1
---
```yaml
sources:
  - id: upstream-primary
    type: primary
    title: "Journal of Discourses 1:1"
    author: "Brigham Young"
    date: "1854"
    locator: "https://corpus.noahairmet.com/b/jod-1/1"
    accessed: "2026-09-13"
    inspected: true
    inspected_via: "GSA read_pages jod-1 p.1"
    quote: null
    verification: null
    grade_supports: fact
    traced_to: null
    used_on_screen: false
    counter: false
    notes: ""
```
""", encoding="utf-8")

    (briefs / "claim1-capy-red-team.md").write_text("""---
role: capy-red-team
claim: 1
---
```yaml
sources:
  - id: fair-lead-1
    type: apologetic-lead
    title: "FAIR answers page"
    author: null
    date: "2024"
    locator: "https://www.fairlatterdaysaints.org/answers/Foo"
    accessed: "2026-09-13"
    inspected: true
    inspected_via: "WebFetch https://www.fairlatterdaysaints.org/answers/Foo"
    quote: null
    verification: null
    grade_supports: fact
    traced_to: upstream-primary
    used_on_screen: false
    counter: false
    notes: ""
```
""", encoding="utf-8")

    rc = m.merge(project, dry_run=False)
    assert rc == 0
    doc = yaml.safe_load((project / "research" / "sources.yaml").read_text(encoding="utf-8"))
    entry = next(s for s in doc["sources"] if s["id"] == "fair-lead-1")
    assert entry["inspected"] is True
    assert "notes" not in entry or "capy_merge_briefs" not in (entry.get("notes") or "")
