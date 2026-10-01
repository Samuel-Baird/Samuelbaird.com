"""Post-caption validation and the RESPONSE INCOMING banner window.

    python -m pytest tools/tests/test_caption_banner.py
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from capy import beats  # noqa: E402
from capy.banner import banner_beat_ids  # noqa: E402


def _doc(kinds):
    return {"beats": [{"id": f"b{i}", "kind": k} for i, k in enumerate(kinds)]}


def test_banner_covers_leading_clip_run_only():
    assert banner_beat_ids(_doc(["clip", "clip", "narration", "clip"])) == {"b0", "b1"}


def test_no_banner_when_script_opens_with_narration():
    assert banner_beat_ids(_doc(["narration", "clip"])) == set()


def _caption_issues(caption):
    doc = {"caption": caption, "beats": [{"id": "x", "kind": "narration", "text": "God bless."}]}
    return [i for i in beats.validate(doc) if "caption" in i.message]


def test_caption_missing_warns():
    assert [i.level for i in _caption_issues(None)] == ["warning"]


def test_caption_three_sentences_ok_four_errors():
    assert not _caption_issues("One. Two? Three!")
    assert [i.level for i in _caption_issues("One. Two. Three. Four.")] == ["error"]


def test_title_missing_or_slug_warns():
    def issues(doc):
        doc = {**doc, "beats": [{"id": "x", "kind": "narration", "text": "God bless."}]}
        return [i for i in beats.validate(doc) if "'title'" in i.message]
    assert [i.level for i in issues({})] == ["warning"]
    assert [i.level for i in issues({"title": "adam-god", "slug": "adam-god"})] == ["warning"]
    assert not issues({"title": "Did Brigham Young teach Adam was God?", "slug": "adam-god"})
