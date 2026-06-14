> **📦 АРХИВ** | 2026-06-14 | Docling-миграция завершена (73/74 PDF). Гибрид (TXT+MD+JSON) принят.

# specs-extracted/ Migration Plan

> **Дата**: 2026-06-12 17:45
> **Цель**: Поэтапная замена PyPDF2 `.txt` на Docling `.md` + `.json`
> **Пилоты**: pymupdf4llm (❌), Docling CPU (✅), Docling CUDA (✅ RTX 3060 12GB)
> **Вердикт**: **Docling побеждает. Гибридный переход: TXT + MD + JSON вместе.**

---

## 0. Результаты пилотов

### 0.1 pymupdf4llm (markdown-only, без ML) — ❌ ЗАБРАКОВАН

| Проблема | Деталь |
|---|---|
| Таблицы дублируются ×3 | `Identifier: '6F07'\|Identifier: '6F07'\|...` |
| Пробелы теряются | `ADFUSIM andDFTELECOM` |
| Непригоден для Reviewer Grep | Артефакты мешают поиску FID/CLA/SW |

### 0.2 Docling (ML-based, через 3gpp-crawler) — ✅ ПРИНЯТ

**Окружение**: docling 2.102.0 + исправленный `pipeline.py` (`PipelineOptions` → `PdfPipelineOptions` для `docx_direct`), LibreOffice 26.2.4.2

**Все 5 спецификаций обработаны успешно:**

| Спецификация | Release | MD | JSON | Примечание |
|---|---|---|---|---|
| TS 31.101 (UICC Interface) | 19.0.0 | 55 KB | 986 KB | CPU |
| TS 31.102 (USIM) | 19.4.0 | 2657 KB | 50790 KB | CPU |
| TS 31.102 (USIM) | 18.9.0 | 2531 KB | 49120 KB | CUDA RTX 3060 |
| TS 31.111 (USAT) | 19.3.0 | 859 KB | 11836 KB | CPU |
| TS 33.102 (Security) | 19.1.0 | 239 KB | 2936 KB | CPU |
| TS 35.206 (MILENAGE) | 19.0.0 | 82 KB | 1544 KB | CPU |

### 0.3 Сравнение качества: Docling vs PyPDF2

| Критерий | PyPDF2 TXT | Docling MD | Победитель |
|---|---|---|---|
| **Структура** | Плоский текст, `=== PAGE N/M ===` | Заголовки `####`, оглавление, разделы | **Docling** |
| **Метаданные** | Нет | YAML frontmatter: spec_number, release, date | **Docling** |
| **Таблицы** | ❌ Разрушены в строки | ⚠️ Восстановлены, merged cells дублируются | **Docling** |
| **FID/CLA чистота** | ✅ `'6F07'` grep-friendly | ⚠️ `6F 07` с пробелом — нужно адаптировать | **PyPDF2** |
| **Provenance** | Нет | ✅ JSON: page → paragraph → table → cell | **Docling** |
| **Reviewer Pass 1** | ✅ Grep → Read контекст | ⚠️ JSON-поиск эффективнее но требует адаптации | **PyPDF2** (пока) |
| **Reviewer Pass 2** | ❌ Нечитабелен | ✅ Структурирован, таблицы видны | **Docling** |
| **Размер (TS 31.102)** | 852 KB | 2657 KB + 50 MB JSON | **PyPDF2** |
| **GPU-ускорение** | Н/Д | ✅ CUDA: ~1.5 мин на 368 стр. | **Docling** |

### 0.4 Ключевой вывод

**Docling + GPU даёт лучший общий результат.** Структура, таблицы, метаданные, provenance — всё на порядок качественнее PyPDF2.

**PyPDF2 TXT нужно СОХРАНИТЬ** — для быстрого Grep Reviewer Pass 1 он всё ещё быстрее и надёжнее. Docling JSON открывает новый путь: поиск по ключам (FID → page → table → row) вместо Grep.

**Исправление в pipeline.py** (`PipelineOptions` → `PdfPipelineOptions` для `docx_direct`) починило docling 2.102.0 compatibility.

### 0.5 Финальная архитектура: гибрид

```
specs-extracted/
├── INDEX.md                                  ← Карта форматов
│
├── 3GPP/                                     ← 3GPP TS/TR (26 файлов)
│   ├── 31.102/
│   │   ├── 17.0/                             ← Release 17 (legacy PyPDF2)
│   │   │   └── ts_131102v171000p.pdf.txt     ← PyPDF2 TXT — Reviewer Pass 1
│   │   ├── 18.9/                             ← Release 18 (Docling CUDA)
│   │   │   ├── 3GPP_TS_31.102_18.9.0.md     ← Docling MD — Reviewer Pass 2
│   │   │   └── 3GPP_TS_31.102_18.9.0.json   ← Docling JSON — Provenance
│   │   ├── 19.4/                             ← Release 19 (Docling CPU)
│   │   │   ├── 3GPP_TS_31.102_19.4.0.md
│   │   │   └── 3GPP_TS_31.102_19.4.0.json
│   │   └── INDEX.md
│   └── ...
│
├── ETSI/  Books/  eSIM/  GSMA/  ISO/  ...    ← Не-3GPP (остаются PyPDF2)
└── ...
```

### 0.6 План действий (актуализированный)

| # | Действие | Статус |
|---|---|---|
| 1 | Установить LibreOffice | ✅ 26.2.4.2 |
| 2 | Починить API docling в 3gpp-crawler | ✅ `PdfPipelineOptions` fix |
| 3 | Пилот Docling CPU на 5 спецификациях | ✅ 5/5 успешно |
| 4 | Пилот Docling CUDA на RTX 3060 | ✅ Ускорение ~2× vs CPU |
| 5 | Сравнить качество с PyPDF2 | ✅ Гибридный вердикт |
| 6 | Docling batch на 20+ спецификациях 3GPP | ⬜ Ждёт подтверждения |
| 7 | Скопировать результаты в specs-extracted/ по новой структуре | ⬜ Зависит от шага 6 |
| 8 | Обновить Reviewer agent (гибридный Pass 1: Grep TXT + JSON lookup) | ⬜ |
| 9 | Обновить SpecExtractor agent (добавить Docling workspace process) | ⬜ |

---

## 1. Текущее состояние specs-extracted/

Всего: 58 файлов в 10 категориях.

### Мигрируемые через Docling (3GPP/ETSI) — 26 файлов

| Категория | Файлы | Номера для spec-crawler |
|---|---|---|
| ETSI_3GPP/USIM | 4 | 31.101, 31.102, 31.213, 151.010.04 |
| ETSI_3GPP/UICC | 3 | 102.221 (×3 версии) |
| ETSI_3GPP/CAT_STK | 3 | 101.476, 102.223, 151.014 |
| ETSI_3GPP/OTA | 3 | 102.225, 102.226 (×2) |
| ETSI_3GPP/Security | 4 | 131.919, 123.048, 133.220, 33.102 |
| ETSI_3GPP/Test_Conformance | 4 | 131.121, 131.124 (×2), 151.017 |
| ETSI_3GPP/UICC_API | 3 | 102.241, 131.130, 143.019 |
| ETSI_3GPP/GSM_Legacy | 2 | GSM 11.11, 151.011 |
| ETSI_3GPP/Numbering | 1 | 101.220 |

### НЕ мигрируемые (остаются PyPDF2 TXT) — 32 файла

| Категория | Файлы | Причина |
|---|---|---|
| Books | 5 | Не 3GPP-спецификации |
| eSIM | 3 | GSMA — не на 3GPP FTP |
| GlobalPlatform | 1 | Не на 3GPP FTP |
| ISO7816_Analysis | 4 | ISO — не на 3GPP FTP |
| JavaCard | 5 | TCA — не на 3GPP FTP |
| Manuals | 5 | Инструменты |
| Papers | 3 | Патенты/дипломные |
| Tutorials | 10 | Пособия |

---

## 2. Batch-миграция: команды

### Шаг 1: Создать workspace для всех 3GPP-спецификаций

```bash
cd "D:\ObsidianDB"
3gpp-crawler workspace create obsidiandb-specs
3gpp-crawler workspace add 31.101 31.102 31.111 31.121 31.124 31.130 31.213 --kind spec
3gpp-crawler workspace add 33.102 33.401 35.206 --kind spec
3gpp-crawler workspace add 101.220 101.476 102.221 102.223 102.225 102.226 102.241 --kind spec
3gpp-crawler workspace add 123.048 131.919 133.220 --kind spec
3gpp-crawler workspace add 143.019 151.011 151.014 151.017 --kind spec
```

### Шаг 2: Process с GPU

```bash
3gpp-crawler workspace process obsidiandb-specs --profile default --docx-direct --device cuda
```

### Шаг 3: Копировать в specs-extracted/

Скрипт для маппинга workspace output → specs-extracted/ (с сохранением структуры `Specifications/<категория>/...`).

---

## 3. Адаптация Reviewer v2

### Текущий Pass 1

```
Grep по TXT → Read контекст → сравнить с wiki
```

### Новый гибридный Pass 1

```
1. specs-extracted/INDEX.md → какие форматы доступны?
2. Если .txt: старый Grep
3. Если .json: JSON lookup по ключу (FID, CLA, размер)
   → получить координаты (page, table, row)
   → Read .md → найти таблицу/секцию
4. Сравнить с wiki
```

---

*План актуален на 2026-06-12 17:45. Docling ML проверен на CPU и CUDA, вердикт: гибрид TXT+MD+JSON.*
