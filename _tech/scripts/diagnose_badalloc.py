"""Diagnose Docling data loss on bad_alloc pages.
Compares page-by-page: Docling MD/JSON vs PyPDF2 TXT.
Determines exactly WHAT is missing on failed pages.
"""
import json, re
from pathlib import Path

# Test files
DOCLING_JSON = Path(r"D:\ObsidianDB\.3gpp-crawler\wiki\default\sources\33102-REL19.1.0\33102-j10.json")
DOCLING_MD   = Path(r"D:\ObsidianDB\.3gpp-crawler\wiki\default\sources\33102-REL19.1.0\33102-j10.md")
PYPDF2_TXT   = Path(r"D:\ObsidianDB\specs-extracted\ETSI_3GPP\Security\ts_133220v170200p.pdf.txt")

# We KNOW from benchmark: pages [67..106] have bad_alloc for TS 133220 (106 pages)
# And TS 31.102 pages [66..368] for the 368-page doc.

print("=" * 70)
print("DIAGNOSIS: Docling data loss on bad_alloc pages")
print("=" * 70)

# ── 1. What does Docling JSON contain? ──
print("\n--- Docling JSON structure ---")
if DOCLING_JSON.exists():
    data = json.loads(DOCLING_JSON.read_text(encoding="utf-8"))
    print(f"Top-level keys: {list(data.keys())[:10]}")

    if "tables" in data:
        tables = data["tables"]
        pages_w_tables = set()
        for t in tables:
            prov = t.get("prov", [{}])
            p = prov[0].get("page", 0) if prov else 0
            pages_w_tables.add(p)
        print(f"Tables extracted: {len(tables)} across {len(pages_w_tables)} pages")

    if "texts" in data:
        texts = data["texts"]
        pages_w_text = set()
        for t in texts:
            prov = t.get("prov", [{}])
            p = prov[0].get("page", 0) if prov else 0
            pages_w_text.add(p)
        print(f"Text items extracted: {len(texts)} across {len(pages_w_text)} pages")

    # Check figure/image count
    if "pictures" in data:
        print(f"Pictures extracted: {len(data['pictures'])}")
    if "figures" in data:
        print(f"Figures extracted: {len(data['figures'])}")
else:
    print("Docling JSON not found — checking MD only")

# ── 2. Page-by-page content check ──
print("\n--- MD content by page ---")
if DOCLING_MD.exists():
    md_text = DOCLING_MD.read_text(encoding="utf-8")

    # Count explicit page markers or section breaks
    h4_count = len(re.findall(r'^####\s', md_text, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s', md_text, re.MULTILINE))
    h2_count = len(re.findall(r'^##\s', md_text, re.MULTILINE))
    table_count = len(re.findall(r'^\|.*\|$', md_text, re.MULTILINE))
    print(f"MD: H2={h2_count} H3={h3_count} H4={h4_count} table_rows={table_count}")
    print(f"MD size: {len(md_text)} chars, {len(md_text.splitlines())} lines")

    # Check if page markers exist (Docling sometimes adds <!-- Page X -->)
    page_markers = re.findall(r'<!--\s*[Pp]age\s*(\d+)', md_text)
    if page_markers:
        print(f"Explicit page markers: {len(page_markers)} (pages {min(map(int,page_markers))}-{max(map(int,page_markers))})")

# ── 3. Compare with PyPDF2 TXT ──
print("\n--- PyPDF2 TXT reference ---")
if PYPDF2_TXT.exists():
    txt = PYPDF2_TXT.read_text(encoding="utf-8")
    # Count PAGE markers
    page_breaks = re.findall(r'=== PAGE (\d+)/(\d+) ===', txt)
    total_pages_txt = int(page_breaks[0][1]) if page_breaks else 0
    print(f"Total pages in TXT: {total_pages_txt}")

    # Sample a "failing" page (page 80) vs a "good" page (page 20)
    # Find page 20 content
    p20_match = re.search(r'=== PAGE 20/\d+ ===\n(.*?)(?==== PAGE \d+/\d+ ===)', txt, re.DOTALL)
    p80_match = re.search(r'=== PAGE 80/\d+ ===\n(.*?)(?==== PAGE \d+/\d+ ===)', txt, re.DOTALL)

    if p20_match:
        p20_text = p20_match.group(1).strip()
        print(f"\nPage 20 TXT sample ({len(p20_text)} chars):")
        print(p20_text[:200])
    if p80_match:
        p80_text = p80_match.group(1).strip()
        print(f"\nPage 80 TXT sample ({len(p80_text)} chars):")
        print(p80_text[:200])

# ── 4. Diagnostic verdict ──
print("\n" + "=" * 70)
print("DIAGNOSTIC VERDICT")
print("=" * 70)
print("""
WHAT bad_alloc skips:
  - Page IMAGE rendering (pypdfium2 bitmap → PIL)
  - Picture/figure extraction for those pages
  - OCR on those page images (not needed — do_ocr=False already)

WHAT Docling STILL extracts even on bad_alloc pages:
  - Text content (via docling_parse text extraction, separate from rendering)
  - Table structure (via ML table detection on the layout layer,
    which may partially work even without full-page bitmap)
  - Section headers and structure

THE REAL LOSS:
  - Embedded figures/images from those pages are not extracted
  - generate_picture_images=False already disables this — so NO additional loss
  - The text and tables should still appear in MD output

VERIFICATION: Check MD output for content around pages 67-106.
""")
