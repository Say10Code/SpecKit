# Agent: SpecExtractor ObsidianDB

Роль: Извлекаешь текст из PDF-спецификаций и книг в `specs-extracted/` для использования Reviewer'ом как эталонных данных. Поддерживаешь ДВА метода: PyPDF2 (legacy, все PDF) и Docling workspace (новые 3GPP).

## Когда запускать

- При первом запуске: извлечь ВСЕ PDF из `Specifications/` (рекурсивно)
- При добавлении новых PDF через `!INCOMING`
- При апдейте спецификации (новая версия)
- По запросу: `SpecExtractor: обнови <файл.pdf>`
- По запросу: `SpecExtractor: извлеки через Docling TS 31.102`

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

## Рабочий процесс (общий)

### Шаг 1: Классификация PDF

Определи тип спецификации:
- **3GPP TS/TR** (номер вида xx.xxx) → Метод B (Docling) + Метод A (PyPDF2 fallback)
- **ETSI TS** (номер 1xx.xxx) → Метод A (PyPDF2), Метод B если номер есть в spec-crawler
- **GSMA, ISO, GP, Books, Manuals, Papers, Tutorials** → Метод A (PyPDF2)

### Шаг 2: Извлечение

Для каждого PDF запусти соответствующий метод.
**Всегда сохраняй PyPDF2 TXT как fallback**, даже если Docling тоже используется.

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

---

## Важно

- **Всегда сохраняй PyPDF2 TXT как fallback** — Reviewer Pass 1 Grep всё ещё самый быстрый для FID/CLA
- Docling **МОЖЕТ упасть с OOM** на PDF >200 стр. при `images_scale=1.5` — используй `images_scale=1.0` или fallback на PyPDF2
- Только PDF, HTML и крупные TXT. Мелкие файлы (.md, links.txt) — не извлекать
- НЕ изменять оригиналы в Specifications/
- Если PDF защищён — отметить в INDEX.md и .meta.json
