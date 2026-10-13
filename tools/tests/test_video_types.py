"""Unit tests for the three Saint Capybara video types -- capy.beats'
`video_type:` budget/format rules and capy.layout's 9:16 vs 16:9 theme
selection (docs/saint-capybara/script-format.md "Video types").

    python -m pytest tools/tests/test_video_types.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from capy import beats  # noqa: E402
from capy.layout import Theme  # noqa: E402


def _load(tmp_path: Path, body: str) -> dict:
    p = tmp_path / "beats.yaml"
    p.write_text("slug: t\ntitle: t\nhook: h\n" + body + "\nbeats:\n"
                 "  - {id: n99, kind: narration, text: 'God bless.', pose: encouraging, opinion: true}\n",
                 encoding="utf-8")
    return beats.load_beats(p)


def _errors(issues) -> list[str]:
    return [i.message for i in issues if i.level == "error"]


REQ = "long_form_requested: \"2026-10-13: 'make this a youtube long form'\""


# ---- beats.yaml rules ------------------------------------------------------

def test_short_is_default_9x16_60_180(tmp_path):
    doc = _load(tmp_path, "")
    assert doc["video_type"] == "short"
    f = doc["format"]
    assert (f["width"], f["height"], f["min_seconds"], f["max_seconds"]) == (1080, 1920, 60, 180)
    assert beats.orientation_for(doc) == "portrait"
    assert _errors(beats.validate_video_type(doc)) == []


def test_long_instagram_is_9x16_180_1200(tmp_path):
    doc = _load(tmp_path, f"video_type: long-instagram\n{REQ}")
    f = doc["format"]
    assert (f["width"], f["height"], f["min_seconds"], f["max_seconds"]) == (1080, 1920, 180, 1200)
    assert beats.orientation_for(doc) == "portrait"
    assert _errors(beats.validate_video_type(doc)) == []


def test_long_youtube_is_16x9_180_1200(tmp_path):
    doc = _load(tmp_path, f"video_type: long-youtube\n{REQ}")
    f = doc["format"]
    assert (f["width"], f["height"], f["min_seconds"], f["max_seconds"]) == (1920, 1080, 180, 1200)
    assert beats.orientation_for(doc) == "landscape"
    assert _errors(beats.validate_video_type(doc)) == []


def test_legacy_length_long_means_instagram(tmp_path):
    doc = _load(tmp_path, f"length: long\n{REQ}")
    assert doc["video_type"] == "long-instagram"


@pytest.mark.parametrize("vt", ["long-instagram", "long-youtube"])
def test_long_form_without_user_request_is_an_error(tmp_path, vt):
    doc = _load(tmp_path, f"video_type: {vt}")
    assert any("long_form_requested" in m for m in _errors(beats.validate(doc)))


def test_short_cannot_raise_its_ceiling(tmp_path):
    doc = _load(tmp_path, "format: {max_seconds: 600}")
    assert any("short-form ceiling" in m for m in _errors(beats.validate_video_type(doc)))


def test_long_cannot_exceed_20_minutes(tmp_path):
    doc = _load(tmp_path, f"video_type: long-youtube\n{REQ}\nformat: {{max_seconds: 1500}}")
    assert any("1200s long-youtube ceiling" in m for m in _errors(beats.validate_video_type(doc)))


def test_format_must_match_orientation(tmp_path):
    doc = _load(tmp_path, f"video_type: long-youtube\n{REQ}\nformat: {{width: 1080, height: 1920}}")
    assert any("doesn't match video_type" in m for m in _errors(beats.validate_video_type(doc)))


def test_unknown_video_type_is_an_error(tmp_path):
    doc = _load(tmp_path, "video_type: medium")
    assert any("unknown video_type" in m for m in _errors(beats.validate_video_type(doc)))


def test_duration_budget_uses_long_bounds(tmp_path):
    doc = _load(tmp_path, f"video_type: long-youtube\n{REQ}")
    assert _errors(beats.check_duration_budget(doc, 900.0)) == []
    assert _errors(beats.check_duration_budget(doc, 1300.0))
    assert any("too short for long form" in m for m in _errors(beats.check_duration_budget(doc, 120.0)))


# ---- theme selection -------------------------------------------------------

def test_portrait_theme_unchanged():
    t = Theme.load()
    assert t.canvas_size == (1080, 1920)
    assert "landscape" not in t.layout
    assert t.caption_zone("host").x_center == 540
    assert t.fit_box() == (0, 230, 1080, 850)
    assert t.source_fills_canvas(1080, 1920) and not t.source_fills_canvas(1920, 1080)


def test_landscape_theme_for_youtube_doc(tmp_path):
    doc = _load(tmp_path, f"video_type: long-youtube\n{REQ}")
    t = Theme.for_doc(doc)
    assert t.orientation == "landscape"
    assert t.canvas_size == (1920, 1080)
    assert t.source_fills_canvas(1920, 1080) and not t.source_fills_canvas(1080, 1920)
    assert t.fit_box() == (0, 0, 1920, 1080)
    # overrides merged over the shared caption/card text styles
    assert t.caption_style("style_capy")["size"] == 80
    assert t.caption_style("style_capy")["font"] == "body"
    assert t.text_style("card_text.quote")["size"] == 72


def test_landscape_zones_stay_on_canvas_and_clear_of_sprites():
    t = Theme.load(orientation="landscape")
    w, h = t.canvas_size
    for mode in ("clip", "host", "card"):
        x0, y0, x1, y1 = t.sprite_spec(mode).box
        assert 0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h, mode
        z = t.caption_zone(mode)
        zx0, zx1 = z.x_center - z.max_width // 2, z.x_center + z.max_width // 2
        assert 96 <= zx0 and zx1 <= w - 96 and 54 <= z.y0 and z.y1 <= 1010, mode
        overlaps = zx0 < x1 and x0 < zx1 and z.y0 < y1 and y0 < z.y1
        assert not overlaps, f"{mode}: captions overlap the sprite box"
    cx0, cy0, cx1, cy1 = t.card_box()
    sx0, *_ = t.sprite_spec("card").box
    assert cx1 <= sx0, "card box overlaps the card-mode sprite"
