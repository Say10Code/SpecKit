"""Tier 1: Direct .docx extraction — no LibreOffice, no PDF, no GPU.

.docx = ZIP/XML. Reads word/document.xml, strips tags, converts tables to Markdown.
875× faster than LibreOffice→PDF→PyPDF2. Tables preserved. Python stdlib only.
"""

import re, zipfile
from pathlib import Path


def docx_to_text(docx_path: Path) -> str:
    """Extract plain text from .docx by stripping XML tags from word/document.xml."""
    with zipfile.ZipFile(docx_path, "r") as z:
        if "word/document.xml" not in z.namelist():
            raise ValueError(f"No word/document.xml in {docx_path.name}")
        xml = z.read("word/document.xml").decode("utf-8")

    # Replace structural elements with spacing
    text = xml
    text = re.sub(r"<w:p\b[^>]*>", "\n", text)         # paragraph
    text = re.sub(r"<w:tr\b[^>]*>", "\n", text)         # table row
    text = re.sub(r"<w:tc\b[^>]*>", " | ", text)        # table cell → column
    text = re.sub(r"<[^>]+>", "", text)                  # strip all tags
    text = re.sub(r"\n{4,}", "\n\n", text)               # collapse blanks
    text = re.sub(r" {2,}", " ", text)                   # collapse spaces

    return text.strip()


def docx_tables_to_md(docx_path: Path) -> str:
    """Extract all tables from .docx as Markdown."""
    with zipfile.ZipFile(docx_path, "r") as z:
        if "word/document.xml" not in z.namelist():
            return ""
        xml = z.read("word/document.xml").decode("utf-8")

    tbl_blocks = re.findall(r"<w:tbl\b.*?</w:tbl>", xml, re.DOTALL)
    md_parts = []
    table_count = 0

    for tbl in tbl_blocks:
        rows = re.findall(r"<w:tr\b.*?</w:tr>", tbl, re.DOTALL)
        if not rows:
            continue

        md_rows = []
        for row in rows:
            cells = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", row)
            cells = [c.strip() for c in cells if c.strip()]
            if cells:
                md_rows.append(cells)

        if len(md_rows) < 2:
            continue  # skip single-row tables

        table_count += 1
        # Normalize column count
        max_cols = max(len(r) for r in md_rows)
        normalized = []
        for r in md_rows:
            while len(r) < max_cols:
                r.append("")
            normalized.append(r[:max_cols])

        lines = [f"## Table {table_count}"]
        lines.append("")
        lines.append("| " + " | ".join(normalized[0]) + " |")
        lines.append("|" + "|".join(["---"] * max_cols) + "|")
        for row in normalized[1:]:
            lines.append("| " + " | ".join(row) + " |")
        md_parts.append("\n".join(lines))

    return "\n\n".join(md_parts)


def extract(docx_path: Path, output_dir: Path | None = None) -> tuple[Path, Path]:
    """Extract a .docx file into TXT + MD tables.

    Returns (txt_path, md_path).
    """
    stem = docx_path.stem
    out = output_dir or docx_path.parent

    # Plain text
    txt_path = out / f"{stem}.txt"
    if not txt_path.exists():
        plain = docx_to_text(docx_path)
        txt_path.write_text(plain, encoding="utf-8")

    # Markdown tables
    md_path = out / f"{stem}.md"
    if not md_path.exists():
        tables = docx_tables_to_md(docx_path)
        if tables:
            md_text = f"# Tables from {docx_path.name}\n\n{tables}\n"
        else:
            md_text = f"# Tables from {docx_path.name}\n\n(no tables found)\n"
        md_path.write_text(md_text, encoding="utf-8")

    return txt_path, md_path
