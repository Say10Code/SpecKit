# _tech/ — Инженерная документация ObsidianDB

> **Назначение**: Техническая папка для архитектурного анализа, планов, отчётов и инструментов.
> **НЕ участвует** в knowledge-пайплайне. НЕ индексируется в `wiki/`. НЕ ссылается из `wiki/`.

---

## Правила работы с `_tech/`

### 1. Структура — по назначению

| Папка | Назначение | Примеры |
|---|---|---|
| `architecture/` | Актуальный архитектурный анализ | `ARCHITECTURE-v2.md` |
| `architecture/archive/` | Предыдущие версии архитектуры | `ARCHITECTURE-v1.md` |
| `plans/` | Планы внедрения и улучшения | `IMPROVEMENT_PLAN.md`, `3gpp-crawler-*.md` |
| `plans/archive/` | Выполненные планы | `cyrillic-rename-plan.md` |
| `reports/` | Отчёты верификации, бенчмарков | `F1F2-verification-report.md` |
| `reports/archive/` | Устаревшие отчёты | — |
| `diagrams/` | Mermaid-диаграммы (визуализация) | `agent-interactions.md` |
| `scripts/` | Python-скрипты для тулинга | `docling_batch_etsi.py` |
| `benchmarks/` | Только `*result.json` (сырые данные) | `benchmark_b3_result.json` |
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

- **Архитектура**: `ARCHITECTURE-v<N>.md` (v1, v2, ...)
- **Планы**: `<тема>-plan.md` или `<тема>.md`
- **Отчёты**: `<тема>-report.md` или `<тема>-verification.md`
- **Скрипты**: `snake_case.py`
- **Бенчмарки**: `<тема>_result.json`

### 5. Backlog

- Единственный файл в корне `_tech/` (кроме README)
- Задачи: формат `P<приоритет>-<N>` (P1-1, P2-3, ...) с приоритетами P0-P3
- **⚠️ После каждого завершения задачи**: обновить BACKLOG.md — перенести в «Завершённые», обновить сводную таблицу, дашборд, хронологию сессий
- **⚠️ После каждой сессии**: обновить BACKLOG.md — актуализировать дату, статусы, хронологию, пересчитать метрики
- После выполнения: задача перемещается в «Завершённые задачи» (НЕ удаляется)
- Хронология сессий: дата + имя сессии + что выполнено + ключевые вехи
- Никогда не закрывай сессию с устаревшим беклогом

---

## Быстрые ссылки

| Назначение | Путь |
|---|---|
| Архитектура (актуально) | [[_tech/architecture/ARCHITECTURE-v2.md\|ARCHITECTURE-v2.md]] |
| Активный беклог | [[_tech/BACKLOG.md\|BACKLOG.md]] |
| План улучшений | [[_tech/plans/IMPROVEMENT_PLAN.md\|IMPROVEMENT_PLAN.md]] |
| Интеграция 3gpp-crawler | [[_tech/plans/3gpp-crawler-build-integration-plan.md\|Build plan]] |
| Миграция specs-extracted | [[_tech/plans/specs-extracted-migration-plan.md\|Migration plan]] |
| Архитектура `Specifications/` | [[_tech/plans/specs-directory-architecture.md\|Directory architecture]] |
| F1+F2 верификация | [[_tech/reports/F1F2-verification-report.md\|F1F2 report]] |
| bad_alloc решение | [[_tech/reports/badalloc-solution.md\|bad_alloc solution]] |

---

## Текущее состояние (срез)

| Метрика | Значение |
|---|---|
| Sub-agents | 8 |
| Skills | 6 |
| Wiki страниц | 129 (+7 index) |
| Reviewed | 100% (0 ошибок) |
| Битых ссылок | 0 |
| Specifications/ PDF | 65 |
| specs-extracted/ | 58 TXT + 16 MD+JSON |
| Torch CUDA | ✅ RTX 3060 12GB |
| 3gpp-crawler | ✅ Интегрирован |
| GPU speedup | 2.4-4.2× CPU |

---

*Обновлено: 2026-06-13 03:00.*
