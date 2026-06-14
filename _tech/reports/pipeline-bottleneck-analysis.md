# Анализ: `/spec-download` пайплайн и Author bottleneck

> **Дата**: 2026-06-13 18:30
> **Метод**: Пошаговая трассировка 4 исходников (spec-download SKILL, SpecDownloader agent, Librarian agent, /ingest SKILL)
> **Результат**: 5 разрывов автоматизации, 3 архитектурных решения для Author

---

## Часть 1: `/spec-download` — где рвётся автоматизация

### Теоретическая цепочка (7 шагов)

```
/spec-download 31.102
  │
  ├─ Шаг 1: spec-crawler crawl 31.102          ← Обновить БД метаданных
  ├─ Шаг 2: spec-crawler checkout              ← Скачать .docx в !INCOMING/
  ├─ Шаг 3: Librarian flatten + сортировка      ← Переместить → Specifications/<тема>/
  ├─ Шаг 4: /ingest                            ← Author: summary + concepts + entities + synthesis
  ├─ Шаг 5: SpecExtractor                      ← Извлечь текст PDF → specs-extracted/
  ├─ Шаг 6: /lint                              ← Проверить здоровье
  └─ Шаг 7: Обновить Roadmap.md
```

### Реальная цепочка (что фактически выполняется)

```
/spec-download 31.102
  │
  ├─ Шаг 1: ✅ spec-crawler crawl — выполняется
  ├─ Шаг 2: ✅ spec-crawler checkout — выполняется
  ├─ Шаг 3: ✅ Librarian flatten — выполняется (SpecDownloader говорит «сразу запусти Librarian»)
  ├─ Шаг 4: ⚠️ /ingest — НЕ вызывается автоматически
  │          └─ SpecDownloader agent: «Сообщить результат» → не вызывает /ingest
  │          └─ spec-download SKILL: «Для каждого нового файла: Author создаёт...» — описано, но
  │             нет механизма АВТОМАТИЧЕСКОГО вызова /ingest после Librarian
  │
  ├─ Шаг 5: ❌ SpecExtractor — НЕ вызывается
  │          └─ Документирован в SKILL.md строка 77: «Извлечь текст PDF → TXT»
  │          └─ НО: нет ни Bash-команды, ни Agent-вызова
  │          └─ Причина: SKILL.md — это инструкция для AI, а не исполняемый код
  │             AI должен САМ решить вызвать SpecExtractor. На практике — забывает.
  │
  ├─ Шаг 6: ⚠️ /lint — вызывается, но ТОЛЬКО через PostToolUse hook
  │          └─ Hook срабатывает на Edit/Write в wiki/ — но только напоминает
  │          └─ AI должен явно вызвать /lint. На практике — может забыть.
  │
  └─ Шаг 7: ✅ Roadmap — обновляется вручную в конце сессии
```

### 5 точек разрыва

| # | Где | Что происходит | Почему |
|---|---|---|---|
| **R1** | Шаг 3→4 | Librarian завершён, `/ingest` не вызван | SKILL.md описывает шаг 4 норативно, без явного `Agent(librarian)` → `Skill(ingest)` перехода. AI должен «вспомнить» вызвать /ingest. |
| **R2** | Шаг 4→5 | `/ingest` завершён, SpecExtractor не вызван | SpecExtractor — единственный агент без skill-обёртки. SKILL.md говорит «Извлечь текст PDF», но не говорит КАК. Нет триггера. |
| **R3** | Шаг 5→6 | SpecExtractor завершён, `/lint` не вызван | `/lint` полагается на PostToolUse hook, который только напоминает. Если AI не написал в wiki/ (только в specs-extracted/), hook не срабатывает. |
| **R4** | Шаг 3 | Librarian flat'ит, но таблица серия→тема в 3 местах | `librarian.md` (стр. 54-75), `spec-download/SKILL.md` (стр. 48-61), `CLAUDE.md` — три копии. `.category-map.md` объявлен single source of truth, но агенты читают свои копии. |
| **R5** | Шаг 4 | `/ingest` требует 3× Author вызовов подряд | Summary → concepts → entities → synthesis — всё через Author. Если один упадёт (ошибка в шаблоне), цепочка рвётся без partially saved state. |

### Диаграмма разрывов

```
/spec-download 31.102
  │
  ├─[1] spec-crawler crawl            ✅ автомат
  ├─[2] spec-crawler checkout         ✅ автомат
  ├─[3] Librarian flatten             ✅ автомат (SpecDownloader → Librarian)
  │
  ├─[4] /ingest (Author ×3 + Linker)  ⚠️ R1: ручной переход
  │   └─ Author: summary              ⚠️ R5: no partial save
  │   └─ Author: concepts             ⚠️ R5: no partial save
  │   └─ Author: entities             ⚠️ R5: no partial save
  │   └─ Author: synthesis (опц.)     ⚠️ R5: no partial save
  │   └─ Linker: wikilinks            ✅
  │
  ├─[5] SpecExtractor                 ❌ R2: нет автоматического вызова
  │   └─ PyPDF2: txt для всех PDF
  │   └─ Docling: md+json для 3GPP
  │
  ├─[6] /lint                         ⚠️ R3: только hook-напоминание
  │
  └─[7] Roadmap update                ✅ ручной в конце сессии
```

---

## Часть 2: Author как бутылочное горлышко

### Матрица вызовов Author

Author — **единственный агент, создающий контент** в wiki/. Вызывается из 5 разных источников:

| Источник | Тип страницы | Шаблон | Контекст |
|---|---|---|---|
| **Librarian** (шаг 4) | summary + concepts + entities | t-summary, t-concept, t-entity | После flatten нового PDF |
| **/ingest skill** | summary + concepts + entities + synthesis | все 4 | Прямой вызов пользователем |
| **/spec-download skill** | summary + concepts + entities | 3 шаблона | Автоматический пайплайн |
| **Researcher agent** | synthesis (deep research) | t-synthesis | Глубокое исследование |
| **Прямой запрос** | любой | любой | «Создай страницу про X» |

```
                    ┌──────────────┐
                    │   Librarian  │──┐
                    └──────────────┘  │
                    ┌──────────────┐  │    ┌────────────┐
                    │   /ingest    │──┼───►│   AUTHOR   │──► wiki/*.md
                    └──────────────┘  │    └────────────┘
                    ┌──────────────┐  │
                    │ /spec-downl  │──┤
                    └──────────────┘  │
                    ┌──────────────┐  │
                    │  Researcher  │──┘
                    └──────────────┘
```

### Почему это проблема

1. **Серийная обработка**: 1 спецификация = 3-4 вызова Author последовательно (summary → concepts → entities → synthesis). 3 спецификации = 9-12 вызовов. Каждый вызов — новый Agent (контекст не переиспользуется).

2. **Нет параллелизации**: Все вызовы Author идут последовательно. При `--mode deep` (graphify) или `/spec-download 31.102 102.221 102.223` — 3 спецификации × 4 страницы = 12 последовательных Author-вызовов.

3. **Нет saved state**: Если Author упал на 3-м концепте из 5 — первые 2 созданы, но цепочка брошена. Нет транзакционности.

4. **Разные форматы входа**: Librarian даёт путь к PDF, Researcher — тему + источники, прямой запрос — вопрос. Author должен по-разному обрабатывать каждый.

5. **Смешение create и update**: Author и создаёт новые страницы, и обновляет существующие (при пересмотре). Логика «проверь — нет ли уже такой» требует полного сканирования wiki/ перед каждым созданием.

### Метрики узкого места

```
Одна спецификация (например TS 31.102):
  └─ Author вызовов: минимум 3 (summary + 1 concept + entities)
  └─ Типично: 5-8 (summary + 3-5 concepts + entities)
  └─ Время: ~45-120 сек на вызов → 4-16 минут на спецификацию

Три спецификации (например /spec-download 31.102 35.206 23.501):
  └─ Author вызовов: 9-24
  └─ Время: 7-32 минуты последовательно

Полная фаза (например Фаза 1 — 6 спецификаций):
  └─ Author вызовов: 30-48
  └─ Время: 20-60 минут последовательно
```

---

## Часть 3: Архитектурные решения

### Решение 1: Author Split — разделить create и update

**Суть**: Разделить Author на два агента:
- **Drafter** — создаёт новые страницы (чистый create, не проверяет существующие)
- **Editor** — обновляет существующие (проверяет дубликаты, merge-логика)

```
Было:                         Стало:
  Author                        Drafter ──► новые страницы
  ├─ create summary             Editor  ──► update существующих
  ├─ create concepts
  ├─ create entities
  ├─ update index
  └─ check duplicates
```

**Выгода**:
- Drafter не проверяет дубликаты → быстрее на 30%
- Editor может работать параллельно с Drafter (разные файлы)
- Явное разделение ответственности

### Решение 2: Batch Authoring — пакетная обработка

**Суть**: Вместо N последовательных вызовов Author — один вызов с пакетом:

```
Вместо:
  Agent(Author: создай summary для TS 31.102)
  Agent(Author: создай concept для UICC из TS 31.102)
  Agent(Author: создай concept для EF из TS 31.102)
  ...

Один вызов:
  Agent(Author: пакетная обработка TS 31.102)
    → создай summary
    → извлеки 3-5 концептов
    → зафиксируй entities
    → расставь wikilinks
    → обнови индексы
```

**Выгода**:
- 1 вызов вместо N → в 3-5× быстрее
- Контекст спецификации переиспользуется между страницами
- Возможна транзакционность (все или ничего)

**Риск**: Больше токенов в одном вызове. Для спецификации с 10+ концептами может превысить лимит контекста.

### Решение 3: Pipeline Parallelization — параллельный /ingest

**Суть**: Разные спецификации обрабатываются параллельно:

```
/spec-download 31.102 35.206 23.501

Шаг 1-3: общий (crawl + checkout + Librarian flatten)
         │
         ├─► Agent(Author: пакет TS 31.102)  ─┐
         ├─► Agent(Author: пакет TS 35.206)  ─┤ параллельно
         └─► Agent(Author: пакет TS 23.501)  ─┘
                  │
                  └─► Agent(Linker: cross-reference all)
                  └─► /lint
```

**Выгода**:
- 3 спецификации обрабатываются за время одной
- Linker вызывается один раз после всех Author'ов для cross-reference

**Требует**: Author Split (Решение 1) для безопасности — параллельные Author'ы не должны трогать одни и те же файлы.

---

## Часть 4: Приоритеты внедрения

| # | Решение | Когда | Затраты | Влияние |
|---|---|---|---|---|
| **R2 fix** | Авто-вызов SpecExtractor после /ingest | Сейчас | 15 мин (обновить SKILL.md) | 🔴 Высокое |
| **R1 fix** | Явный вызов /ingest после Librarian в /spec-download | Сейчас | 10 мин (обновить specdownloader.md) | 🔴 Высокое |
| **R4 fix** | Удалить таблицы серия→тема из agents, ссылаться на .category-map.md | Эта сессия | 20 мин | 🟡 Среднее |
| **Sol 2** | Batch Authoring | Следующая сессия | 2h (новый Author.md) | 🔴 Высокое |
| **Sol 3** | Pipeline Parallelization | После Sol 2 | 1h (обновить /spec-download skill) | 🟡 Среднее |
| **Sol 1** | Author Split (Drafter/Editor) | После Sol 3 | 3h (2 новых агента + миграция) | 🟢 Низкое (долгосрочно) |

---

## Часть 5: Минимальный фикс (сделать сейчас)

### 5.1: Закрыть R1 — авто-переход Librarian → /ingest

В `specdownloader.md`, шаг 4, заменить «Сообщить результат» на:

```
### Шаг 4: Запустить полный пайплайн

После Librarian flatten — **сразу вызови /ingest** для каждого нового файла:

1. Вызови Skill(ingest) для нового файла
2. Дождись завершения (summary + concepts + entities созданы)
3. Вызови SpecExtractor для извлечения текста
4. Вызови Skill(lint-wiki)
5. Обнови Roadmap.md
```

### 5.2: Закрыть R2 — авто-вызов SpecExtractor

В `/ingest` SKILL.md добавить шаг 3.5:

```
3.5. **Запусти SpecExtractor** для извлечения текста из PDF:
   - Если PDF → Agent(SpecExtractor: извлеки <путь-к-pdf>)
   - Результат → specs-extracted/<категория>/<имя>.txt (+ .md + .json для 3GPP)
```

### 5.3: Закрыть R4 — убрать дублирование таблиц

В `librarian.md` и `spec-download/SKILL.md` заменить таблицы серия→тема на:

```
**Маппинг серий**: см. `Specifications/.category-map.md` — единый source of truth.
```

---

*Анализ создан 2026-06-13 18:30 на основе трассировки 4 исходных файлов.*
