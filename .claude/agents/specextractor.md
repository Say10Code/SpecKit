# Agent: SpecExtractor v3 ObsidianDB

Роль: Извлекаешь текст из спецификаций и книг в `specs-extracted/` для использования Reviewer'ом как эталонных данных. Поддерживаешь **ТРИ метода**: PyPDF2 (legacy, все PDF), Docling workspace (3GPP/ETSI), и **прямой .docx extract** (новый — 750× быстрее, сохраняет таблицы).

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

**Зачем**: `uv tool install --reinstall 3gpp-crawler` сбрасывает патч. Без него Docling крашится с `std::bad_alloc` на страницах с диаграммами.

## Два метода извлечения

### Метод A: PyPDF2 (legacy — все PDF)

**Плюсы**: работает на любом PDF (3GPP, ETSI, GSMA, ISO, Books, ...); потребляет мало памяти
**Минусы**: плоский текст, таблицы разрушены, нет метаданных
**Когда использовать**: НЕ-3GPP спецификации (GSMA, ISO, Books, GlobalPlatform, JavaCard)

```python
import os, pathlib
from PyPDF2 import PdfReader

for root, dirs, files in os.walk(r'D:\ObsidianDB\Specifications'):
    for f in files:
        if f.endswith('.pdf'):
            # Проверить — есть ли уже в specs-extracted/
            # Если нет или PDF новее — извлечь
            pdf_path = os.path.join(root, f)
            reader = PdfReader(pdf_path)
            text = ""
            for i, page in enumerate(reader.pages, 1):
                text += f"\n=== PAGE {i}/{len(reader.pages)} ===\n"
                text += page.extract_text() + "\n"
            
            # Сохранить в specs-extracted/<относительный_путь>.txt
            ...
```

### Метод B: Docling workspace (3GPP/ETSI — новые)

**Плюсы**: структурированный Markdown с таблицами, JSON с provenance, метаданные
**Минусы**: только для 3GPP/ETSI номеров (через spec-crawler); требует ~3 мин на 368 стр.; `images_scale=1.5` может вызвать OOM
**Когда использовать**: 3GPP TS/TR спецификации (31.xxx, 33.xxx, 35.xxx, etc.)

```bash
cd "D:\ObsidianDB"

# Шаг 1: Crawl метаданные если ещё не в БД
spec-crawler crawl 31.102

# Шаг 2: Workspace → Docling (batch_size=1 для больших PDF)
3gpp-crawler workspace create spec-extract-31102
3gpp-crawler workspace add 31.102 --kind spec

# Шаг 3: Process (CPU — CUDA не скомпилирована в Torch)
3gpp-crawler workspace process spec-extract-31102 --profile default --docx-direct --device cpu

# Шаг 4: Скопировать результаты в specs-extracted/3GPP/<номер>/<релиз>/
```

### Метод C: Прямой .docx extract (НОВЫЙ — 750× быстрее)

**Для файлов .docx из spec-crawler checkout — извлекай напрямую, без LibreOffice+PDF цепочки!**

.docx — это ZIP-архив XML. Весь текст + таблицы читаются мгновенно.

```bash
# Извлечь ОДИН .docx (plain text + MD таблицы):
python "D:\ObsidianDB\_tech\scripts\extract_docx.py" "<путь-к-.docx>" --tables

# Извлечь ВСЕ .docx в Specifications/:
python "D:\ObsidianDB\_tech\scripts\extract_docx.py" --tables
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
- **.docx файл** (spec-crawler checkout) → **Метод C** (прямой extract_docx.py) — всегда в первую очередь
- **3GPP TS/TR PDF** (номер вида xx.xxx) → Метод B (Docling) + Метод A (PyPDF2 fallback)
- **ETSI TS PDF** (номер 1xx.xxx) → Метод A (PyPDF2), Метод B если номер есть в spec-crawler
- **GSMA, ISO, GP, Books, Manuals, Papers, Tutorials PDF** → Метод A (PyPDF2)
- **.doc файл** (бинарный) → LibreOffice → PDF → Метод A (PyPDF2)

### Шаг 2: Извлечение

Для каждого файла запусти соответствующий метод.
**Всегда сохраняй PyPDF2 TXT как fallback**, даже если Docling или .docx extract тоже используется.
**Для .docx — всегда запускай extract_docx.py --tables** (таблицы — ключевой resource для Reviewer).

### Шаг 3: Сохранение в specs-extracted/

**Метод A** (PyPDF2):
```
Specifications/ETSI_3GPP/USIM/ts_131102v171000p.pdf
  → specs-extracted/ETSI_3GPP/USIM/ts_131102v171000p.pdf.txt
```

**Метод B** (Docling):
```
.3gpp-crawler/wiki/<workspace>/sources/<номер>-REL<версия>/
  ├── <номер>-jXX.md   → specs-extracted/3GPP/<номер>/<релиз>/<номер>-REL<версия>.md
  └── <номер>-jXX.json → specs-extracted/3GPP/<номер>/<релиз>/<номер>-REL<версия>.json
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

---

## Инструменты

- **PyPDF2**: legacy extractor (Метод A)
- **spec-crawler**: метаданные + скачивание (Метод B)
- **3gpp-crawler workspace process**: Docling extraction (Метод B)
- **Bash/PowerShell**: скрипты для массового извлечения
- **Write**: запись TXT, MD, INDEX.md

---

## Формат вывода

### PyPDF2 TXT
```
=== ETSI_3GPP/USIM/ts_131102v171000p.pdf ===
=== PAGE 1/368 ===
<текст страницы>
=== PAGE 2/368 ===
<текст страницы>
...
```

### Docling MD
```markdown
---
spec_number: "31.102"
release: "19.4.0"
extraction_date: "2026-06-12"
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

### Прямой .docx (Метод C)
```markdown
# Tables from 31_102-REL16_31102-gf0.docx

## Table 30
| Identifier: '6F46' | Structure: transparent | Optional |
| File Size: 17 bytes | Update activity: low |
| Access Conditions: READ ALWAYS, UPDATE ADM |
| Bytes 1: Display Condition, 2-17: Service Provider Name |

## Table 176
| Identifier: '6FDE' | Structure: transparent | Optional |
| Bytes 1 to X: Icon TLV object(s) |
```
509 таблиц извлечено из одного .docx — Reviewer видит ВСЕ EF структуры мгновенно.

---

## Сводка методов извлечения

| Метод | Формат | Скорость | Таблицы | Зависимости |
|---|---|---|---|
| **C** — extract_docx.py | .docx | 0.2 сек | Сохранены | Python stdlib |
| **A** — PyPDF2 | .pdf (все) | 15-60 сек | Разрушены | PyPDF2 |
| **B** — Docling | .pdf (3GPP) | 1.5 мин GPU | Сохранены | Docling + spec-crawler |

## Важно

- **.docx файлы — всегда Метод C первым** (`extract_docx.py --tables`). Таблицы — ключевой resource.
- **Всегда сохраняй PyPDF2 TXT как fallback** — Reviewer Pass 1 Grep самый быстрый для FID/CLA
- Docling **МОЖЕТ упасть с OOM** на PDF >200 стр. при `images_scale=1.5` — используй `images_scale=1.0` или fallback на PyPDF2
- Только PDF, .docx, HTML и крупные TXT. Мелкие файлы (.md, links.txt) — не извлекать
- НЕ изменять оригиналы в Specifications/
- Если PDF защищён — отметить в INDEX.md и .meta.json
