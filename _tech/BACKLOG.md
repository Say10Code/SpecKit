# Беклог ObsidianDB

> **Дата**: 2026-06-13 15:30
> **Назначение**: Боевой список задач. Обновляется после каждой сессии.
> **Приоритеты**: 🔴 P0 (критическое) → 🟡 P1 (высокое) → 🟢 P2 (среднее) → 🔵 P3 (низкое)

---

## Быстрый статус

| Метрика | Значение |
|---|---|
| Sub-agents | 8 |
| Skills | 7 (+research) |
| Wiki страниц | 129 (+7 index) |
| Reviewed | 100% |
| Битых ссылок | 0 |
| Specifications PDF | 65 (+ category-map) |
| specs-extracted TXT | 58 (PyPDF2) |
| specs-extracted MD+JSON | **37 пар** (11×3GPP + 26×ETSI) |
| 3gpp-crawler | ✅ Интегрирован |
| LibreOffice | ✅ 26.2.4.2 |
| Torch CUDA | ✅ RTX 3060 (11 GB VRAM) |
| GPU speedup | 2.4-4.2× vs CPU |
| Git | ✅ 4 коммита |
| GitHook | ✅ PostToolUse — напоминание /lint после Edit/Write в wiki/ |
| Docling bad_alloc | ✅ 247→1 (F1 fix) |
| `_tech/` | Организован: architecture/, plans/, reports/, diagrams/, scripts/ |

---

## 🔴 P0 — Критическое

*Нет активных P0 задач.*

Все критические проблемы решены: git есть, бэкапы есть (via git), хуки активны, папки без кириллицы.

---

## 🟡 P1 — Высокое

### U9 fix: допилить `check_frontmatter.py`
**Статус**: 🔄 Скрипт работает, но regex не парсит многострочный YAML — 62 ложных ошибки.
**Решение**: Использовать `yaml` library вместо regex или добавить multi-line поддержку.

### F1 патч — переприменять при апдейте docling
**Статус**: ⚠️ Патч `page_preprocessing_model.py` нужно переприменять после каждого `uv tool install --reinstall` или обновления docling.
**Решение**: Добавить в `pipeline.py` авто-патч при запуске, или инструкцию в README.

---

## 🟢 P2 — Среднее

### P2.1 — Периодический аудит связности
**Проблема**: Linker вызывается только реактивно. Нет еженедельного аудита.
**Решение**: `/lint` с флагом `--deep` для полного анализа графа.

### P2.2 — Метрики качества
**Проблема**: Нет трендов link density, orphan rate, времени от PDF до reviewed.
**Решение**: `_tech/scripts/quality_metrics.py` — снижение метрик при каждом `/roadmap`.

### P2.3 — Модуляризация CLAUDE.md
**Проблема**: 245 строк — монолит.
**Решение**: `.claude/includes/` с ролями, структурой, агентами, стандартами.

---

## 🔵 P3 — Низкое

### P3.1 — Мульти-пользовательская архитектура (будущее)
### P3.2 — Obsidian плагин (будущее)
### P3.3 — Удалить нулевые файлы в Specifications/Tutorials

---

## Завершённые задачи (всего 28)

| # | Задача | Дата |
|---|---|---|
| 1 | 3gpp-crawler: Python 3.13, `uv tool install`, `spec-crawler` CLI | 12 июн |
| 2 | Конфиг: `3gpp-crawler.toml` (кэш в `.3gpp-crawler/`) | 12 июн |
| 3 | `.gitignore` | 12 июн |
| 4 | `spec-crawler crawl` БД метаданных | 12 июн |
| 5 | SpecDownloader agent обновлён | 12 июн |
| 6 | Librarian agent: два пути (!INCOMING flat + spec-crawler nested) | 12 июн |
| 7 | Skill `/spec-download` создан | 12 июн |
| 8 | LibreOffice 26.2.4.2 установлен | 12 июн |
| 9 | Docling fix: `PipelineOptions` → `PdfPipelineOptions` | 12 июн |
| 10 | Docling пилот: 5 спецификаций CPU | 12 июн |
| 11 | Docling миграция: 11×3GPP + 5×ETSI = 16 MD+JSON | 13 июн |
| 12 | `std::bad_alloc` анализ: OOM в PIL/pypdfium2, не GPU | 13 июн |
| 13 | Torch CUDA проверка → `torch-2.12.0+cu126` (RTX 3060) | 13 июн |
| 14 | Reviewer v3: гибридный Pass 1 (TXT Grep / JSON lookup / MD read) | 13 июн |
| 15 | SpecExtractor v2: PyPDF2 + Docling dual approach | 13 июн |
| 16 | B1: `Спецификации` → `Specifications` (90 файлов + 6 агентов) | 13 июн |
| 17 | B2: PyTorch CUDA (RTX 3060) | 13 июн |
| 18 | B3: CPU vs GPU бенчмарк (3 стадии, 2.4-4.2× speedup) | 13 июн |
| 19 | B8/F1-F3: bad_alloc решён (247→1), данные не потеряны | 13 июн |
| 20 | Архитектура v2: `ARCHITECTURE-v2.md` | 13 июн |
| 21 | Глубокий ресерч: 23 находки, 14 проблем, 10 улучшений | 13 июн |
| 22 | U1: Git init + первый коммит (`a35abfc`) | 13 июн |
| 23 | U2: Auto-lint hook (PostToolUse) | 13 июн |
| 24 | U3: Удалён старый `Спецификации/` дубликат | 13 июн |
| 25 | U4-U10: INDEX.md, `/research` skill, category-map, диаграммы, валидатор | 13 июн |
| 26 | B4: ETSI Docling миграция (26 PDF → 37 MD+JSON пар total) | 13 июн |
| 27 | B5-B7: `.claude/CLAUDE.md`, `specs-extracted/INDEX.md`, `outputs/STATUS_AND_PLAN.md` | 13 июн |
| 28 | `_tech/` реорганизация: architecture/, plans/, reports/, README | 13 июн |

---

## Хронология

| Дата | Выполнено | Ключевые вехи |
|---|---|---|
| 12 июн 16:00 | Аудит архитектуры, `_tech/` создан | Старт |
| 12 июн 17:00 | 3gpp-crawler интеграция, SpecDownloader, Librarian v2 | Автоматическая загрузка спецификаций |
| 12 июн 18:00 | Docling fix + миграция 16 спецификаций | Первый Docling GPU прогон |
| 13 июн 00:30 | Reviewer v3, SpecExtractor v2, B3 бенчмарк, анализ OOM | Гибридный Pass 1 |
| 13 июн 01:30 | B2 CUDA, B8 fix, Архитектура v2 | RTX 3060 активирован |
| 13 июн 03:00 | Глубокий ресерч, `.gitignore` аудит, `_tech/` реорганизация | 23 находки |
| 13 июн 14:00 | U1-U10: git, хуки, `/research`, category-map, диаграммы | Критические исправления |
| 13 июн 15:30 | B4-B7: ETSI миграция, обновление системных файлов | **37 MD+JSON пар** |

---

*Беклог актуален на 2026-06-13 15:30. 28 задач выполнено. 3 активные задачи.*
