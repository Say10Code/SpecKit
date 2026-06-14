# INCOMING Pipeline (v4 — speckit + 3-Tier Extraction)

> **Обновлён**: 2026-06-14. spec-crawler → speckit, Tier 1/2/3, Linker consolidation

```mermaid
flowchart TD
    subgraph "Entry Points"
        USER["User: manual file drop"]
        SD["SpecDownloader: python -m _pipeline download"]
    end

    USER --> INCOMING["!INCOMING/ — new file detected"]
    SD -->|".docx via 3GPP FTP"| INCOMING

    INCOMING --> SCAN["Librarian: scan + compare"]

    SCAN --> DUP{"Duplicate?"}

    DUP -->|"YES"| DOUBLE["Move to !double/"]
    DUP -->|"NO"| FLATTEN["Librarian: flatten Specs/archive/"]

    FLATTEN --> SORT["Sort: .category-map.md lookup"]
    SORT --> CATEGORIES["ETSI_3GPP/ | eSIM/ | GlobalPlatform/ | ..."]

    CATEGORIES --> AUTHOR["Author v2: Batch mode — summary + concepts"]
    AUTHOR --> EXTRACT{"File type?"}

    EXTRACT -->|".docx"| TIER1["Tier 1: extract_docx (0.2s, stdlib) → TXT + MD tables"]
    EXTRACT -->|".pdf (3GPP)"| TIER2["Tier 2: extract_docling (1.5m, GPU) → MD + JSON"]
    EXTRACT -->|".pdf (any)"| TIER3["Tier 3: extract_pypdf2 → flat TXT fallback"]

    TIER1 --> EXTRACTED["specs-extracted/ updated"]
    TIER2 --> EXTRACTED
    TIER3 --> EXTRACTED

    EXTRACTED --> LINKER["Linker: cross-references + /lint"]

    LINKER --> LINT{"Lint result?"}
    LINT -->|"0 errors"| ROADMAP["Update Roadmap.md"]
    LINT -->|"errors found"| FIX["Fix + re-lint → Linker"]

    ROADMAP --> DONE["Complete — wiki + specs-extracted + roadmap updated"]
    DOUBLE --> DONE
```

**Что изменилось с v3:**

| Аспект | v3 | v4 |
|---|---|---|
| Download | `spec-crawler checkout` | `python -m _pipeline download` |
| Extraction | Docling GPU + PyPDF2 | Tier 1 (.docx) / Tier 2 (Docling) / Tier 3 (PyPDF2) |
| Линковка | После Author, отдельно | Linker — единая точка (R3) |
| /lint | 5 вызовов | 1 вызов через Linker |
| Время .docx | 2.5 мин (PDF цепочка) | 0.2 сек (Tier 1 прямой) |
