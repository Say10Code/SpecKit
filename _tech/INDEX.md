# _tech/ — Инженерный хаб ObsidianDB

> Навигация по инженерной документации проекта. Для общей карты: [[../STRUCTURE.md|STRUCTURE.md]]

## Быстрые ссылки

| Нужен... | Файл |
|---|---|
| Общий беклог | [[BACKLOG.md]] |
| Актуальная архитектура | [[architecture/ARCHITECTURE-v3.md]] |
| Активный план | [[plans/consolidation-plan.md]] |
| Карта оркестрации агентов | [[reports/agent-orchestration-map.md]] |
| Граф-анализ оркестрации | [[reports/agent-orchestration-graph-analysis.md]] |
| Core vs Data разделение | [[reports/core-vs-data-separation-analysis.md]] |
| speckit миграция (hit-list) | [[reports/speckit-migration-hitlist.md]] |
| speckit переход (анализ) | [[reports/speckit-transition-deep-analysis.md]] |
| Batch Authoring анализ | [[reports/batch-authoring-analysis.md]] |
| .docx извлечение анализ | [[reports/direct-docx-extraction-analysis.md]] |
| Pipeline bottleneck анализ | [[reports/pipeline-bottleneck-analysis.md]] |
| Последний аудит связности | [[reports/connectivity-audit-2026-06-14.md]] |
| Последний замер качества | [[reports/quality-metrics-2026-06-14.md]] |

## Структура

```
_tech/
├── INDEX.md              ← Этот файл
├── BACKLOG.md            ← Боевой беклог (52/57 задач)
├── README.md             ← Правила работы с _tech/
│
├── architecture/         ← Архитектурный анализ
│   ├── ARCHITECTURE-v3.md    ← Актуальная
│   └── archive/              ← v1, v2 (история)
│
├── plans/                ← Планы внедрения
│   ├── consolidation-plan.md ← Единственный активный
│   └── archive/              ← 6 завершённых
│
├── reports/              ← Отчёты, анализы, аудиты (16 шт.)
│   └── archive/              ← (пока пусто)
│
├── diagrams/             ← Mermaid-диаграммы (5 шт.)
│
├── scripts/              ← Python-скрипты (13 шт.)
│
├── benchmarks/           ← Результаты бенчмарков/метрик (JSON)
│
└── graphify-scope.md     ← Параметры обхода graphify
```

## Жизненный цикл документов

```
Создание     → plans/<имя>.md
Выполнение   → plans/<имя>.md (обновляется статус)
Завершён     → plans/archive/<имя>.md
Отчёт        → reports/<имя>-report.md
Анализ       → reports/<имя>-analysis.md
Аудит        → reports/<имя>-audit-YYYY-MM-DD.md
Диаграмма    → diagrams/<имя>.md
Скрипт       → scripts/<имя>.py
Бенчмарк     → benchmarks/<имя>_result.json
```

## Naming convention

| Тип | Формат | Пример |
|---|---|---|
| Архитектура | `ARCHITECTURE-v<N>.md` | `ARCHITECTURE-v3.md` |
| План | `<тема>-plan.md` | `consolidation-plan.md` |
| Отчёт | `<тема>-report.md` | `F1F2-verification-report.md` |
| Анализ | `<тема>-analysis.md` | `batch-authoring-analysis.md` |
| Аудит | `<тема>-audit-YYYY-MM-DD.md` | `connectivity-audit-2026-06-14.md` |
| Review | `review-<страница>.md` | `review-operator_icons_on_sim.md` |
| Диаграмма | `<тема>.md` | `agent-interactions.md` |
| Скрипт | `snake_case.py` | `quality_metrics.py` |
| Бенчмарк | `bench_<тема>_result.json` | `bench_b3_result.json` |

---

*Обновлено: 2026-06-14.*
