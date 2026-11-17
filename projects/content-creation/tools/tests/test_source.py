"""Unit tests for capy.source and capy.excerpts (article/text-source mode).

    python -m pytest tools/tests/test_source.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from capy import excerpts  # noqa: E402
from capy import source  # noqa: E402
from capy.beats import Issue  # noqa: E402

PARAS = [
    "Every July the floats roll down the avenue, and every July I ask the same question.",
    "The parade was once a memorial. The people who walked into this valley in 1847 buried children along the trail.",
    "Consider the floats themselves. In the parade I watched this year, not one carried a handcart.",
    "That is not a memorial; it’s a trade show with a historical name attached — and “everyone” knows it.",
    "Until then I will keep standing on the curb.",
]


@pytest.fixture
def article() -> source.Article:
    return source.Article(paragraphs={i + 1: p for i, p in enumerate(PARAS)})


def _doc(*beats: dict, voices: dict | None = None, voice: dict | None = None) -> dict:
    d = {
        "slug": "t", "title": "t", "hook": "h",
        "voice": voice or {"name": "am_michael", "speed": 0.95},
        "beats": list(beats) + [{"id": "close-01", "kind": "narration", "pose": "encouraging", "text": "God bless.", "opinion": True}],
    }
    if voices is not None:
        d["voices"] = voices
    return d


def _excerpt(**over) -> dict:
    b = {"id": "x01", "kind": "excerpt", "text": "The parade was once a memorial. The people who walked", "para": 2, "pose": "reading"}
    b.update(over)
    return b


def _errors(issues: list[Issue], bid: str | None = "x01") -> list[str]:
    return [i.message for i in issues if i.level == "error" and (bid is None or i.beat_id == bid)]


# ---------------------------------------------------------------------------
# normalize / find_excerpt
# ---------------------------------------------------------------------------

def test_normalize_folds_quotes_dashes_whitespace_case():
    assert source.normalize("  It’s   “fine” — OK ") == "it's \"fine\" - ok"
    assert source.normalize("a -- b … c") == "a - b ... c"
    assert source.normalize(None) == ""


def test_find_excerpt_contiguous_straight_vs_curly(article):
    # excerpt uses straight quotes/hyphen; article has curly apostrophe, em dash, curly quotes
    m = source.find_excerpt(article, "it's a trade show with a historical name attached - and \"everyone\" knows it.", 4)
    assert m.ok, m.message
    # and the reverse direction: excerpt curly, article straight
    art2 = source.Article(paragraphs={1: "it's a trade show - and \"everyone\" knows it."})
    assert source.find_excerpt(art2, "it’s a trade show — and “everyone” knows it.", 1).ok


def test_find_excerpt_rejects_one_word_change_with_hint(article):
    m = source.find_excerpt(article, "The parade was once a festival. The people who walked into this valley", 2)
    assert not m.ok
    assert m.failed_index == 0
    assert "¶2" in m.message and "nearest match ¶2" in m.hint


def test_find_excerpt_fragments_in_order_across_boundary(article):
    text = "In the parade I watched this year, not one carried a handcart [...] That is not a memorial; it's a trade show"
    assert source.find_excerpt(article, text, [3, 4]).ok
    # reversed order -> fails, and says so
    rev = "That is not a memorial; it's a trade show [...] In the parade I watched this year, not one carried a handcart"
    m = source.find_excerpt(article, rev, [3, 4])
    assert not m.ok and "out of order" in m.hint


def test_find_excerpt_outer_quotes_and_missing_para(article):
    assert source.find_excerpt(article, "“Until then I will keep standing on the curb.”", 5).ok
    m = source.find_excerpt(article, "anything", 99)
    assert not m.ok and "¶99" in m.message
    assert not source.find_excerpt(article, "x", "2").ok  # para must be int


# ---------------------------------------------------------------------------
# number_paragraphs / parse / sha256 pin
# ---------------------------------------------------------------------------

def test_number_paragraphs_splits_blocks_strips_headings_and_markers():
    raw = "# Headline\n\nFirst para\nwraps here.\n\n\n## Subhead\n\n---\n\n¶7 Old marker stays out.\n\n![img](x.png)\n\n  Last   para  \n"
    assert source.number_paragraphs(raw) == ["Headline", "First para wraps here.", "Subhead", "Old marker stays out.", "Last para"]
    assert source.number_paragraphs("") == []


def test_source_md_roundtrip_and_sha256_pin(tmp_path):
    info = source.SourceInfo(kind="article", title="T", publication="P", byline="B", publish_date="2026-08-30", url="https://example.com/a")
    paras = source.number_paragraphs("One para here.\n\nTwo para here.\n\nThree.")
    info.text_sha256 = source.sha256_text("\n\n".join(paras))
    info.paragraph_count = len(paras)
    path = source.write_source_md(tmp_path, info, paras)
    assert path.read_text(encoding="utf-8").startswith("# T\nP · B · 2026-08-30\nSource: https://example.com/a\nArchived: (none)\n\n¶1 One para here.\n\n¶2 Two para here.")
    art = source.load_article(tmp_path)
    assert art.count == 3 and art.paragraphs[3] == "Three."
    assert art.header_lines[0] == "# T"
    assert art.sha256 == info.text_sha256
    # any wording edit breaks the pin; CRLF does not
    (tmp_path / "source" / "source.md").write_text(path.read_text(encoding="utf-8").replace("\n", "\r\n"), encoding="utf-8", newline="")
    assert source.load_article(tmp_path).sha256 == info.text_sha256
    (tmp_path / "source" / "source.md").write_text(path.read_text(encoding="utf-8").replace("Two para", "Two paras"), encoding="utf-8")
    assert source.load_article(tmp_path).sha256 != info.text_sha256


def test_parse_article_rejects_gaps_and_duplicates():
    with pytest.raises(ValueError):
        source.parse_article("hdr\n\n¶1 a\n\n¶3 b\n")
    with pytest.raises(ValueError):
        source.parse_article("¶1 a\n\n¶1 b\n")


def test_load_source_info_defaults_to_video(tmp_path):
    assert source.load_source_info(tmp_path).kind == "video"
    assert not source.load_source_info(tmp_path).present
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "source_info.json").write_text(json.dumps({"title": "x", "uploader": "u"}), encoding="utf-8")
    info = source.load_source_info(tmp_path)
    assert info.kind == "video" and info.present and info.uploader == "u"
    (tmp_path / "source" / "source_info.json").write_text(json.dumps({"kind": "article", "title": "H", "publication": "P", "publish_date": "2026-08-30", "url": "u"}), encoding="utf-8")
    assert source.load_source_info(tmp_path).is_article


def test_attribution_line_and_headers():
    info = source.SourceInfo(kind="article", title="Headline", publication="The Salt Lake Tribune", byline="Jane Doe", publish_date="2026-08-30")
    assert source.attribution_line(info) == "The Salt Lake Tribune · “Headline” · Aug 30, 2026"
    assert source.attribution_line(info, cite_byline=True).startswith("Jane Doe, The Salt Lake Tribune")
    assert source.format_date("2024-06") == "Jun 2024" and source.format_date("20240604") == "Jun 4, 2024" and source.format_date("1852") == "1852"
    line = source.excerpt_script_line({"text": "“Quoted words.”", "para": [4, 5], "voice": "quote_female"}, info)
    assert line == "- **Excerpt (¶4–¶5):** “Quoted words.” — The Salt Lake Tribune · “Headline” · Aug 30, 2026 · voice: quote_female"
    assert source.source_header_lines(info)[0].startswith("**Source:** article — “Headline”")
    assert source.source_header_lines(source.SourceInfo(title="Vid", uploader="U"))[0] == "**Source:** video — “Vid” (U)"


# ---------------------------------------------------------------------------
# validate_excerpt_beats rule matrix
# ---------------------------------------------------------------------------

def test_validate_clean_excerpt_has_no_errors():
    assert _errors(excerpts.validate_excerpt_beats(_doc(_excerpt())), None) == []


@pytest.mark.parametrize("over, needle", [
    ({"text": None}, "requires 'text'"),
    ({"para": None}, "requires 'para'"),
    ({"para": "2"}, "invalid para"),
    ({"para": [2, 3, 4]}, "spans 3 paragraphs"),
    ({"para": [2, 4]}, "must be consecutive"),
    ({"para": 0}, "start at 1"),
    ({"text": "[...] The parade was once a memorial"}, "must not start or end with [...]"),
    ({"text": "The parade was once a memorial [...]"}, "must not start or end with [...]"),
    ({"text": "The parade was once [...] a memorial"}, "under 3 words"),
    ({"highlight": ["memorial"]}, "highlight: is forbidden"),
    ({"voice": "quote_robot"}, "unknown voice role"),
    ({"voice": {"speed": 1.0}}, "inline voice needs 'name'"),
    ({"voice": 3}, "voice must be a role name"),
    ({"text": " ".join(["word"] * 101)}, "> 100"),
])
def test_validate_excerpt_errors(over, needle):
    msgs = _errors(excerpts.validate_excerpt_beats(_doc(_excerpt(**over))))
    assert any(needle in m for m in msgs), msgs


def test_validate_excerpt_word_warning_and_span2_ok():
    issues = excerpts.validate_excerpt_beats(_doc(_excerpt(text=" ".join(["word"] * 61), para=[2, 3])))
    assert _errors(issues) == []
    assert any(i.level == "warning" and "> 60" in i.message for i in issues)


def test_validate_freeze_before_clip_is_error_but_after_clip_ok():
    n = {"id": "n01", "kind": "narration", "text": "x", "stage": "freeze", "opinion": True}
    c = {"id": "c01", "kind": "clip", "start": 0, "end": 5}
    assert any("stage: freeze but no clip" in m for m in _errors(excerpts.validate_excerpt_beats(_doc(n)), "n01"))
    assert _errors(excerpts.validate_excerpt_beats(_doc(c, n)), "n01") == []


def test_validate_quote_default_must_exist():
    issues = excerpts.validate_excerpt_beats(_doc(_excerpt(), voices={"quote_default": "nope"}))
    assert any("quote_default" in m for m in _errors(issues, None))


# ---------------------------------------------------------------------------
# resolve_voice precedence / speech_text / source time
# ---------------------------------------------------------------------------

def test_resolve_voice_precedence():
    voices = {"quote_male": {"name": "M", "speed": 1.1}, "quote_female": {"name": "F", "speed": 1.0}, "quote_default": "quote_female"}
    doc = _doc(voices=voices, voice={"name": "H", "speed": 0.9})
    # inline dict wins over role
    assert excerpts.resolve_voice(doc, _excerpt(voice={"name": "X", "speed": 0.8})) == {"name": "X", "speed": 0.8, "role": "inline"}
    # explicit role
    assert excerpts.resolve_voice(doc, _excerpt(voice="quote_male")) == {"name": "M", "speed": 1.1, "role": "quote_male"}
    # kind default: excerpt -> quote_default
    assert excerpts.resolve_voice(doc, _excerpt()) == {"name": "F", "speed": 1.0, "role": "quote_female"}
    # everything else -> doc.voice
    assert excerpts.resolve_voice(doc, {"id": "n01", "kind": "narration"}) == {"name": "H", "speed": 0.9, "role": "host"}
    assert excerpts.resolve_voice(doc, {"id": "n01", "kind": "narration", "voice": "host"})["name"] == "H"
    # no voices block -> DEFAULT_VOICES; no doc.voice -> DEFAULT_HOST_VOICE
    bare = {"beats": []}
    assert excerpts.resolve_voice(bare, _excerpt())["name"] == excerpts.DEFAULT_VOICES[excerpts.DEFAULT_VOICES["quote_default"]]["name"]
    assert excerpts.resolve_voice(bare, {"kind": "narration"})["name"] == excerpts.DEFAULT_HOST_VOICE["name"]
    with pytest.raises(KeyError):
        excerpts.resolve_voice(doc, _excerpt(voice="quote_robot"))


def test_speech_text_and_caption_text():
    b = _excerpt(text="“The parade was once a memorial, [...] and the earliest observances were sober [...] closer to a funeral.”")
    assert excerpts.speech_text(b) == "The parade was once a memorial. and the earliest observances were sober. closer to a funeral."
    assert excerpts.caption_text(b) == "The parade was once a memorial, and the earliest observances were sober closer to a funeral."
    assert "[" not in excerpts.speech_text(b)
    assert excerpts.speech_text({"kind": "narration", "text": "[keep] me"}) == "[keep] me"


def test_source_time_counts_clips_and_excerpts():
    doc = _doc({"id": "c01", "kind": "clip", "start": 0, "end": 5}, _excerpt(), {"id": "n01", "kind": "narration", "text": "x", "opinion": True})
    per_beat = {"c01": 5.0, "x01": 4.0, "n01": 20.0, "close-01": 1.2}
    assert excerpts.source_time_seconds(doc, per_beat) == 9.0
    assert excerpts.excerpt_word_total(doc) == 10  # "The parade was once a memorial. The people who walked"
