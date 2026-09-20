"""Unit tests for capy_check_sources.py's check_traced_to (2026-09-13).

    python -m pytest tools/tests/test_check_sources_traced_to.py
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import capy_check_sources as cs  # noqa: E402


def _src(**kw):
    base = {"type": "primary", "inspected": True, "traced_to": None}
    base.update(kw)
    return base


def test_traced_to_resolves_to_inspected_upstream_is_clean():
    sources = {
        "upstream": _src(type="scholarly", inspected=True),
        "lead": _src(type="apologetic-lead", traced_to="upstream"),
    }
    issues = cs.check_traced_to(sources)
    assert issues == []


def test_traced_to_unresolved_is_error():
    sources = {"lead": _src(type="apologetic-lead", traced_to="ghost")}
    issues = cs.check_traced_to(sources)
    assert len(issues) == 1
    assert issues[0].level == "error"
    assert "does not resolve" in issues[0].message


def test_traced_to_pointing_at_another_lead_is_error():
    sources = {
        "other-lead": _src(type="apologetic-lead"),
        "lead": _src(type="apologetic-lead", traced_to="other-lead"),
    }
    issues = cs.check_traced_to(sources)
    assert len(issues) == 1
    assert "must trace to an upstream" in issues[0].message


def test_traced_to_pointing_at_uninspected_upstream_is_error():
    sources = {
        "upstream": _src(type="primary", inspected=False),
        "lead": _src(type="apologetic-lead", traced_to="upstream"),
    }
    issues = cs.check_traced_to(sources)
    assert len(issues) == 1
    assert "not itself marked inspected" in issues[0].message


def test_non_lead_sources_are_ignored():
    sources = {"x": _src(type="primary"), "y": _src(type="critic")}
    assert cs.check_traced_to(sources) == []


def test_lead_with_no_traced_to_is_skipped_here_other_check_covers_it():
    # field/per-beat checks already error on a missing traced_to; check_traced_to
    # only validates ones that ARE set, to avoid double-reporting.
    sources = {"lead": _src(type="apologetic-lead", traced_to=None)}
    assert cs.check_traced_to(sources) == []
