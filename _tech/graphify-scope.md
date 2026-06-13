# /graphify Scope — Файлы для анализа

> **Дата**: 2026-06-13 03:00
> **Цель**: Определить минимальный набор файлов для глубокого граф-анализа проекта

---

## Категории файлов (31 файл)

### 📋 Главные управляющие
1. `CLAUDE.md` — Главный диспетчер AI-агентов (240 строк)
2. `.claude/CLAUDE.md` — Локальный контекст
3. `Roadmap.md` — Дорожная карта + мастер-список

### 🤖 Агенты (8)
4. `.claude/agents/author.md`
5. `.claude/agents/reviewer.md`
6. `.claude/agents/linker.md`
7. `.claude/agents/librarian.md`
8. `.claude/agents/researcher.md`
9. `.claude/agents/formatter.md`
10. `.claude/agents/specextractor.md`
11. `.claude/agents/specdownloader.md`

### 🔧 Skills (6)
12. `.claude/skills/lint-wiki/SKILL.md`
13. `.claude/skills/ingest/SKILL.md`
14. `.claude/skills/review/SKILL.md`
15. `.claude/skills/format-html/SKILL.md`
16. `.claude/skills/roadmap-status/SKILL.md`
17. `.claude/skills/spec-download/SKILL.md`

### 🧩 Шаблоны (6)
18. `.obsidian/templates/t-concept.md`
19. `.obsidian/templates/t-entity.md`
20. `.obsidian/templates/t-summary.md`
21. `.obsidian/templates/t-synthesis.md`
22. `.obsidian/templates/t-reference.md`
23. `.obsidian/templates/t-note.md`

### 📐 Техническая документация
24. `_tech/README.md` — Правила и структура
25. `_tech/architecture/ARCHITECTURE-v2.md` — Архитектурный анализ
26. `_tech/BACKLOG.md` — Активные задачи
27. `_tech/plans/IMPROVEMENT_PLAN.md` — План улучшений

### 📄 Индексы и конфигурация
28. `wiki/index.md` — Хаб знаний (129 страниц)
29. `specs-extracted/INDEX.md` — Карта эталонных текстов
30. `.gitignore` — Правила исключений
31. `3gpp-crawler.toml` — Конфиг spec-crawler

---

## Ключевые вопросы для graphify-анализа

1. **Карта связности**: как агенты вызывают друг друга через skills?
2. **Узкие места**: где один агент блокирует пайплайн?
3. **Дублирование**: пересекающиеся зоны ответственности агентов
4. **Пробелы**: функции без назначенного агента
5. **Пути данных**: полные цепочки от PDF до wiki-страницы
6. **Нарушения read-only**: где агенты могут записать в защищённые директории?
7. **Неиспользуемые компоненты**: агенты/skills без триггеров

---

*Файлы готовы к `/graphify`.*
