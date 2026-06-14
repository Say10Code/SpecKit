"""Batch Docling for ETSI_3GPP PDFs — copies to ASCII temp dir to avoid Cyrillic path issues."""
import json, shutil, sys, tempfile
from pathlib import Path

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode

specs_dir = Path(r"D:\ObsidianDB\Specifications\ETSI_3GPP")
output_base = Path(r"D:\ObsidianDB\.3gpp-crawler\wiki\etsi-direct\sources")
output_base.mkdir(parents=True, exist_ok=True)

pdfs = sorted(specs_dir.rglob("*.pdf"))
print(f"Found {len(pdfs)} ETSI PDFs. Output: {output_base}")

pipeline = PdfPipelineOptions(
    accelerator_options=AcceleratorOptions(device="cuda"),
    images_scale=1.0,               # B8 fix: safe default, prevents OOM on diagrams
    layout_batch_size=2,
    table_batch_size=2,
    generate_picture_images=False,   # B8 fix: disable to prevent bad_alloc in pypdfium2
)
opts = PdfFormatOption(pipeline_options=pipeline)
converter = DocumentConverter(
    allowed_formats=[InputFormat.PDF],
    format_options={InputFormat.PDF: opts},
)

tmp = Path(tempfile.gettempdir()) / "docling_work"
tmp.mkdir(exist_ok=True)

success = 0
failed = 0

for pdf_path in pdfs:
    name = pdf_path.stem
    out_dir = output_base / name
    out_dir.mkdir(exist_ok=True)

    md_path = out_dir / f"{name}.md"
    json_path = out_dir / f"{name}.json"

    if md_path.exists() and json_path.exists() and md_path.stat().st_size > 100:
        print(f"  SKIP {name} (already done)")
        success += 1
        continue

    # Copy to ASCII-safe temp path, process, clean up
    tmp_pdf = tmp / pdf_path.name
    try:
        shutil.copy2(pdf_path, tmp_pdf)
        size_kb = tmp_pdf.stat().st_size // 1024
        print(f"  Processing {name} ({size_kb} KB)...", end=" ", flush=True)

        result = converter.convert(tmp_pdf)

        result.document.save_as_markdown(md_path, image_mode=ImageRefMode.PLACEHOLDER)
        md_size = md_path.stat().st_size // 1024

        doc_data = result.document.export_to_dict()
        doc_data["source_file"] = str(pdf_path)
        json_path.write_text(json.dumps(doc_data, indent=2, ensure_ascii=False), encoding="utf-8")
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
