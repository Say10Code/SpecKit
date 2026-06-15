# speckit Integration

**speckit** — built-in Python package (`_pipeline/`), downloads & extracts 3GPP/ETSI specs.
**No authentication needed** — 3GPP/ETSI specs via public FTP + WhatTheSpec.net API.

## Key commands

```bash
python -m _pipeline metadata fetch 31.102     # Update metadata (WhatTheSpec API)
python -m _pipeline download 31.102           # Download spec → !INCOMING/
python -m _pipeline download 31.102 -r 18.0   # Specific release (default: latest)
python -m _pipeline extract docx <path>       # Tier 1: .docx → TXT+MD (0.2 sec)
python -m _pipeline extract docling <path>    # Tier 2: PDF → MD+JSON (GPU)
python -m _pipeline extract pypdf2 <path>     # Tier 3: PDF → TXT (fallback)
python -m _pipeline status                    # Status: downloaded/extracted
python -m _pipeline registry suggest "<topic>" # Find relevant specs by topic
```

## Download: DOCX + ZIP fallback (v4.2.2+)

3GPP FTP блокирует прямые .docx запросы (HTTP 403), но разрешает .zip запросы (HTTP 200). Speckit автоматически пробует оба:

```
1. DOCX: https://.../38_series/38.306/38306-j20.docx → HTTP 403
2. ZIP:  https://.../38_series/38.306/38306-j20.zip  → HTTP 200 ✓
   → Извлечь .docx из ZIP → удалить ZIP → сохранить .docx
```

**Detect**: 3GPP FTP доступ → DOCX 403, ZIP 200 — норма. Speckit прозрачно использует ZIP.
**Detect**: 3GPP FTP доступ → DOCX 200 — старый open-access. ZIP fallback не нужен.
**Detect**: DOCX 403, ZIP 403 — FTP недоступен. Нужен 3GPP-аккаунт.

## Cache & Storage

- Config: `pyproject.toml` + `_pipeline/config.py`
- Cache: `./.speckit/` (`.gitignore`d)
  - `metadata.db` — spec metadata (SQLite)
- GPU: CUDA via `.venv` (RTX 3060, 12 GB)

## Supported specs

| Domain | Numbers |
|---|---|
| UICC/SIM/USIM | 31.101, 31.102, 102.221, 102.223, 102.225, 102.226 |
| 5G Core | 23.501, 23.502, 23.503 |
| IMS/VoLTE | 24.229 |
| Security | 33.102, 33.401, 33.501 |
| Test/MILENAGE | 35.206 |
| JavaCard UICC | 31.130, 31.121, 31.124 |

❌ NOT supported: GSMA (SGP.22/SGP.32), ISO 7816, GlobalPlatform.

## Docling pre-flight

Before any Docling extraction — run F1 auto-patch:
```bash
python "D:\ObsidianDB\_tech\scripts\auto_patch_docling.py"
```

## Agent call

`SpecDownloader: download TS 31.102 Release 18`
File: `.claude/agents/specdownloader.md`
