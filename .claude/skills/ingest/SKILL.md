# Skill: ingest
# Trigger: /ingest

Полный пайплайн обработки нового материала (PDF, clipping, заметка).

## Workflow (Author v2 Batch mode)

### Шаг 1: Batch Authoring — ОДИН проход

Вызови **Author v2 в Batch mode** для создания ВСЕХ страниц за один вызов:

```
Agent: Author v2 — пакетная обработка <путь-к-PDF>
```

**Что делает Batch mode** (см. `.claude/agents/author.md`):
- Читает PDF **один раз** (вместо 3-8 раз)
- Создаёт: summary → concepts → entities → (synthesis) за один вызов
- PDF > 150K знаков → автоматический sequential fallback с context reuse
- **3-5× быстрее** последовательных вызовов
- Все страницы знают друг о друге (сразу максимальная связность)

### Шаг 2: SpecExtractor — Tier 1 (.docx) или Tier 2/3 (PDF)

**Сразу после Batch Author** — извлеки эталонный текст.

Для **.docx файла** — Tier 1 (основной путь, 0.2 сек):
```bash
python -m _pipeline extract docx "<путь>" --tables
→ specs-extracted/<категория>/*.txt (plain для grep)
→ specs-extracted/<категория>/*.md (ТАБЛИЦЫ — ключевой resource для Reviewer!)
```

Для **.pdf файла** — Tier 2/3:
```
Agent: SpecExtractor — извлеки <путь-к-PDF>
```

⚠️ **extract_docx.py — всегда первый метод для .docx**. Таблицы — ключевой resource, Reviewer не может проверить структуры EF без них.

### Шаг 3: Linker — внешние связи

Добавь кросс-ссылки на другие кластеры знаний (внутри-пакетные связи уже созданы Batch Author'ом).

### Шаг 4: Индексы + Roadmap + /lint

Обнови `wiki/index.md`, раздельные индексы, `Roadmap.md`. Выполни `/lint`.

---

**Время**: 1 вызов Author вместо 3-8 → спецификация обрабатывается за ~2-3 мин (было 5-8 мин).
