"""Tier 2: Docling extraction with GPU acceleration (RTX 3060).

Converts .pdf → structured .md + provenance .json.
Uses safe settings to avoid std::bad_alloc on pages with complex diagrams.
"""

import json, shutil, tempfile
from pathlib import Path

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode

from .config import DEVICE


def extract(pdf_path: Path, output_dir: Path | None = None) -> tuple[Path, Path]:
    """Extract a PDF via Docling into .md + .json.

    Returns (md_path, json_path).
    """
    stem = pdf_path.stem
    out = output_dir or pdf_path.parent
    md_path = out / f"{stem}.md"
    json_path = out / f"{stem}.json"

    if md_path.exists() and md_path.stat().st_size > 100 and json_path.exists():
        print(f"  SKIP {stem} (already extracted)")
        return md_path, json_path

    pipeline = PdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device=DEVICE),
        images_scale=1.0,                   # safe: prevents OOM on diagrams
        layout_batch_size=2,
        table_batch_size=2,
        generate_picture_images=False,       # safe: prevents bad_alloc in pypdfium2
    )
    opts = PdfFormatOption(pipeline_options=pipeline)
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: opts},
    )

    # Copy to temp dir (Docling can't handle Cyrillic paths)
    tmp = Path(tempfile.gettempdir()) / "docling_speckit"
    tmp.mkdir(exist_ok=True)
    tmp_pdf = tmp / pdf_path.name

    try:
        shutil.copy2(pdf_path, tmp_pdf)
        size_kb = tmp_pdf.stat().st_size // 1024
        print(f"  Processing {stem} ({size_kb} KB)...", end=" ", flush=True)

        result = converter.convert(tmp_pdf)

        result.document.save_as_markdown(md_path, image_mode=ImageRefMode.PLACEHOLDER)
        md_size = md_path.stat().st_size // 1024

        doc_data = result.document.export_to_dict()
        doc_data["source_file"] = str(pdf_path)
        json_path.write_text(json.dumps(doc_data, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        json_size = json_path.stat().st_size // 1024

        pages = getattr(result.input, "page_count", 0) or 0
        print(f"OK: {pages}p, MD={md_size}KB, JSON={json_size}KB")
        return md_path, json_path

    finally:
        if tmp_pdf.exists():
            tmp_pdf.unlink()
