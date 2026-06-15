# CLAUDE.md — локальный контекст ObsidianDB

Основные инструкции: [`D:\ObsidianDB\CLAUDE.md`](../CLAUDE.md)

## Локальные ресурсы

- **Агенты** (`.claude/agents/`): Author v2, Reviewer v3, Linker, Librarian, Researcher, Formatter, SpecExtractor v2, SpecDownloader
- **Skills** (`.claude/skills/`): lint-wiki, ingest, review, format-html, roadmap-status, spec-download, research
- **Шаблоны** (`.obsidian/templates/`): t-concept, t-entity, t-summary, t-synthesis, t-reference, t-note
- **Инклуды** (`.claude/includes/`): structure, agents, skills, standards, incoming, speckit
- **Сессии** (`.claudian/`): НЕ ТРОГАТЬ
- **Настройки** (`.obsidian/`, `.claude/settings.local.json`): НЕ ТРОГАТЬ без явной просьбы
- **Техническая документация**: `_tech/README.md`

## Текущее состояние

- wiki/: 130 страниц (+7 index), 100% reviewed, 0 битых ссылок
- 8 sub-agents, 7 skills, 6 templates, 6 includes
- `Specifications/`: 65 файлов в 11 директориях
- `specs-extracted/`: 58 TXT (PyPDF2) + 37 MD+JSON (Docling: 11x3GPP + 26xETSI) — гибридные форматы
- speckit: `_pipeline/` (10 модулей), `.venv` с CUDA, `python -m _pipeline`
- Torch CUDA: RTX 3060 12GB, GPU speedup 2.4-4.2x CPU
- LibreOffice 26.2.4.2 установлен
- Docling fix: F1 (try/except bad_alloc в page_preprocessing_model.py) + auto_patch_docling.py
- `Specifications/.category-map.md` — единый source of truth серия→тема
- PostToolUse hook: напоминание /lint после Edit/Write в wiki/
- Беклог: `_tech/BACKLOG.md` (обновлять после каждой задачи и сессии)
- Git: 9 коммитов (`0beb915` последний)
- `_pipeline/_download_spec.py`: ZIP-fallback при DOCX 403 (v4.2.2)
- **Приоритет скиллов**: см. [`CLAUDE.md`](../CLAUDE.md) — секция «Приоритет скиллов — КРИТИЧЕСК»
