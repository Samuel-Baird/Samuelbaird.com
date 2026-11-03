"""PDF drawing primitives. A Page works in 'logical' units: the design is 612 units wide and the
page is scaled uniformly to the target width, so every poster size is the same design at a
different scale. y values are measured from the top of the page, as in the reference geometry."""
import unicodedata

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from . import fonts
from .fonts import runs, text_width
from .layout import Seg

BASE_W = 612.0
SKEW = 0.2          # synthetic italic for faces that have none (Deseret, Armenian, Georgian, ...)


def _rtl_word(text):
    return any(unicodedata.bidirectional(ch) in ("R", "AL") for ch in text)


def _ltr_word(text):
    return not _rtl_word(text) and any(unicodedata.bidirectional(ch) in ("L", "EN", "AN") for ch in text)


def visual_order(words):
    """Placement order for a right-to-left line, whose positions advance leftwards: the words in reading order,
    except that a run of left-to-right words (a Latin name, a number) is reversed so it still reads left to right."""
    out, run = [], []
    for i, w in enumerate(words):
        if _ltr_word("".join(sg.text for sg in w.segs)):
            run.append(i)
        else:
            out += run[::-1] + [i]
            run = []
    return out + run[::-1]


class Page:
    def __init__(self, path, width, height, meta=None, rtl=False):
        fonts.register()
        self.rtl = rtl                     # mirror the whole design for right-to-left scripts
        self._forms = {}
        self.k = width / BASE_W
        self.W = BASE_W
        self.H = height / self.k           # logical height
        self.c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1, invariant=1)
        if meta:
            self.c.setTitle(meta.get("title", ""))
            self.c.setAuthor(meta.get("author", ""))
            self.c.setSubject(meta.get("subject", ""))
            self.c.setCreator("Urim proclamations generator")
        self.c.scale(self.k, self.k)

    def Y(self, t):
        return self.H - t

    # ---- vector
    def _stroke(self, color, width):
        self.c.setStrokeColorRGB(*color)
        self.c.setLineWidth(width)

    def X(self, x):
        return self.W - x if self.rtl else x

    def hrule(self, t, x0, x1, width, color):
        self._stroke(color, width)
        self.c.line(self.X(x0), self.Y(t), self.X(x1), self.Y(t))

    def vrule(self, x, t0, t1, width, color):
        self._stroke(color, width)
        self.c.line(self.X(x), self.Y(t0), self.X(x), self.Y(t1))

    def frame(self, x0, t0, x1, t1, width, color):
        self._stroke(color, width)
        a, b = sorted((self.X(x0), self.X(x1)))
        self.c.rect(a, self.Y(t1), b - a, t1 - t0, stroke=1, fill=0)

    def mask(self, x0, t0, x1, t1, color=(1, 1, 1)):
        """Filled rectangle, used to cut a gap in a rule exactly as the printed originals do."""
        self.c.setFillColorRGB(*color)
        a, b = sorted((self.X(x0), self.X(x1)))
        self.c.rect(a, self.Y(t1), b - a, t1 - t0, stroke=0, fill=1)

    def path(self, ops, width, color):
        """ops: list of ('M', x, t) / ('C', x1,t1,x2,t2,x3,t3) in top-based coordinates."""
        self._stroke(color, width)
        p = self.c.beginPath()
        for op in ops:
            if op[0] == "M":
                p.moveTo(self.X(op[1]), self.Y(op[2]))
            else:
                p.curveTo(self.X(op[1]), self.Y(op[2]), self.X(op[3]), self.Y(op[4]), self.X(op[5]), self.Y(op[6]))
        self.c.drawPath(p, stroke=1, fill=0)

    # ---- text
    def seg(self, x, t, s):
        """Draw one Seg whose logical start is x (the left edge, or the right edge on a mirrored page),
        with its baseline at top-offset t. Returns the advance."""
        c = self.c
        parts = runs(s.text, s.style)
        widths = [fonts.shaped_width(f, txt, s.size) if fonts.is_shaped(f)
                  else text_width(txt, s.size, s.style, s.track) for f, _i, _b, txt in parts]
        done = 0.0
        for (font, syn_italic, syn_bold, txt), w in zip(parts, widths):
            left = self.W - x - done - w if self.rtl else x + done
            if fonts.is_shaped(font):
                self._shaped(font, txt, left, t, s, w)
            else:
                c.saveState()
                tx = c.beginText()
                tx.setFont(font, s.size)
                skew = SKEW if syn_italic else 0.0
                tx.setTextTransform(1, 0, skew, 1, left, self.Y(t))
                if s.track:
                    tx.setCharSpace(s.track)
                if s.mode == "open":
                    tx.setTextRenderMode(2)
                    c.setFillColorRGB(*s.color)
                    c.setStrokeColorRGB(*(s.stroke or s.color))
                    c.setLineWidth(s.stroke_w or 0.5)
                elif syn_bold:
                    tx.setTextRenderMode(2)         # no bold face: thicken with a hairline stroke
                    c.setFillColorRGB(*s.color)
                    c.setStrokeColorRGB(*s.color)
                    c.setLineWidth(s.size * 0.035)
                else:
                    c.setFillColorRGB(*s.color)
                tx.textOut(txt)
                c.drawText(tx)
                c.restoreState()
            done += w
        return done

    def _form(self, font, gid, filled_and_stroked):
        """A glyph outline as a reusable form XObject (defined once per document, placed many times)."""
        key = (font, gid, filled_and_stroked)
        if key not in self._forms:
            name = f"G{len(self._forms)}"
            c = self.c
            c.beginForm(name, -3000, -3000, 6000, 4000)
            p = c.beginPath()
            for op in fonts.glyph_path(font, gid):
                if op[0] == "M":
                    p.moveTo(*op[1])
                elif op[0] == "L":
                    p.lineTo(*op[1])
                elif op[0] == "C":
                    p.curveTo(*op[1], *op[2], *op[3])
                else:
                    p.close()
            c.drawPath(p, stroke=1 if filled_and_stroked else 0, fill=1)
            c.endForm()
            self._forms[key] = name
        return self._forms[key]

    def _shaped(self, font, txt, left, t, s, width):
        """Shaped text (Arabic, Indic, Thai, ...): glyph outlines at the positions HarfBuzz computed, plus an
        invisible text layer stretched to the same width, so the PDF can be searched and copied."""
        c = self.c
        gids, adv, xo, yo, upem = fonts.shape(font, txt)
        sc = s.size / upem
        openm = s.mode == "open"
        c.saveState()
        tx = c.beginText()
        tx.setFont(font, s.size)
        tx.setTextRenderMode(3)
        plain = pdfmetrics.stringWidth(txt, font, s.size)
        if plain > 0:
            tx.setHorizScale(100.0 * width / plain)
        tx.setTextOrigin(left, self.Y(t))
        tx.textOut(fonts.visual_text(txt) if fonts.is_rtl(font) else txt)
        c.drawText(tx)
        c.restoreState()
        c.saveState()
        c.setFillColorRGB(*s.color)
        c.setStrokeColorRGB(*(s.stroke or s.color))
        x = left
        for gid, a, dx, dy in zip(gids, adv, xo, yo):
            if fonts.glyph_path(font, gid):
                name = self._form(font, gid, openm)
                c.saveState()
                c.transform(sc, 0, 0, sc, x + dx * sc, self.Y(t) + dy * sc)
                if openm:
                    c.setLineWidth((s.stroke_w or 0.5) / sc)
                c.doForm(name)
                c.restoreState()
            x += a * sc
        c.restoreState()

    def segs(self, x, t, segs):
        for s in segs:
            x += self.seg(x, t, s)
        return x

    def width(self, segs):
        return sum(s.width for s in segs)

    def centered(self, cx, t, segs):
        self.segs(cx - self.width(segs) / 2, t, segs)

    def right(self, rx, t, segs):
        self.segs(rx - self.width(segs), t, segs)

    # ---- lines of body text
    def place_lines(self, lines, col_left, first_baseline, stretch=1.0):
        """Draw one column. Spaces are stretched (or squeezed) so non-final lines fill the measure; in scripts
        written without spaces the slack is spread between the characters instead."""
        t = first_baseline
        for i, ln in enumerate(lines):
            if i:
                t += (ln.leading + (ln.gap_before if ln.first else 0.0)) * stretch
            last_seg = ln.words[-1].segs[-1]
            hy_w = text_width("-", last_seg.size, last_seg.style) if ln.hyphen else 0.0
            words_w = sum(w.width for w in ln.words) + hy_w
            gaps = sum(1 for k, w in enumerate(ln.words) if k and not w.cont)
            x = col_left + ln.x_off
            order = list(range(len(ln.words)))
            if self.rtl:
                order = visual_order(ln.words)
            seq = [ln.words[k] for k in order]
            space = fonts.space_width(last_seg.size)
            fill = ln.justify and (not ln.last or ln.natural > ln.avail + 1e-6)
            extra = 0.0                                   # added to every boundary (per-character justification)
            if ln.chars and fill and len(seq) > 1:
                extra = (ln.avail - ln.natural) / (len(seq) - 1)
                gap = space
            elif gaps and fill:
                gap = (ln.avail - words_w) / gaps
            else:
                gap = space
            for wi, w in enumerate(seq):
                for s in w.segs:
                    x += self.seg(x, t, s)
                if wi == len(seq) - 1:
                    if ln.hyphen:
                        x += self.seg(x, t, Seg("-", last_seg.size, last_seg.style, last_seg.color))
                elif not seq[wi + 1].cont:
                    # a real (invisible) space glyph, so extracted/searched/read-aloud text keeps its word breaks
                    self.seg(x, t, Seg(" ", w.segs[-1].size, color=w.segs[-1].color))
                    x += gap + extra
                else:
                    x += extra
        return t

    def finish(self):
        self.c.showPage()
        self.c.save()
