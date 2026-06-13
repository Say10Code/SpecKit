# ObsidianDB — План улучшения архитектуры

> **Дата**: 2026-06-13 00:45
> **Исходное состояние**: Фаза 4 → Фаза 5 (Automation)
> **Прогресс**: Docling миграция 16/42, Reviewer v3 (гибрид), 6 skills
> **Беклог**: [_tech/BACKLOG.md](_tech/BACKLOG.md)
> **Цель**: Повысить надёжность, автоматизацию и масштабируемость архитектуры

---

## 1. Оценка текущего состояния

### Что работает отлично
- Эталонная цепочка `PDF → TXT → wiki → Review` — уникальная фича
- Модульные агенты с чёткими зонами ответственности (8 шт.)
- 100% review coverage, 0 битых ссылок, 0 сирот
- Provenance-маркировка всех утверждений
- ✅ **SpecDownloader** — автоматическое скачивание 3GPP-спецификаций (внедрён!)
- ✅ **3gpp-crawler интеграция** — spec-crawler CLI установлен глобально

### Что улучшено (сессия 12-13 июня)

- ✅ **SpecDownloader** — автоматическое скачивание 3GPP-спецификаций (spec-crawler)
- ✅ **3gpp-crawler интеграция** — `3gpp-crawler.toml`, `.gitignore`, кэш `.3gpp-crawler/`
- ✅ **Skill `/spec-download`** — 6 skills total
- ✅ **Librarian v2** — два пути (!INCOMING flat + spec-crawler nested flatten)
- ✅ **LibreOffice 26.2.4.2** — `.docx→PDF` конвертация для Docling
- ✅ **Docling fix** — `PipelineOptions` → `PdfPipelineOptions` в `pipeline.py`
- ✅ **Docling миграция** — 16 спецификаций (11×3GPP + 5×ETSI) в `specs-extracted/3GPP/` и `ETSI/`
- ✅ **Reviewer v3** — гибридный Pass 1 (TXT Grep / JSON lookup / MD read)
- ✅ **SpecExtractor v2** — dual approach (PyPDF2 для всех + Docling для 3GPP/ETSI)
- ✅ **CLAUDE.md расширен** — секции 3gpp-crawler, Docling, `/spec-download`

### Что требует улучшения
- ⚠️ **Torch без CUDA** — RTX 3060 12GB простаивает. `AssertionError: Torch not compiled with CUDA enabled`
- ⚠️ **`std::bad_alloc`** — Docling `images_scale=1.5` → OOM на PDF >200 стр. (баг в PIL/pypdfium2)
- ⚠️ **Кириллические пути** — `Specifications/` ломает C++ слой pymupdf → `Input document is not valid`
- Нет version control (git)
- Монолитный CLAUDE.md (240+ строк)
- Нет автоматической валидации frontmatter
- Нет метрик качества

---

## 2. Приоритетные улучшения (актуализировано 13 июн)

### 🔴 P0 — Критические (надёжность)

#### P0.1 — Переименовать `Specifications` → `Specifications`
**Статус**: ⬜ План в `_tech/cyrillic-rename-plan.md`
**Проблема**: pymupdf/docling C++ слой не принимает кириллические пути
**Решение**:
- `Rename-Item` + поиск/замена во всех `.md`, `.py`, `.toml` (160 файлов, ~560 упоминаний)
- Obsidian авто-обновит wikilinks

#### P0.2 — PyTorch CUDA (разблокировать RTX 3060)
**Статус**: ⬜ Ждёт B1 (латиница)
**Проблема**: Torch скомпилирован без CUDA. Docling CPU-only.
**Решение**: `uv run pip install torch --index-url https://download.pytorch.org/whl/cu126 --force-reinstall`
**Ожидаемый эффект**: Docling GPU ~2-3× быстрее + без `std::bad_alloc` (VRAM 12 GB)

#### P0.3 — Git-инициализация
**Статус**: ⬜ Отложено
**Проблема**: Нет истории изменений
**Решение**: `git init`, `.gitignore` уже готов

### 🟡 P1 — Высокие (автоматизация)

#### P1.1 — Pre-commit / Post-edit hooks
**Проблема**: `/lint` запускается вручную, можно забыть
**Решение**:
- Добавить hook в `.claude/settings.json`: после каждого Edit/Write в `wiki/` → авто `/lint`
- Если lint нашёл ошибки → блокировать дальнейшие изменения до исправления

#### P1.2 — Автоматическая валидация frontmatter
**Проблема**: `check_frontmatter.py` упомянут в Roadmap но не реализован
**Решение**:
- Python-скрипт в `_tech/scripts/check_frontmatter.py`
- Проверяет: наличие всех обязательных полей, корректность дат, валидность type/status
- Запускается как часть `/lint`

#### P1.3 — CI/CD для review
**Проблема**: Review запускается точечно, нет автоматического ревью при изменениях
**Решение**:
- Триггер: изменение в `wiki/` → авто-review изменённой страницы (Reviewer agent)
- Приоритезация: страницы с `status: draft` или `^[todo]` → автоматически в очередь

### 🟢 P2 — Средние (качество)

#### P2.1 — Метрики качества графа
**Проблема**: Только бинарная проверка (есть/нет ошибок), нет трендов
**Решение**:
- `_tech/metrics/` — еженедельный снапшот:
  - Количество страниц, размер (KB)
  - Средняя link density (входящих/исходящих на страницу)
  - Количество orphan
  - Распределение по типам и статусам
  - Coverage по доменам знаний
- Команда: `/metrics` → генерирует `_tech/metrics/YYYY-MM-DD.md`

#### P1.4 — Починить `std::bad_alloc` в Docling
**Статус**: ⬜
**Проблема**: `images_scale=1.5` → OOM на PDF >200 стр. Баг в PIL/pypdfium2.
**Решение**: `images_scale=1.0` для PDF >200 стр. в `pipeline.py`

### 🟢 P2 — Средние (качество)

#### P2.1 — Завершить Docling миграцию (ETSI 21 PDF)
**Статус**: 🔄 16/42 выполнено (11×3GPP + 5×ETSI)
**Решение**: `_tech/scripts/docling_batch_etsi.py` после B1 (латиница)

#### P2.2 — Модуляризация CLAUDE.md
**Проблема**: CLAUDE.md — 150+ строк, трудно расширять
**Решение**:
- Разделить на `.claude/includes/`:
  - `roles.md` — роль и философия
  - `structure.md` — структура хранилища
  - `agents.md` — sub-agents таблица (генерируется из `.claude/agents/`)
  - `skills.md` — skills таблица (генерируется из `.claude/skills/`)
  - `standards.md` — стандарты оформления, frontmatter, wikilinks
  - `restrictions.md` — ограничения
- CLAUDE.md собирается из includes автоматически

#### P2.3 — Кэширование Grep-запросов Reviewer
**Проблема**: Reviewer повторно грепает одни и те же спецификации
**Решение**:
- `specs-extracted/.cache/` — кэш частых запросов (FID → значение, CLA → значение)
- Инвалидация при обновлении specs-extracted/

### 🔵 P3 — Низкие (масштабирование)

#### P3.1 — Мульти-пользовательская архитектура
**Проблема**: Рассчитано на одного пользователя
**Решение** (будущее):
- Разделение `notes/` по пользователям
- Права на изменение wiki/ с аудитом (кто изменил, когда, почему)

#### P3.2 — Плагин для Obsidian
**Проблема**: Взаимодействие только через Claude CLI
**Решение** (будущее):
- Obsidian-плагин для вызова агентов из интерфейса
- Кнопки: "Create Summary", "Review Page", "Check Links"

---

## 3. Roadmap улучшений

```
Неделя 1-2:  P0.1 (git), P0.2 (backups)
Неделя 3-4:  P1.1 (hooks), P1.2 (frontmatter checker), P1.3 (CI review)
Неделя 5-6:  P2.1 (metrics), P2.2 (modular CLAUDE.md)
Неделя 7-8:  P2.3 (cache), P3.* (будущее)
```

---

## 4. Предлагаемые новые команды

| Команда | Назначение | Приоритет |
|---|---|---|
| `/backup` | Создать снапшот wiki/ + notes/ | P0 |
| `/metrics` | Сгенерировать отчёт с метриками | P2 |
| `/graph-stats` | Статистика графа знаний (degree, clusters) | P2 |
| `/validate-fm` | Проверить frontmatter во всех wiki/ | P1 |
| `/auto-review` | Авто-review всех изменённых страниц | P1 |

---

## 5. Структура `_tech/` после улучшений

```
_tech/
├── INDEX.md                   ← Индекс (этот файл)
├── ARCHITECTURE.md            ← Архитектурный анализ
├── IMPROVEMENT_PLAN.md        ← План улучшений (этот файл)
├── diagrams/                  ← Mermaid-диаграммы
│   ├── agent-interactions.md
│   ├── incoming-pipeline.md
│   ├── review-pipeline.md
│   ├── system-layers.md
│   └── knowledge-types.md
├── metrics/                   ← Еженедельные снапшоты метрик
│   └── YYYY-MM-DD.md
├── scripts/                   ← Вспомогательные скрипты
│   └── check_frontmatter.py
└── decisions/                 ← Architecture Decision Records
    └── ADR-001-use-specs-as-truth.md
```

---

## 6. Не решаемые сейчас проблемы

1. **ISO 7816 защищённые PDF** — не можем извлечь текст (DRM)
2. **Отсутствующие спецификации** (SGP.22, SGP.32, GP 2.3.1) — нужны исходные PDF
3. **TS 35.206** — теперь доступен через `spec-crawler checkout 35.206` ✅

---

## 7. Беклог — активные задачи

Полный беклог: [_tech/BACKLOG.md](_tech/BACKLOG.md)

| # | Задача | Приоритет | Статус |
|---|---|---|---|
| B1 | `Specifications` → `Specifications` | 🔴 P0 | ⬜ |
| B2 | PyTorch CUDA | 🟡 P1 | ⬜ |
| B3 | CPU vs GPU бенчмарк | 🟡 P1 | ⬜ |
| B4 | ETSI миграция (21 PDF) | 🟢 P2 | ⬜ |
| B5 | Обновить CLAUDE.md | 🟢 P2 | ⬜ |
| B6 | Обновить specs-extracted/INDEX.md | 🟢 P2 | ⬜ |
| B7 | Обновить outputs/STATUS_AND_PLAN.md | 🔵 P3 | ⬜ |
| B8 | Починить `images_scale` OOM | 🟡 P1 | ⬜ |

---

*План актуален на 2026-06-13 00:45. Следующий шаг: B1 (кириллица).*
