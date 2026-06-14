# !INCOMING Pipeline — dual-path ingestion

`Specifications/!INCOMING/` — entry point. Two paths:

## Path A: Manual
User drops flat files (PDF, DOCX) directly in `!INCOMING/`.
→ Librarian compares name+size → duplicate? → `!double/`
→ New? → sort by source type

## Path B: spec-crawler checkout
SpecDownloader creates nested: `!INCOMING/Specs/archive/<series>/<number>/<version>/<file>.docx`
→ Librarian flattens: find all .docx/.pdf, extract spec # from filename
→ Move to `Specifications/<topic>/` per `.category-map.md`
→ Delete `Specs/` structure

## Sort rules

See **`.category-map.md`** — single source of truth for series→topic mapping.
Quick reference: 31.xxx→USIM/UICC, 102.xxx→UICC/CAT_STK/OTA, 33/35xxx→Security, GSMA→eSIM, GP→GlobalPlatform.

## After sorting

1. Process through Librarian → `/ingest`
2. SpecExtractor extracts text → `specs-extracted/`
3. `/lint` checks health
4. Update `Roadmap.md`
