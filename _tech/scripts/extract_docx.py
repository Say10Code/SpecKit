#!/usr/bin/env python3
"""Extract text (plain + tables) directly from .docx files — no LibreOffice needed.

.docx = ZIP archive of XML. We read word/document.xml, strip tags,
and optionally convert tables to Markdown.

Usage:
  python extract_docx.py                     # extract ALL .docx in Specifications/
  python extract_docx.py <path>              # extract single .docx
  python extract_docx.py --tables            # also extract tables as .md
"""

import re, sys, zipfile
from pathlib import Path

SPECS = Path(r"D:\ObsidianDB\Specifications")
EXTRACTED = Path(r"D:\ObsidianDB\specs-extracted")


def docx_to_plain(zip_path: Path) -> str:
    """Extract plain text from .docx by stripping XML tags."""
    with zipfile.ZipFile(zip_path, "r") as z:
        if "word/document.xml" not in z.namelist():
            raise ValueError(f"No word/document.xml in {zip_path.name}")
        xml = z.read("word/document.xml").decode("utf-8")

    # Replace paragraph/table breaks with newlines before stripping tags
    text = xml
    text = re.sub(r"<w:p\b[^>]*>", "\n", text)        # paragraph start
    text = re.sub(r"<w:tr\b[^>]*>", "\n", text)        # table row start
    text = re.sub(r"<w:tc\b[^>]*>", " | ", text)       # table cell = column separator
    text = re.sub(r"<[^>]+>", "", text)                 # strip all remaining tags
    text = re.sub(r"\n{4,}", "\n\n", text)              # collapse blank lines
    text = re.sub(r" {2,}", " ", text)                  # collapse multiple spaces

    return text.strip()


def docx_tables_to_md(zip_path: Path) -> list[tuple[str, str]]:
    """Extract tables from .docx as Markdown. Returns list of (caption, markdown_table)."""
    with zipfile.ZipFile(zip_path, "r") as z:
        if "word/document.xml" not in z.namelist():
            return []
        xml = z.read("word/document.xml").decode("utf-8")

    tables = []
    # Find all table blocks
    tbl_blocks = re.findall(r"<w:tbl\b.*?</w:tbl>", xml, re.DOTALL)

    for i, tbl in enumerate(tbl_blocks):
        rows = re.findall(r"<w:tr\b.*?</w:tr>", tbl, re.DOTALL)
        if not rows:
            continue

        md_rows = []
        for row in rows:
            cells = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", row)
            cells = [c.strip() for c in cells if c.strip()]
            if cells:
                md_rows.append(cells)

        if len(md_rows) < 2:  # skip single-row tables
            continue

        # Normalize column count
        max_cols = max(len(r) for r in md_rows)
        normalized = []
        for r in md_rows:
            while len(r) < max_cols:
                r.append("")
            normalized.append(r[:max_cols])

        # Build Markdown
        lines = []
        # Header row
        lines.append("| " + " | ".join(normalized[0]) + " |")
        lines.append("|" + "|".join(["---"] * max_cols) + "|")
        for row in normalized[1:]:
            lines.append("| " + " | ".join(row) + " |")

        caption = f"Table {i + 1}"
        tables.append((caption, "\n".join(lines)))

    return tables


def extract_one(docx_path: Path, do_tables: bool = False) -> bool:
    """Extract a single .docx file. Returns True if extracted."""
    try:
        topic = docx_path.relative_to(SPECS).parent.as_posix()
    except ValueError:
        topic = docx_path.parent.name

    out_dir = EXTRACTED / topic
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = docx_path.stem

    # Plain text
    txt_path = out_dir / f"{stem}.txt"
    if not txt_path.exists():
        plain = docx_to_plain(docx_path)
        txt_path.write_text(plain, encoding="utf-8")
        print(f"  TXT: {txt_path.relative_to(EXTRACTED)} ({len(plain) // 1024} KB)")
    else:
        print(f"  TXT: {txt_path.relative_to(EXTRACTED)} (exists, skipped)")

    # Markdown tables
    if do_tables:
        md_path = out_dir / f"{stem}.md"
        if not md_path.exists():
            tables = docx_tables_to_md(docx_path)
            if tables:
                md_text = f"# Tables from {docx_path.name}\n\n"
                for caption, table_md in tables:
                    md_text += f"## {caption}\n\n{table_md}\n\n"
                md_path.write_text(md_text, encoding="utf-8")
                print(f"  MD:  {len(tables)} tables -> {md_path.relative_to(EXTRACTED)}")
            else:
                print(f"  MD:  no tables found")
        else:
            print(f"  MD:  {md_path.relative_to(EXTRACTED)} (exists, skipped)")

    return True


def main():
    do_tables = "--tables" in sys.argv

    if len(sys.argv) >= 2 and not sys.argv[-1].startswith("--"):
        target = Path(sys.argv[-1])
        if target.exists() and target.suffix == ".docx":
            print(f"Extracting: {target.name}")
            extract_one(target, do_tables)
            return
        else:
            print(f"Not a .docx file: {target}")
            sys.exit(1)

    # Batch: all .docx in Specifications/
    docs = sorted(SPECS.rglob("*.docx"))
    print(f"Found {len(docs)} .docx files")
    for i, d in enumerate(docs):
        print(f"[{i + 1}/{len(docs)}] {d.name}")
        try:
            extract_one(d, do_tables)
        except Exception as e:
            print(f"  FAIL: {e}")
    print("Done.")


if __name__ == "__main__":
    main()
