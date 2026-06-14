# Core vs Data — архитектурное разделение ObsidianDB

> **Создан**: 2026-06-14 · **Аудит**: полный инвентарный анализ 12 директорий, ~10.8 GB
> **Статус**: Предложение · **Реализация**: ожидает утверждения

---

## 1. Резюме (Executive Summary)

Проект ObsidianDB смешивает две принципиально разные сущности:

| Слой | Что это | Жизненный цикл | Аналог |
|---|---|---|---|
| **Core** — Движок | AI-пайплайн обработки знаний: агенты, skills, `_pipeline`, скрипты, конфиги, шаблоны | Версионируется (git), изменяется разработчиком | Исходный код приложения |
| **Data** — Хранилище | Контент: wiki-страницы, PDF-спецификации, извлечённые тексты, заметки, клиппинги | Растёт органически, изменяется AI-агентами | База данных / файлы пользователя |

Смешение создаёт проблемы: git diff показывает и изменения кода, и новые wiki-страницы; сложно отделить «что бекапить» от «что пересобрать»; `.gitignore` содержит и `.venv/` (сборка), и `Specifications/` (пользовательские данные).

**Предложение**: оставить физическую структуру как есть (риск сломать wikilinks ×130 стр. слишком высок), но ввести **строгое логическое разделение** через:
1. Чёткий документ-манифест: что есть Core, что есть Data
2. `.gitignore`-стратегию: Core под git, Data — отдельное хранение (git-annex / отдельный репозиторий / облачный бэкап)
3. Декомиссию мёртвого груза (3gpp-crawler, .venv из git-трека)
4. Документацию в `CLAUDE.md` — чтобы агенты знали, где что лежит и почему

---

## 2. Инвентаризация: полный срез проекта

### 2.1 Размерный анализ

| Компонент | Размер | Тип | % проекта |
|---|---|---|---|
| `3gpp-crawler/` (бандл исходников) | 5,020 MB | Core (legacy) | 46.3% |
| `.venv/` (Python venv) | 4,703 MB | Core (build) | 43.4% |
| `specs-extracted/` (извлечённые тексты) | 444 MB | **Data** | 4.1% |
| `.3gpp-crawler/` (кэш + БД) | 361 MB | Core (cache) | 3.3% |
| `Specifications/` (PDF спецификации) | 181 MB | **Data** | 1.7% |
| `.git/` (git история) | 115 MB | Core (vcs) | 1.1% |
| `graphify-out/` (граф) | 10 MB | Core (generated) | 0.1% |
| `.obsidian/` (конфиг + плагины) | 6 MB | Core (config) | 0.1% |
| `wiki/` (130 страниц знаний) | 1.6 MB | **Data** | <0.1% |
| `_tech/` (архитектура, планы, скрипты) | 0.5 MB | Core | <0.1% |
| `outputs/` (сгенерированные HTML) | 0.2 MB | Data (generated) | <0.1% |
| `.claude/` (агенты, skills, includes) | 0.1 MB | Core | <0.1% |
| `_pipeline/` (speckit) | 0.1 MB | Core | <0.1% |
| `notes/` (заметки пользователя) | 0.01 MB | **Data** | <0.1% |
| `Clippings/` (web-clippings) | 0.01 MB | **Data** | <0.1% |
| `raw/` (graphify inbox) | 0 MB | Data | 0% |
| **Всего** | **~10,841 MB** | | |

**Ключевой вывод**: 93% размера проекта — это Core (движок). Из них 89% — то, что **не должно быть в git**: `.venv/` (собирается через `uv sync`), `3gpp-crawler/` (внешняя зависимость, будет удалена), `.3gpp-crawler/` (кэш).

### 2.2 Структурная карта

```
D:\ObsidianDB\
│
├── ╔══════════════════════════════════════════════════════╗
│   ║  CORE — ДВИЖОК ОБРАБОТКИ ЗНАНИЙ                    ║
│   ╚══════════════════════════════════════════════════════╝
│
├── .claude/               ← Агенты (8), Skills (7), Includes (6)
│   ├── agents/                Author, Reviewer, Librarian, Linker,
│   │                          Researcher, Formatter, SpecDownloader, SpecExtractor
│   ├── skills/                lint-wiki, ingest, review, research,
│   │                          format-html, roadmap-status, spec-download
│   ├── includes/              structure, agents, skills, standards,
│   │                          incoming, 3gpp-crawler
│   ├── scripts/               spec_download.py
│   ├── settings.local.json    Локальные настройки Claude Code
│   └── CLAUDE.md              Локальный контекст
│
├── _pipeline/             ← speckit: download + extract engine
│   ├── _resolve_spec.py       WhatTheSpec API → metadata DB
│   ├── _metadata_db.py        SQLite (2 таблицы)
│   ├── _download_spec.py      3GPP FTP download (RemoteZipFile)
│   ├── extract_docx.py        Tier 1: .docx → TXT + MD
│   ├── extract_docling.py     Tier 2: PDF → Docling MD+JSON
│   ├── extract_pypdf2.py      Tier 3: PDF → плоский TXT
│   ├── cli.py                 CLI: resolve, download, extract
│   ├── config.py              Конфигурация
│   └── __main__.py            python -m _pipeline
│
├── _tech/                 ← Инженерная документация
│   ├── architecture/          ARCHITECTURE-v3.md (+ v1, v2 в архиве)
│   ├── plans/                 consolidation-plan.md (активный)
│   ├── reports/               14 отчётов
│   ├── scripts/               13 скриптов (quality, audit, extract, etc.)
│   ├── benchmarks/            5 JSON-результатов
│   ├── diagrams/              5 Mermaid-диаграмм
│   ├── BACKLOG.md             Беклог (44/49 задач)
│   └── README.md              Индекс _tech/
│
├── .obsidian/             ← Obsidian-конфигурация
│   ├── templates/             6 шаблонов (t-concept, t-entity, ...)
│   ├── plugins/               claudian, terminal
│   └── *.json                 app, appearance, graph, core-plugins
│
├── CLAUDE.md              ← Главный диспетчер проекта (47 строк)
├── Roadmap.md             ← Дорожная карта
├── pyproject.toml          ← Python-зависимости (speckit)
├── uv.lock                 ← Lock-файл Python-окружения
├── .gitignore              ← Правила исключения
├── .graphifyignore         ← Правила исключения graphify
├── .git/                   ← Git-репозиторий (6 коммитов)
│
├── ╔══════════════════════════════════════════════════════╗
│   ║  LEGACY — ПОДЛЕЖИТ ДЕКОМИССИИ                      ║
│   ╚══════════════════════════════════════════════════════╝
│
├── 3gpp-crawler/          ← Бандл исходников (5 GB) — заменить на speckit
├── 3gpp-crawler.toml       ← Конфиг spec-crawler — удалить
├── .3gpp-crawler/          ← Кэш + БД (361 MB) — оставить как бэкап
│
├── ╔══════════════════════════════════════════════════════╗
│   ║  BUILD ARTIFACTS — НЕ КОММИТИТЬ                    ║
│   ╚══════════════════════════════════════════════════════╝
│
├── .venv/                 ← Python venv (4.7 GB) — uv sync
├── graphify-out/          ← Сгенерированный граф (10 MB)
│
├── ╔══════════════════════════════════════════════════════╗
│   ║  DATA — ОБРАБАТЫВАЕМОЕ ХРАНИЛИЩЕ ЗНАНИЙ            ║
│   ╚══════════════════════════════════════════════════════╝
│
├── wiki/                  ← База знаний (130 стр., 7 индексов)
│   ├── concepts/             Концептуальные страницы
│   ├── entities/             Сущности (EF, AID, файлы UICC)
│   ├── summaries/            Саммари спецификаций
│   ├── syntheses/            Синтез-страницы (кросс-спецификационные)
│   ├── research/             Исследовательские заметки
│   ├── reference/            Справочные материалы
│   └── index.md              Алфавитный индекс
│
├── Specifications/        ← Исходные документы (74 PDF + 20 DOCX)
│   ├── !INCOMING/            Входная точка (ручная + speckit)
│   ├── !double/              Дубликаты
│   ├── ETSI_3GPP/            3GPP/ETSI спецификации (9 подпапок)
│   ├── eSIM/                 GSMA SGP.02
│   ├── GlobalPlatform/       GPC Card Spec
│   ├── ISO7816_Analysis/     ISO/IEC 7816
│   ├── JavaCard/             TCA документы
│   ├── Books/                Учебники
│   ├── Manuals/              Руководства
│   ├── Papers/               Научные статьи
│   └── Tutorials/            Пособия
│
├── specs-extracted/       ← Извлечённые тексты (78 TXT + 86 MD + 73 JSON)
│   ├── INDEX.md              Карта форматов
│   └── */                    Зеркалит структуру Specifications/
│
├── notes/                 ← Пользовательские заметки (5 файлов)
├── Clippings/             ← Obsidian web-clippings (3 файла)
├── outputs/               ← Сгенерированные HTML-отчёты (4 файла)
├── raw/                   ← Входящие для graphify (пусто)
└── Добро пожаловать.md    ← Welcome-страница Obsidian
```

---

## 3. Классификация: что есть что и почему

### 3.1 Core — Движок (93% размера, ~1,000 файлов)

Это **инструмент**, который обрабатывает знания. Он версионируется, изменяется разработчиком, может быть пересобран с нуля.

| Подкатегория | Компоненты | Размер | В git? |
|---|---|---|---|
| **AI-интеллект** | `.claude/agents/` (8), `.claude/skills/` (7), `.claude/includes/` (6) | 0.1 MB | ✅ Да |
| **Конвейер загрузки** | `_pipeline/` (speckit: 10 модулей) | 0.1 MB | ✅ Да |
| **Скрипты** | `_tech/scripts/` (13 .py) | 0.3 MB | ✅ Да |
| **Архитектура** | `_tech/architecture/`, `_tech/plans/`, `_tech/reports/` | 0.2 MB | ✅ Да |
| **Конфигурация** | `.obsidian/`, `CLAUDE.md`, `.claude/settings.local.json`, `pyproject.toml` | 6.1 MB | ⚠️ Частично |
| **Шаблоны** | `.obsidian/templates/` (6) | 0.01 MB | ✅ Да |
| **Беклог** | `_tech/BACKLOG.md`, `Roadmap.md` | 0.03 MB | ✅ Да |
| **Git** | `.git/` | 115 MB | ✅ VCS |
| **Legacy (декомиссия)** | `3gpp-crawler/`, `3gpp-crawler.toml`, `.3gpp-crawler/` | 5,381 MB | ❌ Нет |
| **Build** | `.venv/` | 4,703 MB | ❌ Нет |
| **Сгенерированное** | `graphify-out/` | 10 MB | ❌ Нет |

### 3.2 Data — Хранилище (7% размера, ~400 файлов)

Это **контент**, который обрабатывается движком. Он растёт органически, изменяется AI-агентами, не пересобирается.

| Подкатегория | Компоненты | Размер | В git? |
|---|---|---|---|
| **База знаний** | `wiki/` (130 страниц + 7 индексов) | 1.6 MB | ✅ Да (контент) |
| **Исходные спецификации** | `Specifications/` (74 PDF + 20 DOCX) | 181 MB | ⚠️ LFS/отдельно |
| **Извлечённые тексты** | `specs-extracted/` (78 TXT + 86 MD + 73 JSON) | 444 MB | ⚠️ Кэш/отдельно |
| **Заметки** | `notes/` (5 .md) | 0.01 MB | ✅ Да |
| **Clippings** | `Clippings/` (3 .md) | 0.01 MB | ✅ Да |
| **Сгенерированные отчёты** | `outputs/` (4 HTML) | 0.2 MB | ❌ Нет |
| **Inbox** | `raw/` (пусто) | 0 MB | ❌ Нет |

---

## 4. Проблемы текущего смешения

### 4.1 Git diff зашумлён

Один `git diff` показывает и изменение агента (`core`), и новую wiki-страницу (`data`), и обновление `specs-extracted/INDEX.md` (`data`). Невозможно понять: это изменился код или контент?

### 4.2 Спецификации в git?

`Specifications/` (181 MB PDF) сейчас **не в .gitignore**. При `git add .` они попадут в репозиторий. Это плохо:
- PDF — бинарные файлы, git не diff'ит их эффективно
- Раздувают репозиторий (181 MB и будут расти)
- Нарушают лицензию? (3GPP/ETSI спецификации — copyrighted)

### 4.3 specs-extracted/ как кэш или артефакт?

`specs-extracted/` (444 MB) — это производные данные (извлечённые TXT/MD/JSON). Они **восстанавливаемые**: можно перезапустить извлечение из `Specifications/` и получить тот же результат. Держать их в git нет смысла.

Но они же — эталонные тексты для Reviewer! Reviewer Grep'ает по ним для проверки фактов. Значит, они должны быть **доступны**, но не обязательно в git.

### 4.4 .venv/ и 3gpp-crawler/ — мёртвый груз

`.venv/` (4.7 GB) генерируется `uv sync`. `3gpp-crawler/` (5 GB) — внешний проект, который будет заменён на speckit. Вместе это 9.7 GB — **89% размера проекта** — которые не должны здесь находиться.

### 4.5 Агенты не знают границ

Сейчас агенты ходят везде: Author пишет в `wiki/` (Data) и читает `Specifications/` (Data), SpecDownloader вызывает `_pipeline/` (Core), Librarian двигает файлы в `Specifications/` (Data). Это нормально — движок и должен обрабатывать данные. Но нет явного контракта: «это Data, сюда пишут только агенты Author и Librarian», «это Core, сюда пишет только разработчик».

---

## 5. Предлагаемое разделение

### 5.1 Принципы

1. **Физическая структура не меняется** — риск сломать wikilinks ×130 страниц слишком высок
2. **Логическое разделение фиксируется в документации** — `CLAUDE.md`, `_tech/README.md`, `.gitignore`
3. **Git-стратегия** — Core под version control, Data — под отдельное управление
4. **Мёртвый груз удаляется** — 3gpp-crawler, .venv переносятся вовне
5. **Агенты получают явный контракт** — что читать, куда писать

### 5.2 Git-стратегия

```gitignore
# === BUILD ARTIFACTS (генерируются) ===
.venv/
graphify-out/
__pycache__/
*.pyc

# === LEGACY (декомиссия) ===
3gpp-crawler/
3gpp-crawler.toml
.3gpp-crawler/

# === DATA — PDF спецификации (бинарные, copyrighted) ===
Specifications/
!Specifications/!INCOMING/.gitkeep
!Specifications/!double/.gitkeep
!Specifications/.category-map.md

# === DATA — Извлечённые тексты (восстанавливаемые) ===
specs-extracted/
!specs-extracted/INDEX.md

# === DATA — Сгенерированные отчёты ===
outputs/

# === DATA — Пользовательские заметки ===
notes/
raw/

# === SESSION DATA ===
.claudian/sessions/
```

**Что остаётся в git (Core)**:
- `.claude/` — агенты, skills, includes, настройки
- `_pipeline/` — speckit
- `_tech/` — архитектура, планы, скрипты, беклог
- `.obsidian/` — конфиг хранилища (шаблоны, плагины, настройки)
- `CLAUDE.md`, `Roadmap.md`, `pyproject.toml`, `uv.lock`
- `wiki/` — база знаний (текстовый контент, хорошо diff'ится)
- `Clippings/` — текстовые клиппинги
- `.gitignore`, `.graphifyignore`

**Что вне git (Data — отдельное хранение)**:
- `Specifications/` → Git LFS или отдельный бэкап-репозиторий
- `specs-extracted/` → восстанавливаемые; INDEX.md в git для отслеживания состава
- `notes/` → пользовательские, не часть проекта
- `outputs/` → сгенерированные, не коммитить

### 5.3 Контракт для агентов

```markdown
## Разрешённые операции

| Агент | Читает (Data) | Пишет (Data) | Читает (Core) |
|---|---|---|---|
| Author | Specifications/, specs-extracted/ | wiki/ | _pipeline/ |
| Reviewer | specs-extracted/, wiki/ | wiki/ (исправления) | — |
| Librarian | Specifications/!INCOMING/ | Specifications/ (сортировка) | .category-map.md |
| Linker | wiki/ | wiki/ (wikilinks) | — |
| SpecDownloader | — | Specifications/!INCOMING/ | _pipeline/ |
| SpecExtractor | Specifications/ | specs-extracted/ | _pipeline/ |
| Researcher | wiki/, specs-extracted/ | wiki/research/ | — |
| Formatter | wiki/ | outputs/ | — |
```

### 5.4 Новая карта директорий (логическая)

```
D:\ObsidianDB\
│
├── ═══════════  CORE — ДВИЖОК  ═══════════
│   │              (git versioned)
│   │
│   ├── .claude/            ← AI: агенты, skills, includes, настройки
│   ├── _pipeline/          ← speckit: download + extract
│   ├── _tech/              ← Инженерная документация
│   ├── .obsidian/          ← Obsidian-конфигурация
│   ├── CLAUDE.md           ← Главный диспетчер
│   ├── Roadmap.md          ← Дорожная карта
│   ├── pyproject.toml      ← Python-окружение
│   ├── uv.lock
│   ├── .gitignore
│   └── .git/
│
├── ═══════════  DATA — ХРАНИЛИЩЕ  ═══════════
│   │              (отдельный бэкап / Git LFS)
│   │
│   ├── wiki/               ← База знаний (130 стр.)
│   ├── Specifications/     ← Исходные PDF (74 шт., 181 MB)
│   ├── specs-extracted/    ← Извлечённые тексты (237 файлов)
│   ├── notes/              ← Заметки пользователя
│   ├── Clippings/          ← Web-clippings
│   └── Добро пожаловать.md
│
├── ═══════════  GENERATED / BUILD  ═══════════
│   │              (в .gitignore)
│   │
│   ├── .venv/              ← Python (uv sync)
│   ├── graphify-out/       ← Граф
│   ├── outputs/            ← HTML-отчёты
│   └── raw/                ← graphify inbox
│
└── ═══════════  LEGACY (pending decommission)  ═══════════
    │              (в .gitignore)
    │
    ├── 3gpp-crawler/       ← 5 GB — заменить на _pipeline/
    ├── 3gpp-crawler.toml   ← Удалить после speckit
    └── .3gpp-crawler/      ← Оставить как бэкап метаданных
```

---

## 6. План действий

### Фаза 1: Документирование (сейчас, 10 мин) ✅

- [x] Создать этот отчёт (`_tech/reports/core-vs-data-separation-analysis.md`)
- [ ] Обновить `CLAUDE.md` — добавить секцию «Core vs Data»
- [ ] Обновить `_tech/README.md` — отразить разделение

### Фаза 2: .gitignore (15 мин)

- [ ] Применить новую `.gitignore`-стратегию (Секция 5.2)
- [ ] `git rm --cached` для уже закоммиченных data-файлов (если есть)
- [ ] Проверить: `git status` показывает только Core

### Фаза 3: Декомиссия legacy (после P2-9, ~2h)

- [ ] Завершить speckit (P2-9): `speckit.toml`, утилиты, замена в агентах
- [ ] `uv tool uninstall 3gpp-crawler` (CLI)
- [ ] Удалить `3gpp-crawler/` из проекта (5 GB)
- [ ] Удалить `3gpp-crawler.toml`
- [ ] `.3gpp-crawler/` оставить как read-only бэкап (или удалить)
- [ ] Обновить `.claude/includes/3gpp-crawler.md` → отразить статус «decommissioned»

### Фаза 4: Data-стратегия (будущее)

- [ ] Решить: Git LFS для Specifications/? Или отдельный бэкап?
- [ ] Решить: specs-extracted/ в git (только INDEX.md) или полностью вне?
- [ ] Настроить периодический бэкап Data-директорий

---

## 7. Риски

| Риск | Вероятность | Митигация |
|---|---|---|
| Wikilinks сломаются при перемещении файлов | Высокая | **Ничего не перемещаем**, только логическое разделение |
| Большой `.gitignore` сломает Obsidian | Низкая | Obsidian работает с файловой системой, .gitignore влияет только на git |
| Удаление 3gpp-crawler сломает пайплайн | Средняя | Только после полной верификации _pipeline/ (P2-9) |
| Потеря данных при `git rm --cached` | Низкая | `--cached` удаляет только из индекса, не с диска |
| PDF спецификации нужны агентам оффлайн | Высокая | Data должен быть доступен локально, но не в git |

---

## 8. Метрики после разделения

| Метрика | До | После |
|---|---|---|
| Размер проекта | 10,841 MB | ~130 MB (Core + git) |
| Файлов в git | ~10,000+ | ~500 |
| Git clone время | ~5 мин | ~5 сек |
| `Specifications/` в git | ⚠️ Под риском | ❌ Исключены |
| Ясность: «где код, где данные?» | Размыто | ✅ Документировано |

---

*Отчёт создан 2026-06-14. Требует утверждения перед реализацией Фаз 2-4.*
