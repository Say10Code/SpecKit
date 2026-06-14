# Сравнительный анализ: текущая архитектура vs speckit-консолидация

> **Дата**: 2026-06-14 · **Цель**: Безболезненный переход, сохранить всё хорошо работающее

---

## 0. Что МЕНЯЕТСЯ и что СОХРАНЯЕТСЯ — одним взглядом

```
СОХРАНЯЕТСЯ (без изменений):
  ✅ 8 агентов — system prompts трогать не будем
  ✅ 7 skills — оркестрация пайплайнов неизменна
  ✅ Author v2 (batch), Reviewer v3, Linker, Researcher, Formatter
  ✅ Librarian v2 — логика flatten и dual-path
  ✅ .category-map.md — single source of truth
  ✅ _tech/ — техническая документация
  ✅ wiki/, notes/, outputs/, Clippings/
  ✅ extract_docx.py — логика переносится без переписывания

МЕНЯЕТСЯ (минимально):
  🔄 SpecDownloader agent — строки 29-49: spec-crawler → python -m _pipeline
  🔄 SpecExtractor agent — строки 55-75: docling workspace → extract_docling.py
  🔄 .3gpp-crawler/ → кэш сохраняется, БД схема рядом
  🔄 3gpp-crawler.toml → _pipeline/config.py

УДАЛЯЕТСЯ:
  ❌ 3gpp-crawler/ (локальная копия исходников — 15K строк)
  ❌ uv tool install 3gpp-crawler
  ❌ spec-crawler CLI (заменён на python -m _pipeline)
```

---

## 1. Послойное сравнение

### Layer 4: Skills (оркестраторы)

| Skill | Сейчас | После консолидации | Изменения |
|---|---|---|---|
| `/spec-download` | Вызывает SpecDownloader → spec-crawler | Вызывает SpecDownloader → python -m _pipeline | **0 строк в SKILL.md** |
| `/ingest` | Author v2 + SpecExtractor | Без изменений | **0 строк** |
| `/review` | Reviewer v3 | Без изменений | **0 строк** |
| `/lint` | audit_connectivity.py | Без изменений | **0 строк** |
| `/format-html` | Formatter | Без изменений | **0 строк** |
| `/roadmap` | quality_metrics.py | Без изменений | **0 строк** |
| `/research` | Researcher | Без изменений | **0 строк** |

**Вывод**: Skills не трогаем. Они вызывают агентов, а агенты адаптируются внутри.

### Layer 3: Agents (исполнители)

| Агент | Что делает сейчас | Что изменится | Строк править |
|---|---|---|---|
| **SpecDownloader** | `spec-crawler crawl` + `spec-crawler checkout` | `python -m _pipeline metadata fetch` + `python -m _pipeline download` | **~15 строк** (шаги 1-2) |
| **Librarian** | Flatten `Specs/archive/` → `Specifications/` | **0 изменений** — структура `!INCOMING/Specs/archive/` сохраняется | **0 строк** |
| **Author v2** | Batch mode | Без изменений | **0 строк** |
| **Reviewer v3** | Pass 1 гибридный | Без изменений | **0 строк** |
| **SpecExtractor v3** | Методы A/B/C | Метод B (Docling workspace) → `extract_docling.py` | **~20 строк** (метод B) |
| **Linker** | wikilinks | Без изменений | **0 строк** |
| **Researcher** | deep research | Без изменений | **0 строк** |
| **Formatter** | MD→HTML | Без изменений | **0 строк** |

**Вывод**: Правки только в 2 агентах из 8. ~35 строк. Остальные 6 агентов не трогаем.

### Layer 2: Data (хранилище)

| Компонент | Сейчас | После | Статус |
|---|---|---|---|
| `!INCOMING/` | Входная точка | Без изменений | ✅ |
| `!INCOMING/Specs/archive/` | Структура spec-crawler checkout | **Сохраняется** — downloader создаёт такую же | ✅ |
| `.3gpp-crawler/3gpp_crawler.db` | Метаданные (oxyde ORM) | Рядом: `_pipeline/metadata.db` (sqlite3) | 🔄 Новая схема |
| `.3gpp-crawler/http-cache.sqlite3` | HTTP-кэш | Не обязателен (файлы мелкие) | ⚠️ Опционально |
| `3gpp-crawler.toml` | Конфиг | `_pipeline/config.py` | 🔄 Минимальный |
| `Specifications/` | 65+20 PDF | Без изменений | ✅ |
| `specs-extracted/` | TXT + MD + JSON | Без изменений | ✅ |

**Вывод**: Структура данных сохраняется. Кэш метаданных получает новую упрощённую схему.

### Layer 1: Инфраструктура

| Компонент | Сейчас | После | Статус |
|---|---|---|---|
| Python-окружение | 3 шт (системный, uv tool 3gpp, uv tool graphifyy) | **1 шт** (`.venv` в корне ObsidianDB) | 🔄 Консолидация |
| CUDA | ✅ Системный, ❌ uv tools | ✅ `.venv` (наследует системный PATH) | 🔄 Фикс |
| Зависимости | 37 пакетов (3gpp-crawler) | ~8 пакетов (docling, torch, httpx) | 🔄 Упрощение |
| `auto_patch_docling.py` | Патчит docling в uv tool | Патчит docling в `.venv` | 🔄 Путь изменится |
| `extract_docx.py` | `_tech/scripts/` | `_pipeline/extract_docx.py` | 🔄 Перенос |
| `docling_migrate.py` | `_tech/scripts/` | `_pipeline/extract_docling.py` | 🔄 Перенос + GPU |

---

## 2. Что мы реализовали хорошо — НЕ ТРОГАЕМ

### 2.1 Author v2 Batch mode

**Реализация**: 4 call sites обновлены, 1 вызов вместо 3-8.
**Почему сохраняем**: Работает. Не зависит от 3gpp-crawler. Не зависит от формата входа.
**В консолидации**: 0 изменений.

### 2.2 extract_docx.py (Tier 1)

**Реализация**: Прямое чтение ZIP/XML из .docx — 875× быстрее, таблицы сохранены.
**Почему сохраняем**: Это НАША инновация. Не зависит от 3gpp-crawler. Зависит только от Python stdlib.
**В консолидации**: Перенос в `_pipeline/extract_docx.py`. Логика та же. Вызов меняется с `python _tech/scripts/extract_docx.py` на `python -m _pipeline extract docx`.

### 2.3 Reviewer v3 гибридный Pass 1

**Реализация**: TXT Grep / JSON lookup / MD read в зависимости от типа факта.
**Почему сохраняем**: Это АРХИТЕКТУРНОЕ РЕШЕНИЕ, не зависящее от инструментов извлечения. Reviewer читает `specs-extracted/` — не важно, кто создал файлы.
**В консолидации**: 0 изменений.

### 2.4 Трёхуровневая архитектура извлечения (Tier 1/2/3)

**Реализация**: `.docx → extract_docx (Tier 1) | .pdf 3GPP → Docling (Tier 2) | .pdf остальное → PyPDF2 (Tier 3)`
**Почему сохраняем**: Это архитектурный принцип. Консолидация его УСИЛИВАЕТ — все три уровня в одном пакете `_pipeline/`.
**В консолидации**: Не меняется концептуально. Меняется только реализация Tier 2 (Docling теперь в `.venv` с CUDA).

### 2.5 Librarian dual-path flatten

**Реализация**: Путь A (ручной) + Путь B (spec-crawler checkout).
**Почему сохраняем**: Librarian работает с ФАЙЛАМИ, а не с инструментами. Ему всё равно, кто положил файлы в `!INCOMING/` — spec-crawler или speckit downloader. Структура `Specs/archive/` остаётся той же.
**В консолидации**: 0 изменений в Librarian. Downloader должен создавать ту же структуру `!INCOMING/Specs/archive/<series>/<number>/`.

### 2.6 Batch Authoring + Pipeline Parallelization

**Реализация**: P2-4 + P2-5. Author v2 batch mode, параллельный диспатч.
**Почему сохраняем**: Не зависит от источника PDF. Работает на уровне файлов.
**В консолидации**: 0 изменений.

### 2.7 connectivity audit + quality metrics

**Реализация**: P2-1 + P2-2. `audit_connectivity.py`, `quality_metrics.py`, `/lint --deep`.
**Почему сохраняем**: Чисто аналитические инструменты. Не зависят от пайплайна.
**В консолидации**: 0 изменений.

---

## 3. Что МЕНЯЕТСЯ — и как именно

### 3.1 SpecDownloader agent: строки 29-49

**Сейчас (16 строк про 3gpp-crawler)**:
```bash
spec-crawler crawl 31.102
spec-crawler checkout 31.102 --checkout-dir "...\!INCOMING"
```

**После (те же 16 строк, другая команда)**:
```bash
python -m _pipeline metadata fetch 31.102
python -m _pipeline download 31.102 --checkout-dir "...\!INCOMING"
```

**Что сохраняется**:
- CWD должен быть `D:\ObsidianDB` — правило остаётся
- Поддерживаемые спецификации: те же ✅
- Аргументы: номер, `--release` — те же ✅
- Результат: файлы в `!INCOMING/Specs/archive/` — та же структура ✅

**Единственное изменение**: имя исполняемого файла.

### 3.2 SpecExtractor agent: метод B (Docling workspace)

**Сейчас (20 строк про workspace)**:
```bash
spec-crawler crawl 31.102
3gpp-crawler workspace create spec-extract-31102
3gpp-crawler workspace add 31.102 --kind spec
3gpp-crawler workspace process ... --device cpu
```

**После (~15 строк)**:
```bash
python -m _pipeline extract docling "Specifications/ETSI_3GPP/USIM/31102-j40.docx" --device auto
# или для PDF:
python -m _pipeline extract docling "Specifications/eSIM/sgp02.pdf" --device auto
```

**Что улучшается**:
- `--device auto` вместо `--device cpu` — авто-выбор GPU/CPU
- Без workspace-церемонии (create/add/process)
- F1 auto-patch всё ещё нужен, но живёт в `_pipeline/` и применяется при импорте

### 3.3 auto_patch_docling.py

**Сейчас**: патчит `%APPDATA%/uv/tools/3gpp-crawler/Lib/.../docling/...`
**После**: патчит `.venv/Lib/.../docling/...`
**Решение**: скрипт должен находить docling через `import docling; Path(docling.__file__)` — уже реализовано в `find_docling_preprocessing()`. Будет работать с любым путём.

### 3.4 .3gpp-crawler/ → кэш метаданных

**Сейчас**: `3gpp_crawler.db` (oxyde ORM, 9 таблиц, асинхронный SQLite)
**После**: `_pipeline/metadata.db` (sqlite3, 2 таблицы, синхронный)
**Проблема**: существующая БД содержит метаданные R16/R17/R19 для 20+ спецификаций.
**Решение**: написать однократную миграцию:
```python
# Однократно, при первом запуске
python -m _pipeline migrate-db
# → читает 3gpp_crawler.db, создаёт metadata.db с упрощённой схемой
```

### 3.5 Зависимости: 37 → ~8

| Категория | Сейчас (3gpp-crawler) | После (speckit) |
|---|---|---|
| HTTP | niquests + hishel | **httpx** |
| CLI | typer + rich | **rich** (без typer — argparse) |
| PDF | docling + pypdfium2 + PyPDF2 | docling + PyPDF2 |
| ML | torch (CUDA) | torch (CUDA) |
| БД | oxyde (асинхронный ORM) | **sqlite3** (stdlib) |
| Конфиг | pydantic-settings | **нет** (константы в config.py) |
| Telegram | niquests bridge | ❌ не нужно |
| Форматы | ison, toon | ❌ не нужно |
| Офис | convert-lo | **сохраняем** (для `.doc` → `.docx`) |

---

## 4. Миграционный путь — 6 этапов с верификацией на каждом

### Этап 1: Окружение (30 мин, 0 изменений в агентах)

```
Создать: pyproject.toml
Выполнить: uv sync
Проверить: uv run python -c "import torch; assert torch.cuda.is_available()"
Создать: _pipeline/__init__.py
```

**Верификация**: `nvidia-smi` показывает usage >0% при `uv run python -c "import torch; torch.cuda.init()"`

**Агенты пока не трогаем — старый spec-crawler продолжает работать.**

### Этап 2: Downloader (2h)

```
Реализовать: _resolve_spec.py (WhatTheSpec API)
Реализовать: _metadata_db.py (SQLite)
Реализовать: _download_spec.py (3GPP FTP)
Реализовать: cli.py (metadata fetch + download)
Мигрировать: python -m _pipeline migrate-db
```

**Верификация**: `python -m _pipeline download 31.102` → файл в `!INCOMING/Specs/archive/31_series/31.102/`. Идентичная структура.

### Этап 3: Extractors (30 мин)

```
Перенести: extract_docx.py → _pipeline/extract_docx.py
Перенести: docling_migrate.py → _pipeline/extract_docling.py
Создать: _pipeline/extract_pypdf2.py
```

**Верификация**: `python -m _pipeline extract docx <file>` → TXT + MD идентичны текущим.

**Агенты пока не трогаем.**

### Этап 4: Замена в агентах (1h)

```
Обновить: specdownloader.md → строки 29-49
Обновить: specextractor.md → строки 55-75
**Не трогать**: librarian.md, author.md, reviewer.md, linker.md, ...
```

**Верификация**: `/spec-download 31.102` — полный пайплайн через новый downloader.

### Этап 5: Деcommission (15 мин)

```
Удалить: 3gpp-crawler.toml
Выполнить: uv tool uninstall 3gpp-crawler (опционально — может быть нужно graphifyy)
Оставить: 3gpp-crawler/ исходники (read-only, для справки)
Оставить: .3gpp-crawler/ (кэш, .gitignore'd)
```

### Этап 6: GPU-верификация (30 мин)

```
Запустить: python -m _pipeline extract docling <pdf>
Проверить: nvidia-smi показывает загрузку >30%
Сравнить: время с бенчмарком B3 (2.4-4.2× CPU)
```

---

## 5. Матрица рисков миграции

| Риск | Вероятность | Влияние | Митигация |
|---|---|---|---|
| Downloader создаёт другую структуру чем spec-crawler | 🟡 Средняя | Librarian не найдёт файлы | **Верификация Этапа 2**: сравнить `ls !INCOMING/Specs/archive/` до и после |
| БД метаданных теряет данные R16/R17 | 🟢 Низкая | Повторный crawl | `migrate-db` читает старую БД |
| extract_docling.py не видит GPU в .venv | 🟡 Средняя | Миграция на CPU | **Верификация Этапа 1**: `assert torch.cuda.is_available()` |
| auto_patch_docling ломается | 🟢 Низкая | Docling bad_alloc на стр. 67+ | `find_docling_preprocessing()` уже использует `import docling` |
| Агенты продолжают ссылаться на spec-crawler | 🟡 Средняя | Часть пайплайна сломана | Grep по `.claude/` после Этапа 4 |
| Что-то сломалось — нет быстрого отката | 🟢 Низкая | Блокировка работы | Старый spec-crawler остаётся установлен до Этапа 5 |

---

## 6. Что даёт консолидация

| Метрика | Сейчас | После | Выигрыш |
|---|---|---|---|
| Python-окружений | 3 | 1 | −2 |
| Зависимостей | 37 → ~8 | ~8 | −29 |
| Строк внешнего кода | ~15K (3gpp-crawler) | ~800 (_pipeline/) | −95% |
| CUDA для Docling | ❌ | ✅ | **2.4-4.2×** |
| Время скачивания спека | spec-crawler + crawl overhead | Прямой HTTP GET | Сопоставимо |
| Время извлечения .docx | 0.2 сек (extract_docx.py) | 0.2 сек | Без изменений |
| Время извлечения .pdf (Docling) | 3 мин CPU | **45-75 сек GPU** | **2.4-4.2×** |
| Сложность поддержки | 2 репозитория | 1 репозиторий | −50% |
| Риск upstream breaking changes | Есть | Нет | Устранён |

---

## 7. Итоговый вердикт

**Консолидация безопасна** потому что:

1. **Агенты не меняются концептуально** — только 2 из 8 агентов получают косметические правки (~35 строк)
2. **Skills не трогаем** — оркестрация неизменна
3. **Данные сохраняются** — все файлы на своих местах
4. **Структура `!INCOMING/Specs/archive/` сохраняется** — Librarian работает без изменений
5. **Трёхуровневое извлечение сохраняется** — Tier 1/2/3 теперь в одном пакете
6. **Откат простой** — старый spec-crawler остаётся до Этапа 5
7. **CUDA фиксится сайд-эффектом** — главная проблема P3-5 решается

**Что мы можем потерять (и как этого избежать)**:
- ❌ Workspace-команды Docling → ✅ `extract_docling.py` делает то же самое прямым вызовом
- ❌ oxyde ORM → ✅ sqlite3 (2 таблицы, никакой магии)
- ❌ TDoc/Meetings → ✅ Не используются
- ❌ 3gpp-crawler.toml → ✅ `_pipeline/config.py` с буквально 5 константами

---

*Сравнительный анализ создан 2026-06-14. Рекомендация: приступать к Этапу 1.*
