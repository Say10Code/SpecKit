# Skills — 7 orchestrators

| Skill | Trigger | Agents used | Steps |
|---|---|---|---|
| `/lint` | After every change | Grep + Glob + Read | broken links → orphans → frontmatter → gaps |
| `/ingest` | `/ingest` | Author ×3 + Linker + SpecExtractor | read → summary → concepts → entities → synthesis → extract → links → Roadmap → /lint |
| `/review` | `/review` | Reviewer (Pass 1+2) + Linker (Pass 3) | TXT/MD/JSON check → structure → connectivity → verdict |
| `/format-html` | `/format-html` | Formatter | MD → HTML (Mermaid v10, callouts, dark theme) |
| `/roadmap` | `/roadmap` | Read-only | stats check → consistency → priorities |
| `/spec-download` | `/spec-download 31.102` | SD → Lib → Aut → Lin → SEx → /lint | crawl → checkout → flatten → /ingest → extract → /lint → Roadmap |
| `/research` | `/research` | Researcher → (Author) | deep analysis → `wiki/research/` |

Full pipeline docs per skill: `.claude/skills/<name>/SKILL.md`
