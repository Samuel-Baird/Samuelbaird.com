"""Font registration, per-character font fallback, and text measurement.

Each family is a chain of faces. A character is drawn with the first face in the chain whose cmap has a
glyph for it, so one line can mix scripts (Armenian text with a Latin name, Deseret with digits) without
the template knowing. A face that lacks an italic or bold gets a synthetic one (slant / hairline stroke).
All faces are SIL OFL Noto fonts and are embedded as subsets.

Scripts that need contextual shaping (Arabic, Indic, Thai, Lao, Khmer, Myanmar) use faces flagged "shape":
their runs are shaped with HarfBuzz and drawn as glyph outlines (render.Page.seg), with an invisible text layer
so the PDF stays searchable. Everything else is drawn as ordinary text. See docs/scripts.md.
"""
import unicodedata
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
# scripts that need shaping: chain key -> (font family file stem, right-to-left)
SHAPED = {
    "arabic": ("NotoNaskhArabic", True), "urdu": ("NotoNastaliqUrdu", True),
    "devanagari": ("NotoSerifDevanagari", False), "bengali": ("NotoSerifBengali", False),
    "gujarati": ("NotoSerifGujarati", False), "tamil": ("NotoSerifTamil", False),
    "telugu": ("NotoSerifTelugu", False), "kannada": ("NotoSerifKannada", False),
    "malayalam": ("NotoSerifMalayalam", False), "sinhala": ("NotoSerifSinhala", False),
    "thai": ("NotoSerifThai", False), "lao": ("NotoSerifLao", False),
    "khmer": ("NotoSerifKhmer", False), "myanmar": ("NotoSerifMyanmar", False),
}
for _key, (_stem, _rtl) in SHAPED.items():
    FAMILIES["serif-" + _key] = [FAMILIES["serif"][0],
                                 {"r": _stem + "-Regular", "b": _stem + "-Bold", "shape": True, "rtl": _rtl}]
# Han and Hangul: subset TrueType faces (fonts/build_cjk.py), drawn as ordinary text
for _key, _stem in {"sc": "NotoSerifSC", "tc": "NotoSerifTC", "jp": "NotoSerifJP", "kr": "NotoSerifKR"}.items():
    FAMILIES["serif-" + _key] = [FAMILIES["serif"][0], {"r": _stem + "-Regular", "b": _stem + "-Bold"}]
DSRT = "NotoSansDeseret-Regular"
_family = "sans"


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


_registered = set()


def _register_family(family):
    _tt.makeToUnicodeCMap = _tounicode
    for face in FAMILIES[family]:
        for key, name in face.items():
            if key in ("r", "i", "b") and name not in _registered:
                _registered.add(name)
                pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f"{name}.ttf")))


def register():
    """Register the faces of the current family with ReportLab (others on demand, since CJK faces are large)."""
    _register_family(_family)


def set_family(name):
    """Choose the font family ('serif', 'sans', 'serif-arabic', ...) used for the following text."""
    global _family
    if name not in FAMILIES:
        raise KeyError(name)
    _family = name
    _register_family(name)


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


def _inherits(ch):
    """Combining marks, joiners and variation selectors are drawn with the face of the character before them."""
    return unicodedata.category(ch) in ("Mn", "Mc", "Me", "Cf")


def runs(text, style="r"):
    """Split into runs drawn with one font: [(font name, synthetic italic, synthetic bold, substring)].
    Spaces and combining marks stay with the run they follow."""
    out = []
    for ch in text:
        if out and (ch == " " or _inherits(ch)):
            key = tuple(out[-1][:3])
        else:
            key = pick(ch, style)
        if out and tuple(out[-1][:3]) == key:
            out[-1][3] += ch
        else:
            out.append([*key, ch])
    return [tuple(r) for r in out]


# ---- shaped faces (Arabic, Indic, Thai, ...): HarfBuzz shaping and glyph outlines
_SHAPE_FACES = {}


def _scan_shaped():
    for chain in FAMILIES.values():
        for face in chain:
            if face.get("shape"):
                for key in ("r", "b"):
                    if key in face:
                        _SHAPE_FACES[face[key]] = face


_scan_shaped()


def is_shaped(font):
    return font in _SHAPE_FACES


def is_rtl(font):
    return bool(_SHAPE_FACES.get(font, {}).get("rtl"))


@lru_cache(maxsize=None)
def _hb_font(name):
    import uharfbuzz as hb
    blob = hb.Blob.from_file_path(str(FONT_DIR / f"{name}.ttf"))
    face = hb.Face(blob)
    return hb.Font(face), face.upem


@lru_cache(maxsize=200000)
def shape(font, text):
    """Shape `text` with `font`: (glyph ids, advances, x offsets, y offsets, units per em) in visual left-to-right order."""
    import uharfbuzz as hb
    f, upem = _hb_font(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = "rtl" if is_rtl(font) else "ltr"
    buf.guess_segment_properties()
    buf.direction = "rtl" if is_rtl(font) else "ltr"
    hb.shape(f, buf, {"kern": True, "liga": True})
    infos, pos = buf.glyph_infos, buf.glyph_positions
    return (tuple(i.codepoint for i in infos), tuple(p.x_advance for p in pos),
            tuple(p.x_offset for p in pos), tuple(p.y_offset for p in pos), upem)


def shaped_width(font, text, size):
    return sum(shape(font, text)[1]) * size / shape(font, text)[4]


_PATHS = {}


def glyph_path(font, gid):
    """Outline of one glyph as [(op, points)] in font units; quadratic curves are converted to cubic."""
    key = (font, gid)
    if key not in _PATHS:
        from fontTools.pens.basePen import BasePen

        class P(BasePen):
            def __init__(self, gs):
                super().__init__(gs)
                self.ops = []

            def _moveTo(self, p):
                self.ops.append(("M", p))

            def _lineTo(self, p):
                self.ops.append(("L", p))

            def _curveToOne(self, a, b, c):
                self.ops.append(("C", a, b, c))

            def _qCurveToOne(self, q, e):
                p0 = self._getCurrentPoint()
                a = (p0[0] + 2 / 3 * (q[0] - p0[0]), p0[1] + 2 / 3 * (q[1] - p0[1]))
                b = (e[0] + 2 / 3 * (q[0] - e[0]), e[1] + 2 / 3 * (q[1] - e[1]))
                self.ops.append(("C", a, b, e))

            def _closePath(self):
                self.ops.append(("Z",))

        gs = _glyphset(font)
        name = gs.glyphOrder[gid] if hasattr(gs, "glyphOrder") else _glyph_order(font)[gid]
        pen = P(gs)
        gs[name].draw(pen)
        _PATHS[key] = pen.ops
    return _PATHS[key]


@lru_cache(maxsize=None)
def _ttfont(font):
    return _FT(str(FONT_DIR / f"{font}.ttf"))


def _glyphset(font):
    return _ttfont(font).getGlyphSet()


def _glyph_order(font):
    return _ttfont(font).getGlyphOrder()


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
    w = sum(shaped_width(name, sub, size) if name in _SHAPE_FACES else pdfmetrics.stringWidth(sub, name, size)
            for name, _i, _b, sub in runs(text, style))
    return w + track * len(text)


def space_width(size):
    register()
    return pdfmetrics.stringWidth(" ", FAMILIES[_family][0]["r"], size)


def to_caps(text):
    """Deseret lowercase -> capital forms (code point minus 0x28); everything else upper-cased."""
    return "".join(chr(ord(c) - 0x28) if 0x10428 <= ord(c) <= 0x1044F else c.upper() for c in text)


def is_upper(ch):
    return 0x10400 <= ord(ch) <= 0x10427 or ch.isupper()


def initial_split(text):
    """(first grapheme cluster, rest): the drop cap is a whole letter with its vowel signs, not one code point."""
    import regex
    m = regex.match(r"\X", text)
    return (m.group(), text[m.end():]) if m else ("", text)


def visual_text(text):
    """Right-to-left text in the order it is drawn (clusters reversed). PDF readers expect the invisible text layer
    of a right-to-left run in visual order, as other PDF writers produce it, and restore reading order themselves."""
    import regex
    return "".join(regex.findall(r"\X", text)[::-1])


def drop_width(text, size, style="r"):
    """Width to reserve beside a drop cap: its advance, or its ink if marks and medials stick out further (Myanmar)."""
    w = text_width(text, size, style)
    for font, _i, _b, sub in runs(text, style):
        if font in _SHAPE_FACES:
            gids, adv, xo, _yo, upem = shape(font, sub)
            x, right = 0.0, 0.0
            for gid, a, dx in zip(gids, adv, xo):
                xs = [pt[0] for op in glyph_path(font, gid) for pt in op[1:]] if gid else []
                if xs:
                    right = max(right, x + dx + max(xs))
                x += a
            w = max(w, right * size / upem)
    return w
