# Hit-list: миграция с 3gpp-crawler на speckit

> **Создан**: 2026-06-14 · **Метод**: граф-трассировка (7,580 узлов) + grep по всем файлам
> **Прогресс кода**: 90% · **Прогресс интеграции**: 0% · **Файлов к изменению**: 13

---

## Сводка

| Tier | Тип | Файлов | Действие |
|---|---|---|---|
| **T1** 🔴 | Агенты / Skills / Includes | 7 | Переписать: `spec-crawler` → `python -m _pipeline` |
| **T2** 🟡 | Root config / Dispatcher | 2 | Точечные правки: ссылки и упоминания |
| **T3** 🟢 | Pipeline code / Scripts | 4 | Минорные правки: docstring'и, пути, удаление dead code |
| **D** 🗑️ | Удалить | 2 | `3gpp-crawler.toml` + `3gpp-crawler/` (5 GB) |
| **K** 📋 | Документация | 8 | Обновить после миграции |
| **H** 📦 | Архив | 18 | Никогда не трогать |

---

## 🔴 TIER 1: Агенты / Skills / Includes (7 файлов)

### T1.1 — `.claude/agents/specdownloader.md` (ПОЛНЫЙ ПЕРЕПИС)

**Сейчас**: 20+ упоминаний `spec-crawler`, вся команда — shell-вызовы
**Строки**: 3, 10, 14, 16, 17-18, 23, 33, 39, 46, 52, 60, 69, 140, 165, 168, 171, 173, 180, 183

| Строка | Было | Стало |
|---|---|---|
| 3 | `через spec-crawler напрямую в` | `через speckit (_pipeline/) напрямую в` |
| 10 | `spec-crawler crawl <номер>` | `python -m _pipeline metadata fetch <номер>` |
| 14 | `D:\ObsidianDB\3gpp-crawler\` (локальная копия) | `_pipeline/` (speckit, встроен в проект) |
| 16 | `3gpp-crawler.toml` — авто-обнаружение | `pyproject.toml` + `_pipeline/config.py` |
| 17-18 | `.3gpp-crawler\` + `3gpp_crawler.db` | `.speckit/` + `metadata.db` (или `.3gpp-crawler/` read-only) |
| 23 | `Все команды spec-crawler должны...` | Удалить (speckit — Python-модуль, CWD не важен) |
| 33 | `spec-crawler crawl 31.102` | `python -m _pipeline metadata fetch 31.102` |
| 39 | `spec-crawler crawl 31.102 102.221 102.223` | `python -m _pipeline metadata fetch 31.102 102.221 102.223` |
| 46 | `spec-crawler checkout 31.102 --checkout-dir ...` | `python -m _pipeline download 31.102` |
| 52 | `spec-crawler checkout 31.102 --release 18.0 ...` | `python -m _pipeline download 31.102 --release 18.0` |
| 60 | `spec-crawler checkout 31.102 102.221 ...` | `python -m _pipeline download 31.102 102.221 102.223` |
| 69 | `...создаётся spec-crawler автоматически` | `...создаётся _pipeline (совместимо с spec-crawler)` |
| 165-173 | `3gpp-crawler workspace create/add/process` | Удалить (speckit не требует workspace) |
| 180, 183 | `cd в D:\ObsidianDB` + `.3gpp-crawler/ не коммитится` | Удалить (speckit — Python-модуль) |

**Оценка**: 15 мин. Фактически — замена 20 строк shell-команд на Python-вызовы.

---

### T1.2 — `.claude/agents/specextractor.md` (СРЕДНИЙ ПЕРЕПИС)

**Строки**: 25, 58, 65, 68, 69, 72, 79, 108, 110, 130, 162, 163, 236

| Строка | Что меняется |
|---|---|
| 25 | `uv tool install --reinstall 3gpp-crawler` → `uv sync` (патч больше не нужен — .venv локальный) |
| 58 | `через spec-crawler` → `через _pipeline` |
| 65 | `spec-crawler crawl 31.102` → `python -m _pipeline metadata fetch 31.102` |
| 68-72 | `3gpp-crawler workspace create/add/process` → `python -m _pipeline extract docling <pdf>` |
| 79 | `из spec-crawler checkout` → `из _pipeline download` |
| 108, 110 | `spec-crawler checkout` → `_pipeline download` |
| 130 | `.3gpp-crawler/wiki/<workspace>/...` → `specs-extracted/<category>/...` |
| 162-163 | Удалить строки про spec-crawler и workspace process |
| 236 | `Docling + spec-crawler` → `Docling + _pipeline` |

**Оценка**: 10 мин.

---

### T1.3 — `.claude/agents/librarian.md` (ЛЁГКИЙ ПЕРЕПИС)

**Строки**: 14, 15, 41, 105

| Строка | Что меняется |
|---|---|
| 14-15 | `Путь B: spec-crawler checkout` → убрать упоминание spec-crawler, оставить «Путь B: _pipeline download» |
| 41 | `Обработка spec-crawler checkout (путь B)` → `Обработка _pipeline download (путь B)` |
| 105 | `от spec-crawler` → `от _pipeline` |

**Примечание**: Librarian не меняет логику — `_pipeline/_download_spec.py` зеркалит структуру spec-crawler. Только косметика.

**Оценка**: 5 мин.

---

### T1.4 — `.claude/skills/spec-download/SKILL.md` (ЛЁГКИЙ ПЕРЕПИС)

**Строки**: 4, 32, 39, 73, 109

| Строка | Что меняется |
|---|---|
| 4 | `через spec-crawler` → `через speckit (_pipeline/)` |
| 32 | `spec-crawler crawl 31.102 102.221 ...` → `python -m _pipeline metadata fetch 31.102 ...` |
| 39 | `spec-crawler checkout 31.102 ...` → `python -m _pipeline download 31.102 ...` |
| 73 | `spec-crawler checkout` → `_pipeline download` |
| 109 | `spec-crawler их не найдёт` → `_pipeline их не найдёт` |

**Оценка**: 5 мин.

---

### T1.5 — `.claude/includes/3gpp-crawler.md` (ПОЛНЫЙ ПЕРЕПИС → speckit.md)

**Сейчас**: 21 строка про spec-crawler CLI
**Стало**: include про speckit с командами `python -m _pipeline`

Новое содержание:
```markdown
# speckit Integration

**speckit** — встроенный Python-пакет (`_pipeline/`), загружает и извлекает спецификации 3GPP/ETSI.

## Команды

python -m _pipeline metadata fetch 31.102    # Обновить метаданные (WhatTheSpec API)
python -m _pipeline download 31.102          # Скачать spec → !INCOMING/
python -m _pipeline download 31.102 -r 18.0  # Конкретный релиз
python -m _pipeline extract docx <path>      # Tier 1: .docx → TXT+MD (0.2 сек)
python -m _pipeline extract docling <path>   # Tier 2: PDF → MD+JSON (GPU)
python -m _pipeline extract pypdf2 <path>    # Tier 3: PDF → TXT (fallback)
python -m _pipeline status                   # Статус: что скачано/извлечено

## Кэш

- `.speckit/` — БД метаданных (SQLite) + HTTP-кэш
- GPU: CUDA через `.venv` (RTX 3060, 12 GB)
```

**Оценка**: 10 мин.

---

### T1.6 — `.claude/includes/incoming.md` (ТОЧЕЧНАЯ ПРАВКА)

**Строка 10**: `## Path B: spec-crawler checkout` → `## Path B: _pipeline download`

**Оценка**: 1 мин.

---

### T1.7 — `.claude/includes/structure.md` (ТОЧЕЧНАЯ ПРАВКА)

**Строка 28**: `3gpp-crawler.toml` → убрать из дерева (или заменить на `pyproject.toml`)

**Оценка**: 1 мин.

---

## 🟡 TIER 2: Root config / Dispatcher (2 файла)

### T2.1 — `CLAUDE.md` (корень, строка 16)

| Было | Стало |
|---|---|
| `\| 3gpp-crawler интеграция \| .claude/includes/3gpp-crawler.md \|` | `\| speckit интеграция \| .claude/includes/speckit.md \|` |

**Оценка**: 1 мин.

### T2.2 — `.claude/CLAUDE.md` (строки 10, 21)

| Строка | Было | Стало |
|---|---|---|
| 10 | `3gpp-crawler` в списке includes | `speckit` |
| 21 | `Интеграция с 3gpp-crawler: ...` | `speckit: _pipeline/ (10 модулей), .venv с CUDA` |

**Оценка**: 2 мин.

---

## 🟢 TIER 3: Pipeline code / Scripts (4 файла)

### T3.1 — `_pipeline/_download_spec.py` (строки 1-3, 47-49)

Docstring'и упоминают `spec-crawler-compatible structure` и `spec-crawler creates`. Это корректно — код *зеркалит* структуру. Менять не обязательно, но можно убрать «spec-crawler» из docstring'ов.

**Оценка**: 2 мин (косметика).

### T3.2 — `_pipeline/config.py` (строка 9)

`CACHE_DIR = ROOT / ".3gpp-crawler"` → `CACHE_DIR = ROOT / ".speckit"`

**Важно**: `.3gpp-crawler/` содержит готовую БД метаданных. Либо: (а) переименовать в `.speckit/`, либо (б) оставить `.3gpp-crawler/` read-only и создать новую `.speckit/`. Рекомендую (а) — просто переименовать.

**Оценка**: 1 мин + `mv .3gpp-crawler .speckit`.

### T3.3 — `.claude/scripts/spec_download.py` (ВЕСЬ ФАЙЛ — УДАЛИТЬ/ЗАМЕНИТЬ)

92 строки. Это bridge-скрипт между ObsidianDB и spec-crawler CLI. После миграции не нужен. Заменить на вызов `python -m _pipeline download`.

**Оценка**: 2 мин (удалить или переписать в 5 строк).

### T3.4 — `_tech/scripts/auto_patch_docling.py` (строки 3, 119)

| Строка | Было | Стало |
|---|---|---|
| 3 | `uv tool install --reinstall 3gpp-crawler` | `uv sync` (патч больше не нужен в отдельном venv) |
| 119 | `Install 3gpp-crawler first` | Удалить (speckit управляется через pyproject.toml) |

**Примечание**: F1-патч всё ещё нужен для docling, но теперь он применяется через `.venv/` а не через `uv tool`. Сам `auto_patch_docling.py` остаётся полезным — просто docstring и сообщение об ошибке устарели.

**Оценка**: 2 мин.

---

## 🗑️ TIER D: Удалить (2 объекта)

### D1 — `3gpp-crawler.toml`
Удалить. Конфиг spec-crawler. Speckit использует `pyproject.toml` + `_pipeline/config.py`.

### D2 — `3gpp-crawler/` (5 GB)
Удалить рекурсивно. Исходники внешнего проекта. Не используются после миграции.

### D3 — `.3gpp-crawler/` → переименовать в `.speckit/`
Сохранить как read-only бэкап метаданных (или удалить после верификации).

---

## 📋 TIER K: Обновить документацию (8 файлов — после миграции)

| Файл | Что обновить |
|---|---|
| `_tech/BACKLOG.md` | P2-8 и P2-9 → завершены; P2-10 → обновить статус |
| `_tech/README.md` | Стек: убрать 3gpp-crawler, добавить speckit |
| `_tech/plans/consolidation-plan.md` | Этап 5, 7 → ✅ |
| `_tech/architecture/ARCHITECTURE-v3.md` | Обновить references |
| `_tech/reports/consolidation-comparison.md` | Добавить «post-migration» сноску |
| `Roadmap.md` | Обновить references |
| `Specifications/.category-map.md` | Убрать spec-crawler references |
| `_tech/diagrams/*.md` (3 файла) | Обновить «spec-crawler» → «speckit» |

---

## 📦 TIER H: Архив (18 файлов — никогда не трогать)

Это исторические документы. Они описывают состояние на момент написания. Менять их — falsify history.

```
_tech/plans/archive/3gpp-crawler-build-integration-plan.md
_tech/plans/archive/3gpp-crawler-integration-plan.md
_tech/plans/archive/IMPROVEMENT_PLAN.md
_tech/plans/archive/cyrillic-rename-plan.md
_tech/plans/archive/specs-directory-architecture.md
_tech/plans/archive/specs-extracted-migration-plan.md
_tech/architecture/archive/ARCHITECTURE-v1.md
_tech/architecture/archive/ARCHITECTURE-v2.md
_tech/reports/deep-research-report.md
_tech/reports/architecture-deep-research-report.md
_tech/reports/pipeline-bottleneck-analysis.md
_tech/reports/gitignore-audit.md
_tech/reports/F1F2-verification-report.md
_tech/reports/review-r16r17-specs-2026-06-14.md
_tech/reports/badalloc-solution.md
outputs/STATUS_AND_PLAN.md
.obsidian/workspace.json
_tech/graphify-scope.md
```

---

## 📊 Итого: план работ

| # | Файл | Действие | Мин |
|---|---|---|---|
| T1.1 | `.claude/agents/specdownloader.md` | Полный перепис | 15 |
| T1.2 | `.claude/agents/specextractor.md` | Средний перепис | 10 |
| T1.3 | `.claude/agents/librarian.md` | Косметика | 5 |
| T1.4 | `.claude/skills/spec-download/SKILL.md` | Лёгкий перепис | 5 |
| T1.5 | `.claude/includes/3gpp-crawler.md` | Перепис → `speckit.md` | 10 |
| T1.6 | `.claude/includes/incoming.md` | 1 строка | 1 |
| T1.7 | `.claude/includes/structure.md` | 1 строка | 1 |
| T2.1 | `CLAUDE.md` (корень) | 1 строка | 1 |
| T2.2 | `.claude/CLAUDE.md` | 2 строки | 2 |
| T3.1 | `_pipeline/_download_spec.py` | Косметика docstring | 2 |
| T3.2 | `_pipeline/config.py` | `CACHE_DIR` + `mv .3gpp-crawler .speckit` | 1 |
| T3.3 | `.claude/scripts/spec_download.py` | Удалить / переписать | 2 |
| T3.4 | `_tech/scripts/auto_patch_docling.py` | 2 строки | 2 |
| D1 | `3gpp-crawler.toml` | Удалить | 1 |
| D2 | `3gpp-crawler/` | `rm -rf` (5 GB) | 1 |
| D3 | `.3gpp-crawler/` | `mv .3gpp-crawler .speckit` | 1 |
| K1-8 | Документация | 8 файлов | 15 |
| | **Всего** | **13 файлов изменено, 2 удалено, 1 переименовано** | **~75 мин** |

---

## 🎯 Порядок выполнения

```
Фаза 0: Подготовка (5 мин)
  → mv .3gpp-crawler .speckit
  → mkdir -p _pipeline/__pycache__  (гарантировать что пакет импортируется)

Фаза 1: Кодовые правки (5 мин)  [T3.1-T3.4]
  → поправить docstring'и, config, удалить bridge-скрипт

Фаза 2: Агенты и Skills (35 мин)  [T1.1-T1.4]
  → полный перепис SpecDownloader + SpecExtractor
  → косметика Librarian + spec-download skill

Фаза 3: Includes и Dispatcher (15 мин)  [T1.5-T1.7, T2.1-T2.2]
  → переписать 3gpp-crawler.md → speckit.md
  → обновить CLAUDE.md (оба)

Фаза 4: Документация (15 мин)  [K1-K8]
  → обновить BACKLOG, README, Roadmap, диаграммы

Фаза 5: Декомиссия + верификация (5 мин)  [D1-D3]
  → rm 3gpp-crawler.toml
  → rm -rf 3gpp-crawler/
  → python -m _pipeline download 31.102  (тест)
  → /spec-download 31.102  (полный тест)
```

---

*Hit-list создан 2026-06-14. 13 файлов к изменению. Полная миграция — 1 сессия ~75 мин.*
