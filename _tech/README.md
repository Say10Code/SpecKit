# _tech/ — Инженерная документация ObsidianDB

> **Назначение**: Техническая папка для архитектурного анализа, планов, отчётов и инструментов.
> **НЕ участвует** в knowledge-пайплайне. НЕ индексируется в `wiki/`. НЕ ссылается из `wiki/`.
> **Навигация**: [[INDEX.md]] — полный индекс инженерных документов.

---

## Правила работы с `_tech/`

### 1. Структура — по назначению

| Папка | Назначение | Примеры |
|---|---|---|
| `architecture/` | Актуальный архитектурный анализ | `ARCHITECTURE-v3.md` |
| `architecture/archive/` | Предыдущие версии архитектуры | `ARCHITECTURE-v1.md`, `ARCHITECTURE-v2.md` |
| `plans/` | Планы внедрения и улучшения | `consolidation-plan.md`, `3gpp-crawler-*.md` |
| `plans/archive/` | Выполненные планы | `cyrillic-rename-plan.md` |
| `reports/` | Отчёты верификации, бенчмарков | `review-*.md`, `batch-authoring-analysis.md` |
| `reports/archive/` | Устаревшие отчёты | — |
| `diagrams/` | Mermaid-диаграммы (визуализация) | `agent-interactions.md` |
| `scripts/` | Python-скрипты для тулинга | `quality_metrics.py`, `audit_connectivity.py` |
| `benchmarks/` | Только `*result.json` + `*_history.json` | `benchmark_b3_result.json`, `quality_metrics_history.json` |
| Корень | Активный беклог + этот README | `BACKLOG.md`, `README.md` |

### 2. Жизненный цикл документа

```
Создание        → plans/<имя>.md
После реализации → plans/archive/<имя>.md  (или reports/ если это отчёт)
Устаревание     → reports/archive/<имя>.md
```

**Правило**: в корне `_tech/` — только `README.md` и `BACKLOG.md`. Все остальные файлы в подпапках.

### 3. Обновление при изменениях

- **После каждого завершения задачи**: обновить `BACKLOG.md` (статус задач, дата, хронология, метрики)
- **После каждой сессии**: проверить актуальность `BACKLOG.md`
- **После каждого архитектурного изменения**: обновить `architecture/ARCHITECTURE-vN.md` или создать `vN+1`
- **После каждого бенчмарка/верификации**: добавить `reports/<имя>.md`, сохранить `benchmarks/<имя>_result.json`
- **Старый файл НЕ удалять** — переместить в `archive/` соответствующей папки

### 4. Именование файлов

- **Архитектура**: `ARCHITECTURE-v<N>.md` (v1, v2, v3, ...)
- **Планы**: `<тема>-plan.md` или `<тема>.md`
- **Отчёты**: `<тема>-report.md`, `<тема>-analysis.md`, `review-*.md`
- **Скрипты**: `snake_case.py`
- **Бенчмарки**: `<тема>_result.json`, `<тема>_history.json`

### 5. Backlog

- Единственный файл в корне `_tech/` (кроме README)
- Задачи: формат `P<приоритет>-<N>` (P1-1, P2-3) с приоритетами P0-P3
- **⚠️ После каждого завершения задачи**: обновить BACKLOG.md — перенести в «Завершённые», обновить сводную таблицу, дашборд, хронологию сессий
- **⚠️ После каждой сессии**: обновить BACKLOG.md — актуализировать дату, статусы, хронологию, пересчитать метрики
- После выполнения: задача перемещается в «Завершённые задачи» (НЕ удаляется)
- Хронология сессий: дата + имя сессии + что выполнено + ключевые вехи
- Никогда не закрывай сессию с устаревшим беклогом
- Проставлять общую дату сохранения файла в шапке вверху (внесение изменений)

---

## Быстрые ссылки

| Назначение | Путь |
|---|---|
| Архитектура (актуально) | [[_tech/architecture/ARCHITECTURE-v3.md\|ARCHITECTURE-v3.md]] |
| Предыдущая архитектура | [[_tech/architecture/archive/ARCHITECTURE-v2.md\|v2]] |
| Активный беклог | [[_tech/BACKLOG.md\|BACKLOG.md]] |
| План консолидации (speckit) | [[_tech/plans/consolidation-plan.md\|Consolidation plan]] (v3, 70% реализовано) |
| Batch Authoring анализ | [[_tech/reports/batch-authoring-analysis.md\|Batch Authoring]] |
| Сравнение консолидации | [[_tech/reports/consolidation-comparison.md\|Consolidation comparison]] |
| Архитектурный deep-research | [[_tech/reports/architecture-deep-research-report.md\|Architecture audit]] |
| Прямое .docx извлечение | [[_tech/reports/direct-docx-extraction-analysis.md\|.docx analysis]] |
| Pipeline bottleneck анализ | [[_tech/reports/pipeline-bottleneck-analysis.md\|Pipeline analysis]] |
| Архив: build integration | [[_tech/plans/archive/3gpp-crawler-build-integration-plan.md\|Build plan]] |
| Архив: 3gpp-crawler интеграция | [[_tech/plans/archive/3gpp-crawler-integration-plan.md\|Integration vision]] |
| Архив: improvement plan | [[_tech/plans/archive/IMPROVEMENT_PLAN.md\|Improvement snapshot]] |
| Архив: specs-extracted миграция | [[_tech/plans/archive/specs-extracted-migration-plan.md\|Migration plan]] |
| Архив: directory architecture | [[_tech/plans/archive/specs-directory-architecture.md\|Dir architecture]] |
| Аудит связности (последний) | [[_tech/reports/connectivity-audit-2026-06-14.md\|Connectivity audit]] |
| Quality metrics (последний) | [[_tech/reports/quality-metrics-2026-06-14.md\|Quality metrics]] |
| Review — operator_icons | [[_tech/reports/review-operator_icons_on_sim.md\|Operator icons review]] |
| Review — R16/R17 specs | [[_tech/reports/review-r16r17-specs-2026-06-14.md\|R16/R17 review]] |

---

## Инвентаризация скриптов

| Скрипт | Назначение | Вызывается |
|---|---|---|
| `backup_data.py` | Бэкап Data-слоя в ZIP с манифестом | Вручную / cron |
| `sync_data.py` | Синхронизация Data между проектами | Вручную |
| `quality_metrics.py` | 8 категорий метрик + history JSON | `/roadmap` |
| `audit_connectivity.py` | Граф-анализ wikilinks | `/lint --deep` |
| `check_frontmatter.py` | Валидация YAML frontmatter (yaml.safe_load) | Вручную / quality_metrics |
| `auto_patch_docling.py` | F1 fix для docling (try/except bad_alloc) | SpecExtractor (pre-flight) |
| `docling_migrate.py` | Пакетная миграция PDF → Docling MD+JSON (GPU) | Вручную |
| `bench_cpu_vs_gpu.py` | Бенчмарк CPU vs GPU — проверка CUDA | Вручную (диагностика) |
| `build_html.py` | Пакетный экспорт wiki/ → HTML | Вручную |

> **Примечание**: `extract_docx.py` перенесён в `_pipeline/extract_docx.py` (speckit). Вызов: `python -m _pipeline extract docx`.

> **Удалены** (2026-06-14): `diagnose_badalloc.py`, `docling_batch_etsi.py`, `verify_f1f2_quality.py`, `convert_research.py` — одноразовые/устаревшие.

---

## Текущее состояние (срез)

| Метрика | Значение |
|---|---|
| Sub-agents | 8 (+ Author v2 batch, SpecExtractor v3) |
| Skills | 7 (+research) |
| Includes | 6 (structure, agents, skills, standards, incoming, 3gpp-crawler) |
| Wiki страниц | 130 (+7 index) |
| Reviewed | 94.6% |
| Битых ссылок | 0 |
| Сирот | 1 (`telcoai_3gpp_search`) |
| Specifications/ PDF | 74 (+ 20 R16/R17 docx) |
| specs-extracted/ | 78 TXT + 86 MD + 73 JSON |
| Torch CUDA | ✅ RTX 3060 (11 GB), 2.4-4.2× CPU |
| .venv (uv sync) | ✅ docling + torch (CUDA) + httpx + PyPDF2 + rich |
| _pipeline/ (speckit) | ✅ 10 модулей, 5 CLI-команд, GPU активен |
| 3gpp-crawler | 🗑️ Декомиссия выполнена (2026-06-14) |
| .speckit/ | ✅ Кэш метаданных (бывш. .3gpp-crawler) |
| Quality Score | **98/100 (A)** |
| Git | ✅ 6 коммитов |
| GitHook (PostToolUse) | ✅ Напоминание /lint |
| Frontmatter validator | 0 ошибок, 58 warnings (yaml.safe_load) |
| Graphify | Граф 7,580 узлов, 19,645 рёбер, 380 сообществ (2026-06-14) |
| Беклог | 49/55 задач завершено (0 P0, 0 P1, 1 P2, 3 P3, 2 P4) |

---

## Карта отчётов

| Отчёт | Дата | Тема |
|---|---|---|
| `architecture-deep-research-report.md` | 13 июн | Полный архитектурный аудит (graphify + ручной) |
| `pipeline-bottleneck-analysis.md` | 13 июн | 5 разрывов в /spec-download + Author bottleneck |
| `batch-authoring-analysis.md` | 13 июн | Batch Authoring vs Author Split — польза и риски |
| `direct-docx-extraction-analysis.md` | 14 июн | .docx = ZIP/XML — 875× быстрее, таблицы сохранены |
| `review-operator_icons_on_sim.md` | 14 июн | Review — 3 CRITICAL + 5 HIGH исправлено |
| `review-r16r17-specs-2026-06-14.md` | 14 июн | Review после загрузки R16/R17 — 8 страниц |
| `consolidation-comparison.md` | 14 июн | Сравнение текущей архитектуры vs speckit |
| `connectivity-audit-2026-06-14.md` | 14 июн | Аудит связности — 0 битых, 1 сирота |
| `quality-metrics-2026-06-14.md` | 14 июн | Quality Score 98/100 (A) |

---

*Обновлено: 2026-06-14 15:30. Архитектура: v3. Беклог: 52/57. speckit: 100%. Навигация: [[INDEX.md]].*
