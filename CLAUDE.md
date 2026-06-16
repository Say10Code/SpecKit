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

## Приоритет скиллов — КРИТИЧЕСКИ

**Всегда используй проектные скиллы (`.claude/skills/`) перед глобальными (`~/.claude/skills/`).** Глобальные скиллы (3gpp-skill, deep-research, terminal-log-analyzer и др.) — вспомогательные; они НЕ заменяют пайплайн speckit.

| Задача | ✅ Правильный путь | ❌ Неправильный путь |
|---|---|---|
| Research по спецификациям | `/research` → Researcher → SpecDownloader → SpecExtractor → Author → Reviewer | Глобальный `deep-research` или `3gpp-skill` в обход speckit |
| Скачать спецификацию | `/spec-download 31.102` → загрузить, извлечь, написать страницу | Ответ из training data без загрузки эталонного текста |
| Проверить факты | `/review` → Reviewer v3 (гибридная проверка: TXT/MD/JSON) | Проверка по памяти без сверки с `specs-extracted/` |
| Любой 3GPP-вопрос | Сначала `python -m _pipeline registry suggest "<тема>"` → скачать нужные спецификации → извлечь → ресерч | Глобальный `3gpp-skill` без загрузки спецификаций |

**Правило**: если ответ можно улучшить эталонным текстом из `specs-extracted/` — ты **обязан** сначала загрузить спецификации через пайплайн. Только если скачивание невозможно (FTP заблокирован, ZIP fallback тоже не сработал) — используй knowledge из training data с явным предупреждением пользователю.

## First run after clone

При первом запуске после `git clone` проект находится в состоянии «Core-only»: движок есть, данных нет. Выполни этот чек-лист:

```
[ ] Сообщи пользователю: "Data отсутствует (wiki/, Specifications/, specs-extracted/).
    Для полноценной работы нужно скопировать Data с основного ПК или скачать спецификации."

[ ] Проверить Python-окружение:
    .venv\Scripts\python.exe -m _pipeline status

[ ] Проверить доступ к 3GPP FTP:
    .venv\Scripts\python.exe -m _pipeline download 31.102
    - DOCX HTTP 200 → ок
    - DOCX HTTP 403 → ZIP-fallback сработает автоматически (v4.2.2+)
    - DOCX HTTP 403 + ZIP HTTP 403 → FTP недоступен

[ ] Проверить WhatTheSpec API:
    .venv\Scripts\python.exe -m _pipeline metadata fetch 31.102
    - Успешно → metadata cache работает
    - Ошибка сети → проверить прокси (см. ниже)

[ ] Обход прокси (Windows):
    Если pip/uv/python не могут соединиться с интернетом:
    $env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:NO_PROXY = "*"
    Причина: системный прокси 127.0.0.1:2080 может быть включён, но не запущен.
```

## Ограничения

1. **Core vs Data**: Core (`.claude/`, `_pipeline/`, `_tech/`) — изменяй. Data (`wiki/`, `Specifications/`, `specs-extracted/`) — изменяй через агентов. Карта: [[STRUCTURE.md]]
2. Никогда не изменяй `Specifications/` вне `!INCOMING/` и `Clippings/`
3. Все wikilinks с префиксом `wiki/`
4. После каждого изменения в `wiki/` выполняй `/lint`
5. Полный frontmatter на каждой странице
6. Перед созданием страницы проверь — нет ли уже такой
7. Provenance-пометки на всех фактологических утверждениях
8. Язык ответа: русский. Технические термины: английский.
9. **Приоритет проектных скиллов** (см. секцию выше): `/research`, `/spec-download`, `/review`, `/ingest` — основной инструментарий. Глобальные скиллы — только если проектные недоступны.
