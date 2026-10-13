"""Unit tests for capy.beats' `length: short | long` budget rules
(docs/saint-capybara/script-format.md "Duration budget").

    python -m pytest tools/tests/test_beats_length.py
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from capy import beats  # noqa: E402


def _load(tmp_path: Path, body: str) -> dict:
    p = tmp_path / "beats.yaml"
    p.write_text("slug: t\ntitle: t\nhook: h\n" + body + "\nbeats:\n"
                 "  - {id: n99, kind: narration, text: 'God bless.', pose: encouraging, opinion: true}\n",
                 encoding="utf-8")
    return beats.load_beats(p)


def _errors(issues) -> list[str]:
    return [i.message for i in issues if i.level == "error"]


def test_short_is_default_with_60_180_budget(tmp_path):
    doc = _load(tmp_path, "")
    assert doc["length"] == "short"
    assert (doc["format"]["min_seconds"], doc["format"]["max_seconds"]) == (60, 180)
    assert _errors(beats.validate_length(doc)) == []


def test_long_defaults_to_180_1200_budget(tmp_path):
    doc = _load(tmp_path, "length: long\nlong_form_requested: \"2026-10-09: 'make this one long form'\"")
    assert (doc["format"]["min_seconds"], doc["format"]["max_seconds"]) == (180, 1200)
    assert _errors(beats.validate_length(doc)) == []


def test_long_without_user_request_is_an_error(tmp_path):
    doc = _load(tmp_path, "length: long")
    assert any("long_form_requested" in m for m in _errors(beats.validate_length(doc)))


def test_short_cannot_raise_its_ceiling(tmp_path):
    doc = _load(tmp_path, "format: {max_seconds: 600}")
    assert any("short-form ceiling" in m for m in _errors(beats.validate_length(doc)))


def test_long_cannot_exceed_20_minutes(tmp_path):
    doc = _load(tmp_path, "length: long\nlong_form_requested: x\nformat: {max_seconds: 1500}")
    assert any("1200s long-form ceiling" in m for m in _errors(beats.validate_length(doc)))


def test_unknown_length_is_an_error(tmp_path):
    doc = _load(tmp_path, "length: medium")
    assert any("unknown length" in m for m in _errors(beats.validate_length(doc)))


def test_validate_includes_length_rules(tmp_path):
    doc = _load(tmp_path, "length: long")
    assert any("long_form_requested" in m for m in _errors(beats.validate(doc)))


def test_duration_budget_uses_long_bounds(tmp_path):
    doc = _load(tmp_path, "length: long\nlong_form_requested: x")
    assert _errors(beats.check_duration_budget(doc, 900.0)) == []
    assert _errors(beats.check_duration_budget(doc, 1300.0))
    assert any("too short for long form" in m for m in _errors(beats.check_duration_budget(doc, 120.0)))
