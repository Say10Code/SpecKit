# Оркестрация агентов — граф-анализ (v2, после speckit-миграции)

> **Создан**: 2026-06-14 · **Метод**: graphify 7,642 узла + 5-ракурсный анализ
> **Предыдущий**: `agent-orchestration-map.md` (ручной анализ)

---

## 1. Сводка: что изменилось после миграции

| Метрика | До миграции | После | Δ |
|---|---|---|---|
| Speckit↔Agent EXTRACTED рёбер | **0** (все INFERRED) | **22** | 🔴→🟢 |
| 3gpp-crawler узлов | 1,026 | **0** (pruned) | -1,026 |
| Speckit-узлов | 78 | **126** | +48 |
| Agent orchestration edges | 0 EXTRACTED | **215** (включая pipeline) | Полная цепочка |

---

## 2. Полная карта вызовов (из графа, EXTRACTED)

### 2.1 Триггеры: Skills → Agents

```
/ingest       ──triggers──> SpecExtractor v3
/ingest       ──triggers──> Author v2 (Batch mode)
/ingest       ──triggers──> Linker
/spec-download ◄──triggers── SpecDownloader
/spec-download ◄──triggers── SpecExtractor
/spec-download ◄──triggers── Librarian
/spec-download ◄──triggers── Author v2
/spec-download ◄──triggers── Linker
/review       ◄──triggers── Reviewer v3
/research     ◄──triggers── Researcher
/lint         ──triggers──> PostToolUse Hook
```

### 2.2 Вызовы: Agents → Agents/Tools

```
SpecDownloader ──calls──> _pipeline metadata fetch
SpecDownloader ──calls──> _pipeline download
SpecDownloader ──calls──> Librarian
Librarian      ──calls──> Author v2
Librarian      ──calls──> Linker
Author v2      ──calls──> Librarian         ← обратная связь
Author v2      ──calls──> Researcher
Author v2      ──calls──> wiki/             ← запись знаний
Author v2      ──calls──> /lint
SpecExtractor  ──calls──> _pipeline metadata fetch
SpecExtractor  ──calls──> _pipeline extract docx/docling/pypdf2
SpecExtractor  ──calls──> Librarian
Linker         ──calls──> /lint
Linker         ──conceptually_related_to──> Reviewer v3  [INFERRED — слабая связь]
```

---

## 3. Ролевая карта агентов

### Hub (degree=8): Author v2
```
IN:  6 рёбер (Librarian, /ingest, standards: frontmatter, provenance, page-types, wikilinks, mermaid, callouts)
OUT: 2 рёбра (Librarian ← обратная связь, ingest skill)
```
**Нагрузка**: 6 стандартов имплементируются через Author. Все знания проходят через него.

### Coordinator (degree=5): Librarian
```
IN:  3 рёбра (SpecDownloader, SpecExtractor, Author)
OUT: 2 рёбра (Author, Linker)
```
**Роль**: диспетчер. Принимает от SpecDownloader и SpecExtractor, передаёт Author и Linker.

### Specialist (degree=4): Reviewer v3
```
IN:  1 ребро (Linker, INFERRED)
OUT: 3 ребра (Linker, Truth Hierarchy, /review skill)
```
**Роль**: изолированный валидатор. Слабо связан с остальной оркестрацией.

### Worker (degree=2-3): SpecDownloader, SpecExtractor, Linker, Researcher, Formatter
```
IN:  1 ребро (от skill)
OUT: 1-2 ребра (к pipeline, Librarian, или инструментам)
```
**Роль**: узкоспециализированные исполнители.

---

## 4. Золотой путь — доказательство в графе

Граф подтверждает полную цепочку `/spec-download`:

```
/spec-download SKILL
  └─triggers─> SpecDownloader AGENT
                 ├─calls─> _pipeline metadata fetch   (WhatTheSpec API → .speckit/)
                 └─calls─> _pipeline download          (3GPP FTP → !INCOMING/)
                              │
                 ┌─calls─> Librarian AGENT ◄──────────┘
                 │           ├─calls─> Author v2 AGENT  (создаёт wiki/ страницы)
                 │           │           ├─calls─> /lint
                 │           │           └─calls─> Researcher (для synthesis)
                 │           └─calls─> Linker AGENT     (кросс-ссылки)
                 │                       └─calls─> /lint
                 │
                 └─calls─> SpecExtractor AGENT (через /ingest)
                             ├─calls─> _pipeline extract docx   (Tier 1, 0.2s)
                             ├─calls─> _pipeline extract docling (Tier 2, GPU)
                             └─calls─> _pipeline extract pypdf2 (Tier 3)
```

Все 8 агентов + 5 CLI-команд _pipeline связаны в графе EXTRACTED рёбрами.

---

## 5. Найденные дефекты оркестрации

### 🔴 DEFECT 1: SpecExtractor → Linker (MISSING)

**Проблема**: После извлечения эталонных текстов в `specs-extracted/`, Linker не вызывается. SpecExtractor и Linker не связаны напрямую.

**Путь обхода**: SpecExtractor → /ingest → Linker (2 hop, через skill)

**Почему это проблема**: Автоматическая цепочка рвётся. Linker запускается только Librarian'ом (после flatten), но не после extraction. Если SpecExtractor вызывается отдельно (вне /ingest), Linker не узнает.

**Исправление**: Добавить SpecExtractor → Linker вызов (EXTRACTED ребро) в specextractor.md.

### 🟡 DEFECT 2: SpecDownloader → SpecExtractor (MISSING)

**Проблема**: После скачивания спецификации, SpecExtractor не вызывается автоматически. Вызов идёт через Librarian (SpecDownloader → Librarian → SpecExtractor).

**Почему это проблема**: Дополнительный hop добавляет задержку. Если Librarian занят, extraction ждёт.

**Степень**: Низкая. Librarian всё равно нужен для flatten.

### 🟡 DEFECT 3: Reviewer → Author (MISSING)

**Проблема**: Reviewer находит ошибки в wiki-страницах, но не вызывает Author для исправления. Исправления вносятся вручную.

**Почему это НЕ баг**: Reviewer — человеческий валидатор. Авто-исправление CRITICAL ошибок через Author опасно (Author может внести новые ошибки).

**Рекомендация**: Добавить INFERRED ребро Reviewer → Author как «предложить исправление», не «авто-исправить».

### 🟢 DEFECT 4: Researcher → Linker (MISSING)

**Проблема**: Исследовательские страницы создаются без автоматического линкования.

**Исправление**: Добавить Researcher → Linker в researcher.md.

---

## 6. Потоки данных (подтверждено графом)

```
!INCOMING/        9 узлов — входная точка
    ↓
Specifications/   7 узлов — отсортированные исходники
    ↓
┌───────────────────┬───────────────────┐
↓                   ↓                   ↓
wiki/              specs-extracted/    .speckit/
10 узлов           15 узлов            1 узел
(база знаний)      (эталоны)           (метаданные)
    ↓                   ↓
Reviewer ←──────────────┘
(читает оба источника для Pass 1)
```

---

## 7. Узкие места (граф-верификация)

| # | Узкое место | Граф-подтверждение | Степень |
|---|---|---|---|
| **B1** | Author — single point of failure | degree=8, 6 стандартов → 1 агент. Все wiki-страницы через него | 🟡 Средняя |
| **B2** | /lint — избыточные вызовы | 5 агентов → /lint (Author, Linker, Librarian, SpecExtractor, SpecDownloader) | 🟡 Средняя |
| **B3** | Reviewer — изоляция | degree=4, только 1 входящее INFERRED ребро (от Linker) | 🟢 Осознанно |
| **B4** | SpecExtractor→Linker разрыв | 2 hop через /ingest, нет прямого ребра | 🟡 Средняя |

---

## 8. Рекомендации

| # | Действие | Файл | Приоритет |
|---|---|---|---|
| R1 | Добавить SpecExtractor → Linker вызов | `specextractor.md` | 🟡 P2 |
| R2 | Добавить Researcher → Linker вызов | `researcher.md` | 🟢 P3 |
| R3 | Объединить /lint в конце цепочки | Все агенты | 🟡 P2 |
| R4 | Добавить Reviewer → Author (INFERRED, предложение) | `reviewer.md` | 🟢 P3 |
| R5 | Документировать цепочку в CLAUDE.md | `CLAUDE.md` | 🟡 P2 |

---

*Анализ создан 2026-06-14. Источник: graphify 7,642 узла, 19,792 ребра, 396 сообществ.*
