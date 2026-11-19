"""Shared python-docx helpers for the CSA0406 Assignment 2 report.

Everything here is presentation only: page setup, styles, tables, code blocks,
figures, headers/footers, TOC field and small callout boxes.
"""
from __future__ import annotations

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x1B, 0x36, 0x5D)
ACCENT = RGBColor(0x0B, 0x5C, 0x8A)
GREY = RGBColor(0x4A, 0x4A, 0x4A)
LIGHT = "F2F5F9"
CODE_BG = "F7F7F4"
HEAD_BG = "1B365D"
BOX_BG = "EAF1F8"

BODY_FONT = "Calibri"
MONO_FONT = "Consolas"

# A4 (21 cm) minus the 2.4 cm and 2.2 cm margins.
USABLE_CM = 16.3


def fit_widths(widths, total=USABLE_CM):
    """Scale a column-width list so that it cannot overflow the text column."""
    total_width = float(sum(widths))
    if total_width <= total:
        return list(widths)
    return [w * total / total_width for w in widths]


def set_fixed_layout(table) -> None:
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)


# --------------------------------------------------------------------------- #
# low-level xml helpers
# --------------------------------------------------------------------------- #
def _shade(element, fill: str) -> None:
    """Apply a solid background to a paragraph or table cell properties."""
    pr = element.get_or_add_tcPr() if hasattr(element, "get_or_add_tcPr") else element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def shade_paragraph(paragraph, fill: str) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def shade_cell(cell, fill: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_margins(table, top=60, bottom=60, left=90, right=90) -> None:
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for tag, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        node = OxmlElement(f"w:{tag}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tblPr.append(mar)


def set_table_borders(table, color="B9C6D6", size=6) -> None:
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblPr.append(borders)


def repeat_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def keep_row_together(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def add_field(paragraph, instruction: str, placeholder: str = "") -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for node in (begin, instr, sep, text, end):
        run._r.append(node)


def enable_update_fields(doc: Document) -> None:
    """Ask Word to refresh the TOC and page fields when the file is opened."""
    settings = doc.settings.element
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    settings.append(upd)


# --------------------------------------------------------------------------- #
# document and styles
# --------------------------------------------------------------------------- #
def new_document() -> Document:
    doc = Document()

    sect = doc.sections[0]
    sect.page_width = Cm(21.0)
    sect.page_height = Cm(29.7)
    sect.top_margin = Cm(2.2)
    sect.bottom_margin = Cm(2.0)
    sect.left_margin = Cm(2.4)
    sect.right_margin = Cm(2.2)
    sect.header_distance = Cm(1.0)
    sect.footer_distance = Cm(1.0)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing = 1.12
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), BODY_FONT)

    for name, size, color, before, after in (
        ("Heading 1", 17, NAVY, 2, 8),
        ("Heading 2", 13, ACCENT, 12, 4),
        ("Heading 3", 11.5, NAVY, 9, 3),
    ):
        st = styles[name]
        st.font.name = BODY_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.line_spacing = 1.05

    return doc


def add_header_footer(doc: Document, header_text: str, footer_left: str,
                      only_last: bool = False, start_page: int | None = None) -> None:
    sections = doc.sections[-1:] if only_last else doc.sections
    for section in sections:
        if only_last:
            section.header.is_linked_to_previous = False
            section.footer.is_linked_to_previous = False
            if start_page is not None:
                sectPr = section._sectPr
                pg = OxmlElement("w:pgNumType")
                pg.set(qn("w:start"), str(start_page))
                sectPr.append(pg)
        # header
        hp = section.header.paragraphs[0]
        hp.text = ""
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = hp.add_run(header_text)
        run.font.size = Pt(8.5)
        run.font.color.rgb = GREY
        run.font.name = BODY_FONT
        pPr = hp._p.get_or_add_pPr()
        borders = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "4")
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), "B9C6D6")
        borders.append(bottom)
        pPr.append(borders)

        # footer: left label + page x of y
        fp = section.footer.paragraphs[0]
        fp.text = ""
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if footer_left:
            r = fp.add_run(footer_left + "    |    ")
            r.font.size = Pt(8.5)
            r.font.color.rgb = GREY
        r = fp.add_run("Page ")
        r.font.size = Pt(8.5)
        r.font.color.rgb = GREY
        add_field(fp, " PAGE ", "1")
        r = fp.add_run(" of ")
        r.font.size = Pt(8.5)
        r.font.color.rgb = GREY
        add_field(fp, " NUMPAGES ", "1")
        for run in fp.runs:
            run.font.size = Pt(8.5)
            run.font.color.rgb = GREY
            run.font.name = BODY_FONT


def page_break(doc: Document) -> None:
    doc.add_page_break()


# --------------------------------------------------------------------------- #
# content helpers
# --------------------------------------------------------------------------- #
def h1(doc, text, number: str | None = None):
    label = f"{number}  {text}" if number else text
    p = doc.add_heading(label, level=1)
    p.paragraph_format.page_break_before = True
    if number:
        # thin rule under the section heading
        pPr = p._p.get_or_add_pPr()
        borders = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "8")
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), "1B365D")
        borders.append(bottom)
        pPr.append(borders)
    return p


def h2(doc, text):
    return doc.add_heading(text, level=2)


def h3(doc, text):
    return doc.add_heading(text, level=3)


def body(doc, text, space_after=5, italic=False, size=None, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space_after)
    return p


def rich(doc, chunks, space_after=5):
    """chunks = [(text, bold, italic), ...]"""
    p = doc.add_paragraph()
    for text, bold, italic in chunks:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
    p.paragraph_format.space_after = Pt(space_after)
    return p


def bullets(doc, items, numbered=False):
    style = "List Number" if numbered else "List Bullet"
    for item in items:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.7)
        if isinstance(item, tuple):
            run = p.add_run(item[0])
            run.bold = True
            p.add_run(item[1])
        else:
            p.add_run(item)


def data_table(doc, headers, rows, widths=None, font_size=9, header_fill=HEAD_BG,
               align=None, zebra=True):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_fixed_layout(table)
    set_table_borders(table)
    set_cell_margins(table, left=80, right=80)

    hdr = table.rows[0]
    repeat_header(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(str(text))
        run.bold = True
        run.font.size = Pt(font_size)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade_cell(cell, header_fill)

    for r_idx, row in enumerate(rows):
        cells = table.add_row().cells
        keep_row_together(table.rows[-1])
        for i, value in enumerate(row):
            cell = cells[i]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            run = p.add_run(str(value))
            run.font.size = Pt(font_size)
            if align and i < len(align) and align[i] == "c":
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if zebra and r_idx % 2 == 1:
                shade_cell(cell, LIGHT)

    if widths:
        widths = fit_widths(widths)
        for row in table.rows:
            for i, w in enumerate(widths):
                if i < len(row.cells):
                    row.cells[i].width = Cm(w)

    # A small table should never be split across a page boundary: keep its rows
    # together (the last row is left free so the table can end a page).
    if len(rows) <= 5:
        for row in table.rows[:-1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True
    return table


def code_block(doc, code: str, font_size=8.2, max_lines=None):
    lines = code.replace("\t", "    ").rstrip("\n").split("\n")
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines] + ["... (truncated)"]
    # A short listing is kept on one page; a long one is allowed to flow, so
    # that a 120-line program does not push a half-empty page in front of it.
    keep = len(lines) <= 20
    for idx, line in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = 1.0
        pf.left_indent = Cm(0.25)
        pf.keep_with_next = keep and idx < len(lines) - 1
        shade_paragraph(p, CODE_BG)
        run = p.add_run(line if line else " ")
        run.font.name = MONO_FONT
        run.font.size = Pt(font_size)
        rpr = run._r.get_or_add_rPr()
        rfonts = OxmlElement("w:rFonts")
        rfonts.set(qn("w:ascii"), MONO_FONT)
        rfonts.set(qn("w:hAnsi"), MONO_FONT)
        rpr.append(rfonts)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(8.8)
    run.font.color.rgb = GREY
    return p


def figure(doc, path, cap, width_cm=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    caption(doc, cap)


def callout(doc, title, text, fill=BOX_BG):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="9DB4CC", size=6)
    set_cell_margins(table, top=90, bottom=90, left=140, right=140)
    keep_row_together(table.rows[0])
    cell = table.rows[0].cells[0]
    cell.text = ""
    shade_cell(cell, fill)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(9.5)
    run.font.color.rgb = NAVY
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    r2 = p2.add_run(text)
    r2.font.size = Pt(9.2)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_toc(doc, levels="1-2"):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    add_field(p, f'TOC \\o "{levels}" \\h \\z \\u',
              "Table of contents: in Word press Ctrl+A then F9 (or right-click -> Update Field).")


def signature_block(doc, left_label="Student Signature", right_label="Faculty Signature"):
    table = doc.add_table(rows=3, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="B9C6D6")
    for r, h in enumerate((Cm(1.45), Cm(0.6), Cm(0.85))):
        table.rows[r].height = h
        keep_row_together(table.rows[r])
    labels = [left_label, "", right_label]
    for i, label in enumerate(labels):
        cell = table.rows[1].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(label)
        run.bold = True
        run.font.size = Pt(9)
    last = table.rows[2].cells[0].merge(table.rows[2].cells[2])
    last.text = ""
    p = last.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run("Program Director")
    run.bold = True
    run.font.size = Pt(9)
