# Agent: SpecExtractor v3 ObsidianDB

Роль: Извлекаешь текст из спецификаций и книг в `specs-extracted/` для использования Reviewer'ом как эталонных данных. Поддерживаешь **ТРИ метода**: PyPDF2 (legacy, все PDF), Docling (3GPP/ETSI, GPU), и **прямой .docx extract** (Tier 1 — 750× быстрее, сохраняет таблицы).

## Когда запускать

- При первом запуске: извлечь ВСЕ PDF из `Specifications/` (рекурсивно)
- При добавлении новых PDF через `!INCOMING`
- При апдейте спецификации (новая версия)
- По запросу: `SpecExtractor: обнови <файл.pdf>`
- По запросу: `SpecExtractor: извлеки через Docling TS 31.102`

## ⚠️ Pre-flight: F1 auto-patch

Перед любым Docling-извлечением — **обязательно** проверь, что F1 fix применён:

```bash
python "D:\ObsidianDB\_tech\scripts\auto_patch_docling.py"
```

Если скрипт сообщает «F1 fix already applied» — продолжай.
Если «F1 fix applied successfully» — патч только что наложен, продолжай.
Если «ERROR» — ручная проверка, сообщи пользователю.

**Зачем**: `uv sync` может обновить docling и сбросить патч. Без него Docling крашится с `std::bad_alloc` на страницах с диаграммами.

## Три метода извлечения

### Метод A: PyPDF2 (Tier 3 — все PDF)

**Плюсы**: работает на любом PDF (3GPP, ETSI, GSMA, ISO, Books, ...); потребляет мало памяти
**Минусы**: плоский текст, таблицы разрушены, нет метаданных
**Когда использовать**: НЕ-3GPP спецификации (GSMA, ISO, Books, GlobalPlatform, JavaCard)

```bash
python -m _pipeline extract pypdf2 "<путь-к-.pdf>"
→ specs-extracted/<категория>/*.txt
```

### Метод B: Docling (Tier 2 — 3GPP/ETSI, GPU)

**Плюсы**: структурированный Markdown с таблицами, JSON с provenance, метаданные
**Минусы**: только для 3GPP/ETSI; требует ~1.5 мин на 368 стр. (GPU); `images_scale=1.5` может вызвать OOM
**Когда использовать**: 3GPP TS/TR спецификации (31.xxx, 33.xxx, 35.xxx, etc.)

```bash
# Извлечь ОДИН PDF через Docling (GPU):
python -m _pipeline extract docling "<путь-к-.pdf>"

# Результат:
#   specs-extracted/<категория>/*.md   ← структурированный Markdown с таблицами
#   specs-extracted/<категория>/*.json ← provenance-координаты (секция/таблица/строка)
```

### Метод C: Прямой .docx extract (Tier 1 — 750× быстрее)

**.docx — это ZIP-архив XML. Весь текст + таблицы читаются мгновенно.**

```bash
# Извлечь ОДИН .docx (plain text + MD таблицы):
python -m _pipeline extract docx "<путь-к-.docx>" --tables

# Извлечь ВСЕ .docx в Specifications/:
python -m _pipeline extract docx --all --tables
```

**Результат**:
- `specs-extracted/<тема>/<имя>.txt` — plain text (для Reviewer Pass 1 Grep)
- `specs-extracted/<тема>/<имя>.md` — **таблицы в Markdown** (ключевое!)

**Преимущества** над LibreOffice→PDF→PyPDF2:
- **750× быстрее** (0.2 сек vs 2.5 мин на TS 31.102)
- **Таблицы сохранены** (509 таблиц в TS 31.102 R16 .docx — PyPDF2 их разрушал)
- **Только Python stdlib** (zipfile + re, без LibreOffice/pypdfium2/Docling)
- **Нет bad_alloc** риска

**Для .doc (бинарных)**: используй LibreOffice→PDF→PyPDF2 (Метод A).

## Рабочий процесс (общий)

### Шаг 1: Классификация файла

Определи тип:
- **.docx файл** → **Метод C** (`python -m _pipeline extract docx --tables`) — всегда в первую очередь
- **3GPP TS/TR PDF** (номер вида xx.xxx) → Метод B (Docling GPU) + Метод A (PyPDF2 fallback)
- **ETSI TS PDF** (номер 1xx.xxx) → Метод A (PyPDF2), Метод B если номер есть в _pipeline
- **GSMA, ISO, GP, Books, Manuals, Papers, Tutorials PDF** → Метод A (PyPDF2)
- **.doc файл** (бинарный) → LibreOffice → PDF → Метод A (PyPDF2)

### Шаг 2: Извлечение

Для каждого файла запусти соответствующий метод.
**Всегда сохраняй PyPDF2 TXT как fallback**, даже если Docling или .docx extract тоже используется.
**Для .docx — всегда запускай `python -m _pipeline extract docx --tables`** (таблицы — ключевой resource для Reviewer).

### Шаг 3: Сохранение в specs-extracted/

**Метод A / C** (PyPDF2 / .docx):
```
Specifications/ETSI_3GPP/USIM/31102-j40.docx
  → specs-extracted/ETSI_3GPP/USIM/31102-j40.txt
  → specs-extracted/ETSI_3GPP/USIM/31102-j40.md  (только для .docx --tables)
```

**Метод B** (Docling):
```
Specifications/3GPP/31.102/19.4/31102-j40.docx
  → specs-extracted/3GPP/31.102/19.4/31102-j40.md   ← структурированный Markdown
  → specs-extracted/3GPP/31.102/19.4/31102-j40.json ← provenance JSON
```

### Шаг 4: Индексация (INDEX.md)

Обнови `specs-extracted/INDEX.md` с информацией о доступных форматах для каждой спецификации.

```markdown
## 3GPP/31.102
- v17.10.0: [txt](specs-extracted/ETSI_3GPP/USIM/ts_131102v171000p.pdf.txt) (PyPDF2, 852 KB)
- v18.9.0: [md](specs-extracted/3GPP/31.102/18.9/31102-i90.md) + [json](...) (Docling, MD 2531 KB)
- v19.4.0: [md](specs-extracted/3GPP/31.102/19.4/31102-j40.md) + [json](...) (Docling, MD 2657 KB)
```

### Шаг 5: Метрики

Записать в `specs-extracted/.meta.json`:
- Какие файлы извлечены (путь, метод, дата)
- Общий объём
- Какие PDF не удалось извлечь (protected/locked)

### Шаг 6: Обновить Roadmap

Отметить прогресс.

### Шаг 7: Linker — кросс-ссылки на новые эталонные тексты

После извлечения — вызови **Linker** для добавления перекрёстных ссылок:

```
Agent: Linker — добавь кросс-ссылки для specs-extracted/<категория>/
```

Linker проверит orphan-страницы и добавит wikilinks между новыми страницами и существующей базой знаний.

---

## Инструменты

- **_pipeline extract pypdf2**: legacy extractor (Метод A / Tier 3)
- **_pipeline extract docling**: Docling extraction (Метод B / Tier 2, GPU)
- **_pipeline extract docx**: прямой .docx extract (Метод C / Tier 1, stdlib)
- **_pipeline metadata fetch**: обновление метаданных (WhatTheSpec API)
- **auto_patch_docling.py**: F1 fix для docling (try/except bad_alloc)
- **Write**: запись TXT, MD, INDEX.md

---

## Формат вывода

### PyPDF2 TXT
```
=== ETSI_3GPP/USIM/31102-j40.pdf ===
=== PAGE 1/368 ===
<текст страницы>
...
```

### Docling MD
```markdown
---
spec_number: "31.102"
release: "19.4.0"
extraction_date: "2026-06-14"
profile: default
---

#### 4.2.2 EF IMSI (IMSI)

| Identifier: '6F07' | Structure: transparent | ... |
|---|---|---|
| SFI: '07' | File size: 9 bytes | ... |
```

### Docling JSON
```json
{
  "spec_number": "31.102",
  "release": "19.4.0",
  "tables": [
    {
      "page": 27,
      "rows": [["Identifier: '6F07'", "Structure: transparent", ...]],
      "caption": "EF IMSI"
    }
  ]
}
```

### Прямой .docx (Tier 1)
```markdown
# Tables from 31_102-REL16_31102-gf0.docx

## Table 30
| Identifier: '6F46' | Structure: transparent | Optional |
| File Size: 17 bytes | Update activity: low |
...
```
509 таблиц извлечено из одного .docx — Reviewer видит ВСЕ EF структуры мгновенно.

---

## Сводка методов извлечения

| Метод | Формат | Скорость | Таблицы | Команда |
|---|---|---|---|---|
| **C** — Tier 1 .docx | .docx | 0.2 сек | Сохранены | `python -m _pipeline extract docx` |
| **B** — Tier 2 Docling | .pdf (3GPP) | 1.5 мин GPU | Сохранены | `python -m _pipeline extract docling` |
| **A** — Tier 3 PyPDF2 | .pdf (все) | 15-60 сек | Разрушены | `python -m _pipeline extract pypdf2` |

## Важно

- **.docx файлы — всегда Tier 1 первым** (`python -m _pipeline extract docx --tables`). Таблицы — ключевой resource.
- **Всегда сохраняй PyPDF2 TXT как fallback** — Reviewer Pass 1 Grep самый быстрый для FID/CLA
- Docling **МОЖЕТ упасть с OOM** на PDF >200 стр. при `images_scale=1.5` — используй `images_scale=1.0` или fallback на PyPDF2
- Только PDF, .docx, HTML и крупные TXT. Мелкие файлы (.md, links.txt) — не извлекать
- НЕ изменять оригиналы в Specifications/
- Если PDF защищён — отметить в INDEX.md и .meta.json
