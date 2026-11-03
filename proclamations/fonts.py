"""Font registration, per-character font fallback, and text measurement.

Each family is a chain of faces. A character is drawn with the first face in the chain whose cmap has a
glyph for it, so one line can mix scripts (Armenian text with a Latin name, Deseret with digits) without
the template knowing. A face that lacks an italic or bold gets a synthetic one (slant / hairline stroke).
All faces are SIL OFL Noto fonts and are embedded as subsets.

This is simple text layout only: left-to-right, one glyph per character, no contextual shaping. Scripts
that need shaping, right-to-left layout or dictionary line breaking are not handled here (see docs/scripts.md).
"""
from functools import lru_cache
from pathlib import Path

import reportlab.pdfbase.ttfonts as _tt
from fontTools.ttLib import TTFont as _FT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = Path(__file__).resolve().parent / "fonts"
CAP_HEIGHT = 0.714          # capital height / em, the same across these Noto faces

# family -> ordered faces; each face lists the files it has per style (missing styles are synthesized)
FAMILIES = {
    "serif": [
        {"r": "NotoSerif-Regular", "i": "NotoSerif-Italic", "b": "NotoSerif-Bold"},
        {"r": "NotoSerifArmenian-Regular", "b": "NotoSerifArmenian-Bold"},
        {"r": "NotoSerifGeorgian-Regular", "b": "NotoSerifGeorgian-Bold"},
        {"r": "NotoSerifEthiopic-Regular", "b": "NotoSerifEthiopic-Bold"},
        {"r": "NotoSansDeseret-Regular"},
    ],
    "sans": [
        {"r": "NotoSans-Regular", "i": "NotoSans-Italic", "b": "NotoSans-Bold"},
        {"r": "NotoSansDeseret-Regular"},
    ],
}
DSRT = "NotoSansDeseret-Regular"
_family = "sans"
_done = False


def _tounicode(fontname, subset):
    """ReportLab writes non-BMP code points as invalid hex in the ToUnicode CMap, which makes
    extracted/searched text wrong. Emit UTF-16 surrogate pairs instead."""
    def hex16(v):
        if v > 0xFFFF:
            v -= 0x10000
            return "%04X%04X" % (0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF))
        return "%04X" % v
    lines = ["/CIDInit /ProcSet findresource begin", "12 dict begin", "begincmap", "/CIDSystemInfo",
             "<< /Registry (%s)" % fontname, "/Ordering (%s)" % fontname, "/Supplement 0", ">> def",
             "/CMapName /%s def" % fontname, "/CMapType 2 def", "1 begincodespacerange",
             "<00> <%02X>" % (len(subset) - 1), "endcodespacerange", "%d beginbfchar" % len(subset)]
    lines += ["<%02X> <%s>" % (i, hex16(v)) for i, v in enumerate(subset)]
    lines += ["endbfchar", "endcmap", "CMapName currentdict /CMap defineresource pop", "end", "end"]
    return "\n".join(lines)


def register():
    global _done
    if _done:
        return
    _tt.makeToUnicodeCMap = _tounicode
    seen = set()
    for chain in FAMILIES.values():
        for face in chain:
            for name in face.values():
                if name not in seen:
                    seen.add(name)
                    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f"{name}.ttf")))
    _done = True


def set_family(name):
    """Choose the font family ('serif' or 'sans') used for the following text."""
    global _family
    if name not in FAMILIES:
        raise KeyError(name)
    _family = name


@lru_cache(maxsize=None)
def _cmap(regular_name):
    return frozenset(_FT(str(FONT_DIR / f"{regular_name}.ttf")).getBestCmap())


def _face_for(ch, family):
    cp = ord(ch)
    for face in FAMILIES[family]:
        if cp in _cmap(face["r"]):
            return face
    return None


def is_dsrt(ch):
    return 0x10400 <= ord(ch) <= 0x1044F


def pick(ch, style, family=None):
    """(registered font name, synthetic italic, synthetic bold) for one character."""
    family = family or _family
    face = _face_for(ch, family) or FAMILIES[family][0]
    if style in face:
        return face[style], False, False
    return face["r"], style == "i", style == "b"


def runs(text, style="r"):
    """Split into runs drawn with one font: [(font name, synthetic italic, synthetic bold, substring)].
    Spaces stay with the run they follow."""
    out = []
    for ch in text:
        key = pick(ch, style) if ch != " " else (out[-1][:3] if out else pick(" ", style))
        if out and out[-1][:3] == key:
            out[-1][3] += ch
        else:
            out.append([*key, ch])
    return [tuple(r) for r in out]


def missing_chars(text, family=None):
    """Characters of `text` that no face in the family can draw (they would render as empty boxes)."""
    family = family or _family
    return sorted({ch for ch in text if not ch.isspace() and _face_for(ch, family) is None and ch not in "­​‌‍"})


def sanitize(text, family=None):
    """Replace characters the family cannot draw by their compatibility form when that is drawable
    (for example the Roman numeral character U+2160 becomes a plain "I"). Other characters are left alone."""
    import unicodedata
    family = family or _family
    out = []
    for ch in text:
        if ch.isspace() or _face_for(ch, family) is not None:
            out.append(ch)
            continue
        alt = unicodedata.normalize("NFKC", ch)
        out.append(alt if alt != ch and all(_face_for(c, family) is not None for c in alt) else ch)
    return "".join(out)


def text_width(text, size, style="r", track=0.0):
    register()
    w = sum(pdfmetrics.stringWidth(sub, name, size) for name, _i, _b, sub in runs(text, style))
    return w + track * len(text)


def space_width(size):
    register()
    return pdfmetrics.stringWidth(" ", FAMILIES[_family][0]["r"], size)


def to_caps(text):
    """Deseret lowercase -> capital forms (code point minus 0x28); everything else upper-cased."""
    return "".join(chr(ord(c) - 0x28) if 0x10428 <= ord(c) <= 0x1044F else c.upper() for c in text)


def is_upper(ch):
    return 0x10400 <= ord(ch) <= 0x10427 or ch.isupper()
