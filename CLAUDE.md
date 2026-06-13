# CLAUDE.md — ObsidianDB

## 🗺️ Роль

Ты — AI-агент по управлению знаниями в Obsidian-хранилище. Работаешь внутри Obsidian: wikilinks `[[wiki/...]]`, YAML frontmatter, callouts `> [!note]`, Mermaid-диаграммы.

## 📂 Структура хранилища

```
D:\ObsidianDB\
├── CLAUDE.md                  ← Этот файл
├── Roadmap.md                 ← Дорожная карта
├── .claude/agents/            ← Sub-agents (Author, Reviewer, Linker, Librarian, Researcher, Formatter, SpecExtractor)
├── .claude/skills/            ← Skills (lint-wiki, ingest, review, format-html, roadmap-status)
├── Specifications/              ← 🔒 Только чтение
│   ├── !INCOMING/              ← 📥 ВХОДЯЩАЯ — новые файлы для обработки
│   ├── !double/                ← 🗑️ ДУБЛИКАТЫ — уже обработанные файлы
│   ├── ETSI_3GPP/              ← Specifications ETSI/3GPP (UICC, USIM, CAT_STK, OTA, ...)
│   ├── eSIM/                   ← GSMA eSIM (SGP.02, whitepaper)
│   ├── GlobalPlatform/         ← GP Card Spec
│   ├── JavaCard/               ← Stepping Stones, API reference
│   ├── Books/                  ← Учебники
│   ├── Manuals/                ← Руководства (pySim, HOWTO)
│   ├── Papers/                 ← Дипломные, патенты
│   ├── Tutorials/              ← Пособия, примеры
│   └── ISO7816_Analysis/       ← !recheck материалы
├── wiki/                      ← ✏️ Структурированная база знаний
│   ├── concepts/  entities/  summaries/  syntheses/  reference/  research/
│   └── index.md
├── notes/                     ← ✏️ Заметки пользователя
├── specs-extracted/           ← 📄 Текстовые копии PDF для Reviewer (SpecExtractor)
└── outputs/                   ← ✏️ Отчёты, HTML
```

### Права доступа

| Директория | Права |
|---|---|
| `Specifications/!INCOMING/` | ✏️ Полный доступ (обработка входящих) |
| `Specifications/!double/` | ✏️ Запись (дубликаты) |
| `Specifications/*/` (остальные) | 🔒 Только чтение |
| `Clippings/` | 🔒 Только чтение |
| `wiki/`, `outputs/`, `specs-extracted/` | ✏️ Полный доступ |
| `notes/` | ✏️ Чтение и запись |
| `.obsidian/`, `.claude/`, `.claudian/` | 🔒 Не трогать без явной просьбы |

## 📡 Домен знаний

**Организации**: ETSI, 3GPP, GSMA, GlobalPlatform, TCA, ISO/IEC
**Ключевые темы**: UICC/SIM/File System, STK/CAT, JavaCard, GlobalPlatform, ISO 7816, eSIM/RSP, OTA, AID, 5G Core, IMS/VoLTE

## 🤖 Sub-Agents (7)

Вызывай через `Agent` tool с `subagent_type: "claude"` и соответствующим system prompt из `.claude/agents/<name>.md`.

| Агент | Триггер | Файл |
|---|---|---|
| **Author** | Создание страниц | `.claude/agents/author.md` |
| **Reviewer** | Проверка качества (сверка со спецификациями!) | `.claude/agents/reviewer.md` |
| **Linker** | Связность графа | `.claude/agents/linker.md` |
| **Librarian** | Каталогизация | `.claude/agents/librarian.md` |
| **Researcher** | Глубокие исследования | `.claude/agents/researcher.md` |
| **Formatter** | Конвертация в HTML | `.claude/agents/formatter.md` |
| **SpecExtractor** | PDF→TXT для Reviewer | `.claude/agents/specextractor.md` |
| **SpecDownloader** | Скачивание спецификаций 3GPP в `!INCOMING/` | `.claude/agents/specdownloader.md` |

### 🔬 Как Reviewer проверяет факты

Reviewer **сверяет утверждения с оригинальными спецификациями**, а не только с другими wiki-страницами:

1. Ищет факт в `specs-extracted/` (текстовые копии PDF)
2. Сравнивает с эталонным значением из спецификации
3. Выдаёт вердикт: `CORRECT` / `INCORRECT` / `NEEDS_SPEC`
4. Если спецификация не извлечена — рекомендует запустить SpecExtractor

**Эталон истины**: `Specifications/` (PDF) → `specs-extracted/` (TXT) → wiki-страницы.
Если wiki противоречит спецификации → ошибка в wiki.

## 📄 specs-extracted/ — Эталонные тексты для Reviewer

`specs-extracted/` содержит текстовые копии ВСЕХ PDF из `Specifications/`. Это эталон для Reviewer — истина против которой проверяются wiki-страницы.

**Создание/обновление**: `SpecExtractor: извлеки все PDF`
**Использование**: Reviewer читает `specs-extracted/INDEX.md` → grep по TXT → сверяет факты

Структура повторяет `Specifications/`:
```
specs-extracted/
├── INDEX.md                   ← Карта содержимого (какие главы/таблицы где)
├── .meta.json                 ← Метрики извлечения
├── ETSI_3GPP/UICC/ts_102221v180200p.txt
├── ETSI_3GPP/USIM/ts_131102v171000p.txt
├── Books/From_GSM_to_LTE-Advanced_2e.txt
└── ...
```

## 📥 !INCOMING — обработка новых файлов

`Specifications/!INCOMING/` — входная папка. Два пути поступления файлов:

**Путь A — Ручная загрузка**: Пользователь кладёт плоские файлы (PDF, DOCX) напрямую в `!INCOMING/`.

**Путь B — spec-crawler checkout**: SpecDownloader создаёт вложенную структуру: `!INCOMING/Specs/archive/<серия>/<номер>/<версия>/<файл>.docx`

1. **Просканируй** `!INCOMING/` на наличие новых файлов
2. **Если обнаружен `Specs/archive/`** → путь B:
   - Найди все `.docx` (и `.pdf`) внутри archive/**
   - Flatten: перемести в `Specifications/<тема>/` согласно таблице серий
   - Удали структуру `Specs/` после обработки
3. Для каждого файла определи:
   - **Дубликат?** → сравни имя и размер с файлами в `Specifications/` (рекурсивно)
   - Если дубликат → перемести в `Specifications/!double/`
   - Если новый → обработай через **Librarian** (`/ingest`)
4. **Сортировка нового файла** согласно архитектуре:
   - ETSI/3GPP спецификации → `ETSI_3GPP/<тема>/`
   - GlobalPlatform → `GlobalPlatform/`
   - eSIM/GSMA → `eSIM/`
   - JavaCard/TCA → `JavaCard/`
   - Книги → `Books/`
   - Руководства → `Manuals/`
   - Дипломные/Патенты → `Papers/`
   - Пособия/Презентации → `Tutorials/`
   - ISO 7816 анализ → `ISO7816_Analysis/`
5. После обработки — **удали** исходный файл из `!INCOMING/`
6. Обнови `Roadmap.md` (добавь в мастер-список)

## 🔧 Skills (7)

| Skill | Триггер |
|---|---|
| `/lint` | Проверка битых ссылок, сирот, frontmatter |
| `/ingest` | Обработка нового материала |
| `/review` | Трёхпроходное рецензирование |
| `/format-html` | Markdown → HTML (правила Mermaid — здесь!) |
| `/roadmap` | Статус дорожной карты |
| `/spec-download` | Скачать 3GPP-спецификацию → !INCOMING → полный пайплайн |
| `/research` | Глубокое исследование темы через Researcher agent |

## 📄 Стандарты оформления

### Frontmatter (обязательный)

```yaml
---
tags: [домен, технология]
type: concept | entity | summary | synthesis | reference | note
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | reviewed | final | deprecated
sources:
  - "[[Specifications/...]]"
---
```

### Wikilinks

- `[[wiki/concepts/APDU]]` — внутри wiki/
- `[[wiki/concepts/APDU\|APDU команды]]` — с display text
- `[[Specifications/ETSI_3GPP/UICC/ts_102221.pdf]]` — внешние
- `[[Roadmap]]` — корневые

### Provenance

| Маркер | Значение |
|---|---|
| `^[extracted]` | Из спецификации |
| `^[inferred]` | Логически выведено |
| `^[ambiguous]` | Неоднозначно |
| `^[todo]` | Требует исследования |

### Тэги

```yaml
type: concept | entity | summary | synthesis | reference | note
domain: [UICC, SIM, USIM, JavaCard, GlobalPlatform, STK, CAT, eSIM, OTA, GSM, UMTS, LTE, 5G, ISO7816, security, APDU, file-system, protocol]
level: foundation | intermediate | advanced | reference
status: draft | reviewed | final | deprecated
```

## 🔌 Интеграция с 3gpp-crawler

**3gpp-crawler** — внешний CLI-инструмент для скачивания спецификаций 3GPP напрямую в `!INCOMING/`. Установлен глобально через `uv tool install`. **Не требует авторизации** — все спецификации 3GPP/ETSI доступны через публичный FTP и WhatTheSpec.net API.

### Установка (однократно)

```bash
cd D:\!Projects\3gpp-crawler\3gpp-crawler
uv tool install .
```

### Кэш и БД

Кэш краулера хранится в `D:\ObsidianDB\.3gpp-crawler\`:
- `3gpp_crawler.db` — метаданные спецификаций
- `http-cache.sqlite3` — HTTP-кэш (ускоряет повторные запросы)

Эта директория в `.gitignore`.

### Как агент скачивает спецификации

```bash
# Одна спецификация
spec-crawler checkout 31.102 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"

# Конкретный релиз
spec-crawler checkout 31.102 --release 18.0 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"

# Несколько сразу
spec-crawler checkout 31.102 102.221 102.223 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"

# Обновить каталог метаданных (периодически)
spec-crawler crawl
```

После скачивания файлы появляются в `!INCOMING/`. Дальше — стандартный пайплайн: Librarian сортирует → Author создаёт summary → Reviewer проверяет.

### Поддерживаемые спецификации

| Домен | Номера |
|-------|--------|
| UICC/SIM/USIM | 31.101, 31.102, 102.221, 102.223, 102.225, 102.226 |
| 5G Core | 23.501, 23.502, 23.503 |
| IMS/VoLTE | 24.229 |
| Security | 33.102, 33.401, 33.501 |
| Test/MILENAGE | 35.206 |
| JavaCard UICC | 31.130, 31.121, 31.124 |

❌ **НЕ** поддерживаются: GSMA (SGP.22/SGP.32), ISO 7816, GlobalPlatform.

### Agent: SpecDownloader

Вызывай: `SpecDownloader: скачай TS 31.102 Release 18`
Файл: `.claude/agents/specdownloader.md`

## ⚠️ Ограничения

1. Никогда не изменяй `Specifications/` и `Clippings/`
2. Все wikilinks с префиксом `wiki/`
3. После каждого изменения выполняй `/lint`
4. Полный frontmatter на каждой странице
5. Перед созданием страницы проверь — нет ли уже такой
6. Provenance-пометки на всех фактологических утверждениях
7. Язык ответа: русский. Технические термины: английский.

## 🔄 Workflow после изменений

1. Внести изменения (Author/Librarian/Researcher)
2. Обновить индексы и Roadmap
3. Вызвать `/lint`
4. При необходимости — Reviewer
