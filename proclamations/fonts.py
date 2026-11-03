"""Font registration and text measurement.

Noto Sans Deseret covers only the 80 Deseret letters, so digits, quotation marks, dashes and
any word without a Deseret spelling use Noto Sans (same OFL family). Text is split into runs by
script and each run is drawn with the matching font. Both fonts are embedded as subsets.
"""
from pathlib import Path

import reportlab.pdfbase.ttfonts as _tt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = Path(__file__).resolve().parent / "fonts"
DSRT, LAT, LATI, LATB = "NotoSansDeseret", "NotoSans", "NotoSans-Italic", "NotoSans-Bold"
CAP_HEIGHT = 0.714          # Noto Sans Deseret capital height / em
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
    for name, file in ((DSRT, "NotoSansDeseret-Regular.ttf"), (LAT, "NotoSans-Regular.ttf"),
                       (LATI, "NotoSans-Italic.ttf"), (LATB, "NotoSans-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
    _done = True


def is_dsrt(ch):
    return 0x10400 <= ord(ch) <= 0x1044F


def runs(text):
    """Split into (is_deseret, substring). Spaces stay with the run they follow."""
    out = []
    for ch in text:
        d = is_dsrt(ch) if ch != " " else (out[-1][0] if out else False)
        if out and out[-1][0] == d:
            out[-1][1] += ch
        else:
            out.append([d, ch])
    return [(d, s) for d, s in out]


def font_for(dsrt, style):
    if dsrt:
        return DSRT
    return {"i": LATI, "b": LATB}.get(style, LAT)


def text_width(text, size, style="r", track=0.0):
    register()
    w = sum(pdfmetrics.stringWidth(s, font_for(d, style), size) for d, s in runs(text))
    return w + track * len(text)


def space_width(size):
    register()
    return pdfmetrics.stringWidth(" ", DSRT, size)


def to_caps(text):
    """Deseret lowercase -> capital forms (code point minus 0x28); Latin upper-cased."""
    return "".join(chr(ord(c) - 0x28) if 0x10428 <= ord(c) <= 0x1044F else c.upper() for c in text)


def is_upper(ch):
    return 0x10400 <= ord(ch) <= 0x10427 or ch.isupper()
