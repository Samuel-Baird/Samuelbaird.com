"""Build pipeline/reference.docx: the Word styles pandoc uses for every assignment.

    python make_reference_docx.py

Styles: Normal (Calibri 11), headings in navy, "AI Statement" (shaded box), "Hand Calc"
(light green engineering-paper shading), "Calc Note" (small grey), bordered tables.
"""
import subprocess
from pathlib import Path

import pypandoc
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches

HERE = Path(__file__).parent
OUT = HERE / "reference.docx"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)


def shade(pf_el, fill, border):
    ppr = pf_el.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)
    bdr = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "8")
        b.set(qn("w:space"), "4")
        b.set(qn("w:color"), border)
        bdr.append(b)
    ppr.append(bdr)


def para_style(doc, name, base="Normal"):
    st = doc.styles
    s = st[name] if name in [x.name for x in st] else st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = st[base]
    return s


def main():
    # Start from pandoc's own reference.docx so every style it expects exists.
    data = subprocess.run([pypandoc.get_pandoc_path(), "--print-default-data-file", "reference.docx"],
                          capture_output=True, check=True).stdout
    OUT.write_bytes(data)
    doc = Document(str(OUT))
    st = doc.styles
    normal = st["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    for name in ("Body Text", "First Paragraph", "Compact"):
        if name in [x.name for x in st]:
            st[name].font.name = "Calibri"
            st[name].font.size = Pt(11)
            st[name].paragraph_format.space_after = Pt(4)
    for name, size in (("Title", 20), ("Subtitle", 12), ("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 11.5)):
        s = st[name]
        s.font.name = "Calibri"
        s.font.size = Pt(size)
        s.font.color.rgb = NAVY if name != "Subtitle" else RGBColor(0x33, 0x33, 0x33)
        s.font.bold = name != "Subtitle"
    ai = para_style(doc, "AI Statement")
    ai.font.size = Pt(10)
    ai.paragraph_format.space_before = Pt(6)
    ai.paragraph_format.space_after = Pt(10)
    shade(ai.element, "FFF7ED", "B45309")
    hc = para_style(doc, "Hand Calc")
    hc.paragraph_format.left_indent = Inches(0.1)
    hc.paragraph_format.space_after = Pt(2)
    hc.paragraph_format.keep_together = True
    shade(hc.element, "F3FAF1", "9FB8A0")
    hcn = para_style(doc, "Calc Note", "Hand Calc")
    hcn.font.size = Pt(9)
    hcn.font.italic = True
    hcn.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)
    hch = para_style(doc, "Calc Title", "Hand Calc")
    hch.font.bold = True
    hch.font.color.rgb = RGBColor(0x2F, 0x5D, 0x33)
    co = para_style(doc, "Callout")
    co.font.size = Pt(10)
    shade(co.element, "F3F6FA", "1F3A5F")
    meta = para_style(doc, "Meta")
    meta.font.size = Pt(9)
    meta.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    for name in ("Image Caption", "Table Caption"):
        if name in [x.name for x in st]:
            st[name].font.size = Pt(9)
            st[name].font.italic = False
            st[name].font.bold = name == "Table Caption"
    # Table style: thin grey grid
    if "Table" in [x.name for x in st]:
        tbl = st["Table"].element
        tblPr = tbl.find(qn("w:tblPr"))
        if tblPr is None:
            tblPr = OxmlElement("w:tblPr")
            tbl.append(tblPr)
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "4")
            b.set(qn("w:color"), "A6B3C4")
            borders.append(b)
        tblPr.append(borders)
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Inches(0.8)
    sec.top_margin = sec.bottom_margin = Inches(0.75)
    doc.save(str(OUT))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
