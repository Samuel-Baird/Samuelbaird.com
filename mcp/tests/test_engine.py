import json

import pytest

from urim_translate import config, segment
from urim_translate.glossary import Glossary
from urim_translate.store import Store
from urim_translate.translator import Translator

DOC = """---
title: Test
---

# The priesthood

Brothers, the **priesthood** is the power of God.[^1] See Alma 32:21 and D&C 93:29.

> A quote about the endowment.

- one item with https://example.com/x
- two

```
code block stays
```

[^1]: Footnote about the Godhead.
"""


@pytest.fixture(autouse=True)
def fixtures(tmp_path, monkeypatch):
    gdir = tmp_path / "gloss"
    gdir.mkdir()
    (gdir / "pt.json").write_text(json.dumps({"lang": "pt", "entries": [
        {"id": "concept.priesthood", "slug": "priesthood", "en": ["priesthood"], "preferred": "sacerdócio",
         "confidence": "attested", "variants": []},
        {"id": "concept.endowment", "slug": "endowment", "en": ["endowment"], "preferred": "investidura",
         "confidence": "attested", "variants": []},
        {"id": "concept.godhead", "slug": "godhead", "en": ["Godhead"], "preferred": "Trindade",
         "confidence": "approved", "variants": [{"term": "Divindade", "share": 0.2}]},
        {"id": "concept.priesthood-keys", "slug": "priesthood-keys", "en": ["priesthood keys"],
         "preferred": "chaves do sacerdócio", "confidence": "attested", "variants": []},
        {"id": "concept.hintonly", "slug": "", "en": ["hintword"], "preferred": "dica", "confidence": "hint",
         "variants": []},
    ]}), encoding="utf-8")
    books = tmp_path / "books.json"
    books.write_text(json.dumps({"Alma": {"pt": "Alma"}, "John": {"pt": "João"},
                                 "D&C": {"pt": "D&C", "es": "D. y C."},
                                 "Doctrine and Covenants": {"pt": "D&C"}}), encoding="utf-8")
    monkeypatch.setattr(config, "GLOSSARY_DIR", gdir)
    monkeypatch.setattr(config, "BOOKS_FILE", books)
    segment.Books._cache.clear()


def tr(_unused=None):
    return Translator(Store(":memory:"))


def test_roundtrip_is_exact():
    blocks = segment.split_document(DOC)
    assert segment.join_blocks(blocks, use_target=False) == DOC
    kinds = [b.is_seg for b in blocks]
    assert kinds.count(True) >= 5
    assert all(not b.is_seg for b in blocks if "code block" in b.raw or b.raw.strip() == "---")


def test_protect_restore_and_citations():
    masked, ph = segment.protect("See Alma 32:21 and John 3:16, D&C 93:29.[^1] https://a.b/c", "pt")
    assert "Alma" not in masked and "[^1]" not in masked
    restored = segment.restore(masked, ph)
    assert "João 3:16" in restored
    assert "D&C 93:29" in restored and "Alma 32:21" in restored


def test_citation_localized_for_es():
    masked, ph = segment.protect("Read D&C 93:29.", "es")
    assert segment.restore(masked, ph) == "Read D. y C. 93:29."


def test_glossary_longest_match_and_validation():
    g = Glossary("pt")
    ms = g.match("The priesthood keys and the priesthood are here")
    assert [m.entry.id for m in ms] == ["concept.priesthood-keys", "concept.priesthood"]
    assert g.missing(ms, "As chaves do sacerdócio e o sacerdócio") == []
    bad = g.missing(ms, "As chaves do sacerdote e o sacerdote")
    assert {e.id for e in bad} == {"concept.priesthood-keys", "concept.priesthood"}
    # accent/inflection tolerant, variants allowed, hints never enforced
    assert g.missing(g.match("the Godhead"), "a divindade") == []
    assert g.missing(g.match("hintword"), "qualquer coisa") == []


def test_only_relevant_entries_surface():
    g = Glossary("pt")
    assert {m.entry.id for m in g.match("Nothing relevant here.")} == set()


def test_tm_search_fts():
    s = Store(":memory:")
    s.tm_put("pt", "The endowment is a gift.", "A investidura é uma dádiva.", "church")
    assert s.tm_search("investidura", "pt")[0]["origin"] == "church"
    assert s.tm_search("endowment", origin="argos") == []


def test_user_override_wins_over_the_church_glossary():
    t = tr()
    t.store.override_put("pt", "priesthood", "sacerdócio santo", "test")
    t.reload_glossary("pt")
    assert t.glossary("pt").match("priesthood")[0].entry.preferred == "sacerdócio santo"
