# 3gpp-crawler Integration

**3gpp-crawler** — external CLI (`uv tool install`), downloads 3GPP specs into `!INCOMING/`.
**No authentication needed** — 3GPP/ETSI specs via public FTP + WhatTheSpec.net API.

## Key commands

```bash
cd "D:\ObsidianDB"  # ⚠️ CWD MUST be project root — config won't be found otherwise

spec-crawler crawl                      # Update metadata DB (run periodically)
spec-crawler checkout 31.102            # Download spec → !INCOMING/
  --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"
  [--release 18.0]                      # Specific release (default: latest)
```

## Cache & Storage

- Config: `D:\ObsidianDB\3gpp-crawler.toml` (auto-discovered)
- Cache: `D:\ObsidianDB\.3gpp-crawler\` (`.gitignore`d)
  - `3gpp_crawler.db` — spec metadata
  - `http-cache.sqlite3` — HTTP cache

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
