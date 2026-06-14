"""Tier 3: PyPDF2 extraction — universal fallback for any PDF.

Produces flat .txt. Tables are destroyed. Use only when Tier 1 (.docx)
and Tier 2 (Docling) are unavailable.
"""

from pathlib import Path

from PyPDF2 import PdfReader


def extract(pdf_path: Path, output_dir: Path | None = None) -> Path:
    """Extract text from any PDF via PyPDF2. Returns txt_path."""
    stem = pdf_path.stem
    out = output_dir or pdf_path.parent
    txt_path = out / f"{stem}.txt"

    if txt_path.exists():
        return txt_path

    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    txt_path.write_text(text, encoding="utf-8")

    print(f"  {stem}: {len(reader.pages)}p -> {txt_path.name} ({len(text)//1024} KB)")
    return txt_path
