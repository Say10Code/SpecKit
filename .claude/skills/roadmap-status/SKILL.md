# Skill: roadmap-status
# Trigger: /roadmap

Проверка и обновление Roadmap.md с метриками качества.

## Workflow

1. Прочитай текущий `Roadmap.md`
2. **Запусти quality_metrics.py** для сбора метрик качества:
   ```bash
   python "D:\ObsidianDB\_tech\scripts\quality_metrics.py"
   ```
   Скрипт сохраняет замер в историю и создаёт отчёт: `_tech/reports/quality-metrics-YYYY-MM-DD.md`

3. Проверь актуальность статистики:
   - Количество страниц в каждом разделе `wiki/`
   - Статус reviewed/draft в frontmatter
   - Quality Score (из отчёта — 0-100)
4. Проверь согласованность:
   - Все ли страницы из `wiki/` упомянуты в мастер-списке?
   - Нет ли в мастер-списке удалённых страниц?
5. **Покажи Quality Score и ключевые дельты** из отчёта:
   - Score: A (90+) / B (75-89) / C (60-74) / D (<60)
   - Δ pages, Δ orphans, Δ coverage с прошлого замера
6. Обнови дату последнего обновления в Roadmap.md
7. Предложи приоритеты на основе текущего состояния

⚠️ Не изменяй Roadmap.md без подтверждения пользователем.

## Ключевые метрики (из quality_metrics.py)

| Метрика | Цель | Что значит при отклонении |
|---|---|---|
| Quality Score | ≥90 (A) | Падение → проверить orphans/errors |
| Orphans | 0 | >0 → запустить Linker |
| Reviewed % | ≥95% | <95% → запустить Reviewer |
| Spec coverage | ≥100% | <100% → запустить SpecExtractor |
| Frontmatter errors | 0 | >0 → запустить check_frontmatter.py |
| Weak pages (<3 in) | ≤10 | >10 → запустить Linker |
