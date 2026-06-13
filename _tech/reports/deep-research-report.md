# Глубокий ресерч ObsidianDB — узкие места, проблемы, план улучшения

> **Дата**: 2026-06-13 03:30
> **Метод**: Полный анализ 43 архитектурных файлов (8 агентов, 6 skills, шаблоны, планы, конфигурация)
> **Результат**: 23 находки, 14 проблем, план из 10 улучшений

---

## 1. Методология

Проведён сквозной анализ всех компонентов архитектуры:

| Слой | Файлов | Что анализировалось |
|---|---|---|
| Главный контекст | 2 | `CLAUDE.md`, `.claude/CLAUDE.md` |
| Агенты | 8 | `author.md`, `reviewer.md`, `linker.md`, `librarian.md`, `researcher.md`, `formatter.md`, `specextractor.md`, `specdownloader.md` |
| Skills | 6 | `lint-wiki`, `ingest`, `review`, `format-html`, `roadmap-status`, `spec-download` |
| Шаблоны | 6 | `t-concept`, `t-entity`, `t-summary`, `t-synthesis`, `t-reference`, `t-note` |
| Тех. документация | 15 | `ARCHITECTURE-v2.md`, `BACKLOG.md`, планы, отчёты |
| Индексы/конфиги | 6 | `Roadmap.md`, `wiki/index.md`, `specs-extracted/INDEX.md`, `.gitignore`, `3gpp-crawler.toml` |

---

## 2. Карта связей агентов и skills

```
                    ┌──────────────────────────┐
                    │      CLAUDE.md            │
                    │   (главный диспетчер)     │
                    └────────────┬─────────────┘
                                 │
     ┌───────────────┬───────────┼───────────────┬───────────────┐
     │               │           │               │               │
     ▼               ▼           ▼               ▼               ▼
┌─────────┐   ┌──────────┐ ┌─────────┐   ┌──────────┐   ┌───────────┐
│/ingest  │   │/review   │ │/lint    │   │/format-  │   │/spec-     │
│ skill   │   │ skill    │ │skill    │   │html skill│   │download   │
└────┬────┘   └────┬─────┘ └────┬────┘   └────┬─────┘   └─────┬─────┘
     │             │            │             │               │
     ▼             ▼            ▼             ▼               ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│Author   │ │Reviewer  │ │Grep/Glob │ │Formatter │ │SpecDownloader│
│Linker   │ │Linker    │ │Read tools│ │(agent)   │ │Librarian     │
│Librarian│ │(specs)   │ └──────────┘ └──────────┘ │Author/Linker │
└─────────┘ └──────────┘                            └──────────────┘
     ▲
     │ (вызывается всеми)
┌─────────┐
│ Author  │ ← УЗКОЕ МЕСТО #1
└─────────┘
```

---

## 3. Находки (23)

### 3.1 Структурные находки (8)

**F1 — Author как бутылочное горлышко**
Author вызывается из 4 разных skills (`/ingest`, `/review`, `/spec-download`, прямой запрос). Это единственный агент, создающий контент. При масштабировании — узкое место.

**F2 — Librarian — двойная ответственность**
Librarian одновременно каталогизирует (сортировка файлов) И управляет пайплайном (запускает Author для summary/concepts/entities). Две разные зоны ответственности в одном агенте.

**F3 — Reviewer зависит от SpecExtractor, но не наоборот**
Reviewer требует TXT/MD/JSON в `specs-extracted/`. Если SpecExtractor не запущен — Reviewer не может проверить новые страницы. Нет автоматического триггера.

**F4 — Linker вызывается реактивно, не проактивно**
Linker запускается ТОЛЬКО когда `/lint` находит сирот или `/ingest` доходит до шага 6. Нет периодического аудита связности.

**F5 — `/spec-download` — неполный пайплайн**
Skill документирует 7 шагов, но шаг 5 (SpecExtractor) и шаг 6 (/lint) не вызываются автоматически — они описаны как «должен вызвать пользователь».

**F6 — Researcher не интегрирован в skills**
Researcher — единственный агент без skill-обёртки. Вызывается только прямым запросом. Нет `/research` skill.

**F7 — Дублирование логики сортировки**
Таблица «серия → тема» дублируется в трёх местах: `librarian.md`, `spec-download/SKILL.md`, `CLAUDE.md`. Изменение в одном месте не отражается в других.

**F8 — Шаблоны не валидируются**
6 шаблонов `.obsidian/templates/` описывают структуру, но нет проверки что созданные страницы им соответствуют. `check_frontmatter.py` упомянут в Roadmap с июня, не реализован.

### 3.2 Технические находки (8)

**F9 — `specs-extracted/` — две параллельные структуры**
```
specs-extracted/
├── ETSI_3GPP/USIM/ts_131102v171000p.pdf.txt    ← PyPDF2 (старая структура)
├── 3GPP/31.102/19.4/31102-j40.md               ← Docling (новая структура)
```
Reviewer должен знать про обе. INDEX.md не отражает новую.

**F10 — `generate_picture_images=False` отключён в `pipeline.py`, но включён в `workspace process` по умолчанию**
При вызове `3gpp-crawler workspace process` без флагов — `generate_picture_images=True` (дефолт Docling), что вызовет bad_alloc на старых версиях.

**F11 — Путь к soffice.exe не сконфигурирован**
3gpp-crawler ищет LibreOffice в `PATH`, но на Windows `soffice.exe` в `C:\Program Files\LibreOffice\program\`. Может не найтись при вызове из разных окружений.

**F12 — CWD-зависимость spec-crawler**
Config discovery 3gpp-crawler зависит от CWD. Если агент запущен из другого пути — конфиг не найдётся, кэш уйдёт в `~/.3gpp-crawler/`.

**F13 — `uv tool install` требует ручного обновления**
При изменении `pipeline.py` или `page_preprocessing_model.py` нужно вручную переустанавливать глобальный инструмент. Легко забыть.

**F14 — Нет graceful degradation при отсутствии GPU**
Если `torch.cuda.is_available()` = False, Docling молча падает на CPU без предупреждения. Пользователь не знает что GPU не используется.

**F15 — `Спецификации/` дубликат**
Старая папка `D:\ObsidianDB\Спецификации\` всё ещё существует (Obsidian блокирует удаление). Занимает ~53 MB. Может вызвать путаницу.

**F16 — Mermaid-диаграммы в `_tech/diagrams/` не обновлены**
Диаграммы показывают 7 агентов (без SpecDownloader) и старую структуру без Docling.

### 3.3 Процессные находки (7)

**F17 — Нет автоматического `/lint` после изменений**
CLAUDE.md говорит «После каждого изменения выполняй /lint», но это relies на человеческую память. Нет pre-commit hook.

**F18 — Нет инкрементального Review**
Review запускается для конкретной страницы. Если изменилась спецификация (новая версия PDF), все связанные wiki-страницы должны быть перепроверены — но это не автоматизировано.

**F19 — BACKLOG.md и Roadmap.md пересекаются**
Оба файла содержат списки задач. BACKLOG — детальный беклог, Roadmap — высокоуровневая дорожная карта. Но часть информации дублируется.

**F20 — Нет метрик здоровья проекта**
100% reviewed и 0 битых ссылок — это бинарные метрики. Нет трендов: link density, orphan rate, review coverage over time, среднее время от PDF до reviewed.

**F21 — `_tech/` правила не зафиксированы в CLAUDE.md**
`README.md` описывает правила работы с `_tech/`, но главный `CLAUDE.md` не ссылается на них. Агенты не знают о существовании `_tech/`.

**F22 — Wiki-страницы не имеют machine-readable связей со спецификациями**
`sources` в frontmatter — это wikilinks, не машинные идентификаторы. Нельзя автоматически определить «какие wiki-страницы затронуты при обновлении TS 31.102».

**F23 — Нет стратегии отката**
Без git нет возможности откатить ошибочное изменение. При 129 страницах и 8 агентах вероятность ошибки растёт.

---

## 4. Матрица проблем (14)

| # | Проблема | Серьёзность | Затрагивает | Находка |
|---|---|---|---|---|
| **P1** | Author — единая точка отказа | 🔴 CRITICAL | 4 skills | F1 |
| **P2** | Нет git/отката | 🔴 CRITICAL | ВСЁ | F23 |
| **P3** | `/lint` не автоматический | 🟡 HIGH | Все изменения | F17 |
| **P4** | `specs-extracted/` двойная структура | 🟡 HIGH | Reviewer | F9 |
| **P5** | CWD-зависимость spec-crawler | 🟡 HIGH | SpecDownloader | F12 |
| **P6** | `generate_picture_images` дефолт | 🟡 HIGH | Docling | F10 |
| **P7** | `Спецификации/` дубликат (53 MB) | 🟡 HIGH | Диск | F15 |
| **P8** | Дублирование логики сортировки | 🟢 MEDIUM | 3 файла | F7 |
| **P9** | Researcher без skill-обёртки | 🟢 MEDIUM | Researcher | F6 |
| **P10** | `/spec-download` неполный пайплайн | 🟢 MEDIUM | SpecDownloader | F5 |
| **P11** | Шаблоны не валидируются | 🟢 MEDIUM | Author | F8 |
| **P12** | Диаграммы устарели | 🟢 MEDIUM | Документация | F16 |
| **P13** | Нет graceful degradation GPU | 🔵 LOW | Docling | F14 |
| **P14** | Wiki-страницы без machine-readable связей | 🔵 LOW | Reviewer | F22 |

---

## 5. План улучшения: 10 шагов

### 🔴 Фаза 1: Критические исправления (P1-P3)

#### U1 — Git-инициализация
**Проблема**: P2 — нет истории, нет отката.
**Решение**:
```bash
cd D:\ObsidianDB
git init
git add -A  # кроме .gitignore исключений
git commit -m "Initial commit: ObsidianDB — 8 agents, 129 wiki pages, Docling integration"
```
**Файлы**: `.gitignore` (уже готов)
**Валидация**: `git log` показывает коммит
**Время**: 2 мин

#### U2 — Auto-lint hook
**Проблема**: P3 — `/lint` запускается вручную.
**Решение**: Добавить в `.claude/settings.local.json` хук `after_edit`:
```json
{
  "hooks": {
    "after_edit": {
      "wiki/**/*.md": "/lint"
    }
  }
}
```
**Валидация**: После Edit в wiki/ → автоматический `/lint`
**Время**: 5 мин

#### U3 — Удалить `Спецификации/` дубликат
**Проблема**: P7 — 53 MB мусора, путаница.
**Решение**: Закрыть Obsidian → `Remove-Item "D:\ObsidianDB\Спецификации" -Recurse -Force`
**Валидация**: `Test-Path "D:\ObsidianDB\Спецификации"` → `False`
**Время**: 1 мин (после закрытия Obsidian)

### 🟡 Фаза 2: Структурные исправления (P4-P6)

#### U4 — Обновить `specs-extracted/INDEX.md`
**Проблема**: P4 — не отражает 3GPP/ETSI структуру.
**Решение**: Добавить колонку `Format` (TXT/MD/JSON), секции `## 3GPP/` и `## ETSI/` с таблицами доступных форматов.
**Шаблон**:
```markdown
## 3GPP/31.102 (USIM)
| Release | Format | Path | Size | Method |
|---|---|---|---|---|
| 17.10.0 | TXT | ETSI_3GPP/USIM/ts_131102v171000p.pdf.txt | 852 KB | PyPDF2 |
| 18.9.0 | MD+JSON | 3GPP/31.102/18.9/ | 2531 KB | Docling GPU |
| 19.4.0 | MD+JSON | 3GPP/31.102/19.4/ | 2657 KB | Docling CPU |
```
**Время**: 15 мин

#### U5 — Починить `generate_picture_images` дефолт
**Проблема**: P6 — дефолтное значение вызывает bad_alloc.
**Решение**: В `pipeline.py` всегда `generate_picture_images = False` для `DEFAULT` профиля. В `converter.py` передавать этот параметр явно.
**Файл**: `3gpp-crawler/src/tdoc_crawler/extraction/docling/pipeline.py` (уже частично)
**Валидация**: `workspace process` без флагов → не падает
**Время**: 5 мин

#### U6 — Зафиксировать CWD в агенте
**Проблема**: P5 — spec-crawler требует CWD.
**Решение**: В `specdownloader.md` уже есть «ВСЕГДА cd D:\ObsidianDB». Добавить `$env:TDC_CACHE_DIR = "D:\ObsidianDB\.3gpp-crawler"` как дополнительную страховку.
**Время**: 2 мин

### 🟢 Фаза 3: Качество и автоматизация (P8-P12)

#### U7 — Выделить «серия→тема» в единый source of truth
**Проблема**: P8 — дублирование в 3 файлах.
**Решение**: Создать `Specifications/.category-map.md` — единственный файл с таблицей маппинга. Все агенты ссылаются на него.
**Файл**: новый `Specifications/.category-map.md`
**Время**: 5 мин

#### U8 — Создать `/research` skill
**Проблема**: P9 — Researcher без skill-обёртки.
**Решение**: Создать `.claude/skills/research/SKILL.md` — skill-обёртка для Researcher. Интегрировать в CLAUDE.md.
**Время**: 10 мин

#### U9 — Валидатор frontmatter
**Проблема**: P11 — нет проверки шаблонов.
**Решение**: `_tech/scripts/check_frontmatter.py`:
- Проверяет `tags`, `type`, `status`, `created`, `updated`, `sources` во всех `wiki/**/*.md`
- Валидирует допустимые значения `type` и `status`
- Проверяет что `sources` wikilinks ведут к существующим файлам
**Время**: 20 мин

#### U10 — Обновить Mermaid-диаграммы
**Проблема**: P12 — диаграммы показывают 7 агентов.
**Решение**: Обновить `agent-interactions.md`, `system-layers.md`, `incoming-pipeline.md` с SpecDownloader, Docling, GPU.
**Время**: 10 мин

---

## 6. Дорожная карта

```
Неделя 1:  U1 (git) → U2 (auto-lint) → U3 (удалить дубликат)
Неделя 2:  U4 (INDEX.md) → U5 (picture_images fix) → U6 (CWD fix)
Неделя 3:  U7 (category-map) → U8 (/research skill) → U9 (frontmatter checker)
Неделя 4:  U10 (диаграммы) → обновить CLAUDE.md → финальный аудит
```

---

## 7. Итоговая оценка архитектуры

| Измерение | Оценка | Комментарий |
|---|---|---|
| **Модульность агентов** | 🟢 8/10 | Чёткие зоны ответственности, но Author — узкое место |
| **Покрытие пайплайнов** | 🟡 6/10 | INCOMING и Review покрыты, но нет CI/CD и авто-lint |
| **Качество данных** | 🟢 9/10 | 100% reviewed, provenance, гибрид TXT+MD+JSON |
| **Инструментарий** | 🟢 8/10 | PyPDF2+Docling, GPU, spec-crawler — мощный стек |
| **Документированность** | 🟡 7/10 | `_tech/` отличный, но диаграммы устарели и CLAUDE.md монолитный |
| **Надёжность** | 🔴 4/10 | Нет git, нет бэкапов, CWD-зависимость |
| **Масштабируемость** | 🟡 6/10 | Author как SPOF, но агенты независимы |
| **Общая** | 🟡 **7.3/10** | Сильный фундамент, критические пробелы в надёжности |

---

*Ресерч завершён 2026-06-13 03:30. План из 10 улучшений готов к реализации после подтверждения.*
