import pytest

from urim_translate import deseret

pytestmark = pytest.mark.skipif(not deseret.available()[0], reason="Node.js or the deseret package is unavailable")

DOC = """---
title: Test
---

# The priesthood

The priesthood is the power of God.[^1] See [the page](https://example.com/priesthood) and `priesthood`.

```
priesthood stays
```

[^1]: A note.
"""


def is_dsrt(s):
    return any(0x10400 <= ord(c) <= 0x1044F for c in s)


def test_text_conversion_and_coverage():
    out, cov = deseret.convert_text("The priesthood is the power of God. Xyzzyfoo")
    assert is_dsrt(out) and out.endswith("Xyzzyfoo")
    assert cov["left_in_latin"] == ["xyzzyfoo"] and cov["converted"] == cov["words"] - 1


def test_document_keeps_markup_and_converts_prose():
    out, cov = deseret.convert_document(DOC)
    assert out.startswith("---\ntitle: Test\n---")
    assert "[^1]" in out and "https://example.com/priesthood" in out
    assert "`priesthood`" in out and "```\npriesthood stays\n```" in out
    assert is_dsrt(out) and cov["words"] > 5
    # the prose line is converted, and its link text with it, but the URL is not
    line = [l for l in out.split("\n") if "example.com" in l][0]
    assert is_dsrt(line) and "(https://example.com/priesthood)" in line


def test_straight_roundtrip_of_structure():
    out, _ = deseret.convert_document(DOC)
    assert out.count("\n") == DOC.count("\n")
