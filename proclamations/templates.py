"""One template per proclamation, modelled on the Church's own PDFs.

Geometry (in a 612 x 792 design page, y from the top) was measured from the originals; see
reference.py. A template draws the fixed header, builds the body paragraphs, lets layout.fit
choose the largest type size that fills the page's height, and draws the footer. Pages taller
than the design (every poster size is) keep the header and footer proportions and give the
extra height to the text block.
"""
from dataclasses import dataclass, field

from .fonts import CAP_HEIGHT, text_width, to_caps
from .layout import Para, Seg, Word, balanced_lines, fit, small_caps_word, word
from .render import Page

H0 = 792.0
INK = (35 / 255, 31 / 255, 32 / 255)
MAROON = (130 / 255, 0, 36 / 255)
BROWN = (116 / 255, 71 / 255, 57 / 255)
GOLD = (189 / 255, 156 / 255, 105 / 255)
GRAY_FILL = (166 / 255, 168 / 255, 171 / 255)
CREDIT = (0.45, 0.45, 0.45)

# Words per printed line for headings. Counts survive a word-for-word conversion (Deseret reuses "en");
# Spanish has its own because its phrases are longer.
BREAKS = {
    "en": {
        "family": {"subtitle": [2, 3], "author": [9, 9]},
        "restoration": {"title": [5, 6], "author": [9, 9]},
        "living-christ": {"subtitle": [5], "author": [8]},
        "articles-of-faith": {"title": [2, 2], "subtitle": [8]},
    },
    "es": {
        "family": {"subtitle": [2, 3], "author": [10, 12]},
        "restoration": {"title": [5, 4], "author": [10, 12]},
        "living-christ": {"subtitle": [5], "author": [11]},
        "articles-of-faith": {"title": [2, 2], "subtitle": [9]},
    },
}
# Small-caps lead-in words of each Family paragraph (the English counts are read from the original PDF;
# the Spanish ones follow the same phrases: "Nosotros, la Primera Presidencia", "Todos los seres humanos", ...)
FAMILY_LEADS = {"en": [4, 3, 4, 3, 2, 3, 2, 2, 3], "es": [4, 4, 4, 3, 2, 5, 2, 2, 3]}


@dataclass
class Loc:
    """A proclamation's text, already converted to the target script."""
    slug: str
    script: object
    title: str
    subtitle: str = ""
    author: str = ""
    paragraphs: list = field(default_factory=list)
    note: str = ""
    verses: list = field(default_factory=list)       # [(number, text)]
    signature: str = ""
    date: str = ""
    groups: list = field(default_factory=list)       # signature group headings
    names: dict = field(default_factory=dict)        # group -> [names]
    credit: str = ""
    lang: str = "en"          # language of the source text (selects heading breaks and lead-ins)


# ------------------------------------------------------------------ helpers
def split_words(text, counts):
    ws, out, i = text.split(), [], 0
    for c in counts:
        out.append(" ".join(ws[i:i + c]))
        i += c
    if i < len(ws):
        out[-1] += " " + " ".join(ws[i:])
    return out


def fit_size(text, size, max_w, style="r", track=0.0):
    w = text_width(text, size, style, track)
    return size if w <= max_w else size * max_w / w


def sc_segs(text, big, small, color, first_big=True):
    """Small-caps line: each word's initial capital at `big`, the rest as capitals at `small`."""
    segs = []
    for i, w in enumerate(text.split()):
        if i:
            segs.append(Seg(" ", small, color=color))
        segs.extend(small_caps_word(w, big, small, color, first_big=first_big).segs)
    return segs


def lead_word(w, big, small, color=INK):
    return small_caps_word(w, big, small, color, first_big=True)


def body(pg, spec, build, delta_last=0.0):
    """Fit the paragraphs into two columns and draw them. Returns (scale, line_stretch, columns)."""
    last = spec["last"] + (pg.H - H0) + delta_last
    cap = last - spec["first"]
    s, (c1, c2, h1, h2) = fit(build, spec["col_w"], lambda s: cap)
    stretch = min(1.10, cap / max(h1, h2)) if max(h1, h2) > 0 else 1.0
    pg.place_lines(c1, spec["left"], spec["first"], stretch)
    pg.place_lines(c2, spec["left2"], spec["first"], stretch)
    return s, stretch, (c1, c2)


def dropcap(pg, ch, size, color, x, baseline, style="r"):
    pg.seg(x, baseline, Seg(ch, size, style, color))


def dc_size(lines, lead, size):
    """Font size whose capital height spans `lines` lines of body text."""
    return ((lines - 1) * lead + CAP_HEIGHT * size) / CAP_HEIGHT


def centered_note(pg, text, baseline, size, color, max_w, leading, style="i"):
    for i, line in enumerate(balanced_lines(text, size, style, max_w, 2)):
        pg.centered(306, baseline + i * leading, [Seg(line, size, style, color)])


def credit(pg, L):
    """Small unofficial-edition line in the bottom margin, below the design's own frame and rules."""
    size = fit_size(L.credit, 4.6, 560)
    pg.centered(306, pg.H - 10, [Seg(L.credit, size, "r", CREDIT)])


# ------------------------------------------------------------------ The Family (1995)
def family(pg, L):
    d = pg.H - H0
    S = L.script
    pg.hrule(45, 54, 558, 2.5, MAROON)
    title = S.caps(L.title)
    ts = fit_size(title, 45.5, 330)
    pg.centered(306, 90, [Seg(title, ts, color=GRAY_FILL, mode="open", stroke=MAROON, stroke_w=0.9)])
    pg.hrule(102.5, 102.9, 506, 0.5, INK)
    pg.hrule(102.7, 165, 441.8, 2.5, MAROON)
    for i, line in enumerate(split_words(S.caps(L.subtitle), BREAKS[L.lang]["family"]["subtitle"])):
        ls = fit_size(line, 28, 300)
        pg.centered(306, 134 + i * 30, [Seg(line, ls, color=(0.92, 0.85, 0.87), mode="open", stroke=MAROON, stroke_w=0.8)])
    for i, line in enumerate(split_words(L.author, BREAKS[L.lang]["family"]["author"])):
        segs = sc_segs(line, 15, 12.2, INK)
        sc = 1.0 if pg.width(segs) <= 470 else 470 / pg.width(segs)
        if sc != 1.0:
            segs = sc_segs(line, 15 * sc, 12.2 * sc, INK)
        pg.centered(306, 191 + i * 16, segs)

    spec = dict(left=54, left2=320, col_w=238, first=231.0, last=676.0)
    pg.vrule(306, 226.4, 678.4 + d, 0.5, INK)

    def build(s):
        size, lead, gap = 9 * s, 12.5 * s, 6.2 * s
        paras = []
        for i, text in enumerate(L.paragraphs):
            toks, n = text.split(" "), FAMILY_LEADS[L.lang][i]
            words = []
            if i == 0:
                first = toks[0][1:]
                words.append(small_caps_word(first, 7 * s, 7.2 * s, INK, first_big=False)) if first else None
            for j, t in enumerate(toks):
                if i == 0 and j == 0:
                    continue
                if j < n:
                    words.append(small_caps_word(t, 12.4 * s, 7.2 * s, INK, first_big=(j == 0)))
                else:
                    words.append(word(t, size, color=INK))
            p = Para(words, size, lead, gap_before=gap)
            if i == 0:
                dcs = dc_size(3, lead, size)
                p.dropcap_lines, p.dropcap_w = 3, text_width(toks[0][0], dcs) + 3 * s
                p.tag = toks[0][0]
            paras.append(p)
        return paras

    s, st, (c1, c2) = body(pg, spec, build)
    lead = 12.5 * s * st
    dcs = dc_size(3, 12.5 * s, 9 * s)
    dropcap(pg, L.paragraphs[0][0], dcs, MAROON, 54, 231.0 + 2 * lead)
    centered_note(pg, L.note, 705 + d, 9, INK, 470, 13)
    pg.hrule(738 + d, 54, 558, 0.5, INK)


# ------------------------------------------------------------------ The Living Christ (2000)
def living_christ(pg, L):
    d = pg.H - H0
    S = L.script
    pg.frame(36, 36, 576, 756 + d, 0.25, INK)
    title = S.caps(L.title)
    pg.centered(306, 82, [Seg(title, fit_size(title, 36, 400), color=BROWN)])
    pg.centered(306, 100, sc_segs(L.subtitle, 16, 12, INK))
    pg.centered(306, 114.5, sc_segs(L.author, 12, 9, INK))

    spec = dict(left=63, left2=312, col_w=237, first=134.0, last=619.0)
    pg.vrule(306, 125.5, 622 + d, 0.25, INK)

    s, st, _ = body(pg, spec, _lc_build(L))
    lead = 14.0 * s * st
    dcs = dc_size(4, 14.0 * s, 10.7 * s)
    dropcap(pg, L.paragraphs[0][0], dcs, BROWN, 65, 134.0 + 3 * lead)

    # signatures: the originals carry facsimile signatures; here the signers' names are typeset instead
    g1, g2 = (L.groups + ["", ""])[:2]
    for x, g in ((64, g1), (236, g2)):
        pg.segs(x, 647 + d, [Seg(S.caps(g), 9, "b", INK)])
    for i, n in enumerate(L.names.get(0, [])):
        pg.segs(64, 668 + d + i * 15.5, [Seg(n, 10.2, color=INK)])
    for i, n in enumerate(L.names.get(1, [])):
        x = 236 if i < 6 else 412
        pg.segs(x, 668 + d + (i % 6) * 15.5, [Seg(n, 10.2, color=INK)])
    pg.segs(64, 738 + d, [Seg(L.date, 9.5, color=INK)])


def _lc_build(L):
    def build(s):
        size, lead = 10.7 * s, 14.0 * s
        paras = []
        for i, text in enumerate(L.paragraphs):
            toks = text.split(" ")
            if i == 0:
                rest = toks[0][1:]
                words = ([word(rest, size, color=INK)] if rest else []) + [word(t, size, color=INK) for t in toks[1:]]
            else:
                words = [word(t, size, color=INK) for t in toks]
            p = Para(words, size, lead, indent_first=0 if i == 0 else 12 * s)
            if i == 0:
                dcs = dc_size(4, lead, size)
                p.dropcap_lines, p.dropcap_w = 4, text_width(toks[0][0], dcs) + 2 * s
            paras.append(p)
        return paras
    return build


# ------------------------------------------------------------------ The Restoration (2020)
def restoration(pg, L):
    d = pg.H - H0
    S = L.script
    pg.frame(21.6, 21.6, 589.5, 769.5 + d, 0.5, INK)
    for i, line in enumerate(split_words(S.caps(L.title), BREAKS[L.lang]["restoration"]["title"])):
        pg.centered(306, 66 + i * 27, [Seg(line, fit_size(line, 22.5, 470), color=INK)])
    pg.hrule(103.8, 77.6, 533.6, 0.35, INK)
    pg.hrule(121.1, 77.6, 534.6, 0.35, INK)
    sub = S.caps(L.subtitle)
    track = 3.2
    ss = fit_size(sub, 13, 440, track=track)
    pg.centered(306, 116.5, [Seg(sub, ss, color=INK, track=track)])
    for i, line in enumerate(split_words(L.author, BREAKS[L.lang]["restoration"]["author"])):
        segs = sc_segs(line, 13, 10.4, INK)
        if pg.width(segs) > 470:
            sc = 470 / pg.width(segs)
            segs = sc_segs(line, 13 * sc, 10.4 * sc, INK)
        pg.centered(306, 142 + i * 15.5, segs)

    spec = dict(left=60, left2=324, col_w=229, first=188.0, last=709.0)
    pg.vrule(305.6, 182, 712.8 + d, 0.35, INK)

    def build(s):
        size, lead, gap = 9.3 * s, 15.0 * s, 3.0 * s
        paras = []
        for i, text in enumerate(L.paragraphs):
            toks = text.split(" ")
            if i == 0:
                rest = toks[0][1:]
                words = ([word(rest, size, color=INK)] if rest else []) + [word(t, size, color=INK) for t in toks[1:]]
            else:
                words = [word(t, size, color=INK) for t in toks]
            p = Para(words, size, lead, gap_before=gap)
            if i == 0:
                dcs = dc_size(3, lead, size)
                p.dropcap_lines, p.dropcap_w = 3, text_width(toks[0][0], dcs) + 3 * s
            paras.append(p)
        return paras

    s, st, _ = body(pg, spec, build)
    lead = 15.0 * s * st
    dropcap(pg, L.paragraphs[0][0], dc_size(3, 15.0 * s, 9.3 * s), INK, 60, 188.0 + 2 * lead)
    centered_note(pg, L.note, 735 + d, 8.5, INK, 400, 11.5)


# ------------------------------------------------------------------ The Articles of Faith
def articles_of_faith(pg, L):
    d = pg.H - H0
    S = L.script
    pg.hrule(44.6, 54, 558, 1.0, GOLD)
    for i, line in enumerate(split_words(S.caps(L.title), BREAKS[L.lang]["articles-of-faith"]["title"])):
        pg.centered(306, 105 + i * 42, [Seg(line, fit_size(line, 42.8, 380), color=MAROON)])
    segs = sc_segs(L.subtitle, 15, 12.5, MAROON)
    if pg.width(segs) > 470:
        sc = 470 / pg.width(segs)
        segs = sc_segs(L.subtitle, 15 * sc, 12.5 * sc, MAROON)
    pg.centered(306, 175, segs)
    # ornamental rule: two hairlines with a small flourish between
    pg.hrule(197.9, 150.9, 458.7, 0.5, MAROON)
    pg.mask(279.0, 189.1, 331.1, 215.1)
    pg.path([("M", 283, 198.4), ("C", 291, 191.5, 299, 191.5, 305, 197.2), ("C", 308, 200, 312, 200.2, 315, 197.6),
             ("C", 320, 193.5, 327, 194, 329, 198.4)], 0.7, MAROON)
    pg.path([("M", 285, 199.2), ("C", 293, 203.4, 301, 203.6, 306, 199.6)], 0.5, MAROON)

    spec = dict(left=54, left2=318, col_w=240, first=242.0, last=676.0)
    pg.vrule(306, 229.5, 729.9 + d, 0.5, GOLD)

    def build(s):
        size, lead, gap = 12 * s, 15.5 * s, 10.2 * s
        paras = []
        for i, (n, text) in enumerate(L.verses):
            toks = text.split(" ")
            if i == 0:
                rest = toks[0][1:]
                words = [small_caps_word(rest, 0.86 * size, 0.86 * size, INK, first_big=False)] if rest else []
                for j, t in enumerate(toks[1:], start=1):
                    words.append(small_caps_word(t, 0.86 * size, 0.86 * size, INK, first_big=False) if j < 4 else word(t, size, color=INK))
            else:
                words = [Word([Seg(f"{n} ", 18 * s, color=(0, 0, 0))])] + [word(t, size, color=INK) for t in toks]
            p = Para(words, size, lead, gap_before=gap)
            if i == 0:
                dcs = 59.4 * s * 0.78
                p.dropcap_lines, p.dropcap_w = 2, text_width(toks[0][0], dcs) + 3 * s
            paras.append(p)
        return paras

    s, st, _ = body(pg, spec, build)
    lead = 15.5 * s * st
    dropcap(pg, L.verses[0][1][0], 59.4 * s * 0.78, MAROON, 54, 242.0 + lead)
    pg.right(558, 702 + d, sc_segs(L.signature.rstrip("."), 13.3, 10.6, INK) + [Seg(".", 10.6, color=INK)])
    pg.hrule(749.9 + d, 54, 558, 0.5, GOLD)


TEMPLATES = {"family": family, "living-christ": living_christ, "restoration": restoration,
             "articles-of-faith": articles_of_faith}
