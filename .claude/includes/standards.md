# Content Standards

## Frontmatter (mandatory)

```yaml
---
tags: [domain, technology]
type: concept | entity | summary | synthesis | reference | note | research | hub
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | reviewed | final | deprecated
sources:
  - "[[Specifications/...]]"
---
```

## Wikilinks

- `[[wiki/concepts/APDU]]` — inside wiki/
- `[[wiki/concepts/APDU|APDU Commands]]` — display text
- `[[Specifications/ETSI_3GPP/UICC/ts_102221.pdf]]` — external
- `[[Roadmap]]` — root files

## Provenance markers

Every factual claim must be tagged:

| Marker | Meaning |
|---|---|
| `^[extracted]` | From specification |
| `^[inferred]` | Logically deduced |
| `^[ambiguous]` | Uncertain |
| `^[todo]` | Needs research |

## Page types

| Type | Template | Directory | Size | When |
|---|---|---|---|---|
| concept | t-concept | wiki/concepts/ | 2-4 KB | Foundational ideas |
| entity | t-entity | wiki/entities/ | 1-2 KB | Organizations |
| summary | t-summary | wiki/summaries/ | 2-5 KB | Source abstracts |
| synthesis | t-synthesis | wiki/syntheses/ | 5-15 KB | Cross-topic analysis |
| reference | t-reference | wiki/reference/ | variable | Lookup tables |
| note | t-note | notes/ | variable | Informal |

## Callouts

```markdown
> [!note] Historical context
> [!warning] Attention
> [!tip] Practical advice
> [!info] Key idea
> [!danger] Critical issue
> [!example] Example
> [!abstract] Definition
```

## Mermaid rules (v10)

- ✅ ASCII arrows: `-->`, `->>`, `-->>` (NEVER `&gt;`)
- ✅ Text without emoji or box-drawing chars
- ✅ `/` instead of `||` (parser conflict)
- ✅ Separate `Note` blocks instead of `<br/>`
- ✅ `flowchart TB/LR/TD` for flows, `graph TD` for architecture
