"""Assignment report builder: blocks -> HTML (server-side KaTeX) -> PDF (headless Chrome).

Every report starts with the AI-use statement the instructor requires. Hand calculations are
written as `step()` blocks: symbolic form, numbers substituted, result. The numbers come from
Python variables, so nothing is typed by hand.

    r = Report("Term Project Part I", "Spar A (I-section)", due="Nov 13, 2026")
    r.h2("Statics"); r.p("Text with inline math $V(x)$.")
    r.step("I", r"\\frac{b h^3}{12}", rf"\\frac{{({b})({h})^3}}{{12}}", I, "mm^4")
    r.img("ansys_out/constant_LC1_td.png", "Total deformation, LC1")
    r.pdf("out/part1_spar_a.pdf")
"""
from __future__ import annotations

import base64
import html
import json
import mimetypes
import re
import subprocess
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STUDENT = "Samuel Baird"
COURSE = "ME 3410 Applied Finite Element Analysis (Fall 2026, Dr. Seibi)"

AI_STATEMENT = (
    "This assignment was completed with AI assistance (Claude, by Anthropic), as permitted by "
    "the instructor provided AI use is stated at the beginning of each assignment. AI drafted "
    "the hand calculations, wrote the Python and PyMechanical scripts that built, meshed and "
    "solved the ANSYS Mechanical 2026 R1 (Student) models, captured the ANSYS screenshots, and "
    "drafted the text. Every number in the hand calculations is computed by script, and the FEA "
    "results are checked against them in the comparison tables. {student} reviewed the work and "
    "is responsible for this submission."
)


def fmt(x: float, sig: int = 4) -> str:
    """Engineering-friendly number formatting for substituted values."""
    if x == 0:
        return "0"
    ax = abs(x)
    if 1e-3 <= ax < 1e5:
        s = f"{x:.{sig}g}"
        return s
    m, e = f"{x:.{sig - 1}e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"


class Report:
    def __init__(self, title: str, subtitle: str = "", due: str = "", student: str = STUDENT,
                 ai_statement: str | None = None):
        self.title, self.subtitle, self.due, self.student = title, subtitle, due, student
        self.ai = (ai_statement or AI_STATEMENT).format(student=student)
        self.blocks: list[str] = []
        self.math: list[dict] = []
        self.n_fig = 0
        self.n_tab = 0

    # ---- math placeholders -------------------------------------------------------------
    def _m(self, tex: str, display=False) -> str:
        self.math.append({"tex": tex, "display": display})
        return f"\x00M{len(self.math) - 1}\x00"

    def _inline(self, text: str) -> str:
        """Escape text, keep $...$ as inline math and **bold**."""
        parts = re.split(r"(\$[^$]+\$)", text)
        out = []
        for part in parts:
            if part.startswith("$") and part.endswith("$") and len(part) > 1:
                out.append(self._m(part[1:-1]))
            else:
                t = html.escape(part)
                t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
                t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
                out.append(t)
        return "".join(out)

    # ---- blocks ------------------------------------------------------------------------
    def h1(self, t):
        self.blocks.append(f"<h1>{self._inline(t)}</h1>")

    def h2(self, t):
        self.blocks.append(f"<h2>{self._inline(t)}</h2>")

    def h3(self, t):
        self.blocks.append(f"<h3>{self._inline(t)}</h3>")

    def p(self, t):
        self.blocks.append(f"<p>{self._inline(t)}</p>")

    def bullets(self, items):
        lis = "".join(f"<li>{self._inline(i)}</li>" for i in items)
        self.blocks.append(f"<ul>{lis}</ul>")

    def eq(self, tex):
        self.blocks.append(f'<div class="eq">{self._m(tex, True)}</div>')

    def step(self, lhs: str, symbolic: str | None, numeric: str | None, value: float | str,
             unit: str = "", note: str = ""):
        """One hand-calculation line: lhs = symbolic = numeric = value unit."""
        val = value if isinstance(value, str) else fmt(value)
        u = rf"\ \mathrm{{{unit}}}" if unit else ""
        chain = [lhs]
        if symbolic:
            chain.append(symbolic)
        if numeric:
            chain.append(numeric)
        tex = " = ".join(chain) + rf" = \boxed{{{val}{u}}}"
        n = f'<span class="note">{self._inline(note)}</span>' if note else ""
        self.blocks.append(f'<div class="step">{self._m(tex, True)}{n}</div>')

    def handcalc(self, title: str):
        """Open a hand-calculation sheet (engineering-paper styling) until end_handcalc()."""
        self.blocks.append(f'<section class="sheet"><div class="sheet-h">{self._inline(title)}</div>')

    def end_handcalc(self):
        self.blocks.append("</section>")

    def table(self, headers, rows, caption="", widths=None, cls=""):
        self.n_tab += 1
        cap = f"<caption>Table {self.n_tab}. {self._inline(caption)}</caption>" if caption else ""
        th = "".join(f"<th>{self._inline(str(h))}</th>" for h in headers)
        trs = []
        for row in rows:
            tds = "".join(f"<td>{self._inline(str(c))}</td>" for c in row)
            trs.append(f"<tr>{tds}</tr>")
        self.blocks.append(f'<table class="{cls}">{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>')
        return self.n_tab

    def img(self, path, caption="", width="100%", border=True):
        self.n_fig += 1
        p = Path(path)
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        data = base64.b64encode(p.read_bytes()).decode()
        cap = f"<figcaption>Figure {self.n_fig}. {self._inline(caption)}</figcaption>" if caption else ""
        b = " bordered" if border else ""
        self.blocks.append(f'<figure class="fig{b}"><img src="data:{mime};base64,{data}" style="width:{width}">{cap}</figure>')
        return self.n_fig

    def img_row(self, items, height="2.6in"):
        """Side-by-side figures: items = [(path, caption), ...]."""
        cells = []
        for path, caption in items:
            self.n_fig += 1
            p = Path(path)
            data = base64.b64encode(p.read_bytes()).decode()
            cells.append(f'<figure class="fig bordered"><img src="data:image/png;base64,{data}" style="height:{height};max-width:100%;object-fit:contain">'
                         f"<figcaption>Figure {self.n_fig}. {self._inline(caption)}</figcaption></figure>")
        self.blocks.append(f'<div class="row">{"".join(cells)}</div>')

    def callout(self, text, kind="note"):
        self.blocks.append(f'<div class="callout {kind}">{self._inline(text)}</div>')

    def pagebreak(self):
        self.blocks.append('<div class="pb"></div>')

    # ---- output ------------------------------------------------------------------------
    def html(self) -> str:
        body = "\n".join(self.blocks)
        rendered = self._render_math()
        body = re.sub("\x00M(\\d+)\x00", lambda m: rendered[int(m.group(1))], body)
        head = re.sub("\x00M(\\d+)\x00", lambda m: rendered[int(m.group(1))], self._header())
        css = (HERE / "report.css").read_text(encoding="utf-8")
        katex_css = (HERE / "node_modules/katex/dist/katex.min.css").read_text(encoding="utf-8")
        fonts = (HERE / "node_modules/katex/dist/fonts").as_uri()
        katex_css = katex_css.replace("url(fonts/", f"url({fonts}/")
        return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(self.title)}</title>"
                f"<style>{katex_css}</style><style>{css}</style></head><body>{head}{body}</body></html>")

    def _header(self) -> str:
        meta = f"{html.escape(self.student)} · {html.escape(COURSE)}"
        due = f" · Due {html.escape(self.due)}" if self.due else ""
        sub = f"<div class='subtitle'>{self._inline(self.subtitle)}</div>" if self.subtitle else ""
        return (f"<header><div class='meta'>{meta}{due} · Prepared {date.today():%b %d, %Y}</div>"
                f"<h1 class='title'>{self._inline(self.title)}</h1>{sub}</header>"
                f"<div class='ai'><b>AI use statement.</b> {self._inline(self.ai)}</div>")

    def _render_math(self):
        if not self.math:
            return []
        res = subprocess.run(["node", str(HERE / "katex_render.cjs")], input=json.dumps(self.math),
                             capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            raise SystemExit("KaTeX failed:\n" + res.stderr)
        return json.loads(res.stdout)

    def pdf(self, out_pdf):
        out_pdf = Path(out_pdf).resolve()
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        html_path = out_pdf.with_suffix(".html")
        html_path.write_text(self.html(), encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", f"--print-to-pdf={out_pdf}",
                        html_path.as_uri()], check=True, capture_output=True)
        return out_pdf
