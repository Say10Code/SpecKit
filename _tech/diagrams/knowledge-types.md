# Knowledge Types and Their Relationships

```mermaid
graph TD
    DOCX[".docx Specification"]
    PDF["PDF Specification"]

    DOCX -->|"Tier 1: extract_docx (0.2s)"| TXT
    DOCX -->|"Tier 1: extract_docx --tables"| MD_TABLES["MD Tables"]
    PDF -->|"Tier 2: extract_docling (GPU)"| MD_JSON["MD + JSON"]
    PDF -->|"Tier 3: extract_pypdf2"| TXT

    TXT["Extracted TXT — flat text"]
    MD_TABLES -->|"structured tables"| REVIEWER
    MD_JSON -->|"provenance coords"| REVIEWER
    TXT -->|"grep FID/CLA"| REVIEWER["Reviewer — hybrid Pass 1"]
    REVIEWER -->|"validates"| WIKI

    TXT -->|"extracted facts"| REFERENCE["Reference Tables"]
    TXT -->|"read + summarize"| SUMMARY["Summaries"]
    MD_TABLES -->|"EF structures"| CONCEPT

    REFERENCE -->|"verified values"| CONCEPT
    SUMMARY -->|"extract key ideas"| CONCEPT["Concepts"]
    SUMMARY -->|"identify orgs"| ENTITY["Entities"]

    CONCEPT -->|"cross-analyze"| SYNTHESIS["Syntheses"]
    ENTITY -->|"cross-analyze"| SYNTHESIS
    REFERENCE -->|"cross-analyze"| SYNTHESIS
    SUMMARY -->|"cross-analyze"| SYNTHESIS

    SYNTHESIS -->|"deep dive"| RESEARCH["Research"]
    CONCEPT -->|"deep dive"| RESEARCH
    REFERENCE -->|"deep dive"| RESEARCH

    WIKI["wiki/ — 130 pages, knowledge graph"]

    RESEARCH --> WIKI
    SYNTHESIS --> WIKI
    CONCEPT --> WIKI
    ENTITY --> WIKI
    SUMMARY --> WIKI
    REFERENCE --> WIKI

    WIKI -->|"R4 feedback"| AUTHOR["Author v2"]
    AUTHOR -->|"creates/updates"| WIKI
```

**3 источника эталонного текста (для Reviewer Pass 1):**

| Источник | Инструмент | Формат | Скорость |
|---|---|---|---|
| .docx прямой | Tier 1: extract_docx | TXT + MD tables | 0.2 сек |
| PDF (3GPP) | Tier 2: extract_docling | MD + JSON (GPU) | 1.5 мин |
| PDF (любой) | Tier 3: extract_pypdf2 | TXT плоский | 15-60 сек |
