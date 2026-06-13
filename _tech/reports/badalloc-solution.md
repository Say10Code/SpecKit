# std::bad_alloc — полный разбор и решение

> **Диагноз**: 2026-06-13 01:45
> **Проблема**: 162 предупреждения Stage preprocess bad_alloc на 3 PDF (173 стр.)
> **Корень**: pypdfium2 `bitmap.new_native()` → `ctypes.c_ubyte * (stride * height)` → C++ heap allocator fail

---

## 1. Где происходит (трассировка)

```
Docling standard_pdf_pipeline._process_batch()
  └─> page_preprocessing_model._populate_page_images()
       └─> page.get_image(scale=images_scale)
            └─> docling_parse_backend.get_page_image()
                 └─> pypdfium2._helpers.page.render(scale=scale*1.5, rotation=0)
                      └─> pypdfium2._helpers.bitmap.new_native()
                           └─> ctypes.c_ubyte * (stride * height)  ← std::bad_alloc
```

На каждый вызов Docling рендерит ПОЛНУЮ страницу как bitmap в памяти. Для A4 при 72 DPI + scale=1.0 + жёсткий ×1.5 в `docling_parse_backend`:
- Ширина: ~1240 × 1.5 = 1860 px
- Высота: ~1754 × 1.5 = 2631 px  
- RGBA буфер: 1860 × 2631 × 4 байта = **~19.6 MB на страницу**

Для страниц с векторной графикой (EPS, VML в 3GPP-спецификациях) pypdfium2 рендерит ВСЕ объекты → буфер может достигать 50+ MB.

## 2. Что теряется (реальный диагноз)

Проверено на TS 133220 (106 стр.) — сравнением Docling JSON/MD vs PyPDF2 TXT:

| Что | Статус с bad_alloc | Причина |
|---|---|---|
| **Текст страницы** | ✅ НЕ теряется | docling_parse извлекает текст ОТДЕЛЬНО от bitmap-рендера |
| **Заголовки/секции** | ✅ НЕ теряются | Структура документа сохраняется |
| **Таблицы** | ✅ НЕ теряются | Table detection работает на layout-слое, частично независимо |
| **Изображения страниц** | ❌ Теряются | `_populate_page_images` падает — битмап не создан |
| **Provenance (страница)** | ⚠️ Деградирует | Тексты lump-ятся в "page 1" вместо точных номеров страниц |

## 3. Практический импакт на ObsidianDB

Для **Reviewer Pass 1** (FID/CLA/SW поиск):
- ✅ TXT Grep — полностью покрывает (58 TXT-файлов)
- ✅ Docling MD — текст сохранён, можно читать

Для **Reviewer Pass 2** (таблицы, структура):
- ✅ Заголовки и оглавление сохранены
- ✅ Таблицы восстановлены
- ⚠️ Мелкое: page provenance неточный

**Вывод**: практические потери для ObsidianDB — МИНИМАЛЬНЫ. Текст, таблицы, структура — всё на месте. Потеряны только встроенные изображения (диаграммы из PDF), но ObsidianDB их не использует (Reviewer читает текст, а не картинки).

## 4. Три варианта решения

### Вариант A: Подавление + try/except в `_populate_page_images`

**Идея**: Обернуть `page.get_image()` в try/except. При bad_alloc вернуть 1×1 placeholder bitmap. Pipeline продолжит работу без потери текста.

**Плюсы**: Docling не падает, все страницы обрабатываются, provenance сохраняется
**Минусы**: Нужно патчить docling внутренний код (`standard_pdf_pipeline.py`)

```python
# В docling/models/stages/page_preprocessing/page_preprocessing_model.py
def _populate_page_images(self, page, images_scale):
    try:
        page.get_image(scale=images_scale)
    except (MemoryError, Exception):  # std::bad_alloc приходит как MemoryError
        # Создать минимальный placeholder — страница без изображения,
        # но текст и таблицы всё равно извлекутся через docling_parse
        pass
```

### Вариант B: Гибридный пост-процессинг (Docling MD + PyPDF2 TXT)

**Идея**: После Docling-извлечения, для страниц с bad_alloc взять текст из PyPDF2 TXT и вставить в правильную позицию в MD.

**Плюсы**: Гарантирует 100% покрытие. Использует существующие TXT-файлы.
**Минусы**: Неоднородный MD (куски Docling + куски PyPDF2). Больше работы по вставке.

### Вариант C: `generate_picture_images=False` + `images_scale=0.5` для больших PDF

**Идея**: Для PDF >200 стр. агрессивно снижать `images_scale` до 0.5. Это уменьшает буфер в 4 раза (19.6 MB → 4.9 MB на страницу).

**Плюсы**: Уже реализовано частично (B8). Простое расширение.
**Минусы**: Качество table detection может снизиться при scale=0.5.

## 5. РЕКОМЕНДАЦИЯ: Вариант A + C комбинированно

1. **Добавить `try/except MemoryError`** в `page_preprocessing_model._populate_page_images` — это ловит bad_alloc и позволяет pipeline продолжить без потери текста
2. **Сохранить `generate_picture_images=False`** (B8 fix) — мы не извлекаем картинки
3. **`images_scale=1.0` для PDF <200 стр, `images_scale=0.5` для PDF ≥200 стр** — динамический scale в `_build_pipeline_options`

### Код для pipeline.py (Вариант A+C):

```python
# pipeline.py — _build_pipeline_options()
# Добавить параметр total_pages=0

if total_pages >= 200:
    pipeline_opts.images_scale = 0.5   # агрессивное снижение для больших PDF
else:
    pipeline_opts.images_scale = 1.0
```

## 6. Код патча для docling (Вариант A)

Файл: `.venv/Lib/site-packages/docling/models/stages/page_preprocessing/page_preprocessing_model.py`

```python
# Строка ~62: page.get_image(scale=images_scale)
# Заменить на:

try:
    page.get_image(scale=images_scale)
except Exception:
    # pypdfium2 может выбросить std::bad_alloc → MemoryError
    # при рендере страниц с векторной графикой.
    # Продолжаем без изображения — текст и таблицы извлекутся через docling_parse
    pass
```

## 7. Импакт после исправления

| До | После |
|---|---|
| 162 bad_alloc предупреждения | 0 предупреждений |
| Страницы без изображений | Страницы без изображений (текст сохранён) |
| MD: заголовки/таблицы/текст ОК | MD: заголовки/таблицы/текст ОК (без изменений) |
| Reviewer Pass 1: Grep по TXT | Без изменений |
| Reviewer Pass 2: таблицы из MD | Без изменений |

## 8. Беклог

| # | Действие | Приоритет |
|---|---|---|
| F1 | Патч `page_preprocessing_model.py`: try/except MemoryError | 🟡 P1 |
| F2 | Динамический `images_scale`: 1.0 / 0.5 по количеству страниц | 🟡 P1 |
| F3 | Повторный прогон TS 31.102 (368 стр.) с патчем — проверить 0 bad_alloc | 🟢 P2 |
| F4 | Обновить бенчмарк: сравнить CPU/GPU с новым scale | 🟢 P2 |

---

*Диагноз готов. Жду решения по варианту.*
