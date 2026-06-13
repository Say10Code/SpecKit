"""F3 v2: Verify F1 quality — images_scale=1.0 + batch_size=1.
Compare TWO scales: 0.5 vs 1.0 on the SAME 368-page PDF.
"""
import json, re, shutil, sys, tempfile, time
from pathlib import Path
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode
import torch

SRC = Path(r"D:\ObsidianDB\Specifications\ETSI_3GPP\USIM\ts_131102v171000p.pdf")
TXT = Path(r"D:\ObsidianDB\specs-extracted\ETSI_3GPP\USIM\ts_131102v171000p.pdf.txt")
OUT = Path(r"D:\ObsidianDB\_tech\benchmarks")
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path(tempfile.gettempdir()) / "verify_f1f2_v2"
TMP.mkdir(exist_ok=True)
TMP_PDF = TMP / "v2_31102.pdf"
shutil.copy2(SRC, TMP_PDF)

DEV = "cuda" if torch.cuda.is_available() else "cpu"
print(f"GPU: {torch.cuda.get_device_name(0) if DEV=='cuda' else 'CPU'}")
print()

results = {}

for label, scale, batch_size in [
    ("SCALE 1.0 — batch 1", 1.0, 1),
    ("SCALE 0.5 — batch 1", 0.5, 1),
]:
    print("=" * 70)
    print(f"RUN: {label}")
    print("=" * 70)

    pipeline = PdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device=DEV),
        images_scale=scale,
        layout_batch_size=batch_size,
        table_batch_size=batch_size,
        generate_picture_images=False,
        do_ocr=False,
    )
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline)},
    )

    t0 = time.monotonic()
    result = converter.convert(TMP_PDF)
    elapsed = time.monotonic() - t0

    tag = label.replace(" ", "_").replace("—", "-")
    md_path = OUT / f"ts_31102_v2_{tag}.md"
    result.document.save_as_markdown(md_path, image_mode=ImageRefMode.PLACEHOLDER)

    md_kb = md_path.stat().st_size // 1024
    md_text = md_path.read_text(encoding="utf-8")
    lines = len(md_text.splitlines())
    pages = getattr(result.input, "page_count", 0) or 0

    # Quick quality metrics
    h2 = len(re.findall(r'^##\s', md_text, re.MULTILINE))
    h3 = len(re.findall(r'^###\s', md_text, re.MULTILINE))
    h4 = len(re.findall(r'^####\s', md_text, re.MULTILINE))
    table_rows = len(re.findall(r'^\|.*\|$', md_text, re.MULTILINE))

    # Check key EFs
    EFS = ["6F07", "6F05", "6F46", "6F38", "6F3B", "6F3C", "4F01", "2FE2"]
    efs_found = sum(1 for e in EFS if e in md_text)

    print(f"  {elapsed:.0f}s  {pages}p  MD={md_kb}KB ({lines} lines)")
    print(f"  H2={h2}  H3={h3}  H4={h4}  table_rows={table_rows}")
    print(f"  EFs found: {efs_found}/{len(EFS)}")

    results[label] = {
        "time_s": round(elapsed), "pages": pages, "md_kb": md_kb, "lines": lines,
        "h2": h2, "h3": h3, "h4": h4, "table_rows": table_rows, "efs": efs_found,
    }

    # Spot-check: does section 4.2.2 (EF_IMSI) have clean data?
    imsi_idx = md_text.find("IMSI")
    if imsi_idx > 0:
        chunk = md_text[imsi_idx:imsi_idx+600]
        has_fid = "6F07" in chunk or "6F 07" in chunk
        has_size = "9" in chunk
        has_structure = "transparent" in chunk.lower()
        print(f"  IMSI section: FID={'YES' if has_fid else 'NO'} SIZE={'YES' if has_size else 'NO'} STRUCT={'YES' if has_structure else 'NO'}")

    del converter
    import gc; gc.collect()
    print()

# SUMMARY
print("=" * 70)
print("COMPARISON: scale=1.0 vs scale=0.5 on 368-page PDF")
print("=" * 70)
print(f"{'Metric':<25} {'1.0 batch=1':>15} {'0.5 batch=1':>15} {'Delta':>15}")
print("-" * 70)

for key, label in [("time_s", "Time"), ("md_kb", "MD size"), ("lines", "Lines"),
                     ("h2", "H2 headers"), ("h3", "H3"), ("h4", "H4"),
                     ("table_rows", "Table rows"), ("efs", "EFs found")]:
    v1 = results.get("SCALE 1.0 — batch 1", {}).get(key, "?")
    v2 = results.get("SCALE 0.5 — batch 1", {}).get(key, "?")
    unit = "s" if key == "time_s" else ("KB" if key == "md_kb" else "")
    print(f"{label:<25} {str(v1)+unit:>15} {str(v2)+unit:>15}")

# PyPDF2 reference
txt_kb = TXT.stat().st_size // 1024
txt_pages = len(re.findall(r'=== PAGE (\d+)/(\d+) ===', TXT.read_text(encoding="utf-8")))
print(f"\nPyPDF2 TXT reference: {txt_kb} KB, {txt_pages} pages")

(OUT / "verify_f1f2_v2_result.json").write_text(json.dumps(results, indent=2))
print("\nReport: _tech/benchmarks/verify_f1f2_v2_result.json")
TMP_PDF.unlink()
shutil.rmtree(TMP, ignore_errors=True)
