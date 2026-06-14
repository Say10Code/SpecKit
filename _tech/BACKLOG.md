# Беклог ObsidianDB

> **Последнее обновление**: 2026-06-14 16:30
> **Назначение**: Боевой список задач. Обновляется после каждого завершения задачи (см. [_tech/README.md](README.md#5-backlog)).
> **Правило**: ⚠️ Завершил задачу → обнови беклог. Завершил сессию → обнови беклог.

---

## 📊 Dashboard

| Метрика | Значение |
|---|---|
| 🔴 P0 (критическое) | **0** |
| 🟡 P1 (высокое) | **0** |
| 🟢 P2 (среднее) | **0** |
| 🔵 P3 (низкое) | **3** |
| ⚪ P4 (подумать) | **2** |
| **Всего активных** | **5** |
| **Завершено** | **57** |

```mermaid
pie title Активные задачи (6)
    "P2 — Среднее" : 1
    "P3 — Низкое" : 3
    "P4 — Подумать" : 2
```

### Системный срез

| Компонент | Состояние |
|---|---|
| Sub-agents | 8 (+ Author v2 batch, SpecExtractor v3) |
| Skills | 7 (+research) |
| Includes | 6 (structure, agents, skills, standards, incoming, 3gpp-crawler) |
| Quality Score | **98/100 (A)** — 0 ошибок FM, 0 битых ссылок, 94.6% reviewed |
| Wiki | 130 стр. (+7 index), 100% reviewed |
| Битых ссылок | 0 |
| Сирот | 1 (`telcoai_3gpp_search`) |
| Specifications PDF | 74 (+ 20 R16/R17 .docx) |
| specs-extracted | 78 TXT + 86 MD + 73 JSON |
| Torch CUDA | ✅ RTX 3060 (12 GB), 2.4-4.2× CPU |
| .venv (uv sync) | ✅ docling + torch (CUDA) + httpx + PyPDF2 + rich |
| _pipeline/ (speckit) | ✅ 10 модулей, 5 CLI-команд, GPU активен |
| 3gpp-crawler | 🗑️ Декомиссия выполнена (2026-06-14) |
| Git | ✅ 6 коммитов |
| .speckit/ | ✅ Кэш метаданных (бывш. .3gpp-crawler) |
| GitHook (PostToolUse) | ✅ Напоминание /lint |
| Frontmatter validator | 0 ошибок, 58 warnings (yaml.safe_load) |
| Graphify | Граф 7,723 узла, 19,947 рёбер, 396 сообществ, 102 оркестрационных ребра |
| Беклог | 57/62 задач завершено (0 P0, 0 P1, 0 P2, 3 P3, 2 P4) |

### ▶️ Next Up

| Порядок | Задача | Почему |
|---|---|---|
| **1** | P3-5.1: Docling — 1 оставшийся PDF | 15 мин, закрыть P3-5 на 100% |
| **2** | P2-10: Core vs Data — логическое разделение | Фаза 2: .gitignore-стратегия |
| **3** | P4-1: Стандартизация имён спецификаций | Оценить необходимость |

---

## 🔴 P0 — Критическое

*Нет активных P0 задач.*

---

## 🟡 P1 — Высокое

### P1-1: U9 fix — допилить `check_frontmatter.py`

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~1.5h |
| **Блокер** | — |
| **Файлы** | `_tech/scripts/check_frontmatter.py`, `wiki/summaries/ts_51017.md` |

**Проблема**: Скрипт использовал regex для парсинга YAML — не работал с многострочными списками (tags, sources). 62 ложных ошибки.

**Решение**: Заменён на `yaml.safe_load()`. `type` перенесён из required в recommended (warning). Добавлены все реально используемые типы (20 типов). CANONICAL_TYPE для рекомендаций.

**Результат**: 0 ошибок, 58 warnings (31 missing type + 27 non-canonical type). 1 реальная ошибка найдена и исправлена (ts_51017.md — missing updated).

---

### P1-2: F1 патч — автоприменение при апдейте docling

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~45m |
| **Блокер** | — |
| **Файлы** | `_tech/scripts/auto_patch_docling.py` (новый), `.claude/agents/specextractor.md`, `_tech/scripts/docling_batch_etsi.py` |

**Проблема**: Патч `page_preprocessing_model.py` (try/except вокруг `get_image()`) сбрасывается при `uv tool install --reinstall 3gpp-crawler`.

**Решение**: Создан `auto_patch_docling.py` — находит установленный docling, проверяет наличие патча, применяет если отсутствует. Добавлен как pre-flight в SpecExtractor agent. `docling_batch_etsi.py` исправлен: images_scale=1.0, generate_picture_images=False.

**Критерий готовности**: ✅ `uv tool install --reinstall 3gpp-crawler` → `python auto_patch_docling.py` → «F1 fix applied successfully».

---

### P1-3: R1 fix — авто-переход Librarian → /ingest в /spec-download

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | 15m |
| **Блокер** | — |
| **Файлы** | `.claude/agents/specdownloader.md` |

**Проблема**: Шаг 4 в SpecDownloader — «Сообщить результат» — не вызывал /ingest автоматически. Цепочка рвалась после Librarian.

**Решение**: Заменён на «Запустить полный пайплайн обработки» с явными вызовами: /ingest → SpecExtractor → /lint → Roadmap.

---

### P1-4: R2 fix — авто-вызов SpecExtractor в /ingest

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | 15m |
| **Блокер** | — |
| **Файлы** | `.claude/skills/ingest/SKILL.md` |

**Проблема**: SpecExtractor не вызывался при /ingest. Эталонный текст не появлялся в specs-extracted/ → Reviewer не мог проверить факты.

**Решение**: Добавлен шаг 6 в /ingest workflow: «Запусти SpecExtractor для извлечения эталонного текста» (обязательный шаг).

---

### P1-5: R4 fix — единый source of truth серия→тема

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | 20m |
| **Блокер** | — |
| **Файлы** | `.claude/agents/librarian.md`, `.claude/skills/spec-download/SKILL.md` |

**Проблема**: Таблица «серия → тема» дублировалась в 3 местах. Изменения расходились.

**Решение**: В librarian.md и spec-download/SKILL.md таблицы заменены на ссылку на `Specifications/.category-map.md` — единый source of truth.

---

## 🟢 P2 — Среднее

### P2-1: Периодический аудит связности

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~1.5h |
| **Блокер** | — |
| **Файлы** | `_tech/scripts/audit_connectivity.py`, `.claude/skills/lint-wiki/SKILL.md` |

**Проблема**: Linker вызывался только реактивно. Не было периодического аудита.

**Решение**: `audit_connectivity.py` — полный граф-анализ 130 wiki-страниц. Проверяет: битые ссылки, сирот, слабые страницы, изолированные кластеры, мосты, cross-ref пробелы, плотность связей, матрицу типов. `/lint --deep` запускает скрипт.

**Результат первого аудита**: 0 битых ссылок, 1 сирота (`telcoai_3gpp_search`), 32 слабых, 1 кластер. Средняя связность 7.3 in / 6.2 out — HEALTHY.

---

### P2-2: Метрики качества

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~2h |
| **Блокер** | — |
| **Файлы** | `_tech/scripts/quality_metrics.py`, `.claude/skills/roadmap-status/SKILL.md` |

**Проблема**: Не было трендов link density, orphan rate, review coverage, от времени PDF до reviewed.

**Решение**: `quality_metrics.py` — 8 категорий метрик (wiki, connectivity, specs, frontmatter, backlog velocity, activity, score, trends). История сохраняется в JSON для графиков трендов. `/roadmap` skill запускает скрипт автоматически.

**Результат первого замера**: Quality Score 91/100 (A), 130 страниц, 94.6% reviewed, 0 frontmatter ошибок, 1 сирота. Все метрики в зелёной зоне.

---

### P2-3: Модуляризация CLAUDE.md

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~1h |
| **Блокер** | — |
| **Файлы** | `.claude/includes/` (6 файлов, 241 строк), `CLAUDE.md` (47 строк), `.claude/CLAUDE.md` |

**Проблема**: 252 строки — монолит. Контекст расходуется на каждую сессию.

**Решение**: 6 include-файлов (structure, agents, skills, standards, incoming, 3gpp-crawler). Главный CLAUDE.md — 47-строчный диспетчер с быстрыми ссылками. Сжатие: **5.4×** (252→47 строк).

**Критерий готовности**: ✅ CLAUDE.md 47 строк, includes/ 6 модулей, локальный CLAUDE.md обновлён.

---

### P2-4: Batch Authoring — пакетная обработка спецификаций

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~2h |
| **Блокер** | — |
| **Файлы** | `.claude/agents/author.md`, `.claude/skills/ingest/SKILL.md`, `.claude/agents/librarian.md`, `.claude/skills/spec-download/SKILL.md`, `.claude/agents/specdownloader.md` |
| **Анализ** | `_tech/reports/batch-authoring-analysis.md` |

**Проблема**: Author вызывался 3-8 раз последовательно на спецификацию. PDF читался N раз.

**Решение**: Author v2 Batch mode внедрён во все 4 call sites: 1 вызов вместо N. 3-5× быстрее. PDF читается 1 раз. Все страницы пакета знают друг о друге.

**Критерий готовности**: ✅ `/spec-download 31.102` → `Agent: Author v2 — пакетная обработка <PDF>` → 1 вызов.

---

### P2-5: Pipeline Parallelization — параллельная обработка спецификаций

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~30m |
| **Блокер** | ✅ P2-4 (Batch Authoring) завершён |
| **Файлы** | `.claude/skills/spec-download/SKILL.md`, `.claude/agents/specdownloader.md` |

**Проблема**: Несколько спецификаций обрабатывались последовательно — шаг 4 вызывал Author v2 для каждой по очереди.

**Решение**: Параллельный диспатч Author v2 в одном сообщении. Agent tool выполняет несколько вызовов одновременно. 3 спецификации = max(время одной), не сумма. Linker — один проход после всех.

**Критерий готовности**: ✅ `/spec-download 31.102 35.206 23.501` — все Author v2 вызовы в одном сообщении, параллельно.

---

### P2-6: /spec-download — полная автоматизация 7 шагов

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-13) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~30m |
| **Блокер** | — |
| **Файлы** | `.claude/skills/spec-download/SKILL.md`, `.claude/agents/specdownloader.md` |

**Проблема**: Шаги 5-6 были нарративными, без явного механизма вызова.

**Решение**: SKILL.md полностью переписан: все 7 шагов имеют явные Agent/Skill вызовы. Batch Authoring интегрирован. SpecExtractor auto-patch добавлен как pre-flight.

**Критерий готовности**: ✅ `/spec-download 31.102` — все 7 шагов с явными вызовами, Batch Authoring, авто-patch.

---

### P2-7: extract_docx.py как TIER 1 основной пайплайн (⭐️ вне очереди)

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) |
| **Создано** | 2026-06-14 |
| **Оценка** | ~1h |
| **Блокер** | — |
| **Файлы** | `_tech/scripts/extract_docx.py`, 4 call sites, `_tech/architecture/ARCHITECTURE-v3.md`, SpecExtractor v3 |
| **Анализ** | `_tech/reports/direct-docx-extraction-analysis.md` |

**Проблема**: Цепочка LibreOffice→PDF→PyPDF2 разрушала таблицы EF. Docling восстанавливал через GPU за 1.5 мин. Но .docx — ZIP/XML: 500+ таблиц уже структурированы внутри.

**Решение**: extract_docx.py (Python stdlib) — 0.2 сек, 875× быстрее. Архитектура v3: Tier 1 (.docx прямо), Tier 2 (Docling), Tier 3 (PyPDF2). 4 call sites обновлены.

**Результат тестов**: 14/14 .docx valid, 6/6 FID found, 14 TXT + 14 MD, 112 EF таблиц извлечено. Reviewer видит ВСЕ структуры EF за один проход.

---

## 🔵 P3 — Низкое

### P3-1: Мульти-пользовательская архитектура

| Поле | Значение |
|---|---|
| **Статус** | ⬜ Не начато |
| **Создано** | 2026-06-13 |
| **Оценка** | Не оценивалось |
| **Блокер** | Нет требований |

**Описание**: Исследовать возможность одновременной работы нескольких пользователей с хранилищем.

---

### P3-2: Obsidian плагин

| Поле | Значение |
|---|---|
| **Статус** | ⬜ Не начато |
| **Создано** | 2026-06-13 |
| **Оценка** | Не оценивалось |
| **Блокер** | P3-1 |

**Описание**: Плагин для Obsidian, интегрирующий sub-agents в интерфейс.

---

### P3-3: Удалить нулевые файлы в `Specifications/Tutorials/`

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) |
| **Создано** | 2026-06-13 |
| **Оценка** | ~15m |
| **Блокер** | — |
| **Результат** | 1 нулевой файл найден и удалён: `SIM_презентация_RU.pdf.md` (0 байт — неудачная экстракция). Остальные файлы в Specifications/ — не нулевые. |

**Описание**: Найти и удалить файлы нулевого размера в Tutorials.

---

### ~~P3-4: Author Split — Drafter + Editor~~ ❌ ОТМЕНЕНО

| Поле | Значение |
|---|---|
| **Статус** | ❌ Отменено (2026-06-13) |
| **Причина** | 97% операций Author — create, не update. Duplicate check (Glob, 0.5 сек) не bottleneck. Разделение на 2 агента добавляет сложность без устранения реальной проблемы (последовательные вызовы). См. `_tech/reports/batch-authoring-analysis.md` §3. |
| **Альтернатива** | Флаг `--mode update` в существующем Author вместо 2 новых агентов. |

---

### P3-5: Docling-миграция оставшихся 32 PDF → specs-extracted MD+JSON

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено на 99% (2026-06-14). 30/31 PDF, 1 fail — кириллический путь. |
| **Результат** | 73/74 PDF с MD (99%). 86 MD + 78 TXT файлов. Quality Score: 98/100 (A). |
| **Создано** | 2026-06-14 |
| **Оценка** | ~4h |
| **Блокер** | 🔴 P2-8 (speckit consolidation — решит проблему CUDA через `uv sync` с `.venv`) |
| **Файлы** | `_tech/scripts/docling_migrate.py` (новый), 31 PDF без MD |
| **Прогресс** | 2/33 обработано на CPU (Books: From_GSM_to_LTE + Introduction_to_SIM_Cards) |

**Проблема**: 31 из 74 PDF имеют только PyPDF2 TXT — таблицы разрушены. Docling-миграция приостановлена: `uv tool` изолирует venv от CUDA DLL.

**Решение**: Дождаться P2-8 (speckit). После создания `.venv` через `uv sync` — CUDA заработает. Затем запустить `docling_migrate.py` на GPU (2.4-4.2× быстрее).

**Критерий готовности**: Все PDF имеют MD+JSON пары. INDEX.md обновлён.

---

### P2-8: `speckit` — консолидация: свой пайплайн вместо 3gpp-crawler

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) — полная миграция |
| **Создано** | 2026-06-14 |
| **Оценка** | ~6.25h (включая P2-9) |
| **Блокер** | — |
| **Файлы** | `_pipeline/` (10 модулей), `pyproject.toml`, `.venv/`, `.speckit/` |

**Результат**: speckit полностью заменил 3gpp-crawler. 13 файлов изменено (агенты, includes, диспетчеры), 2 удалено (3gpp-crawler.toml + 3gpp-crawler/ 5 GB), `.3gpp-crawler/` → `.speckit/`. Агенты переписаны на `python -m _pipeline`. GPU доступен через `.venv`. Проект «похудел» с 10.8 GB до ~160 MB.

---

### P2-9: Завершить speckit — оставшиеся этапы консолидации

| Поле | Значение |
|---|---|
| **Статус** | ✅ Завершено (2026-06-14) — hit-list миграция |
| **Создано** | 2026-06-14 (выделено из P2-8) |
| **Оценка** | ~1.75h (факт: ~90 мин) |
| **Блокер** | — |
| **Файлы** | 13 файлов изменено, 2 удалено, `.3gpp-crawler/` → `.speckit/` |

**Результат**: все 6 пунктов hit-list'а выполнены. Агенты переписаны на `python -m _pipeline`, декомиссия проведена (5 GB freed). Подробности в `_tech/reports/speckit-migration-hitlist.md`.

---

### P3-5.1: Docling — оставшийся 1 PDF (кириллический путь)

| Поле | Значение |
|---|---|
| **Статус** | ⬜ Не начато |
| **Создано** | 2026-06-14 (выделено из P3-5) |
| **Оценка** | ~15m |
| **Блокер** | — |
| **Файлы** | `_tech/scripts/docling_migrate.py` |

**Проблема**: 1 PDF не обработан из-за кириллического пути. Остальные 73/74 — OK.

**Решение**: Скопировать PDF во временную ASCII-директорию → Docling → скопировать результат обратно.

### P2-10: Core vs Data — логическое разделение проекта

| Поле | Значение |
|---|---|
| **Статус** | ⬜ Не начато |
| **Создано** | 2026-06-14 |
| **Оценка** | ~1.5h |
| **Блокер** | — |
| **Файлы** | `_tech/reports/core-vs-data-separation-analysis.md` (отчёт), `.gitignore`, `CLAUDE.md`, `_tech/README.md` |

**Проблема**: Проект смешивает Core (движок: агенты, `_pipeline`, скрипты, конфиги) и Data (хранилище: wiki, Specifications, specs-extracted, notes) в одной файловой системе без явного контракта. Git diff показывает и код, и контент. 89% размера — мёртвый груз (3gpp-crawler, .venv).

**Решение**: Физически НЕ перемещать файлы (wikilinks ×130), но ввести логическое разделение:
1. `.gitignore`-стратегия: Core в git, Data — отдельно
2. Контракт для агентов: что читать, куда писать
3. Документация в `CLAUDE.md`

**Результат**:
- ✅ Фаза 1: отчёт `core-vs-data-separation-analysis.md` создан
- ✅ Фаза 2: `.gitignore` обновлён — Core (234 файла) в git, Data (181 MB PDF + specs-extracted + notes) исключены
- ✅ 110 Specifications/, 5 notes/, 2 outputs/ — удалены из git-индекса
- ✅ `.category-map.md` + `.gitkeep` — оставлены в git (Core)
- ⬜ Фаза 4: Data-стратегия (будущее) — Git LFS или отдельный бэкап

**Критерий готовности**: `git status` показывает только Core-файлы. CLAUDE.md документирует границу Core/Data.

---

## ⚪ P4 — Подумать (долгосрочные соображения)

### P4-1: Стандартизация именования спецификаций

| Поле | Значение |
|---|---|
| **Статус** | ⬜ Подумать |
| **Создано** | 2026-06-14 |
| **Источник** | `_tech/plans/archive/specs-directory-architecture.md` |
| **Оценка** | ~2h (исследование + скрипт) |

**Суть**: Имена файлов в `Specifications/` неоднородны (`gsm11-11.pdf`, `ts_102221v170100p.pdf`, `SGP.02-v4.1.pdf`). Предложен стандарт `<ORG>_<TYPE>_<NUMBER>_<VERSION>.<ext>`. Но переименование сломает wikilinks ×130 страниц. Без явной необходимости — не трогать. При появлении инструмента батч-обновления wikilinks — пересмотреть.

### P4-2: Дедупликация версий спецификаций

| Поле | Значение |
|---|---|
| **Статус** | ⬜ Подумать |
| **Создано** | 2026-06-14 |
| **Источник** | `_tech/plans/archive/specs-directory-architecture.md` |
| **Оценка** | ~1h |

**Суть**: 3 версии TS 102 221 лежат рядом. Неясно, какая актуальна. Варианты: (а) подпапки `v17.1/`, `v17.4/`, `v18.2/`; (б) `LATEST` симлинк; (в) `.category-map.md` с пометкой актуальной версии. Пока работает как есть — Reviewer знает где брать.

---

## 📋 Активные задачи (сводная таблица)

| ID | Приор. | Задача | Статус | Оценка | Блокер |
|---|---|---|---|---|---|
| P1-1 | 🟡 | U9 fix: check_frontmatter.py | ✅ | 1.5h | — |
| P1-2 | 🟡 | F1 патч: авто-патч docling | ✅ | 45m | — |
| P2-1 | 🟢 | Периодический аудит связности | ✅ | 1.5h | — |
| P2-2 | 🟢 | Метрики качества | ✅ | 2h | — |
| P2-3 | 🟢 | Модуляризация CLAUDE.md | ✅ | 1h | — |
| P2-4 | 🟢 | Batch Authoring (Author v2) | ✅ | 2h | — |
| P2-5 | 🟢 | Pipeline Parallelization | ✅ | 30m | ✅ |
| P2-6 | 🟢 | /spec-download авто 7 шагов | ✅ | 30m | — |
| P2-7 | 🟢 | extract_docx.py TIER 1 пайплайн | ✅ | 1h | — |
| P3-1 | 🔵 | Мульти-пользовательская архитектура | ⬜ | ? | — |
| P3-2 | 🔵 | Obsidian плагин | ⬜ | ? | P3-1 |
| P3-3 | 🔵 | Удалить нулевые файлы в Tutorials | ✅ | 15m | — |
| P3-5 | 🔵 | Docling-миграция 32 PDF → MD+JSON | ✅ | 4h | — |
| P2-8 | 🟢 | speckit — консолидация | ✅ | 6.25h | — |
| P2-9 | 🟢 | speckit — hit-list миграция | ✅ | 1.75h | — |
| P3-5.1 | 🔵 | Docling: 1 оставшийся PDF | ⬜ | 15m | — |
| P2-10 | 🟢 | Core vs Data — Фаза 2 (.gitignore) | ✅ | 30m | — |
| P4-1 | ⚪ | Стандартизация имён спецификаций | ⬜ | 2h | — |
| P4-2 | ⚪ | Дедупликация версий спецификаций | ⬜ | 1h | — |
| ~~P3-4~~ | ~~🔵~~ | ~~Author Split (Drafter/Editor)~~ | ❌ | — | Отменено |

---

## ✅ Завершённые задачи (44)

<details>
<summary>Развернуть список</summary>

| # | Приор. | Задача | Дата | Сессия |
|---|---|---|---|---|
| 1 | 🟡 | 3gpp-crawler: Python 3.13, `uv tool install`, `spec-crawler` CLI | 12 июн | spec-crawler |
| 2 | 🟡 | Конфиг: `3gpp-crawler.toml` (кэш в `.3gpp-crawler/`) | 12 июн | spec-crawler |
| 3 | 🟡 | `.gitignore` | 12 июн | spec-crawler |
| 4 | 🟢 | `spec-crawler crawl` БД метаданных | 12 июн | spec-crawler |
| 5 | 🟡 | SpecDownloader agent обновлён | 12 июн | spec-crawler |
| 6 | 🟡 | Librarian agent: два пути (!INCOMING flat + spec-crawler nested) | 12 июн | spec-crawler |
| 7 | 🟡 | Skill `/spec-download` создан | 12 июн | spec-crawler |
| 8 | 🟡 | LibreOffice 26.2.4.2 установлен | 12 июн | docling |
| 9 | 🟡 | Docling fix: `PipelineOptions` → `PdfPipelineOptions` | 12 июн | docling |
| 10 | 🟡 | Docling пилот: 5 спецификаций CPU | 12 июн | docling |
| 11 | 🟡 | Docling миграция: 11×3GPP + 5×ETSI = 16 MD+JSON | 13 июн | docling |
| 12 | 🔴 | `std::bad_alloc` анализ: OOM в PIL/pypdfium2, не GPU | 13 июн | debugging |
| 13 | 🔴 | Torch CUDA проверка → `torch-2.12.0+cu126` (RTX 3060) | 13 июн | cuda |
| 14 | 🟡 | Reviewer v3: гибридный Pass 1 (TXT Grep / JSON lookup / MD read) | 13 июн | reviewer |
| 15 | 🟡 | SpecExtractor v2: PyPDF2 + Docling dual approach | 13 июн | specextractor |
| 16 | 🔴 | B1: `Спецификации` → `Specifications` (90 файлов + 6 агентов) | 13 июн | cyrillic |
| 17 | 🔴 | B2: PyTorch CUDA (RTX 3060) | 13 июн | cuda |
| 18 | 🟡 | B3: CPU vs GPU бенчмарк (3 стадии, 2.4-4.2× speedup) | 13 июн | cuda |
| 19 | 🔴 | B8/F1-F3: bad_alloc решён (247→1), данные не потеряны | 13 июн | debugging |
| 20 | 🟡 | Архитектура v2: `ARCHITECTURE-v2.md` | 13 июн | architecture |
| 21 | 🟡 | Глубокий ресерч: 23 находки, 14 проблем, 10 улучшений | 13 июн | deep-research |
| 22 | 🔴 | U1: Git init + первый коммит (`a35abfc`) | 13 июн | git |
| 23 | 🟡 | U2: Auto-lint hook (PostToolUse) | 13 июн | git |
| 24 | 🟢 | U3: Удалён старый `Спецификации/` дубликат | 13 июн | cyrillic |
| 25 | 🟡 | U4-U10: INDEX.md, `/research` skill, category-map, диаграммы, валидатор | 13 июн | infrastructure |
| 26 | 🟡 | B4: ETSI Docling миграция (26 PDF → 37 MD+JSON пар total) | 13 июн | docling |
| 27 | 🟢 | B5-B7: `.claude/CLAUDE.md`, `specs-extracted/INDEX.md`, `outputs/STATUS_AND_PLAN.md` | 13 июн | documentation |
| 28 | 🟢 | `_tech/` реорганизация: architecture/, plans/, reports/, README | 13 июн | infrastructure |
| 29 | 🟡 | R1 fix: авто-переход Librarian→/ingest в specdownloader.md | 13 июн | pipeline-fix |
| 30 | 🟡 | R2 fix: авто-вызов SpecExtractor в /ingest SKILL.md | 13 июн | pipeline-fix |
| 31 | 🟡 | R4 fix: единый source of truth серия→тема (.category-map.md) | 13 июн | pipeline-fix |
| 32 | 🟡 | U9 fix: check_frontmatter.py — yaml.safe_load, 0 ошибок, 58 warnings | 13 июн | validator |
| 33 | 🟡 | F1 fix: auto_patch_docling.py + pre-flight в SpecExtractor | 13 июн | pipeline-fix |
| 34 | 🟢 | P2-3: CLAUDE.md модуляризация — 6 includes, 47 строк, 5.4× сжатие | 13 июн | modularization |
| 35 | 🟢 | P2-4: Batch Authoring — 4 call sites обновлены на Author v2 | 13 июн | batch-authoring |
| 36 | 🟢 | P2-6: /spec-download полная автоматизация 7 шагов | 13 июн | pipeline-fix |
| 37 | 🟢 | P2-7: extract_docx.py TIER 1 — ARCHITECTURE-v3, 4 call sites, тесты | 14 июн | tier1-pipeline |
| 38 | 🟢 | P2-5: Pipeline Parallelization — параллельный Author v2 dispatch | 14 июн | pipeline-parallel |
| 39 | 🟢 | P2-1: connectivity audit — audit_connectivity.py, 0 битых, 1 сирота | 14 июн | connectivity |
| 40 | 🟢 | P2-2: quality_metrics.py — 8 категорий, history JSON, Score 91/100 (A) | 14 июн | quality |
| 41 | 🔵 | P3-3: Удалён нулевой файл `SIM_презентация_RU.pdf.md` (0 байт) | 14 июн | cleanup |
| 42 | 🔵 | P3-5: Docling-миграция 32 PDF — 30/31 (99%), 1 fail (кириллица) | 14 июн | docling-migration |
| 43 | 🟢 | P2-8 (частично): speckit — `_pipeline/` (10 модулей), `.venv` с CUDA, CLI | 14 июн | speckit |
| 44 | 🟢 | Аудит `_tech/plans`: 5 планов в архив, consolidation-plan актуализирован | 14 июн | plans-audit |
| 45 | 🟢 | Graphify: граф ObsidianDB — 7,580 узлов, 19,645 рёбер, 380 сообществ | 14 июн | graphify |
| 46 | 🟢 | Core vs Data: отчёт-анализ разделения (P2-10 создан) | 14 июн | architecture |
| 47 | 🟢 | BACKLOG v3: +3 задачи (P2-10, P3-5.1, P4-1, P4-2), ребаланс приоритетов | 14 июн | backlog |
| 48 | 🟢 | speckit hit-list миграция: 13 файлов, декомиссия 5 GB, агенты → _pipeline | 14 июн | speckit-migration |
| 49 | 🟢 | P2-8 + P2-9 завершены: speckit 100%, CIAO 3gpp-crawler | 14 июн | speckit |
| 50 | 🟢 | R1-R4 применены: 7 оркестрационных рёбер, /lint консолидация, граф обновлён | 14 июн | orchestration |
| 51 | 🟢 | P2-10 Фаза 2: .gitignore Core/Data (234 tracked, 110 PDF excluded) | 14 июн | git-strategy |
| 52 | 🟢 | Диаграммы обновлены: 5 Mermaid-диаграмм по реальным данным графа | 14 июн | diagrams |
| 53 | 🟢 | STRUCTURE.md + _tech/INDEX.md: навигационная карта проекта | 14 июн | structure |
| 54 | 🟢 | Root cleanup: дубликаты удалены, Добро пожаловать.md → notes/ | 14 июн | cleanup |
| 55 | 🟢 | Research-пайплайн: operator_icon_display_pipeline.md, R1-R4, Reviewer | 14 июн | research-test |
| 56 | 🟢 | .spec-registry.md: 99 спецификаций, Researcher v2 (spec-first priority) | 14 июн | spec-registry |
| 57 | 🟢 | registry suggest/update CLI, 68 названий из WhatTheSpec API | 14 июн | registry-cli |

</details>

---

## 📅 Хронология сессий

| Дата | Сессия | Выполнено | Ключевые вехи |
|---|---|---|---|
| 12 июн 16:00 | architecture | Аудит, `_tech/` создан | Старт |
| 12 июн 17:00 | spec-crawler | 3gpp-crawler интеграция, SpecDownloader, Librarian v2 | Автоматическая загрузка |
| 12 июн 18:00 | docling | Docling fix + миграция 16 спецификаций | Первый Docling GPU прогон |
| 13 июн 00:30 | reviewer+cuda | Reviewer v3, SpecExtractor v2, B3 бенчмарк, анализ OOM | Гибридный Pass 1 |
| 13 июн 01:30 | cuda+fix | B2 CUDA, B8 fix, Архитектура v2 | RTX 3060 активирован |
| 13 июн 03:00 | deep-research | Глубокий ресерч, `.gitignore` аудит, `_tech/` реорганизация | 23 находки |
| 13 июн 14:00 | git+infra | U1-U10: git, хуки, `/research`, category-map, диаграммы | Критические исправления |
| 13 июн 15:30 | docling+docs | B4-B7: ETSI миграция, обновление системных файлов | **37 MD+JSON пар** |
| 13 июн 16:30 | backlog | Редизайн BACKLOG.md: dashboard, mermaid, сводная таблица | **Это обновление** |
| 13 июн 18:00 | graphify+audit | Graphify-граф (7,410 узлов), architecture-deep-research-report.md | Полный архитектурный аудит |
| 13 июн 18:30 | pipeline-fix | R1+R2+R4 fixes, pipeline-bottleneck-analysis.md | Минимальный фикс пайплайнов |
| 13 июн 19:15 | batch-authoring | Author v2 (Batch+Single режимы), batch-authoring-analysis.md | P3-4 отменён, Author Split не нужен |
| 13 июн 20:15 | validator-fix | P1-1 U9 fix: check_frontmatter.py yaml.safe_load | 0 ошибок, 58 warnings |
| 13 июн 21:15 | batch-authoring | P2-4+P2-6: Batch Authoring в 4 call sites + авто 7 шагов | 4 call sites обновлены |
| 14 июн 02:00 | tier1-pipeline | P2-7: extract_docx.py TIER 1 — ARCHITECTURE-v3, 4 call sites | 0.2 сек vs 3 мин |
| 14 июн 11:00 | connectivity+quality | P2-1+P2-2: connectivity audit + quality metrics | Score 98/100 (A) |
| 14 июн 12:00 | speckit | P2-8: `_pipeline/` (10 модулей), `.venv` с CUDA, CLI рабочий | GPU через venv |
| 14 июн 13:30 | plans-audit | Аудит `_tech/plans`: 5 планов в архив, consolidation-plan v3, BACKLOG v2 | Планы разобраны |
| 14 июн 14:00 | graphify | `/graphify . --enhanced`: 7,580 узлов, 19,645 рёбер, 380 сообществ | 30.7× сжатие |
| 14 июн 14:20 | core-vs-data | Отчёт-анализ Core vs Data разделения, P2-10 в беклог | Разделение спроектировано |
| 14 июн 14:30 | speckit-migration | **speckit hit-list миграция**: 13 файлов, декомиссия 5 GB, 100% переход | **CIAO 3gpp-crawler** |
| 14 июн 15:00 | orchestration | R1-R4: 7 рёбер, /lint консолидация, Agent Orchestration Map + Graph Analysis | Граф доказал исправления |
| 14 июн 15:30 | core-vs-data-p2 | P2-10 Phase 2: .gitignore (Core 234 tracked, Data excluded), 5 диаграмм по графу | Структура зафиксирована |
| 14 июн 16:00 | backup-sync | backup_data.py + sync_data.py + README, тест: 376 файлов → 53 MB zip | Data-инфраструктура |
| 14 июн 16:20 | spec-registry | .spec-registry.md (99 specs, 14 cat), Researcher v2 (spec-first), registry suggest CLI | **Эта сессия** |

---

## 🏷️ Легенда статусов

| Символ | Статус | Значение |
|---|---|---|
| ⬜ | Не начато | Задача создана, работа не начиналась |
| 🔄 | В работе | Активно выполняется |
| ⚠️ | Требует внимания | Не actively в работе, но требует действий |
| ⏸️ | Отложено | Временно приостановлено |
| ✅ | Завершено | Перенесено в «Завершённые задачи» |
| ❌ | Отменено | Задача более не актуальна |

---

*Беклог актуален на 2026-06-14 16:30. 57 задач завершено. 5 активных (0 P2, 3 P3, 2 P4).*
