# STRUCTURE — карта проекта ObsidianDB

> Быстрый ответ на вопрос «где что лежит». Для *почему* — `.core-paths.md`.

---

## Схема

```
D:\ObsidianDB\
│
├── 🧠 CORE — движок (версионируется в git, ~240 файлов)
│   │
│   ├── .claude/            ← AI-интеллект: 8 agents + 7 skills + 6 includes
│   ├── .obsidian/          ← Obsidian config: 6 templates, плагины, тема, граф
│   ├── _pipeline/          ← speckit: download + 3-tier extraction + spec-registry
│   ├── _tech/              ← Инженерная документация: архитектура, планы, отчёты
│   │
│   ├── CLAUDE.md            ← Главный диспетчер AI (точка входа для Claude Code)
│   ├── README.md            ← Описание проекта (точка входа для людей)
│   ├── Roadmap.md           ← Дорожная карта (Management слой)
│   ├── STRUCTURE.md         ← Этот файл — навигационная карта
│   ├── .core-paths.md       ← Манифест: почему каждый Core-файл на своём месте
│   └── pyproject.toml       ← Python-зависимости (speckit)
│
├── 📚 DATA — хранилище знаний (НЕ в git)
│   │
│   ├── wiki/                ← База знаний (124 стр. + 7 индексов)
│   ├── Specifications/      ← Исходные PDF/DOCX спецификаций (74 + 16)
│   ├── specs-extracted/     ← Эталонные тексты (78 TXT + 86 MD + 70 JSON)
│   ├── notes/               ← Заметки пользователя (6 файлов)
│   └── Clippings/           ← Web-clippings из Obsidian (4 файла)
│
├── 📦 GENERATED — артефакты пайплайнов (НЕ в git)
│   │
│   ├── graphify-out/        ← Граф знаний (graph.json + GRAPH_REPORT.md)
│   ├── outputs/             ← HTML-отчёты Formatter'а (2 файла)
│   ├── raw/                 ← Inbox для graphify
│   └── _backups/            ← Data-бэкапы от backup_data.py
│
└── ⚙️ BUILD — окружение (НЕ в git)
    │
    ├── .venv/               ← Python: docling + torch + httpx (uv sync)
    ├── .speckit/            ← speckit кэш: metadata.db (120 KB)
    └── .git/                ← История версий (9 коммитов)
```

---

## Как ориентироваться

### 🧠 CORE

| Что | Где | Ключевой файл |
|---|---|---|
| **Агенты** | `.claude/agents/` | `author.md` — создаёт wiki-страницы |
| **Скиллы** | `.claude/skills/` | `spec-download/SKILL.md` — скачать + обработать |
| **Инклуды** | `.claude/includes/` | `speckit.md` — интеграция speckit |
| **Шаблоны** | `.obsidian/templates/` | 6 шаблонов: t-concept, t-entity, t-summary, ... |
| **Speckit** | `_pipeline/` | `cli.py` — `python -m _pipeline` |
| **Spec Registry** | `_pipeline/.spec-registry.md` | 99 спецификаций, 14 категорий |
| **Архитектура** | `_tech/architecture/` | `ARCHITECTURE-v3.md` — 3-tier extraction |
| **Планы** | `_tech/plans/` | `consolidation-plan.md` — единственный активный |
| **Отчёты** | `_tech/reports/` | 18 отчётов: speckit-миграция, оркестрация, аудиты |
| **Скрипты** | `_tech/scripts/` | `backup_data.py`, `sync_data.py`, quality, audit |
| **Диаграммы** | `_tech/diagrams/` | `agent-interactions.md`, `system-layers.md` |
| **Беклог** | `_tech/BACKLOG.md` | 57/62 задач завершено |
| **Индекс** | `_tech/INDEX.md` | Навигация по инженерной документации |

### 📚 DATA

| Что | Где | Кем наполняется |
|---|---|---|
| **Concepts** | `wiki/concepts/` | Author v2 |
| **Summaries** | `wiki/summaries/` | Author v2 |
| **Syntheses** | `wiki/syntheses/` | Author v2 |
| **Research** | `wiki/research/` | Researcher |
| **Reference** | `wiki/reference/` | Author v2 |
| **Entities** | `wiki/entities/` | Author v2 |
| **!INCOMING** | `Specifications/!INCOMING/` | SpecDownloader |
| **3GPP/ETSI** | `Specifications/ETSI_3GPP/` | Librarian |
| **Эталоны** | `specs-extracted/` | SpecExtractor |

### 📦 GENERATED

| Что | Где | Создаётся |
|---|---|---|
| **Граф** | `graphify-out/graph.json` | `/graphify` |
| **Отчёт графа** | `graphify-out/GRAPH_REPORT.md` | `/graphify` |
| **HTML** | `outputs/*.html` | Formatter |
| **Data-бэкапы** | `_backups/*.zip` | `backup_data.py` |

---

## Точки входа

| Хочешь... | Иди сюда |
|---|---|
| Понять что такое проект | `README.md` |
| Понять где что лежит | `STRUCTURE.md` (этот файл) |
| Понять почему так лежит | `.core-paths.md` |
| Понять как думает AI | `CLAUDE.md` → `.claude/includes/` |
| Понять архитектуру | `_tech/architecture/ARCHITECTURE-v3.md` |
| Понять что делается сейчас | `_tech/BACKLOG.md` |
| Скачать спецификацию | `python -m _pipeline download 31.102` |
| Извлечь текст | `python -m _pipeline extract docx <путь>` |
| Найти спецификацию по теме | `python -m _pipeline registry suggest "5G NR"` |

---

## Исключения Core-в-Data

Два файла физически лежат внутри Data, но являются Core и версионируются:

| Файл | Почему в Data | Почему Core |
|---|---|---|
| `Specifications/.category-map.md` | Нужен Librarian'у для сортировки — должен быть рядом с файлами | Единственный source of truth серия→тема. Обновляется вручную. Версионируется |
| `specs-extracted/INDEX.md` | Нужен Reviewer'у для выбора формата — должен быть рядом с извлечёнными текстами | Реестр доступных форматов. Обновляется SpecExtractor'ом. Версионируется |

---

*Обновлено: 2026-06-14. Синхронизировано с `.core-paths.md`. Core: 10 позиций + 4 исключения.*
