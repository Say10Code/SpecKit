# Agents — 8 narrow experts

Trigger via `Agent` tool with `subagent_type: "claude"` and system prompt from file.

## Matrix

| # | Agent | File | Trigger | Input → Output |
|---|---|---|---|---|
| 1 | **SpecDownloader** | `specdownloader.md` | `/spec-download`, direct | TS # → `!INCOMING/Specs/archive/` .docx |
| 2 | **Librarian v2** | `librarian.md` | files in `!INCOMING/` | `!INCOMING/` → `Specifications/<topic>/` |
| 3 | **Author v2** | `author.md` | `/ingest`, page creation | material → `wiki/` .md + frontmatter |
| 4 | **Reviewer v3** | `reviewer.md` | `/review`, after Author | wiki → CRITICAL/HIGH/MEDIUM/LOW report |
| 5 | **Linker** | `linker.md` | `/lint` orphans, `/ingest` step 6 | `wiki/` → wikilink suggestions |
| 6 | **Researcher** | `researcher.md` | research request | topic → `wiki/research/` (15-50 KB) |
| 7 | **Formatter** | `formatter.md` | `/format-html` | `wiki/*.md` → `outputs/*.html` |
| 8 | **SpecExtractor v2** | `specextractor.md` | first run, new PDF | PDF → `specs-extracted/*.txt` + `*.md` + `*.json` |

## Reviewer v3 — Truth hierarchy

Reviewer verifies claims against **original specs**, not other wiki pages:
1. Find fact in `specs-extracted/` (extracted texts)
2. Compare with spec ground truth
3. Verdict: `CORRECT` / `INCORRECT` / `NEEDS_SPEC`
4. If spec not extracted → recommend SpecExtractor

**Truth chain**: `Specifications/` (PDF) → `specs-extracted/` (TXT/MD/JSON) → wiki pages.
Wiki contradicts spec → wiki is wrong.

**Hybrid Pass 1**: picks method by fact type:
- FID/CLA/SW codes → TXT Grep (fast)
- Table/structure → JSON lookup → MD read (Docling tables preserved)
- Context/description → MD read (structured text)

## specs-extracted/ — Extracted ground truth

Contains text copies of ALL PDFs from `Specifications/`. **Ground truth for Reviewer.**

**Create/update**: `SpecExtractor: extract all PDF`
**Use**: Reviewer reads `specs-extracted/INDEX.md` → grep TXT/MD/JSON → verify

Structure mirrors `Specifications/`:
```
specs-extracted/
├── INDEX.md                   ← Content map (chapters, tables, FIDs)
├── .meta.json                 ← Extraction metrics
├── 3GPP/                      ← 11 specs (MD+JSON per release)
├── ETSI/                      ← 5 specs (MD+JSON)
└── ETSI_3GPP/ Books/ eSIM/ ... ← 58 TXT (PyPDF2)
```
