# ObsidianDB — Архитектура v2

> **Аудит**: 2026-06-13 01:30 — полный анализ всех компонентов
> **Состояние**: Фаза 5 (Automation) — active
> **Беклог**: `BACKLOG.md`

---

## 1. Архитектурная схема

```
                        ┌─────────────────────┐
                        │     CLAUDE.md       │  Главный диспетчер (240 строк)
                        │  (Main Agent)        │
                        └──────────┬──────────┘
                                   │
          ┌────────────────────────┼──────────────────────────┐
          │                        │                          │
   ┌──────▼──────┐          ┌──────▼──────┐           ┌──────▼──────┐
   │   SKILLS    │          │   AGENTS    │           │    DATA     │
   │ (pipelines) │          │  (workers)  │           │  (storage)  │
   └──────┬──────┘          └──────┬──────┘           └──────┬──────┘
          │                        │                          │
   ┌──────┴──────────┐     ┌───────┴──────────┐       ┌──────┴──────────┐
   │ 6 skills        │     │ 8 agents         │       │ 3 слоя данных   │
   │ orchestrators   │     │ narrow experts   │       │ read/write/lock │
   └─────────────────┘     └──────────────────┘       └─────────────────┘
```

---

## 2. 8 Агентов — матрица ответственности

| # | Агент | Файл | Триггер | Вход → Выход | Ключевое правило |
|---|---|---|---|---|---|
| 1 | **SpecDownloader** | `specdownloader.md` | `/spec-download`, запрос | номер TS → `!INCOMING/Specs/archive/` .docx | `cd D:\ObsidianDB` перед spec-crawler |
| 2 | **Librarian** | `librarian.md` | появление файлов в `!INCOMING/` | `!INCOMING/` → каталог `Specifications/<тема>/` | flatten вложенной структуры от spec-crawler |
| 3 | **Author** | `author.md` | `/ingest`, создание страницы | материал → `wiki/` .md + frontmatter | шаблоны `.obsidian/templates/`, provenance-пометки |
| 4 | **Reviewer v3** | `reviewer.md` | `/review`, после Author | wiki-страница → отчёт (CRITICAL/HIGH/MEDIUM/LOW) | **гибридный Pass 1**: TXT Grep / JSON lookup / MD read |
| 5 | **Linker** | `linker.md` | `/lint` (сироты), `/ingest` шаг 6 | `wiki/` → предложения wikilinks | ≥3 входящих, ≥3 исходящих на страницу |
| 6 | **Researcher** | `researcher.md` | запрос на исследование | тема + источники → `wiki/research/` (15-50 KB) | 5-20 источников, Mermaid, таблицы |
| 7 | **Formatter** | `formatter.md` | `/format-html` | `wiki/*.md` → `outputs/*.html` | тёмная тема, Mermaid literal `>`, callouts |
| 8 | **SpecExtractor v2** | `specextractor.md` | первый запуск, новый PDF | PDF → `specs-extracted/*.txt` + `*.md` + `*.json` | **dual**: PyPDF2 (все) + Docling (3GPP/ETSI) |

---

## 3. 6 Skills — оркестрационные пайплайны

| # | Skill | Триггер | Задействованные агенты | Шаги |
|---|---|---|---|---|
| 1 | **/spec-download** | `/spec-download 31.102` | SpecDownloader → Librarian → Author → Linker → SpecExtractor | crawl → checkout → flatten → /ingest → /lint → Roadmap |
| 2 | **/ingest** | `/ingest` | Author (3×) + Linker | read → summary → concepts → entities → synthesis → links → Roadmap → /lint |
| 3 | **/review** | `/review` | Reviewer (Pass 1+2) + Linker (Pass 3) | TXT/MD/JSON check → structure → connectivity → verdict |
| 4 | **/lint** | после каждого изменения | Grep + Glob + Read | битые ссылки → сироты → frontmatter → противоречия → пробелы |
| 5 | **/format-html** | `/format-html` | Formatter | MD → HTML (Mermaid, callouts, dark theme) |
| 6 | **/roadmap** | `/roadmap` | Read-only | проверка статистики → согласованность → приоритеты |

---

## 4. Пайплайны данных

### 4.1 INCOMING Pipeline (2 входа)

```
ВХОД A: Ручной                      ВХОД B: spec-crawler
Пользователь кладёт PDF             spec-crawler checkout 31.102
    │                                      │
    ▼                                      ▼
!INCOMING/ts_xxx.pdf              !INCOMING/Specs/archive/31_series/31.102/31102-j40.docx
    │                                      │
    └──────────────┬───────────────────────┘
                   ▼
            LIBRARIAN
         • Сканирование !INCOMING/
         • Путь A: сравнить имя+размер → дубликат? → !double/
         • Путь B: пройти Specs/archive/ → flatten в Specifications/<тема>/
         • Сортировка: номер серии → тематическая директория
                   │
                   ▼
              /ingest SKILL
         • Author: summary → concepts → entities → synthesis
         • Linker: связи
         • Обновление wiki/index.md, Roadmap
                   │
                   ▼
              /lint SKILL
         • 0 битых ссылок, 0 сирот → ОК
         • Иначе → исправить → /lint повторно
                   │
                   ▼
            SPECEXTRACTOR
         • Метод A: PyPDF2 (все PDF) → specs-extracted/*.txt
         • Метод B: Docling (3GPP PDF) → specs-extracted/3GPP/*/md+json
```

### 4.2 Review Pipeline (гибридный)

```
/wiki/страница.md
    │
    ▼
REVIEWER Pass 1: Техническая точность
    │
    ├── FID/CLA/SW? → TXT Grep (быстро, надёжно)
    ├── Таблица/структура? → JSON lookup → MD read (таблицы сохранены)
    ├── Контекст/описание? → MD read (структурированный текст)
    └── Ничего нет? → NEEDS_SPEC
    │
    ▼
REVIEWER Pass 2: Структура
    • Frontmatter (tags, type, status, dates, sources)
    • Mermaid (literal `>`, без emoji, без box-drawing)
    • Callouts, заголовки, длина разделов
    │
    ▼
LINKER Pass 3: Связность
    • ≥3 inbound links, ≥3 outbound links
    • Предложить мосты между кластерами
    │
    ▼
ОТЧЁТ: CRITICAL / HIGH / MEDIUM / LOW / NEEDS_SPEC → Pass / Fail / Needs Specs
```

### 4.3 Extraction Pipeline (dual)

```
PDF в Specifications/
    │
    ├── 3GPP TS/TR (31.xxx, 33.xxx, 35.xxx)?
    │       │
    │       ├── DOCLING (Метод B)           ← Новый
    │       │   • spec-crawler crawl <номер>
    │       │   • workspace create + add + process
    │       │   • → specs-extracted/3GPP/<номер>/<релиз>/*.md + *.json
    │       │   • GPU: ~1.5 мин/368 стр (RTX 3060)
    │       │   • CPU: ~3 мин/368 стр
    │       │   • ⚠️ std::bad_alloc на отдельных страницах (косметика)
    │       │
    │       └── PYPDF2 (Метод A)           ← Fallback всегда
    │           • PdfReader → .txt
    │           • → specs-extracted/<категория>/*.txt
    │
    └── Остальные (GSMA, ISO, Books, ...)?
            │
            └── PYPDF2 (Метод A)           ← Единственный
                • → specs-extracted/<категория>/*.txt
```

---

## 5. Файловая структура (актуально)

```
D:\ObsidianDB\
├── CLAUDE.md                       ← Главный AI-контекст (240 строк)
├── Roadmap.md                      ← Дорожная карта + мастер-список
├── 3gpp-crawler.toml               ← Конфиг spec-crawler (cache_dir)
├── .gitignore                      ← .3gpp-crawler/, сессии, Python
├── Добро пожаловать.md
│
├── Specifications/                 ← 📄 65 PDF + 8 TXT/HTML в 11 папках
│   ├── !INCOMING/                  ← Вход (ручной + spec-crawler)
│   ├── !double/                    ← Дубликаты (24)
│   ├── ETSI_3GPP/                  ← CAT_STK, GSM_Legacy, Numbering, OTA, Security, Test_Conformance, UICC, UICC_API, USIM
│   ├── Books/  eSIM/  GlobalPlatform/  ISO7816_Analysis/
│   ├── JavaCard/  Manuals/  Papers/  Tutorials/
│   └── Спецификации/               ← ⚠️ СТАРАЯ копия (Obsidian не дал удалить)
│
├── specs-extracted/                ← 📄 Эталонные тексты (58 TXT + 16 MD+JSON)
│   ├── INDEX.md                    ← Карта: главы, таблицы, FID
│   ├── .meta.json                  ← Метрики извлечения
│   ├── 3GPP/                       ← 🆕 11 спецификаций (MD+JSON per release)
│   │   ├── 31.101/19.0/  31.102/{18.9,19.4}/  31.111/19.3/
│   │   ├── 31.121/18.5/  31.124/18.6/  31.130/19.2/  31.213/18.4/
│   │   └── 33.102/19.1/  33.401/19.2/  35.206/19.0/
│   ├── ETSI/                       ← 🆕 5 спецификаций (MD+JSON)
│   │   └── gsm11-11/  ts_101476v080500p/  ts_102223v180200p/  ts_151011v041500p/  ts_151014v040100p/
│   └── ETSI_3GPP/ Books/ eSIM/ ... ← 58 TXT (PyPDF2)
│
├── wiki/                           ← 📝 База знаний (129 .md + 7 index)
│   ├── index.md                    ← Хаб
│   ├── concepts/    (25)           ← Фундаментальные идеи
│   ├── entities/    (8)            ← Организации
│   ├── summaries/   (49)           ← Конспекты источников
│   ├── syntheses/   (31)           ← Кросс-анализ и гайды
│   ├── reference/   (6)            ← Справочные таблицы
│   └── research/    (10)           ← Глубокие исследования
│
├── notes/                          ← 📝 Заметки (4)
├── outputs/                        ← 📝 Отчёты, HTML
├── Clippings/                      ← 🔒 Read-only
│
├── .claude/                        ← 🔒 AI-инфраструктура
│   ├── agents/     (8)             ← System prompts
│   ├── skills/     (6)             ← Skills
│   ├── commands/                   ← Пользовательские команды
│   ├── settings.local.json         ← Permissions
│   └── CLAUDE.md                   ← ⚠️ УСТАРЕЛ (нет spec-download, нет Docling)
│
├── .claudian/                      ← 🔒 Сессии
├── .obsidian/                      ← 🔒 Obsidian config
├── .3gpp-crawler/                  ← 🔒 Кэш и БД (.gitignore)
│   ├── 3gpp_crawler.db             ← Метаданные спецификаций 3GPP
│   ├── http-cache.sqlite3
│   └── wiki/default/sources/       ← Docling workspace output
│
├── 3gpp-crawler/                   ← 📦 Исходники (локальная копия)
└── _tech/                          ← 📐 Техническая документация
    ├── INDEX.md                    ← Индекс
    ├── BACKLOG.md                  ← Активный беклог (8 задач)
    ├── ARCHITECTURE-v2.md          ← Этот документ
    ├── ARCHITECTURE.md             ← v1.0 (предыдущая версия)
    ├── IMPROVEMENT_PLAN.md         ← План улучшений
    ├── 3gpp-crawler-integration-plan.md
    ├── 3gpp-crawler-build-integration-plan.md
    ├── specs-extracted-migration-plan.md
    ├── specs-directory-architecture.md
    ├── cyrillic-rename-plan.md
    ├── diagrams/        (5)        ← Mermaid-диаграммы
    ├── scripts/         (2)        ← docling_batch, bench_cpu_vs_gpu
    └── benchmarks/      (3)        ← benchmark_b3_result.json
```

---

## 6. Технический стек

| Слой | Технология | Версия | Статус |
|---|---|---|---|
| **AI-оркестрация** | Claude Code (Opus 4.8) | — | ✅ |
| **Python** | CPython | 3.13.13 | ✅ |
| **Менеджер пакетов** | uv | 0.11.21 | ✅ |
| **ML-фреймворк** | PyTorch CUDA | 2.12.0+cu126 | ✅ RTX 3060 |
| **PDF-извлечение (legacy)** | PyPDF2 | — | ✅ все PDF |
| **PDF-извлечение (ML)** | Docling | 2.102.0 | ✅ 3GPP/ETSI |
| **PDF-рендер (Docling)** | pypdfium2 | 5.9.0 | ⚠️ bad_alloc на стр. 67+ |
| **Office-конвертация** | LibreOffice | 26.2.4.2 | ✅ soffice.exe |
| **Скачивание спец.** | spec-crawler | v0.0.1 (dev) | ✅ WhatTheSpec + 3GPP FTP |
| **Mermaid** | mermaid.js | v10 (CDN) | ✅ |
| **Obsidian** | Obsidian | — | ✅ |

---

## 7. GPU B3 Benchmark — итоги

| Тест | CPU | GPU (RTX 3060) | Speedup | MD качество |
|---|---|---|---|---|
| TS 35.206 (106 стр.) | 175 с | 73 с | **2.4×** | Идентично |
| TS 31.130 (28 стр.) | 114 с | 27 с | **4.2×** | Идентично |
| Batch 3 док. (173 стр.) | 319 с | 122 с | **2.6×** | Идентично |

| Параметр | Значение |
|---|---|
| `generate_picture_images` | `False` (ключевой фикс OOM) |
| `images_scale` | `1.0` (B8 fix) |
| `bad_alloc` предупреждений | 162 (страницы с диаграммами — пропускаются,不影响 output) |
| MD CPU vs GPU | **Бит-в-бит идентично** |

---

## 8. Обнаруженные расхождения

| # | Где | Проблема | Серьёзность |
|---|---|---|---|
| **D1** | `.claude/CLAUDE.md` | "5 skills" → должно быть **6** (+spec-download) | 🟡 P1 |
| **D2** | `.claude/CLAUDE.md` | "Спецификации/" → должно быть **Specifications/** | 🟡 P1 |
| **D3** | `.claude/CLAUDE.md` | "58 текстовых копий" → должно быть **58 TXT + 16 MD/JSON** | 🟢 P2 |
| **D4** | `Reviewer agent` | Ссылается на `Спецификации/` в шагах | 🟡 P1 |
| **D5** | `SpecExtractor agent` | Ссылается на `Спецификации/` в путях | 🟡 P1 |
| **D6** | `Librarian agent` | Ссылается на `Спецификации/` в путях | 🟡 P1 |
| **D7** | `SpecDownloader agent` | Ссылается на `Спецификации/` в путях | 🟡 P1 |
| **D8** | `spec-download skill` | Ссылается на `Спецификации/` в путях | 🟡 P1 |
| **D9** | `specs-extracted/INDEX.md` | Не отражает `3GPP/` и `ETSI/` структуру | 🟢 P2 |
| **D10** | `outputs/STATUS_AND_PLAN.md` | Устаревшие цифры wiki | 🔵 P3 |
| **D11** | `Specifications/Спецификации/` | Старая копия папки (Obsidian блокирует удаление) | 🟢 P2 |
| **D12** | `docling pipeline.py` | `bad_alloc` на стр. 67+ при любом `images_scale` | 🟡 P1 |
| **D13** | `_tech/ARCHITECTURE.md` | v1.0 устарела (7 агентов, нет Docling, нет spec-download) | 🟢 P2 |

---

## 9. План улучшения архитектуры

### 🔴 P0 — Срочно (эта сессия)

| # | Задача | Файлы |
|---|---|---|
| **A1** | Обновить `.claude/CLAUDE.md`: 6 skills, 8 agents, актуальные пути | 1 файл |
| **A2** | Починить `Спецификации` → `Specifications` в 4 агентах + 1 skill | 5 файлов |
| **A3** | Удалить старую `Спецификации/` директорию | `Remove-Item` (после закрытия Obsidian) |

### 🟡 P1 — Важно (следующая сессия)

| # | Задача | Файлы |
|---|---|---|
| **A4** | Исследовать `bad_alloc` в pypdfium2 — найти причину и обход | `pipeline.py`, бенчмарк |
| **A5** | Обновить `specs-extracted/INDEX.md`: Format колонка, 3GPP/ETSI | 1 файл |
| **A6** | Обновить `outputs/STATUS_AND_PLAN.md`: актуальные цифры | 1 файл |

### 🟢 P2 — Планово

| # | Задача |
|---|---|
| **A7** | Завершить ETSI Docling миграцию (21 PDF) после A2+A3 |
| **A8** | Модуляризировать CLAUDE.md (240 строк → includes) |
| **A9** | Git init |
| **A10** | Frontmatter валидатор (`check_frontmatter.py`) |

---

## 10. Беклог (из BACKLOG.md)

| # | Задача | Статус |
|---|---|---|
| B1 | `Спецификации` → `Specifications` в коде | 🔄 90 файлов обновлено, 5 агентов осталось |
| B2 | PyTorch CUDA | ✅ RTX 3060 активирован |
| B3 | CPU vs GPU бенчмарк | ✅ 2.4-4.2× speedup |
| B4 | ETSI миграция (21 PDF) | ⬜ |
| B5 | Обновить CLAUDE.md | ⬜ |
| B6 | Обновить specs-extracted/INDEX.md | ⬜ |
| B7 | Обновить outputs/STATUS_AND_PLAN.md | ⬜ |
| B8 | Починить `images_scale` OOM | ✅ `images_scale=1.0`, `generate_picture_images=False` |

---

*Архитектура актуальна на 2026-06-13 01:30. Беклог сохранён в `BACKLOG.md`. Жду подтверждения перед реализацией.*
