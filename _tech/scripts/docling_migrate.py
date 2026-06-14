"""Batch Docling migration for remaining PDFs → specs-extracted/ MD+JSON.

Processes PDFs that don't yet have Docling MD+JSON output.
Uses GPU acceleration (RTX 3060) with safe settings to avoid OOM.
"""

import json, shutil, sys, tempfile
from pathlib import Path

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode

SPECS = Path(r"D:\ObsidianDB\Specifications")
EXTRACTED = Path(r"D:\ObsidianDB\specs-extracted")


def find_pdfs_without_md():
    """Find PDFs that don't have MD+JSON in specs-extracted."""
    all_pdfs = [
        p for p in sorted(SPECS.rglob("*.pdf"))
        if "!INCOMING" not in str(p) and "!double" not in str(p)
    ]
    need_md = []
    for pdf in all_pdfs:
        stem = pdf.stem
        candidates = list(EXTRACTED.rglob(f"*{stem}*.md"))
        if not candidates:
            need_md.append(pdf)
    return need_md


def main():
    pdfs = find_pdfs_without_md()
    print(f"PDFs without MD: {len(pdfs)}")

    if not pdfs:
        print("All PDFs have MD — nothing to migrate.")
        return

    # Setup Docling with safe GPU settings
    pipeline = PdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device="cuda"),
        images_scale=1.0,
        layout_batch_size=2,
        table_batch_size=2,
        generate_picture_images=False,
    )
    opts = PdfFormatOption(pipeline_options=pipeline)
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: opts},
    )

    tmp = Path(tempfile.gettempdir()) / "docling_migrate"
    tmp.mkdir(exist_ok=True)

    success = 0
    failed = 0

    for i, pdf_path in enumerate(pdfs):
        rel = pdf_path.relative_to(SPECS)
        topic = rel.parts[0] if len(rel.parts) > 1 else "root"
        name = pdf_path.stem

        # Output dir mirrors Specifications/ structure
        out_dir = EXTRACTED / topic
        out_dir.mkdir(parents=True, exist_ok=True)

        md_path = out_dir / f"{name}.md"
        json_path = out_dir / f"{name}.json"

        if md_path.exists() and md_path.stat().st_size > 100:
            print(f"  [{i+1}/{len(pdfs)}] SKIP {rel} (exists)")
            success += 1
            continue

        # Copy to ASCII-safe temp path (Docling can't handle Cyrillic paths)
        tmp_pdf = tmp / pdf_path.name
        try:
            shutil.copy2(pdf_path, tmp_pdf)
            size_kb = tmp_pdf.stat().st_size // 1024
            print(f"  [{i+1}/{len(pdfs)}] {rel} ({size_kb} KB)...", end=" ", flush=True)

            result = converter.convert(tmp_pdf)

            result.document.save_as_markdown(md_path, image_mode=ImageRefMode.PLACEHOLDER)
            md_size = md_path.stat().st_size // 1024

            doc_data = result.document.export_to_dict()
            doc_data["source_file"] = str(pdf_path)
            json_path.write_text(
                json.dumps(doc_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            json_size = json_path.stat().st_size // 1024

            pages = getattr(result.input, "page_count", 0) or 0
            print(f"OK: {pages}p, MD={md_size}KB, JSON={json_size}KB")
            success += 1
        except Exception as exc:
            print(f"FAIL: {exc}")
            failed += 1
        finally:
            if tmp_pdf.exists():
                tmp_pdf.unlink()

    print(f"\nDone. Success: {success}, Failed: {failed}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
