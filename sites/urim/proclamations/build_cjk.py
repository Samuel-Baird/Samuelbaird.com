"""Build the small CJK faces in fonts/ from the full Noto Serif CJK OpenType files.

    python -m proclamations.build_cjk <dir with NotoSerif{SC,TC,JP,KR}-{Regular,Bold}.otf>

The full faces are 6 to 12 MB each (https://github.com/notofonts/noto-cjk, Serif/SubsetOTF). Each is cut down
to the characters used by that language's proclamation texts plus ASCII and CJK punctuation, then converted from
CFF to TrueType outlines so ReportLab can embed it. Re-run after fetching new texts for these languages;
a character missing from the subset is reported by `python -m proclamations.register`.
"""
import glob
import sys
import unicodedata
from pathlib import Path

import yaml
from fontTools import subset
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
LANGS = {"SC": ["zhs"], "TC": ["zho", "yue"], "JP": ["jpn"], "KR": ["kor"]}
EXTRA = (set(chr(c) for c in range(0x20, 0x7F)) | set(chr(c) for c in range(0x3000, 0x3040))
         | set(chr(c) for c in range(0xFF01, 0xFF5F)) | set("‐–—‘’“”…· "))


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


def used_chars(codes):
    chars = set(EXTRA)
    for code in codes:
        for f in glob.glob(str(HERE / "texts" / code / "*.yaml")):
            for t in strings(yaml.safe_load(open(f, encoding="utf-8"))):
                chars |= set(unicodedata.normalize("NFC", t))
    return chars


def otf_to_ttf(font, max_err=1.0):
    """CFF -> TrueType outlines (fontTools' otf2ttf snippet)."""
    order = font.getGlyphOrder()
    gs = font.getGlyphSet()
    glyphs = {}
    for name in order:
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, max_err, reverse_direction=True))
        glyphs[name] = pen.glyph()
    font["loca"] = newTable("loca")
    font["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder, glyf.glyphs = order, glyphs
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    for g in glyphs.values():
        if g.numberOfContours != 0:
            g.recalcBounds(glyf)
    glyf.compile(font)
    hmtx = font["hmtx"]
    for name, g in glyf.glyphs.items():
        if hasattr(g, "xMin"):
            hmtx[name] = (hmtx[name][0], g.xMin)
    font["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    maxp.maxZones, maxp.maxTwilightPoints, maxp.maxStorage = 1, 0, 0
    maxp.maxFunctionDefs = maxp.maxInstructionDefs = maxp.maxStackElements = maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = max(len(getattr(g, "components", [])) for g in glyf.glyphs.values())
    maxp.maxPoints = maxp.maxContours = maxp.maxCompositePoints = maxp.maxCompositeContours = 0
    maxp.maxComponentDepth = maxp.maxZones - 1 + 0
    maxp.numGlyphs = len(order)           # the real maxima are recalculated when the font is saved
    post = font["post"]
    post.formatType, post.extraNames, post.mapping, post.glyphOrder = 2.0, [], {}, order
    font.sfntVersion = "\x00\x01\x00\x00"


def main(argv):
    src = Path(argv[0])
    for region, codes in LANGS.items():
        chars = used_chars(codes)
        for weight in ("Regular", "Bold"):
            name = f"NotoSerif{region}-{weight}"
            opts = subset.Options()
            opts.layout_features = ["kern", "vert", "locl"]
            opts.name_IDs = ["*"]
            opts.notdef_outline = True
            font = subset.load_font(str(src / f"{name}.otf"), opts)
            sub = subset.Subsetter(opts)
            sub.populate(text="".join(sorted(chars)))
            sub.subset(font)
            otf_to_ttf(font)
            out = FONTS / f"{name}.ttf"
            font.save(str(out))
            print(f"{name}: {len(chars)} characters, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
