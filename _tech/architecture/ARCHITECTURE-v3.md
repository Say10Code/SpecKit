# ObsidianDB — Архитектура v3

> **Аудит**: 2026-06-14 · **Состояние**: Фаза 5 (Automation) — active
> **Ключевое изменение v2→v3**: Прямое извлечение из .docx как основной пайплайн
> **Предыдущая**: `_tech/architecture/archive/ARCHITECTURE-v2.md`

---

## 0. Фундаментальный сдвиг v2 → v3

### Что изменилось

Архитектура v2 строилась на предположении: «PDF — первичный формат, извлечение текста требует рендера + парсинга». Это было неверно.

**Открытие**: `.docx` = ZIP-архив XML. Весь контент (текст + таблицы) находится в `word/document.xml` в структурированном виде, доступном для чтения стандартной библиотекой Python. Преобразование `.docx → LibreOffice → PDF → PyPDF2` было ненужным рендером структурированных данных в плоское изображение с последующим OCR-подобным восстановлением.

### Доказательная база

| Метрика | LibreOffice→PDF→PyPDF2 | Прямой .docx | Разница |
|---|---|---|---|
| TS 31.102 R16 (336 стр., 513 таблиц) | 175 сек | 0.2 сек | **875×** |
| Таблицы EF | Разрушены (плоский текст) | 513 таблиц в Markdown | **∞** |
| FID grep | 0.5ms | 0.1ms | 5× |
| Зависимости | LibreOffice + PyPDF2 + pypdfium2 | Python stdlib (zipfile + re) | −3 внешних зависимости |
| bad_alloc риск | Да | Нет | Устранён |
| GPU | Требуется (Docling) | Нет | Экономия энергии |

### Новая иерархия форматов

```
ПРИОРИТЕТ 1: .docx (ZIP/XML)
  → extract_docx.py — 0.2 сек, TXT + MD таблицы
  → Всегда первичный метод для spec-crawler checkout

ПРИОРИТЕТ 2: .pdf с Docling (3GPP)
  → Docling workspace — 1.5 мин GPU, MD + JSON
  → Для PDF без соответствующего .docx

ПРИОРИТЕТ 3: .pdf с PyPDF2 (все)
  → PyPDF2 — 15 сек, плоский TXT
  → Универсальный fallback для всего
```

---

## 1. Архитектурная схема (v3)

```
                        ┌─────────────────────────┐
                        │     CLAUDE.md (47 строк) │
                        │  Main Dispatcher         │
                        └────────────┬────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
    ┌──────▼──────┐           ┌──────▼──────┐           ┌──────▼──────┐
    │   SKILLS    │           │   AGENTS    │           │    DATA     │
    │ (pipelines) │           │  (workers)  │           │  (storage)  │
    └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
           │                         │                          │
    ┌──────┴──────────┐      ┌───────┴──────────┐       ┌──────┴──────────┐
    │ 7 skills        │      │ 8 agents         │       │ 3 extraction    │
    │ orchestrators   │      │ narrow experts   │       │ tiers           │
    └─────────────────┘      └──────────────────┘       └─────────────────┘
```

---

## 2. Extraction Pipeline v3 — три уровня

```
spec-crawler checkout
  │
  ├── .docx? ──► TIER 1: extract_docx.py (0.2 сек)
  │              ├── specs-extracted/<topic>/<name>.txt   (plain, grep)
  │              └── specs-extracted/<topic>/<name>.md    (tables, structured)
  │
  ├── .pdf (3GPP)? ──► TIER 2: Docling workspace (~1.5 мин GPU)
  │                    ├── specs-extracted/3GPP/<num>/<rel>/*.md
  │                    └── specs-extracted/3GPP/<num>/<rel>/*.json
  │
  └── .pdf (other) ──► TIER 3: PyPDF2 (~15 сек)
                       └── specs-extracted/<topic>/<name>.txt
```

### Приоритет выбора метода

| Формат | Метод | Автоматически? |
|---|---|---|
| `.docx` | **extract_docx.py --tables** (Tier 1) | ✅ Да — сразу после Librarian flatten |
| `.pdf` 3GPP с .docx | extract_docx.py (Tier 1) — уже извлечён | ✅ Да |
| `.pdf` 3GPP без .docx | Docling (Tier 2) + PyPDF2 fallback | ⚠️ GPU |
| `.pdf` не-3GPP | PyPDF2 (Tier 3) | ✅ Да |
| `.doc` бинарный | LibreOffice → PDF → PyPDF2 | ⚠️ Ручной |

---

## 3. 8 Агентов — матрица ответственности (v3)

| # | Агент | Версия | Ключевое изменение v3 |
|---|---|---|---|
| 1 | **SpecDownloader** | v1 | — |
| 2 | **Librarian** | v2 | После flatten: авто-вызов `extract_docx.py --tables` |
| 3 | **Author** | v2 (batch) | Batch mode — 1 вызов вместо N |
| 4 | **Reviewer** | v3 | Pass 1: приоритет .md таблиц над TXT grep |
| 5 | **Linker** | v1 | — |
| 6 | **Researcher** | v1 | — |
| 7 | **Formatter** | v1 | — |
| 8 | **SpecExtractor** | **v3** | **Метод C**: `extract_docx.py` (Tier 1) |

---

## 4. Reviewer v3 — ревизия Pass 1

### Старая модель (v2)

```
Pass 1: FID/CLA → TXT Grep (быстро, таблиц нет)
        Таблицы → JSON lookup → MD (только если Docling делал)
        Контекст → MD read (структурированный текст)
```

### Новая модель (v3)

```
Pass 1:  1. Проверить — есть ли specs-extracted/<topic>/<name>.md?
           → ДА: прочитать .md → ВСЕ таблицы EF одним проходом
           → НЕТ: fallback на TXT grep + JSON lookup
        2. FID/CLA/SW → grep по .txt (быстро, работает всегда)
        3. Контекст → MD read
```

**Выгода**: Для .docx источников — однофазный Pass 1. Reviewer читает `.md`, видит таблицу EF, мгновенно сверяет FID + структуру + access conditions. Без переключения форматов.

---

## 5. Стек технологий (v3)

| Слой | v2 | v3 | Изменение |
|---|---|---|---|
| **Первичное извлечение** | LibreOffice → PDF → PyPDF2 | **extract_docx.py** (stdlib) | −3 инструмента |
| **Вторичное извлечение** | Docling GPU (3GPP) | Docling GPU (3GPP) | Без изменений |
| **Fallback** | PyPDF2 | PyPDF2 | Без изменений |
| **Конвертация .doc** | LibreOffice | LibreOffice | Без изменений |
| **Таблицы** | Разрушены (кроме Docling) | **Сохранены всегда** (.docx) | **Ключевое** |

---

## 6. Технический стек (актуально)

| Слой | Технология | Версия | Роль |
|---|---|---|---|
| AI-оркестрация | Claude Code (Opus 4.8) | — | Главный диспетчер |
| Python | CPython | 3.13.13 | Скрипты, извлечение |
| Менеджер пакетов | uv | 0.11.21 | Управление окружением |
| **Первичное извлечение** | **Python stdlib** (zipfile, re) | **—** | **.docx → TXT + MD таблицы** |
| PDF-извлечение (ML) | Docling | 2.102.0 | 3GPP/ETSI → MD+JSON |
| PDF-извлечение (legacy) | PyPDF2 | — | Все PDF → плоский текст |
| Office-конвертация | LibreOffice | 26.2.4.2 | .doc → PDF |
| Скачивание спец. | spec-crawler | v0.0.1 (dev) | 3GPP FTP + WhatTheSpec |
| Mermaid | mermaid.js | v10 (CDN) | Диаграммы |
| Obsidian | Obsidian | — | GUI |

---

## 7. Пайплайн /spec-download (v3)

```
/spec-download 31.102
  │
  ├─[1] spec-crawler crawl 31.102                    ✅
  ├─[2] spec-crawler checkout → !INCOMING/ .docx      ✅
  ├─[3] Librarian flatten → Specifications/<topic>/   ✅
  ├─[3.5] 🆕 extract_docx.py --tables                  ✅ TIER 1
  │       → specs-extracted/<topic>/*.txt + *.md
  ├─[4] Author v2 Batch → wiki/                       ✅
  ├─[5] SpecExtractor (если PDF без .docx)             ⚠️ TIER 2/3
  ├─[6] /lint                                          ✅
  └─[7] Roadmap update                                 ✅
```

**Шаг 3.5 — новый**: сразу после flatten, до Author. Reviewer получает эталонные таблицы до того, как Author начнёт писать wiki-страницы.

---

## 8. Обнаруженные расхождения (v2 legacy + новые)

| # | Где | Проблема | Статус |
|---|---|---|---|
| D14 | USIM_EF_Table.md | FID 6FD7/6FD8 → 6FDE/6FDF | ✅ Исправлено |
| D15 | UICC_File_System.md | Отсутствовал DF_TELECOM + DF_GRAPHICS | ✅ Исправлено |
| D16 | auth_evolution.md | Отсутствовали ссылки TS 35.205/35.206/35.231/35.232 | ✅ Исправлено |
| D17 | milenage_vs_tuak.md | Отсутствовали TS 35.206/35.232 | ✅ Исправлено |
| D18 | specs-extracted/INDEX.md | Устарел (16 MD+JSON → 37+14+20) | ⬜ P2 |
| D19 | 32 PDF без MD+JSON | Books/eSIM/GP/ISO/JavaCard... — только TXT | ⬜ P3-5 |

---

## 9. Беклог (ключевые задачи)

| # | Задача | Статус |
|---|---|---|
| P2-4 | Batch Authoring — 4 call sites обновлены | ✅ |
| P2-6 | /spec-download полная автоматизация | ✅ |
| **P2-7** | **extract_docx.py → основной пайплайн (TIER 1)** | 🔄 Эта сессия |
| P3-5 | Docling-миграция оставшихся 32 PDF | ⬜ |
| P2-5 | Pipeline Parallelization | ⬜ |
| P2-1 | Аудит связности | ⬜ |
| P2-2 | Метрики качества | ⬜ |

---

*Архитектура актуальна на 2026-06-14 05:00. Ключевое изменение v2→v3: .docx прямой extract как Tier 1, исключающий LibreOffice→PDF→PyPDF2 для 3GPP .docx файлов.*
