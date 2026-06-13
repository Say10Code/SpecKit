# System Architecture Layers (5 layers, 8 agents)

```mermaid
graph TD
    subgraph "Layer 5: User Interface"
        OBSIDIAN["Obsidian GUI"]
        TERMINAL["Terminal / Claude CLI"]
    end

    subgraph "Layer 4: Orchestration Skills — 5 total"
        INGEST_SKILL["/ingest"]
        REVIEW_SKILL["/review"]
        LINT_SKILL["/lint"]
        FORMAT_SKILL["/format-html"]
        ROADMAP_SKILL["/roadmap"]
    end

    subgraph "Layer 3: Sub-Agents — 8 total"
        AUTHOR["Author"]
        REVIEWER["Reviewer v2"]
        LINKER["Linker"]
        LIBRARIAN["Librarian"]
        RESEARCHER["Researcher"]
        FORMATTER["Formatter"]
        SPECEXTRACTOR["SpecExtractor"]
        SPECDOWNLOADER["SpecDownloader"]
    end

    subgraph "Layer 2: Data"
        SPECS["Specifications/ PDF — 65 files"]
        INCOMING["!INCOMING/"]
        EXTRACTED["specs-extracted/ TXT — 58 files"]
        WIKI["wiki/ .md — 129 pages"]
        NOTES["notes/ .md — 4 files"]
        OUTPUTS["outputs/ .html and reports"]
    end

    subgraph "Layer 1: Meta"
        CLAUDE_MD["CLAUDE.md — 240 lines"]
        ROADMAP["Roadmap.md"]
        TEMPLATES[".obsidian/templates/ — 6 files"]
        AGENTS_DEF[".claude/agents/ — 8 files"]
        SKILLS_DEF[".claude/skills/ — 5 files"]
        EXTERNAL["3gpp-crawler (spec-crawler CLI)"]
    end

    OBSIDIAN --> CLAUDE_MD
    TERMINAL --> CLAUDE_MD

    CLAUDE_MD --> INGEST_SKILL
    CLAUDE_MD --> REVIEW_SKILL
    CLAUDE_MD --> LINT_SKILL
    CLAUDE_MD --> FORMAT_SKILL
    CLAUDE_MD --> ROADMAP_SKILL

    INGEST_SKILL --> AUTHOR
    INGEST_SKILL --> LINKER
    INGEST_SKILL --> LIBRARIAN

    REVIEW_SKILL --> REVIEWER
    REVIEW_SKILL --> LINKER

    LINT_SKILL --> WIKI

    FORMAT_SKILL --> FORMATTER

    ROADMAP_SKILL --> ROADMAP

    SPECDOWNLOADER -->|spec-crawler| EXTERNAL
    SPECDOWNLOADER -->|downloads to| INCOMING

    AUTHOR --> WIKI
    AUTHOR --> TEMPLATES

    REVIEWER --> EXTRACTED
    REVIEWER --> WIKI

    LINKER --> WIKI

    LIBRARIAN --> SPECS
    LIBRARIAN --> INCOMING
    LIBRARIAN --> WIKI

    RESEARCHER --> WIKI
    RESEARCHER --> SPECS

    FORMATTER --> WIKI
    FORMATTER --> OUTPUTS

    SPECEXTRACTOR --> SPECS
    SPECEXTRACTOR --> EXTRACTED

    INCOMING --> LIBRARIAN
```

## Notes

- `SpecDownloader` is the newest agent (added 2026-06-12) — bridges 3gpp-crawler ↔ `!INCOMING/`
- `3gpp-crawler` is an external CLI tool installed globally via `uv tool install`, not part of the ObsidianDB repo
- Cache: `D:\ObsidianDB\.3gpp-crawler\` (in `.gitignore`)
