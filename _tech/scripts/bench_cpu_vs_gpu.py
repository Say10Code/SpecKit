"""B3: CPU vs GPU Docling benchmark — 3 stages.

Root cause analysis of std::bad_alloc on TS 31.102 PDF:
- `Stage preprocess` = _populate_page_images → pypdfium2 renders page → PIL Image
- `generate_picture_images=True` forces full-page renders even for text-only pages
- 3GPP PDF pages with embedded diagrams (EPS, VML, PNG) can produce 50+ MB bitmaps
- pypdfium2 + PIL heap fragmentation → C++ allocator fails on large sequential allocations
- Fix: generate_picture_images=False for benchmark. We don't need embedded images in specs-extracted.

Stages:
  1. Single small doc (TS 35.206, 82 pages) — CPU then GPU, establish baseline
  2. Single medium doc (TS 31.130, 28 pages) — CPU then GPU, confirm speedup
  3. Batch of 3 docs (TS 35.206 + TS 31.130 + TS 31.111 85p) — CPU then GPU, real-world
  (Large TS 31.102 368p skipped — known OOM, needs generate_picture_images=False)

Each stage measures wall-clock time and compares output quality (MD bytes + line count).
"""
import gc, json, shutil, sys, tempfile, time
from pathlib import Path
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode
import torch

OUT = Path(r"D:\ObsidianDB\_tech\benchmarks")
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path(tempfile.gettempdir()) / "docling_bench_b3"
TMP.mkdir(exist_ok=True)

# ── Test documents ───────────────────────────────────────
DOCS = [
    # (label, path, expected_pages, description)
    ("TS 35.206 (MILENAGE)", r"D:\ObsidianDB\Specifications\ETSI_3GPP\Security\ts_133220v170200p.pdf", 106, "Security, 106p, medium tables"),
    ("TS 31.130 (JC API)",   r"D:\ObsidianDB\Specifications\ETSI_3GPP\UICC_API\ts_131130v180400p.pdf", 28, "JavaCard API, 28p, simple"),
    ("TS 31.111 (USAT)",     r"D:\ObsidianDB\Specifications\ETSI_3GPP\USIM\ts_131101v170100p.pdf", 39, "UICC Interface, 39p"),
]

CUDA_OK = torch.cuda.is_available()
DEVICE = "cuda" if CUDA_OK else "cpu"
GPU_NAME = torch.cuda.get_device_name(0) if CUDA_OK else "N/A"

print(f"GPU: {GPU_NAME} ({'11 GB VRAM' if CUDA_OK else 'N/A'})")
print(f"CUDA: {CUDA_OK}")
print()

all_results = {}

def build_pipeline(device):
    return PdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device=device),
        images_scale=1.0,
        layout_batch_size=1,
        table_batch_size=1,
        generate_picture_images=False,   # ← KEY FIX: no embedded images → no OOM
        do_ocr=False,
    )

def run_docling(pdf_path, device):
    """Run Docling on one PDF. Returns (ok, time_s, md_kb, json_kb, lines, pages, error)."""
    pipeline = build_pipeline(device)
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline)},
    )
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()

    t0 = time.monotonic()
    try:
        res = converter.convert(pdf_path)
        elapsed = time.monotonic() - t0

        slug = pdf_path.stem
        md_path = OUT / f"{slug}_{device}.md"
        j_path = OUT / f"{slug}_{device}.json"

        res.document.save_as_markdown(md_path, image_mode=ImageRefMode.PLACEHOLDER)
        md_kb = md_path.stat().st_size // 1024
        lines = len(md_path.read_text(encoding="utf-8").splitlines())

        doc = res.document.export_to_dict()
        doc["benchmark"] = {"device": device, "time_s": round(elapsed), "file": str(pdf_path)}
        j_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        j_kb = j_path.stat().st_size // 1024
        pages = getattr(res.input, "page_count", 0) or 0

        return (True, elapsed, md_kb, j_kb, lines, pages, None)
    except Exception as e:
        elapsed = time.monotonic() - t0
        return (False, elapsed, 0, 0, 0, 0, str(e)[:250])
    finally:
        del converter
        gc.collect()

# ── STAGE 1: Single doc CPU vs GPU ───────────────────────
print("=" * 70)
print("STAGE 1 — Single document: TS 35.206 CPU vs GPU")
print("=" * 70)

for label, path, exp_pages, desc in DOCS[:1]:
    src = Path(path)
    if not src.exists():
        print(f"SKIP {label}: file not found at {path}")
        continue

    size_kb = src.stat().st_size // 1024
    print(f"\n{label}: {desc} ({size_kb} KB, ~{exp_pages} pages)")
    print("-" * 50)

    # CPU
    ok, t, md_kb, j_kb, lines, pages, err = run_docling(src, "cpu")
    cpu_r = {"ok": ok, "time_s": round(t), "md_kb": md_kb, "json_kb": j_kb, "lines": lines, "pages": pages}
    if ok:
        print(f"  CPU: {t:.0f}s  {pages}p  MD={md_kb}KB ({lines} lines)  JSON={j_kb}KB")
    else:
        print(f"  CPU FAIL: {err[:120]}")

    # GPU
    if CUDA_OK:
        ok, t, md_kb, j_kb, lines, pages, err = run_docling(src, "cuda")
        gpu_r = {"ok": ok, "time_s": round(t), "md_kb": md_kb, "json_kb": j_kb, "lines": lines, "pages": pages}
        if ok:
            sp = cpu_r["time_s"] / t if cpu_r["ok"] else 0
            print(f"  GPU: {t:.0f}s  {pages}p  MD={md_kb}KB ({lines} lines)  JSON={j_kb}KB  speedup={sp:.1f}x")
        else:
            print(f"  GPU FAIL: {err[:120]}")
    else:
        gpu_r = {"ok": False, "error": "CUDA not available"}

    all_results[label] = {"cpu": cpu_r, "gpu": gpu_r}

# ── STAGE 2: Another single doc ──────────────────────────
print("\n" + "=" * 70)
print("STAGE 2 — Single document: TS 31.130 CPU vs GPU")
print("=" * 70)

for label, path, exp_pages, desc in DOCS[1:2]:
    src = Path(path)
    size_kb = src.stat().st_size // 1024
    print(f"\n{label}: {desc} ({size_kb} KB, ~{exp_pages} pages)")
    print("-" * 50)

    ok, t, md_kb, j_kb, lines, pages, err = run_docling(src, "cpu")
    cpu_r = {"ok": ok, "time_s": round(t), "md_kb": md_kb, "json_kb": j_kb, "lines": lines, "pages": pages}
    if ok:
        print(f"  CPU: {t:.0f}s  {pages}p  MD={md_kb}KB ({lines} lines)  JSON={j_kb}KB")
    else:
        print(f"  CPU FAIL: {err[:120]}")

    if CUDA_OK:
        ok, t, md_kb, j_kb, lines, pages, err = run_docling(src, "cuda")
        gpu_r = {"ok": ok, "time_s": round(t), "md_kb": md_kb, "json_kb": j_kb, "lines": lines, "pages": pages}
        if ok:
            sp = cpu_r["time_s"] / t if cpu_r["ok"] else 0
            print(f"  GPU: {t:.0f}s  {pages}p  MD={md_kb}KB ({lines} lines)  JSON={j_kb}KB  speedup={sp:.1f}x")
        else:
            print(f"  GPU FAIL: {err[:120]}")
    else:
        gpu_r = {"ok": False}

    all_results[label] = {"cpu": cpu_r, "gpu": gpu_r}

# ── STAGE 3: Batch of 3 docs ─────────────────────────────
print("\n" + "=" * 70)
print("STAGE 3 — Batch: 3 documents CPU vs GPU")
print("=" * 70)

batch_pdfs = []
for label, path, exp_pages, desc in DOCS:
    p = Path(path)
    if p.exists():
        batch_pdfs.append((label, p))

print(f"\nBatch: {len(batch_pdfs)} PDFs ({', '.join(l for l,_ in batch_pdfs)})\n")

for device_name in ["cpu", "cuda"] if CUDA_OK else ["cpu"]:
    print(f"--- {device_name.upper()} batch ---")
    batch_t0 = time.monotonic()
    batch_ok = 0
    batch_fail = 0
    total_pages = 0

    for label, pdf_path in batch_pdfs:
        ok, t, md_kb, j_kb, lines, pages, err = run_docling(pdf_path, device_name)
        if ok:
            batch_ok += 1
            total_pages += pages
            print(f"  {label}: {t:.0f}s  {pages}p  MD={md_kb}KB  JSON={j_kb}KB")
        else:
            batch_fail += 1
            print(f"  {label}: FAIL — {err[:100] if err else '?'}")

    batch_total = time.monotonic() - batch_t0
    all_results[f"batch_{device_name}"] = {"ok": batch_ok, "failed": batch_fail, "time_s": round(batch_total), "total_pages": total_pages}
    print(f"  Total: {batch_total:.0f}s  OK={batch_ok}  FAIL={batch_fail}  Pages={total_pages}")
    print()

# ── FINAL SUMMARY ────────────────────────────────────────
print("=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

for label, data in all_results.items():
    if "batch" in label:
        print(f"\n{label}: {data['time_s']}s  OK={data['ok']}  FAIL={data['failed']}  Pages={data['total_pages']}")
    else:
        cpu = data["cpu"]
        gpu = data["gpu"]
        print(f"\n{label}:")
        if cpu["ok"]:
            print(f"  CPU: {cpu['time_s']}s  {cpu['pages']}p  MD={cpu['md_kb']}KB ({cpu['lines']} lines)")
        else:
            print(f"  CPU: FAILED")
        if gpu.get("ok"):
            sp = cpu["time_s"] / gpu["time_s"] if cpu["ok"] else 0
            print(f"  GPU: {gpu['time_s']}s  {gpu['pages']}p  MD={gpu['md_kb']}KB ({gpu['lines']} lines)  speedup={sp:.1f}x")
        else:
            print(f"  GPU: {'FAILED' if gpu else 'N/A'}")

(OUT / "benchmark_b3_result.json").write_text(json.dumps(all_results, indent=2))
print(f"\nSaved: _tech/benchmarks/benchmark_b3_result.json")

# Cleanup temp
shutil.rmtree(TMP, ignore_errors=True)
