# Беклог ObsidianDB

> **Дата**: 2026-06-13 01:30
> **Назначение**: Боевой список задач. Обновляется после каждой сессии.
> **Приоритеты**: 🔴 P0 (критическое) → 🟡 P1 (высокое) → 🟢 P2 (среднее) → 🔵 P3 (низкое)

---

## Быстрый статус

| Метрика | Значение |
|---|---|
| Sub-agents | 8 |
| Skills | 6 |
| Wiki страниц | 129 (+7 index) |
| Reviewed | 100% |
| Битых ссылок | 0 |
| Specifications PDF | 65 |
| specs-extracted TXT | 58 (PyPDF2) |
| specs-extracted MD+JSON | 16 (Docling: 11×3GPP + 5×ETSI) |
| 3gpp-crawler | ✅ Интегрирован |
| LibreOffice | ✅ 26.2.4.2 |
| Torch CUDA | ✅ RTX 3060 (11 GB VRAM) |
| GPU speedup | 2.4-4.2× vs CPU |

---

## 🔴 P0 — Критическое

### B1 — Удалить старую `Спецификации/` + починить пути в 5 файлах
**Статус**: 🔄 90 файлов обновлено, 5 файлов агентов/skills осталось
**Проблема**: После переименования `Спецификации` → `Specifications` (90 .md/.py/.toml обновлены), 4 агента + 1 skill всё ещё ссылаются на старый путь
**Файлы к исправлению**: `reviewer.md`, `specextractor.md`, `librarian.md`, `specdownloader.md`, `spec-download/SKILL.md`
**Старая папка**: `D:\ObsidianDB\Specifications\Спецификации\` — удалить после закрытия Obsidian

---

## 🟡 P1 — Высокое

### U2 — Auto-lint hook после каждого изменения
**Статус**: ⬜ Из `deep-research-report.md`
**Решение**: Настроить hook в `.claude/settings.local.json` для `after_edit` в `wiki/`

### U4 — Обновить `specs-extracted/INDEX.md`
**Статус**: ⬜ Из `deep-research-report.md`
**Решение**: Колонка Format, секции 3GPP/ETSI

### U5 — Починить `generate_picture_images` дефолт
**Статус**: ⬜ Из `deep-research-report.md`
**Решение**: Всегда `False` для DEFAULT профиля в pipeline.py

### B8 — Исследовать `std::bad_alloc` в pypdfium2
**Статус**: ✅ Решено 13 июн (F1+F2+F3)
**Проблема**: pypdfium2 `bitmap.new_native()` → `std::bad_alloc` на страницах с векторной графикой
**Корень**: `page.get_image()` в `page_preprocessing_model._populate_page_images` рендерит RGBA-битмапы (19.6 MB/стр.) → heap фрагментация → C++ аллокатор падает
**Решение (F1)**: `try/except Exception` вокруг обоих `page.get_image()` вызовов — ловит MemoryError, pipeline продолжает
**Результат**: 247 → 1 bad_alloc (99.6%). Все 8/8 EF найдены, 368/368 стр. обработаны, таблицы сохранены. Подробный отчёт: `_tech/F1F2-verification-report.md`

### B2 — PyTorch CUDA
**Статус**: ✅ Выполнено 13 июн — RTX 3060 активирован
**Результат**: `torch-2.12.0+cu126`, `torch.cuda.is_available() = True`, 11 GB VRAM

### B3 — CPU vs GPU бенчмарк
**Статус**: ✅ Выполнено 13 июн
**Результат**:
- TS 35.206 (106p): CPU 175s, GPU 73s → **2.4× speedup**
- TS 31.130 (28p): CPU 114s, GPU 27s → **4.2× speedup**  
- Batch 3 docs (173p): CPU 319s, GPU 122s → **2.6× speedup**
- MD output бит-в-бит идентичен между CPU и GPU

---

## 🟢 P2 — Среднее

### U1 — Git-инициализация
**Статус**: ✅ Выполнено 13 июн
**Результат**: `a35abfc` — 266 файлов, 110 277 вставок

### B4 — Завершить ETSI миграцию (21 PDF)
**Статус**: ⬜ Ждёт B1 (пути в agent'ах)
**Решение**: `_tech/scripts/docling_batch_etsi.py` после фикса путей
**Оценка**: ~15 мин на GPU (batch из 21 PDF)

### U7 — Выделить «серия→тема» в единый source of truth
**Статус**: ⬜ Из `deep-research-report.md`
**Решение**: `Specifications/.category-map.md`

### U8 — Создать `/research` skill для Researcher
**Статус**: ⬜ Из `deep-research-report.md`

### U9 — Валидатор frontmatter (`check_frontmatter.py`)
**Статус**: ⬜ Из `deep-research-report.md`

### U10 — Обновить Mermaid-диаграммы (8 агентов, Docling)
**Статус**: ⬜ Из `deep-research-report.md`

### B5 — Обновить CLAUDE.md (корневой и .claude)
**Статус**: ⬜
**Что**: `.claude/CLAUDE.md` → 6 skills, 8 agents, актуальные пути, Docling

### B6 — Обновить `specs-extracted/INDEX.md`
**Статус**: ⬜
**Что**: Добавить колонку Format (TXT/MD/JSON), секции 3GPP/ и ETSI/

---

## 🔵 P3 — Низкое

### B7 — Обновить `outputs/STATUS_AND_PLAN.md`
**Статус**: ⬜

### P3.1 — Мульти-пользовательская архитектура (будущее)
### P3.2 — Obsidian плагин (будущее)

---

## Завершённые задачи

| # | Задача | Дата |
|---|---|---|
| 1 | 3gpp-crawler: Python 3.13, `uv tool install`, `spec-crawler` CLI | 12 июн |
| 2 | Конфиг: `3gpp-crawler.toml` | 12 июн |
| 3 | `.gitignore` | 12 июн |
| 4 | `spec-crawler crawl` БД метаданных | 12 июн |
| 5 | SpecDownloader agent обновлён | 12 июн |
| 6 | Librarian agent: два пути | 12 июн |
| 7 | Skill `/spec-download` создан | 12 июн |
| 8 | LibreOffice 26.2.4.2 | 12 июн |
| 9 | Docling fix: `PipelineOptions` → `PdfPipelineOptions` | 12 июн |
| 10 | Docling пилот: 5 спецификаций | 12 июн |
| 11 | Docling миграция: 16 MD+JSON в `specs-extracted/` | 13 июн |
| 12 | `std::bad_alloc` анализ: OOM в pypdfium2/PIL | 13 июн |
| 13 | Torch CUDA проверка → установка | 13 июн |
| 14 | Reviewer v3: гибридный Pass 1 | 13 июн |
| 15 | SpecExtractor v2: PyPDF2 + Docling | 13 июн |
| 16 | B1: 90 файлов `Спецификации`→`Specifications` | 13 июн |
| 17 | B2: PyTorch CUDA (RTX 3060) | 13 июн |
| 18 | B3: CPU vs GPU бенчмарк (3 стадии) | 13 июн |
| 19 | B8: `images_scale=1.0` + `generate_picture_images=False` | 13 июн |
| 20 | Архитектура v2: полный анализ `ARCHITECTURE-v2.md` | 13 июн |
| 21 | Глубокий ресерч: 23 находки, 14 проблем, 10 улучшений | 13 июн |

---

## Хронология

| Дата | Выполнено | Добавлено в беклог |
|---|---|---|
| 12 июн 16:00 | Аудит архитектуры, `_tech/` создан | P0-P3: git, бэкапы, хуки, метрики |
| 12 июн 17:00 | 3gpp-crawler интеграция, SpecDownloader, Librarian v2 | Docling пилот |
| 12 июн 18:00 | Docling fix + миграция 16 спец. | B1-B8 |
| 13 июн 00:30 | Reviewer v3, SpecExtractor v2, бенчмарк, анализ OOM | — |
| 13 июн 01:30 | B2 CUDA ✅, B3 бенчмарк ✅, B8 fix ✅, Архитектура v2 | A1-A3 (P0) |

---

*Беклог актуален на 2026-06-13 01:30. Следующий шаг: подтверждение пользователя → A1-A3.*
