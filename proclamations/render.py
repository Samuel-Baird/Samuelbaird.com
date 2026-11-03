"""PDF drawing primitives. A Page works in 'logical' units: the design is 612 units wide and the
page is scaled uniformly to the target width, so every poster size is the same design at a
different scale. y values are measured from the top of the page, as in the reference geometry."""
from reportlab.pdfgen import canvas

from . import fonts
from .fonts import DSRT, font_for, is_dsrt, runs, text_width
from .layout import Seg

BASE_W = 612.0
SKEW = 0.2          # synthetic italic for Deseret, which has no italic face


class Page:
    def __init__(self, path, width, height, meta=None):
        fonts.register()
        self.k = width / BASE_W
        self.W = BASE_W
        self.H = height / self.k           # logical height
        self.c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
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

    def hrule(self, t, x0, x1, width, color):
        self._stroke(color, width)
        self.c.line(x0, self.Y(t), x1, self.Y(t))

    def vrule(self, x, t0, t1, width, color):
        self._stroke(color, width)
        self.c.line(x, self.Y(t0), x, self.Y(t1))

    def frame(self, x0, t0, x1, t1, width, color):
        self._stroke(color, width)
        self.c.rect(x0, self.Y(t1), x1 - x0, t1 - t0, stroke=1, fill=0)

    def mask(self, x0, t0, x1, t1, color=(1, 1, 1)):
        """Filled rectangle, used to cut a gap in a rule exactly as the printed originals do."""
        self.c.setFillColorRGB(*color)
        self.c.rect(x0, self.Y(t1), x1 - x0, t1 - t0, stroke=0, fill=1)

    def path(self, ops, width, color):
        """ops: list of ('M', x, t) / ('C', x1,t1,x2,t2,x3,t3) in top-based coordinates."""
        self._stroke(color, width)
        p = self.c.beginPath()
        for op in ops:
            if op[0] == "M":
                p.moveTo(op[1], self.Y(op[2]))
            else:
                p.curveTo(op[1], self.Y(op[2]), op[3], self.Y(op[4]), op[5], self.Y(op[6]))
        self.c.drawPath(p, stroke=1, fill=0)

    # ---- text
    def seg(self, x, t, s):
        """Draw one Seg with its baseline at top-offset t. Returns the advance."""
        c = self.c
        pos = x
        for dsrt, txt in runs(s.text):
            font = font_for(dsrt, s.style)
            w = text_width(txt, s.size, s.style, s.track)
            c.saveState()
            tx = c.beginText()
            tx.setFont(font, s.size)
            skew = SKEW if (s.style == "i" and dsrt) else 0.0
            tx.setTextTransform(1, 0, skew, 1, pos, self.Y(t))
            if s.track:
                tx.setCharSpace(s.track)
            if s.mode == "open":
                tx.setTextRenderMode(2)
                c.setFillColorRGB(*s.color)
                c.setStrokeColorRGB(*(s.stroke or s.color))
                c.setLineWidth(s.stroke_w or 0.5)
            elif s.style == "b" and dsrt:
                tx.setTextRenderMode(2)         # Deseret has no bold face: thicken with a hairline stroke
                c.setFillColorRGB(*s.color)
                c.setStrokeColorRGB(*s.color)
                c.setLineWidth(s.size * 0.035)
            else:
                c.setFillColorRGB(*s.color)
            tx.textOut(txt)
            c.drawText(tx)
            c.restoreState()
            pos += w
        return pos - x

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
        """Draw one column. Spaces are stretched (or squeezed) so non-final lines fill the measure."""
        t = first_baseline
        for i, ln in enumerate(lines):
            if i:
                t += (ln.leading + (ln.gap_before if ln.first else 0.0)) * stretch
            last_seg = ln.words[-1].segs[-1]
            hy_w = text_width("-", last_seg.size, last_seg.style) if ln.hyphen else 0.0
            words_w = sum(w.width for w in ln.words) + hy_w
            gaps = sum(1 for k, w in enumerate(ln.words) if k and not w.cont)
            x = col_left + ln.x_off
            if gaps and (not ln.last or ln.natural > ln.avail + 1e-6):
                gap = (ln.avail - words_w) / gaps
            else:
                gap = fonts.space_width(last_seg.size)
            for wi, w in enumerate(ln.words):
                for s in w.segs:
                    x += self.seg(x, t, s)
                if wi == len(ln.words) - 1:
                    if ln.hyphen:
                        x += self.seg(x, t, Seg("-", last_seg.size, last_seg.style, last_seg.color))
                elif not ln.words[wi + 1].cont:
                    # a real (invisible) space glyph, so extracted/searched/read-aloud text keeps its word breaks
                    self.seg(x, t, Seg(" ", w.segs[-1].size, color=w.segs[-1].color))
                    x += gap
        return t

    def finish(self):
        self.c.showPage()
        self.c.save()
