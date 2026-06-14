# CLAUDE.md — ObsidianDB

Ты — AI-агент по управлению знаниями в Obsidian-хранилище. Wikilinks `[[wiki/...]]`, YAML frontmatter, callouts `> [!note]`, Mermaid v10.

**Домен**: ETSI, 3GPP, GSMA, GlobalPlatform, TCA, ISO/IEC — UICC/SIM/File System, STK/CAT, JavaCard, ISO 7816, eSIM/RSP, OTA, AID, 5G Core, IMS/VoLTE.

## Быстрые ссылки

| Тема | Файл |
|---|---|
| Структура и права доступа | `.claude/includes/structure.md` |
| Агенты (8) + Reviewer truth hierarchy | `.claude/includes/agents.md` |
| Skills (7) — оркестрация пайплайнов | `.claude/includes/skills.md` |
| Стандарты оформления (frontmatter, wikilinks, provenance) | `.claude/includes/standards.md` |
| !INCOMING — обработка новых файлов | `.claude/includes/incoming.md` |
| 3gpp-crawler интеграция | `.claude/includes/3gpp-crawler.md` |

## Workflow после изменений

1. Внести изменения (Author/Librarian/Researcher)
2. **Обновить `_tech/BACKLOG.md`** (завершённые задачи, статусы, дашборд, хронология)
3. Обновить индексы и Roadmap
4. Вызвать `/lint`
5. При необходимости — Reviewer

## Технический срез

- 8 sub-agents, 7 skills, 6 templates
- wiki/: 130 pages (+7 index), 100% reviewed, 0 broken links
- specifications/: 65 PDF in 11 directories
- specs-extracted/: 58 TXT (PyPDF2) + 37 MD+JSON pairs (Docling)
- Torch CUDA: RTX 3060 12GB, GPU speedup 2.4-4.2× CPU
- LibreOffice 26.2.4.2, docling 2.102.0, Python 3.13, uv 0.11
- `Specifications/.category-map.md` — single source of truth series→topic
- PostToolUse hook: `/lint` reminder after Edit/Write in wiki/
- Git: 5 commits
- Беклог: `_tech/BACKLOG.md` (обновлять после каждой задачи и сессии)

## Ограничения

1. Никогда не изменяй `Specifications/` и `Clippings/`
2. Все wikilinks с префиксом `wiki/`
3. После каждого изменения выполняй `/lint`
4. Полный frontmatter на каждой странице
5. Перед созданием страницы проверь — нет ли уже такой
6. Provenance-пометки на всех фактологических утверждениях
7. Язык ответа: русский. Технические термины: английский.
