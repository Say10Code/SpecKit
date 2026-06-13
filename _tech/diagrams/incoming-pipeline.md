# INCOMING Pipeline (v2 — with SpecDownloader)

```mermaid
flowchart TD
    subgraph "Entry Points"
        USER["User: manual PDF download"]
        SD["SpecDownloader: spec-crawler checkout"]
    end

    USER --> INCOMING["!INCOMING/ New PDF"]
    SD -->|PDF appears| INCOMING

    INCOMING --> SCAN["Scan: compare name and size"]

    SCAN --> DUP{Is Duplicate?}

    DUP -->|YES| DOUBLE["Move to !double/"]
    DUP -->|NO| LIBRARIAN["Librarian: catalog and sort"]

    LIBRARIAN --> SORT["Sort by category"]

    SORT --> CAT1["ETSI_3GPP/"]
    SORT --> CAT2["eSIM/"]
    SORT --> CAT3["JavaCard/"]
    SORT --> CAT4["Books/"]
    SORT --> CAT5["Manuals/"]
    SORT --> CAT6["Papers/"]
    SORT --> CAT7["Tutorials/"]

    CAT1 --> INGEST["/ingest skill"]
    CAT2 --> INGEST
    CAT3 --> INGEST
    CAT4 --> INGEST
    CAT5 --> INGEST
    CAT6 --> INGEST
    CAT7 --> INGEST

    INGEST --> STEP1["Step 1: Read file (PyPDF2)"]
    STEP1 --> STEP2["Step 2: Create summary via Author"]
    STEP2 --> STEP3["Step 3: Extract concepts via Author"]
    STEP3 --> STEP4["Step 4: Record entities via Author"]
    STEP4 --> STEP5["Step 5: Create synthesis via Author"]
    STEP5 --> STEP6["Step 6: Cross-link via Linker"]

    STEP6 --> LINT["/lint: health check"]
    LINT -->|0 errors| ROADMAP["Update Roadmap.md"]
    LINT -->|errors found| FIX["Fix issues"]
    FIX --> LINT

    ROADMAP --> SPECEXTRACT["SpecExtractor: PDF to TXT"]
    SPECEXTRACT --> DONE["Complete"]
    DOUBLE --> DONE
```

## What changed from v1

| Change | Detail |
|---|---|
| New entry: SpecDownloader | `spec-crawler checkout` → PDF in `!INCOMING/` automatically |
| 3GPP FTP + WhatTheSpec API | No manual download from portal needed |
| Same pipeline after `!INCOMING/` | Librarian → /ingest → /lint unchanged |
