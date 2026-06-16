# speckit Integration

**speckit** — built-in Python package (`_pipeline/`), downloads & extracts 3GPP/ETSI specs.
**No authentication needed** — 3GPP/ETSI specs via public FTP + WhatTheSpec.net API.

## Key commands

**Все команды — через `.venv`.** После `uv sync` используй явный путь или активируй окружение:

```bash
# Вариант 1: явный путь (надёжно, не требует активации)
.venv\Scripts\python.exe -m _pipeline metadata fetch 31.102
.venv\Scripts\python.exe -m _pipeline download 31.102
.venv\Scripts\python.exe -m _pipeline download 31.102 -r 18.0
.venv\Scripts\python.exe -m _pipeline extract docx <path>
.venv\Scripts\python.exe -m _pipeline extract docling <path>
.venv\Scripts\python.exe -m _pipeline extract pypdf2 <path>
.venv\Scripts\python.exe -m _pipeline status
.venv\Scripts\python.exe -m _pipeline registry suggest "<topic>"

# Вариант 2: активировать venv (короче, но требует активации на каждую сессию)
.venv\Scripts\Activate.ps1
python -m _pipeline download 31.102    # теперь python = .venv\Scripts\python.exe
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
