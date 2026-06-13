# Agent Interaction Graph (8 agents)

```mermaid
graph TD
    CLAUDE["CLAUDE.md — Main Dispatcher"]

    CLAUDE --> Librarian
    CLAUDE --> Researcher
    CLAUDE --> Reviewer
    CLAUDE --> SpecExtractor
    CLAUDE --> SpecDownloader

    SpecDownloader -->|downloads PDFs to| IncomingDir
    IncomingDir["!INCOMING/"] -->|triggers| Librarian

    Librarian -->|catalog new files| Author
    Researcher -->|deep analysis| Author

    Reviewer -->|reads TXT| SpecExtractor
    Reviewer -->|checks wiki pages| Author

    Author -->|creates pages| Linker
    Linker -->|finds orphans| Author

    Author -->|produces MD| Formatter
    Formatter -->|outputs HTML| Outputs

    SpecExtractor -->|writes TXT| SpecsExtracted
    SpecExtractor -->|reads PDF| SpecsDir

    Reviewer -->|reads| SpecsExtracted
    Reviewer -->|checks| Wiki

    SpecDownloader -->|spec-crawler checkout| SpecSource
    SpecSource["3GPP FTP + WhatTheSpec.net API"]

    subgraph "Agents — 8 total"
        Author
        Reviewer
        Linker
        Librarian
        Researcher
        Formatter
        SpecExtractor
        SpecDownloader
    end

    subgraph "Data"
        SpecsDir["Specifications/ PDF — 65 files"]
        SpecsExtracted["specs-extracted/ TXT — 58 files"]
        Wiki["wiki/ .md — 129 pages"]
        Outputs["outputs/ .html + reports"]
        IncomingDir
    end

    subgraph "External"
        SpecSource
    end
```

## Flow directions (updated)

```
SpecDownloader → !INCOMING/ → Librarian → Author → Linker     (new: auto-download pipeline)
User → !INCOMING/ → Librarian → Author → Linker                (manual pipeline)
Researcher → Author → Linker                                   (research pipeline)
SpecExtractor → Reviewer → Author                              (review pipeline)
Author → Formatter → Outputs                                   (formatting pipeline)
```
