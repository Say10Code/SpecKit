# speckit Transition — глубокий анализ

> **Создан**: 2026-06-14 · **Метод**: graphify-граф (7,580 узлов) + ручная инспекция кода
> **Вопрос**: Насколько осуществлён переход с 3gpp-crawler на speckit?

---

## 1. Трёхмерная оценка перехода

Переход нельзя измерить одной цифрой. Он идёт на трёх независимых уровнях:

| Уровень | Прогресс | Что сделано | Что не сделано |
|---|---|---|---|
| **Код (движок)** | ✅ **90%** | 10 модулей `_pipeline/`, CLI с 5 командами, `.venv` с CUDA | `speckit.toml`, `index.py`, `status.py` (пустая заглушка) |
| **Интеграция (агенты)** | ❌ **0%** | Ничего | Все агенты вызывают `spec-crawler`, никто не знает про `python -m _pipeline` |
| **Декомиссия (legacy)** | ❌ **0%** | Ничего | `3gpp-crawler/` (5 GB), `3gpp-crawler.toml`, `.3gpp-crawler/` (361 MB) всё ещё на месте |

**Интегральная оценка: ~35%** (код почти готов, но никто его не использует).

---

## 2. Доказательная база

### 2.1 Граф: _pipeline/ почти не связан с 3gpp-crawler

```
_pipeline/ nodes: 78
Pipeline connections:
  _pipeline/ internal:    274  ← самодостаточен
  3gpp-crawler code:        2  ← только Docling-модули (INFERRED)
  other:                    1
```

2 соединения с 3gpp-crawler — оба INFERRED (не реальные import'ы, а семантическое сходство Docling-обёрток).

### 2.2 Агенты: spec-crawler повсюду

```
$ grep -r "spec-crawler\|3gpp-crawler" .claude/agents/ .claude/skills/
  specdownloader.md:  20+ упоминаний
  specextractor.md:    8+ упоминаний
  librarian.md:        5+ упоминаний
  (includes/3gpp-crawler.md: весь файл)

$ grep -r "_pipeline\|speckit" .claude/agents/ .claude/skills/
  (пусто — 0 результатов)
```

**Ни один агент не знает о существовании `_pipeline/`.** Это главный блокер.

### 2.3 CLI: команды есть, но status — заглушка

| Команда | Статус | Что реально делает |
|---|---|---|
| `python -m _pipeline metadata fetch` | ✅ Работает | WhatTheSpec API → SQLite |
| `python -m _pipeline download` | ✅ Работает | 3GPP FTP → `!INCOMING/` |
| `python -m _pipeline extract docx` | ✅ Работает | .docx → TXT + MD (Tier 1) |
| `python -m _pipeline extract docling` | ✅ Работает | PDF → MD + JSON (Tier 2, GPU) |
| `python -m _pipeline extract pypdf2` | ✅ Работает | PDF → TXT (Tier 3) |
| `python -m _pipeline status` | ❌ Заглушка | `cmd_status()` определена, но пустая |

### 2.4 3gpp-crawler: 1,026 узлов в графе

Это самая большая компонента графа (больше чем все остальные Core-слои вместе). При этом ObsidianDB использует только 2 команды из 8 (`crawl`, `checkout`).

---

## 3. 5 Layers of Core — что реально внутри

Граф выявил 5-слойную архитектуру ядра:

```
Layer 5: MANAGEMENT (19 узлов)
    CLAUDE.md, Roadmap.md, BACKLOG.md, _tech/README.md
    ↓ (связей нет — только человеческое понимание)

Layer 4: AI INTELLIGENCE (43 узла)
    8 agents + 7 skills + 6 includes
    Связи: Author → Reviewer, Librarian → Author, SpecDownloader → spec-crawler
    ↓ (0 перекрёстных мостов с Pipeline!)

Layer 3: PROCESSING ENGINE (165 узлов)
    _pipeline/ (78) + _tech/scripts/ (87)
    Связи: _pipeline/ самодостаточен, scripts/ изолированы
    ↓ (2 INFERRED ребра к 3gpp-crawler)

Layer 2: ENGINEERING DOCS (228 узлов)
    _tech/architecture, plans, reports
    Связи: референсы между отчётами, планы ссылаются на архитектуру
    ↓ (документирует, но не соединён с кодом)

Layer 1: EXTERNAL / LEGACY (1,026 узлов)
    3gpp-crawler/ (5 GB исходников)
    Связи: агенты → spec-crawler CLI (EXTRACTED)
```

### Ключевой разрыв: Layer 4 → Layer 3

**0 перекрёстных мостов между AI Intelligence и Processing Engine.** Агенты не знают о `_pipeline/`. Все вызовы идут через `spec-crawler` CLI — внешнюю команду, а не через Python-пакет.

Это архитектурный дефект: агенты спроектированы как «вызыватели shell-команд», а не как «оркестраторы Python-модулей».

---

## 4. Что SPEC DOWNLOADER вызывает на самом деле

Текущий flow:
```
User: /spec-download 31.102
  → SpecDownloader agent
    → shell: spec-crawler checkout 31.102 --checkout-dir "!INCOMING"
    → shell: spec-crawler crawl 31.102  (для метаданных)
    → Librarian agent (сортировка)
    → Author agent (создание wiki)
    → SpecExtractor agent
      → shell: spec-crawler crawl 31.102
      → shell: 3gpp-crawler workspace create/process
```

Целевой flow (speckit):
```
User: /spec-download 31.102
  → SpecDownloader agent
    → python -m _pipeline download 31.102          (один вызов вместо двух)
    → python -m _pipeline metadata fetch 31.102    (опционально)
    → Librarian agent (без изменений — _pipeline зеркалит структуру spec-crawler)
    → Author agent (без изменений)
    → SpecExtractor agent
      → python -m _pipeline extract docx <path>    (Tier 1, 0.2 сек)
      → python -m _pipeline extract docling <path> (Tier 2, GPU, 1.5 мин)
      → python -m _pipeline extract pypdf2 <path>  (Tier 3, fallback)
```

---

## 5. Что конкретно осталось сделать (честная инвентаризация)

### Блок А: Код (~30 мин)

| # | Задача | Файлы | Сложность |
|---|---|---|---|
| A1 | `speckit.toml` — конфиг вместо захардкоженных констант | Новый файл | Низкая |
| A2 | `cmd_status()` — реальная имплементация | `_pipeline/cli.py` | Низкая |
| A3 | `_pipeline/index.py` — обновление `specs-extracted/INDEX.md` | Новый файл | Средняя |

### Блок Б: Агенты (~30 мин)

| # | Задача | Файл | Сложность |
|---|---|---|---|
| Б1 | SpecDownloader: `spec-crawler` → `python -m _pipeline` | `specdownloader.md` | Средняя |
| Б2 | SpecExtractor: `3gpp-crawler workspace` → `python -m _pipeline extract` | `specextractor.md` | Средняя |
| Б3 | Librarian: убрать путь Б (spec-crawler nested), оставить только flat | `librarian.md` | Низкая |

### Блок В: Документация (~20 мин)

| # | Задача | Файл | Сложность |
|---|---|---|---|
| В1 | Обновить `CLAUDE.md` — убрать упоминания spec-crawler | `CLAUDE.md` | Низкая |
| В2 | Обновить `_tech/README.md` — стек | `_tech/README.md` | Низкая |
| В3 | Обновить `.claude/includes/3gpp-crawler.md` → статус «decommissioned» | includes | Низкая |

### Блок Г: Декомиссия (~10 мин)

| # | Задача | Команда |
|---|---|---|
| Г1 | Удалить `3gpp-crawler.toml` | `rm 3gpp-crawler.toml` |
| Г2 | Удалить `3gpp-crawler/` из проекта (5 GB) | `rm -rf 3gpp-crawler/` |
| Г3 | Оставить `.3gpp-crawler/` как read-only бэкап метаданных | — |

### Блок Д: Верификация (~15 мин)

| # | Тест |
|---|---|
| Д1 | `python -m _pipeline download 31.102` → файл в `!INCOMING/` |
| Д2 | `/spec-download 31.102` → полный пайплайн без spec-crawler |
| Д3 | `nvidia-smi` → GPU активен при docling extract |

**Итого: ~1.75 часа** — совпадает с оценкой P2-9 в BACKLOG.

---

## 6. Граф-инсайты: что ещё uncovered

### 6.1 Скрытая связность

Граф показал, что `extract()` из `_pipeline/extract_docling.py` И `extract()` из `3gpp-crawler/extraction/docling/converter.py` — **семантически идентичны** (same function signature, same Docling API). Это правильная переработка: мы не скопировали код, а переписали с тем же контрактом.

### 6.2 Мёртвый код в 3gpp-crawler

Из 1,026 узлов 3gpp-crawler в графе:
- ~600 относятся к TDoc/Meetings (не используются ObsidianDB)
- ~200 — CLI/форматы вывода (ison, toon — не используются)
- ~100 — конфигурация (mise-style cascade — не используется)
- ~100 — workspace management (не используется после speckit)
- ~26 — реально нужные (Docling converter, pipeline options, LibreOffice wrapper)

**Использование: ~2.5% кода 3gpp-crawler.**

### 6.3 Изоляция слоёв

0 перекрёстных мостов между AI Intelligence и Processing Engine — это одновременно и проблема, и архитектурное свойство:
- **Хорошо**: слои не связаны жёстко, можно заменить один не трогая другой
- **Плохо**: нет явного контракта, замена происходит через документацию а не через код

---

## 7. Рекомендация

**Завершить переход за одну сессию (~1.75h).** Код готов на 90%. Блокеры чисто организационные: переписать 2 агента и 3 конфигурационных файла.

После декомиссии:
- Проект «похудеет» с 10.8 GB до ~150 MB
- Исчезнет внешняя зависимость от `uv tool`
- GPU станет доступен всем Python-вызовам (единый `.venv`)
- Агенты получат единый интерфейс: `python -m _pipeline <команда>`

---

*Анализ создан 2026-06-14. Источники: graphify-граф (7,580 узлов), ручная инспекция _pipeline/ (10 модулей), grep по .claude/agents/ (0 упоминаний speckit).*
