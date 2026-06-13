# Skill: research
# Trigger: /research

Запуск глубокого исследования через Researcher agent.

## Синтаксис

```
/research <тема> [--sources <N>] [--depth deep]
```

**Примеры**:
- `/research 5G NR MAC scheduling` — исследование темы
- `/research eSIM SGP.22 architecture --depth deep` — углублённое
- `/research AKA authentication evolution --sources 15` — не менее 15 источников

## Workflow

1. Researcher собирает ВСЕ релевантные источники: summaries, concepts, syntheses, спецификации
2. При необходимости — WebSearch
3. Создаёт страницу в `wiki/research/<slug>.md`

## Параметры Researcher

- **Объём**: 15-50+ KB
- **Источников**: 5-20+
- **Структура**: Обзор → Методология → Основная часть → Код/Практика → Выводы → Ссылки
- **Mermaid-диаграммы** для сложных процессов
- **Сравнительные таблицы** (3+ колонок)
- Добавляет страницу в `wiki/research/index.md`
- Выполняет `/lint` и отмечает в `Roadmap.md`

## Отличия от других форматов

| | Summary | Synthesis | Research |
|---|---|---|---|
| Глубина | Конспект | Кросс-анализ | Исчерпывающий разбор |
| Объём | 1-3 KB | 5-15 KB | 15-50+ KB |
| Источников | 1-2 | 3-7 | 5-20+ |
