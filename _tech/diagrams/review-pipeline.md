# Review Pipeline (3-pass + R4 feedback loop)

> **Обновлён**: 2026-06-14. Гибридный Pass 1 (3 формата), R4: Reviewer → Author

```mermaid
flowchart TD
    WIKI["wiki/ page.md — 130 страниц"]

    WIKI --> REVIEW["/review skill"]

    REVIEW --> PASS1

    subgraph "Pass 1: Technical Accuracy (hybrid)"
        P1_0["Check specs-extracted/INDEX.md — available formats"]
        P1_0 --> P1_1["TXT: Grep FID/CLA/INS/SW (fastest)"]
        P1_0 --> P1_2["JSON: lookup coords → MD table (provenance)"]
        P1_0 --> P1_3["MD: read structured section (context)"]
        P1_1 --> P1_4["Compare with wiki claims"]
        P1_2 --> P1_4
        P1_3 --> P1_4
        P1_4 --> P1_5["Verdict: CORRECT / INCORRECT / NOT_IN_SPEC / NEEDS_SPEC"]
    end

    PASS1 --> PASS2

    subgraph "Pass 2: Structure and Readability"
        P2_1["Check frontmatter: tags, type, status, dates, sources"]
        P2_2["Check Mermaid: ASCII arrows, no entities, no box-drawing"]
        P2_3["Check callouts: note/warning/danger/tip/etc"]
        P2_4["Check header flow, section length"]
        P2_1 --> P2_2 --> P2_3 --> P2_4
    end

    PASS2 --> PASS3

    subgraph "Pass 3: Connectivity"
        P3_1["Count inbound links (target >= 3)"]
        P3_2["Count outbound links (target >= 3)"]
        P3_3["Suggest additional cross-links"]
        P3_4["Detect orphan risk"]
        P3_1 --> P3_2 --> P3_3 --> P3_4
    end

    PASS3 --> REPORT

    subgraph "Final Report"
        R1["CRITICAL: FID/CLA/INS/AID/SW wrong"]
        R2["HIGH: EF size, data structure, protocol params"]
        R3["MEDIUM: TERMINAL PROFILE bits, access conditions"]
        R4["LOW: typos, style"]
        R5["NEEDS_SPEC: missing specification"]
        R6["VERDICT: Pass / Fail / Needs Specs"]
    end

    REPORT --> ACTION{Action}
    ACTION -->|"Pass"| DONE["Status: reviewed"]
    ACTION -->|"Fail: CRITICAL/HIGH"| FEEDBACK["R4: Reviewer → Author feedback"]
    ACTION -->|"Needs Specs"| WAIT["Request SpecExtractor / SpecDownloader"]

    FEEDBACK --> AUTHOR["Author v2: Single mode update"]
    AUTHOR -->|"fixes applied"| WIKI
    WIKI -.->|"re-review"| REVIEW
```

**3 источника для гибридного Pass 1:**

| Инструмент | Тип утверждения | Формат |
|---|---|---|
| TXT Grep | FID, CLA, SW, размеры | PyPDF2 / Tier 3 |
| JSON lookup | Координаты таблиц, provenance | Docling / Tier 2 |
| MD read | Контекст, структуры EF | Docling / Tier 1-2 |

**R4 Feedback Loop (NEW):**
```
Reviewer → Author v2 (Single mode update) → wiki page → re-review
```
