# CLAUDE.md — ObsidianDB

Ты — AI-агент по управлению знаниями в Obsidian-хранилище. Wikilinks `[[wiki/...]]`, YAML frontmatter, callouts `> [!note]`, Mermaid v10.

**Домен**: ETSI, 3GPP, GSMA, GlobalPlatform, TCA, ISO/IEC — UICC/SIM/File System, STK/CAT, JavaCard, ISO 7816, eSIM/RSP, OTA, AID, 5G Core, IMS/VoLTE.

## Быстрые ссылки

| Тема | Файл |
|---|---|
| **Карта проекта** | [[STRUCTURE.md]] |
| **Core-манифест** | `.core-paths.md` |
| Инженерный хаб | `_tech/INDEX.md` |
| Структура и права доступа | `.claude/includes/structure.md` |
| Агенты (8) + Reviewer truth hierarchy | `.claude/includes/agents.md` |
| Skills (7) — оркестрация пайплайнов | `.claude/includes/skills.md` |
| Стандарты оформления (frontmatter, wikilinks, provenance) | `.claude/includes/standards.md` |
| !INCOMING — обработка новых файлов | `.claude/includes/incoming.md` |
| speckit (загрузка спецификаций) | `.claude/includes/speckit.md` |

## Workflow после изменений

1. Внести изменения (Author/Librarian/Researcher)
2. **Обновить `_tech/BACKLOG.md`** (завершённые задачи, статусы, дашборд, хронология)
3. Обновить индексы и Roadmap
4. Вызвать `/lint`
5. При необходимости — Reviewer

## Технический срез

- 8 sub-agents, 7 skills, 6 templates
- wiki/: 130 pages (+7 index), 100% reviewed, 0 broken links
- Specifications/: 74 PDF + 20 DOCX в 11 директориях
- specs-extracted/: 78 TXT + 86 MD + 73 JSON (гибрид)
- speckit: `_pipeline/` (10 модулей), `.venv` с CUDA, `python -m _pipeline`
- Torch CUDA: RTX 3060 12GB, GPU speedup 2.4-4.2× CPU
- LibreOffice 26.2.4.2, docling 2.102.0, Python 3.13, uv 0.11
- `Specifications/.category-map.md` — single source of truth series→topic
- PostToolUse hook: `/lint` reminder after Edit/Write in wiki/
- Git: 6 commits
- Беклог: `_tech/BACKLOG.md` (обновлять после каждой задачи и сессии)

## Ограничения

1. **Core vs Data**: Core (`.claude/`, `_pipeline/`, `_tech/`) — изменяй. Data (`wiki/`, `Specifications/`, `specs-extracted/`) — изменяй через агентов. Карта: [[STRUCTURE.md]]
2. Никогда не изменяй `Specifications/` вне `!INCOMING/` и `Clippings/`
3. Все wikilinks с префиксом `wiki/`
4. После каждого изменения в `wiki/` выполняй `/lint`
5. Полный frontmatter на каждой странице
6. Перед созданием страницы проверь — нет ли уже такой
7. Provenance-пометки на всех фактологических утверждениях
8. Язык ответа: русский. Технические термины: английский.
