# STRUCTURE — карта проекта

> Быстрый ответ на вопрос «где что лежит»

---

## Как ориентироваться

```
D:\ObsidianDB\
│
├── 🧠 CORE — движок (версионируется в git, 234 файла)
│   │  _префикс = Python-пакет или инженерная документация
│   │  .префикс = конфигурация (скрытая в проводнике)
│   │
│   ├── .claude/          AI-интеллект (8 агентов + 7 скиллов + 6 includes)
│   ├── .obsidian/        Конфиг Obsidian (шаблоны, плагины, тема)
│   ├── _pipeline/        speckit: скачивание + извлечение спецификаций
│   ├── _tech/            Инженерная документация (архитектура, планы, отчёты)
│   │
│   ├── CLAUDE.md         Главный диспетчер — точка входа для AI
│   ├── README.md         Описание проекта — для людей
│   ├── Roadmap.md        Дорожная карта
│   ├── STRUCTURE.md      Этот файл — навигационная карта
│   ├── pyproject.toml    Python-зависимости
│   └── uv.lock           Lock-файл окружения
│
├── 📚 DATA — хранилище знаний (НЕ в git)
│   │  без префикса = контент, с которым работают агенты
│   │
│   ├── wiki/             База знаний (130 страниц + 7 индексов)
│   ├── Specifications/   Исходные PDF/DOCX спецификаций (74 + 20)
│   ├── specs-extracted/  Эталонные тексты — TXT + MD + JSON (237 файлов)
│   ├── notes/            Заметки пользователя (5 файлов)
│   └── Clippings/        Web-clippings из Obsidian (3 файла)
│
├── ⚙️ BUILD & CACHE — генерируется, НЕ в git
│   │
│   ├── .venv/            Python-окружение (uv sync)
│   ├── .speckit/         Кэш метаданных 3GPP/ETSI (SQLite)
│   └── .git/             История версий
│
└── 📦 GENERATED — вывод пайплайнов, НЕ в git
    │
    ├── graphify-out/     Граф знаний (graph.json + GRAPH_REPORT.md)
    ├── outputs/          HTML-отчёты (Formatter)
    └── raw/              Входящие для graphify
```

## Что где

### 🧠 CORE

| Директория | Что внутри | Ключевой файл |
|---|---|---|
| `.claude/agents/` | 8 агентов: Author, Reviewer, Linker, Librarian, Researcher, Formatter, SpecDownloader, SpecExtractor | `author.md` |
| `.claude/skills/` | 7 скиллов: lint-wiki, ingest, review, format-html, roadmap-status, spec-download, research | `spec-download/SKILL.md` |
| `.claude/includes/` | 6 includes: structure, agents, skills, standards, incoming, speckit | `speckit.md` |
| `.obsidian/templates/` | 6 шаблонов: t-concept, t-entity, t-summary, t-synthesis, t-reference, t-note | |
| `_pipeline/` | 10 модулей speckit: download, metadata, extract (docx/docling/pypdf2), cli | `cli.py` |
| `_tech/architecture/` | Архитектура v3 + архив v1-v2 | `ARCHITECTURE-v3.md` |
| `_tech/plans/` | 1 активный план (consolidation) + 6 в архиве | `consolidation-plan.md` |
| `_tech/reports/` | 16 отчётов: speckit-миграция, оркестрация, Core-vs-Data, аудиты, ревью | |
| `_tech/scripts/` | 13 скриптов: quality_metrics, audit_connectivity, extract_docx, ... | |
| `_tech/diagrams/` | 5 Mermaid-диаграмм | `agent-interactions.md` |
| `_tech/benchmarks/` | 5 результатов бенчмарков/метрик (JSON) | |
| `_tech/BACKLOG.md` | Беклог задач (52 завершено) | |
| `_tech/README.md` | Индекс инженерной документации | |

### 📚 DATA

| Директория | Что внутри | Кем наполняется |
|---|---|---|
| `wiki/concepts/` | Концепты (2-4 KB) | Author v2 |
| `wiki/summaries/` | Саммари спецификаций (2-5 KB) | Author v2 |
| `wiki/syntheses/` | Кросс-анализ (5-15 KB) | Author v2 |
| `wiki/entities/` | Организации/стандарты | Author v2 |
| `wiki/research/` | Глубокие исследования (15-50 KB) | Researcher |
| `wiki/reference/` | Справочные таблицы | Author v2 |
| `Specifications/!INCOMING/` | Входная точка для новых файлов | SpecDownloader, пользователь |
| `Specifications/ETSI_3GPP/` | 3GPP/ETSI спецификации (9 подпапок) | Librarian |
| `Specifications/eSIM/` | GSMA eSIM | Librarian |
| `Specifications/GlobalPlatform/` | GPC Card Spec | Librarian |
| `Specifications/ISO7816_Analysis/` | ISO/IEC 7816 | Librarian |
| `Specifications/JavaCard/` | TCA документы | Librarian |
| `Specifications/Books/` | Учебники | Пользователь |
| `specs-extracted/` | Зеркалит структуру Specifications/ | SpecExtractor |

## Как не сломать wikilinks

```
✅ Можно    — Создавать/удалять файлы внутри wiki/, Specifications/, specs-extracted/
✅ Можно    — Перемещать Core (.claude/, _pipeline/, _tech/)
✅ Можно    — Менять корневые .md (CLAUDE.md, README.md, Roadmap.md)
❌ Нельзя   — Переименовывать wiki/, Specifications/, specs-extracted/
❌ Нельзя   — Перемещать файлы МЕЖДУ директориями верхнего уровня внутри Data
```

## Соглашения

| Правило | Зачем |
|---|---|
| `_префикс` = Core | Сразу видно что это движок, а не контент |
| `.префикс` = Конфиг/кэш | Не мешается в проводнике, не коммитится (venv, speckit) |
| Без префикса = Data | Контент хранилища и сгенерированные артефакты |
| Core в git, Data нет | `.gitignore` отражает границу (см. `_tech/reports/core-vs-data-separation-analysis.md`) |
| `_tech/` для инженеров | Архитектура, планы, отчёты, скрипты — всё что нужно для развития проекта |

## Точки входа

| Ты хочешь... | Иди сюда |
|---|---|
| Понять что такое проект | `README.md` |
| Понять где что лежит | `STRUCTURE.md` (этот файл) |
| Понять как думает AI | `CLAUDE.md` → `.claude/includes/` |
| Понять архитектуру | `_tech/architecture/ARCHITECTURE-v3.md` |
| Понять что делается сейчас | `_tech/BACKLOG.md` |
| Понять куда движемся | `Roadmap.md` |
| Скачать спецификацию | `python -m _pipeline download 31.102` |
| Извлечь текст | `python -m _pipeline extract docx <путь>` |

---

*Обновлено: 2026-06-14. Структура отражает Core/Data разделение из P2-10.*
