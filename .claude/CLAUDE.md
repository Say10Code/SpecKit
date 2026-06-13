# CLAUDE.md — локальный контекст ObsidianDB

Основные инструкции: [`D:\ObsidianDB\CLAUDE.md`](../CLAUDE.md)

## Локальные ресурсы

- **Агенты** (`.claude/agents/`): Author, Reviewer v3, Linker, Librarian, Researcher, Formatter, SpecExtractor v2, SpecDownloader
- **Skills** (`.claude/skills/`): lint-wiki, ingest, review, format-html, roadmap-status, spec-download, research
- **Шаблоны** (`.obsidian/templates/`): t-concept, t-entity, t-summary, t-synthesis, t-reference, t-note
- **Сессии** (`.claudian/`): НЕ ТРОГАТЬ
- **Настройки** (`.obsidian/`, `.claude/settings.local.json`): НЕ ТРОГАТЬ без явной просьбы
- **Техническая документация**: `_tech/README.md`

## Текущее состояние

- wiki/: 129 страниц (+7 index), 100% reviewed, 0 битых ссылок
- 8 sub-agents, 7 skills
- `Specifications/`: 65 файлов в 11 директориях
- `specs-extracted/`: 58 TXT (PyPDF2) + 16 MD+JSON (Docling: 11x3GPP + 5xETSI) — гибридные форматы
- Интеграция с 3gpp-crawler: SpecDownloader + spec-crawler CLI + `3gpp-crawler.toml`
- Torch CUDA: RTX 3060 12GB, GPU speedup 2.4-4.2x CPU
- LibreOffice 26.2.4.2 установлен
- Docling fix: F1 (try/except bad_alloc в page_preprocessing_model.py)
- `Specifications/.category-map.md` — единый source of truth серия->тема
- Git: 2 коммита (`a35abfc` + `050752d`)
