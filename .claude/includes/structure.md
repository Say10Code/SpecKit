# Structure & Permissions

## Directory tree

```
D:\ObsidianDB\
├── CLAUDE.md                  ← Main dispatcher
├── Roadmap.md                 ← Roadmap + master inventory
├── .claude/agents/            ← Sub-agents (8)
├── .claude/skills/            ← Skills (7)
├── .claude/includes/          ← Modular docs (this dir)
├── Specifications/              ← 🔒 Read-only
│   ├── !INCOMING/              ← 📥 Inbox — new files
│   ├── !double/                ← 🗑️ Duplicates
│   ├── ETSI_3GPP/              ← UICC, USIM, CAT_STK, OTA, GSM, Security, ...
│   ├── eSIM/                   ← GSMA SGP.02, whitepaper
│   ├── GlobalPlatform/         ← GP Card Spec
│   ├── JavaCard/               ← Stepping Stones, API ref
│   ├── Books/  Manuals/  Papers/  Tutorials/
│   └── ISO7816_Analysis/       ← !recheck materials
├── wiki/                      ← ✏️ Knowledge base
│   ├── concepts/  entities/  summaries/  syntheses/  reference/  research/
│   └── index.md
├── notes/                     ← ✏️ User notes
├── specs-extracted/           ← 📄 Extracted texts (58 TXT + 37 MD+JSON)
├── outputs/                   ← ✏️ Reports, HTML
├── _tech/                     ← Engineering docs (BACKLOG, architecture, plans)
└── 3gpp-crawler.toml          ← spec-crawler config
```

## Permissions

| Directory | Access | Who writes |
|---|---|---|
| `Specifications/!INCOMING/` | ✏️ Full | SpecDownloader, user |
| `Specifications/!double/` | ✏️ Write | Librarian |
| `Specifications/*/` (rest) | 🔒 Read-only | — |
| `Clippings/` | 🔒 Read-only | — |
| `wiki/`, `outputs/`, `specs-extracted/` | ✏️ Full | Author, SpecExtractor, Formatter |
| `notes/` | ✏️ Read+Write | User |
| `.obsidian/`, `.claude/`, `.claudian/` | 🔒 No touch | — |
| `_tech/` | ✏️ Full | All agents |
