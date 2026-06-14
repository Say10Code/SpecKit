# Agent Interaction Graph (8 agents + 7 skills + speckit pipeline)

> **Обновлён**: 2026-06-14 из графа (7,642 узла, 19,799 рёбер, 102 оркестрационных)
> **R1-R4 применены**: SpecExtractor→Linker, Researcher→Linker, /lint консолидация, Reviewer→Author

```mermaid
graph TD
    CLAUDE["CLAUDE.md — 47-строчный диспетчер"]

    CLAUDE -->|/spec-download| SpecDownloader
    CLAUDE -->|/ingest| Librarian
    CLAUDE -->|/research| Researcher
    CLAUDE -->|/review| Reviewer
    CLAUDE -->|/format-html| Formatter
    CLAUDE -->|/lint| LintTool

    SpecDownloader -->|"python -m _pipeline download"| Pipeline
    SpecDownloader -->|"сортировка"| Librarian
    SpecDownloader -->|"R3: кросс-ссылки"| Linker

    Pipeline["_pipeline/ (speckit) — 10 модулей"] -->|"FTP download"| IncomingDir
    Pipeline -->|"Tier 1 docx"| SpecsExtracted
    Pipeline -->|"Tier 2 docling GPU"| SpecsExtracted
    Pipeline -->|"Tier 3 pypdf2"| SpecsExtracted

    IncomingDir["!INCOMING/"] -->|"flatten"| Librarian

    Librarian -->|"Batch Author"| Author
    Librarian -->|"R3: кросс-ссылки"| Linker
    Researcher -->|"Single Author"| Author
    Researcher -->|"R2: кросс-ссылки"| Linker

    Reviewer -->|"читает эталоны"| SpecsExtracted
    Reviewer -->|"R4: предлагает правки"| Author
    SpecExtractor -->|"читает"| SpecsDir
    SpecExtractor -->|"пишет эталоны"| SpecsExtracted
    SpecExtractor -->|"R1: кросс-ссылки"| Linker

    Author -->|"создаёт страницы"| Wiki
    Author -->|"R3: кросс-ссылки"| Linker
    Linker -->|"добавляет wikilinks"| Wiki
    Linker -->|"единственная точка"| LintTool
    LintTool -->|"проверяет"| Wiki

    Author -->|"MD на вход"| Formatter
    Formatter -->|"HTML на выход"| Outputs

    subgraph "Skills — 7 total"
        LintTool["/lint — единая точка вызова"]
        IngestSkill["/ingest"]
        ReviewSkill["/review"]
        FormatSkill["/format-html"]
        RoadmapSkill["/roadmap"]
        DownloadSkill["/spec-download"]
        ResearchSkill["/research"]
    end

    subgraph "Agents — 8 total"
        Author["Author v2 — Batch + Single"]
        Reviewer["Reviewer v3 — гибридный Pass 1"]
        Linker["Linker — граф-анализ"]
        Librarian["Librarian v2 — flatten + сортировка"]
        Researcher["Researcher — deep investigations"]
        Formatter["Formatter — MD → HTML"]
        SpecExtractor["SpecExtractor v3 — 3-tier extraction"]
        SpecDownloader["SpecDownloader — speckit download"]
    end

    subgraph "Data"
        SpecsDir["Specifications/ — 74 PDF + 20 DOCX"]
        SpecsExtracted["specs-extracted/ — 78 TXT + 86 MD + 73 JSON"]
        Wiki["wiki/ — 130 страниц + 7 индексов"]
        Outputs["outputs/ — HTML отчёты"]
        IncomingDir
    end

    subgraph "Pipeline"
        Pipeline
    end
```

**Изменения (R1-R4):**
- 🔴→🟢 SpecExtractor → Linker (R1) — после extraction
- 🔴→🟢 Researcher → Linker (R2) — после research
- 🔴→🟢 /lint консолидация (R3) — 5 агентов → Linker → /lint (1 вызов)
- 🔴→🟢 Reviewer → Author (R4) — обратная связь через Single update
- 🔴→🟢 spec-crawler → speckit (_pipeline/) — полная замена
