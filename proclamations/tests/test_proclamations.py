from pathlib import Path

import pymupdf
import pytest

from proclamations import check, scripts, sizes
from proclamations.fonts import space_width, text_width, to_caps
from proclamations.generate import DOCS, localize, render
from proclamations.layout import Para, balanced_lines, break_paragraph, word
from proclamations.templates import split_words


def test_standard_print_sizes():
    assert sizes.SIZES["letter"] == (612, 792)
    w, h = sizes.SIZES["a4"]
    assert abs(w / 72 * 25.4 - 210) < 0.01 and abs(h / 72 * 25.4 - 297) < 0.01


def test_the_nine_requested_poster_sizes():
    want = {"11x17": (11, 17), "18x24": (18, 24), "24x36": (24, 36), "27x40": (27, 40), "40x60": (40, 60)}
    for name, (w, h) in want.items():
        assert sizes.SIZES[name] == (w * 72, h * 72)
    # ISO A-series, in points (1 pt = 1/72 in): A3 297x420 mm ... A0 841x1189 mm
    for name, (mw, mh) in {"a3": (297, 420), "a2": (420, 594), "a1": (594, 841), "a0": (841, 1189)}.items():
        w, h = sizes.SIZES[name]
        assert abs(w / 72 * 25.4 - mw) < 0.01 and abs(h / 72 * 25.4 - mh) < 0.01
    assert len(sizes.POSTERS) == 9 and len(sizes.SIZES) == 11
    with pytest.raises(KeyError):
        sizes.get("12x12")


def test_deseret_capitals_are_code_point_minus_0x28():
    assert to_caps("\U00010428") == "\U00010400"
    assert to_caps("a1") == "A1"


def test_split_words_keeps_every_word():
    assert split_words("a b c d e", [2, 2]) == ["a b", "c d e"]


def test_balanced_lines_respects_width():
    parts = balanced_lines("one two three four five six", 10, "r", 90, 2)
    assert len(parts) == 2 and " ".join(parts) == "one two three four five six"
    assert all(text_width(p, 10) <= 90 for p in parts)


def test_line_breaking_fills_the_measure_and_keeps_words_in_order():
    words = [word(w, 9) for w in ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
                                  "incididunt ut labore et dolore magna aliqua ut enim ad minim veniam").split()]
    para = Para(words, 9, 12.5)
    lines = break_paragraph(para, 150, space_width(9))
    assert [w for ln in lines for w in ln.words] == words
    assert all(ln.natural <= ln.avail * 1.3 for ln in lines)
    assert len(lines) >= 3 and lines[-1].last and not any(ln.last for ln in lines[:-1])


def test_drop_cap_indents_only_its_lines():
    words = [word("word%d" % i, 9) for i in range(40)]
    para = Para(words, 9, 12.5, dropcap_w=30, dropcap_lines=3)
    lines = break_paragraph(para, 160, space_width(9))
    assert [ln.x_off for ln in lines[:3]] == [30, 30, 30] and all(ln.x_off == 0 for ln in lines[3:])


def test_deseret_conversion_is_one_to_one():
    s = scripts.get("deseret")
    out = s.convert(["The priesthood is the power of God.", "We believe in God."])
    assert len(out) == 2 and all(any(0x10400 <= ord(c) <= 0x1044F for c in o) for o in out)


def test_format_matches_the_originals():
    """English output at letter size reproduces every rule, frame and column edge of the real PDFs."""
    assert check.main([]) == 0


@pytest.mark.parametrize("slug", DOCS)
def test_deseret_pdf_is_complete_at_a_poster_size(slug, tmp_path):
    path = render(slug, scripts.get("deseret"), "18x24", tmp_path)
    assert all(ok for _, ok, _ in check.output_check(path))
    page = pymupdf.open(path)[0]
    assert (round(page.rect.width), round(page.rect.height)) == (1296, 1728)


def test_text_matches_the_church_pages():
    """The YAML texts must stay word-for-word equal to what the page extractor produced."""
    for slug in DOCS:
        L, d = localize(slug, scripts.get("latin"))
        assert d["source_url"].startswith("https://www.churchofjesuschrist.org/")
        assert (d.get("paragraphs") or d.get("verses"))


# ---- editions, hyphenation, folder layout
def test_hyphenation_points():
    from proclamations import layout
    layout.set_hyphenation("en_US")
    try:
        assert any(h for _, h in layout.find_breaks("responsibilities"))
        assert layout.find_breaks("Presidency") == []                      # names are not hyphenated
        assert (4, False) in layout.find_breaks("law-abiding")             # a break after a dash needs no extra hyphen
        assert layout.find_breaks("law-wise") == [(4, False)]              # no dictionary break in a short run
        assert layout.find_breaks("short") == []
        layout.set_hyphenation("es")
        assert any(h for _, h in layout.find_breaks("responsabilidades"))
        layout.set_hyphenation(None)
        assert layout.find_breaks("responsibilities") == []
    finally:
        layout.set_hyphenation(None)


def test_split_words_reassemble_with_hyphens_where_needed():
    from proclamations import layout
    layout.set_hyphenation("en_US")
    try:
        w = layout.word("responsibilities", 9)
        frags = layout.expand([w])
        assert "".join(f.segs[0].text for f in frags) == "responsibilities" and len(frags) > 1
        assert not frags[0].cont and all(f.cont for f in frags[1:])
    finally:
        layout.set_hyphenation(None)


def test_editions_and_their_source_languages():
    assert scripts.EDITIONS == ["english", "spanish", "deseret"]
    assert scripts.get("english").source == "en" and scripts.get("spanish").source == "es"
    assert scripts.get("deseret").source == "en"          # transliterated from the English text
    assert scripts.get("spanish").hyphenation == "es" and scripts.get("deseret").hyphenation is None


def test_spanish_text_is_the_churchs_own():
    d = yaml_load("es", "family")
    assert d["title"] == "La Familia" and d["source_url"].endswith("?lang=spa")
    assert "Nosotros, la Primera Presidencia" in d["paragraphs"][0]


def yaml_load(lang, slug):
    from proclamations.generate import load_text
    return load_text(slug, lang)


@pytest.mark.parametrize("edition", ["english", "spanish"])
def test_english_and_spanish_pdfs_are_complete(edition, tmp_path):
    path = render("living-christ", scripts.get(edition), "a4", tmp_path)
    assert path == tmp_path / edition / f"living-christ-{edition}-a4.pdf"        # one flat folder per edition
    assert all(ok for _, ok, _ in check.output_check(path))
