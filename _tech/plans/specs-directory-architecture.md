# Архитектура хранения спецификаций — анализ и план улучшения

> **Аудит**: 2026-06-12 17:15
> **Текущее состояние**: 65 файлов (57 PDF + 8 TXT/HTML/MD) в 11 директориях
> **Цель**: Единая, самодокументированная структура хранения с поддержкой версионирования и SpecDownloader

---

## 1. Текущая структура — аудит

### 1.1 Дерево и статистика

```
Specifications/                          ← 65 файлов, 11 категорий, ~53 MB
├── !INCOMING/          (0)            ← Вход: ручной + spec-crawler
├── !double/            (24)           ← Дубликаты (уже обработанные)
│
├── Books/              (5 PDF)        ← Учебники (4.3K KB макс)
├── eSIM/               (3 PDF)        ← GSMA SGP.02 + whitepaper
├── ETSI_3GPP/          (0 в корне)    ← 🔴 ПУСТАЯ — все файлы в подпапках
│   ├── CAT_STK/        (3 PDF)
│   ├── GSM_Legacy/     (2 PDF)
│   ├── Numbering/      (1 PDF)
│   ├── OTA/            (3 PDF)
│   ├── Security/       (3 PDF + 1 PNG)
│   ├── Test_Conformance/(4 PDF)
│   ├── UICC/           (3 PDF — 3 версии TS 102 221!)
│   ├── UICC_API/       (3 PDF)
│   └── USIM/           (4 PDF)
│
├── GlobalPlatform/     (1 PDF)
├── ISO7816_Analysis/   (4 PDF)
├── JavaCard/           (3 PDF + 2 TXT + 1 HTML)
├── Manuals/            (5 PDF)
├── Papers/             (3 PDF)
└── Tutorials/          (8 PDF + 2 TXT + 1 MD)
```

### 1.2 Проблемы текущей структуры

| # | Проблема | Пример | Последствие |
|---|---|---|---|
| **P1** | Неоднородное именование | `gsm11-11.pdf`, `ts_102221v170100p.pdf`, `31213-730.pdf`, `SGP.02-v4.1.pdf` | Нельзя автоматически извлечь номер/версию из имени |
| **P2** | Смешение форматов | `JavaCard/`: PDF + TXT + HTML в одной папке | Нарушает принцип единообразия |
| **P3** | Спецсимволы в именах | `In-depth analysis of ISO7816 -2- understand PPS.pdf` (пробелы), `SIM_презентация_RU.pdf` (кириллица) | Проблемы с CLI-тулзами и кросс-платформой |
| **P4** | Множественные версии | `ts_102221v170100p.pdf`, `ts_102221v170400p.pdf`, `ts_102221v180200p.pdf` — 3 версии лежат рядом | Неясно какая актуальная; Reviewer использует все три |
| **P5** | Нет разграничения источников | 3GPP, ETSI, GSMA, ISO, TCA — все перемешаны на верхнем уровне | Непонятно откуда что; SpecDownloader не знает где искать |
| **P6** | Два уровня под ETSI_3GPP | 9 подпапок по темам — но нет стандарта именования тем | При добавлении новой спецификации неясно в какую подпапку |
| **P7** | Нулевые файлы | `links.txt` (0 KB), `SIM_презентация_RU.pdf.md` (0 KB) — файлы-призраки | Захламляют; PyPDF2 падает на них |
| **P8** | Битые ссылки на PNG | `EPS-AKA_full-sec.png` в Security/ — не обрабатывается SpecExtractor | Исключение в пайплайне |

### 1.3 Naming Convention Analysis

Текущие паттерны имён (все разные):

| Паттерн | Пример | Стандарт? |
|---|---|---|
| `ts_NNNNNNvXXYYZZp.pdf` | `ts_102221v170100p.pdf` | ETSI — почти стандарт |
| `NNNNN-XXX.pdf` | `31213-730.pdf` | 3GPP archive |
| `gsmNN-NN.pdf` | `gsm11-11.pdf` | Legacy GSM |
| `SGP.XX-vX.X.pdf` | `SGP.02-v4.1.pdf` | GSMA |
| `tr_NNNNNNvXXYYZZp.pdf` | `tr_131919v070000p.pdf` | ETSI TR |
| `Organization_Document_vX.X.X.pdf` | `GPC_CardSpecification_v2.3.1.pdf` | Свободная форма |
| `Описание_на_русском.pdf` | `SIM_презентация_RU.pdf` | Кириллица |
| `Descriptive Name - with - dashes.pdf` | `In-depth analysis of ISO7816...` | Пробелы и дефисы |

---

## 2. Целевая архитектура (предложение)

### 2.1 Принципы проектирования

1. **По источнику на верхнем уровне** — 3GPP, GSMA, ISO, TCA, Misc разделены явно
2. **Единое именование** — `<ORG>_<TYPE>_<NUMBER>_<VERSION>.<ext>` для всех спецификаций
3. **Версионирование через подпапки** — `N.N/` для разных версий одной спецификации
4. **Самодокументированность** — `README.md` в каждой категории с таблицей содержимого
5. **Совместимость с spec-crawler** — структура `Specs/archive/` маппится напрямую

### 2.2 Предлагаемая структура

```
Specifications/
│
├── README.md                          ← Индекс: карта всех спецификаций
├── .index.json                        ← Машинный индекс для tooling'а
│
├── !INCOMING/                         ← Вход (ручной + spec-crawler)
├── !double/                           ← Дубликаты
│
├── 3GPP/                              ← Все 3GPP TS/TR (26 файлов + будущие)
│   ├── 31.101/                        ← UICC-Terminal Interface
│   │   ├── 18.0/                      ← Release 18
│   │   │   └── 3GPP_TS_31.101_18.0.0.pdf
│   │   └── INDEX.md                   ← Версии и их различия
│   │
│   ├── 31.102/                        ← USIM
│   │   ├── 17.0/                      ← Release 17 (текущий)
│   │   │   └── 3GPP_TS_31.102_17.10.0.pdf
│   │   ├── 19.0/                      ← Release 19 (новый, spec-crawler)
│   │   │   └── 3GPP_TS_31.102_19.4.0.docx
│   │   └── INDEX.md
│   │
│   ├── 31.111/                        ← USAT
│   ├── 31.121/                        ← USIM Conformance
│   ├── 31.124/                        ← USAT Conformance
│   ├── 31.130/                        ← JavaCard API (UICC)
│   ├── 33.102/                        ← Security: Generic Auth
│   ├── 33.401/                        ← EPS AKA
│   ├── 33.501/                        ← 5G AKA
│   ├── 35.206/                        ← MILENAGE test vectors
│   │
│   ├── GSM_11.11/                     ← Legacy GSM SIM
│   └── ... (остальные 3GPP TS/TR)
│
├── ETSI/                              ← ETSI-специфичные (не через 3GPP)
│   ├── 102.221/                       ← UICC Platform (3 версии)
│   │   ├── 17.0/
│   │   │   └── ETSI_TS_102.221_17.1.0.pdf
│   │   ├── 17.4/
│   │   │   └── ETSI_TS_102.221_17.4.0.pdf
│   │   ├── 18.2/
│   │   │   └── ETSI_TS_102.221_18.2.0.pdf
│   │   └── INDEX.md
│   │
│   ├── 102.223/                       ← CAT/STK
│   ├── 102.225/                       ← OTA Security
│   ├── 102.226/                       ← Remote APDU
│   ├── 102.241/                       ← UICC API
│   ├── 101.220/                       ← Numbering System
│   ├── 151.011/                       ← Legacy SIM (GSM 11.11 mirror)
│   ├── 151.014/                       ← STK Test
│   └── 151.017/                       ← SIM Test
│
├── GSMA/                              ← GSMA eSIM
│   ├── SGP.02/
│   │   └── 4.1/
│   │       └── GSMA_SGP.02_4.1.pdf
│   ├── eSIM_Whitepaper/
│   │   └── GSMA_eSIM_Whitepaper_1.0.pdf
│   └── LTE_UICC_Profile/
│       └── SIMalliance_LTE_UICC_Profile_1.0.pdf
│
├── ISO/                               ← ISO/IEC 7816
│   ├── 7816-1/  (ATR analysis)
│   ├── 7816-2/  (PPS analysis)
│   └── 7816-3/  (T=0 analysis)
│
├── GlobalPlatform/
│   └── Card_Spec/
│       └── 2.3.1/
│           └── GPC_CardSpec_2.3.1.pdf
│
├── TCA/                               ← Trusted Connectivity Alliance (JavaCard)
│   ├── Stepping_Stones_FINAL.pdf
│   ├── StepStones_Release6_v1.0.0.pdf
│   ├── StepStones_Release6.txt
│   └── JavaCard_3.0.5_API.html
│
├── Books/                             ← Без изменений (не спецификации)
├── Manuals/                           ← Без изменений
├── Papers/                            ← Без изменений
└── Tutorials/                         ← Без изменений
```

### 2.3 Стандарт именования

```
<ORG>_<TYPE>_<NUMBER>_<VERSION>.<ext>

Где:
  ORG     = 3GPP | ETSI | GSMA | ISO | GPC | TCA
  TYPE    = TS | TR | SGP | IS | WP (whitepaper)
  NUMBER  = dotted spec number (31.102, 102.221, SGP.02)
  VERSION = semver-like release (18.2.0, 4.1)

Примеры:
  3GPP_TS_31.102_17.10.0.pdf     ← USIM Release 17
  3GPP_TS_35.206_19.0.0.docx     ← MILENAGE vectors Release 19 (spec-crawler)
  ETSI_TS_102.221_18.2.0.pdf     ← UICC Platform Release 18
  GSMA_SGP.02_4.1.pdf            ← eSIM RSP
  GPC_CardSpec_2.3.1.pdf         ← GlobalPlatform Card
```

**Правила**: только ASCII, `_` вместо пробелов, dotted-номера с точкой, без спецсимволов.

### 2.4 Маппинг spec-crawler → директория

Spec-crawler checkout создаёт: `Specs/archive/<series>/<number>/`

| spec-crawler output | → | Target directory |
|---|---|---|
| `31_series/31.102/` | → | `3GPP/31.102/<release>/` |
| `33_series/33.102/` | → | `3GPP/33.102/<release>/` |
| `35_series/35.206/` | → | `3GPP/35.206/<release>/` |
| (н/д для ETSI 102.xxx) | → | `ETSI/102.221/<release>/` |

---

## 3. План миграции

### Фаза 1: Новые файлы (0 риска)

Все **новые** спецификации (через SpecDownloader) сразу класть в новую структуру:
- `spec-crawler checkout 35.206` → flatten в `3GPP/35.206/19.0/3GPP_TS_35.206_19.0.0.docx`
- Librarian использует новую логику flatten'а

### Фаза 2: Миграция 3GPP/ETSI (26 файлов)

| Старая директория | Файлы | → Новая |
|---|---|---|
| `ETSI_3GPP/USIM/` | 4 | → `3GPP/` + `ETSI/` |
| `ETSI_3GPP/UICC/` | 3 | → `ETSI/102.221/` |
| `ETSI_3GPP/CAT_STK/` | 3 | → `ETSI/` |
| `ETSI_3GPP/OTA/` | 3 | → `ETSI/` |
| `ETSI_3GPP/Security/` | 4 | → `3GPP/` (33.xxx) |
| `ETSI_3GPP/Test_Conformance/` | 4 | → `3GPP/` (31.xxx) + `ETSI/` (151.xxx) |
| `ETSI_3GPP/UICC_API/` | 3 | → `3GPP/` + `ETSI/` |
| `ETSI_3GPP/GSM_Legacy/` | 2 | → `3GPP/GSM_11.11/` + `ETSI/151.011/` |
| `ETSI_3GPP/Numbering/` | 1 | → `ETSI/101.220/` |

**Общий принцип маппинга**:
- 2x.xxx и 3x.xxx номера → `3GPP/` (это 3GPP-спецификации)
- 1xx.xxx номера → `ETSI/` (это ETSI-спецификации, даже если зеркалятся на 3GPP FTP)
- GSM 11.11 → `3GPP/GSM_11.11/` (исторически 3GPP)

### Фаза 3: Миграция не-3GPP (13 файлов)

| Старая директория | → Новая |
|---|---|
| `eSIM/` | → `GSMA/` (+ Whitepaper → подпапка) |
| `GlobalPlatform/` | → `GlobalPlatform/Card_Spec/2.3.1/` |
| `ISO7816_Analysis/` | → `ISO/` |
| `JavaCard/` | → `TCA/` |

### Фаза 4: Очистка

- Удалить нулевые файлы (`links.txt`, `SIM_презентация_RU.pdf.md`)
- Переместить `EPS-AKA_full-sec.png` в `wiki/` или `outputs/` (это не спецификация)
- Удалить пустую `ETSI_3GPP/` директорию после миграции
- Обновить все wikilinks `[[Specifications/...]]` → новые пути

### Фаза 5: Создать README.md и .index.json

```markdown
# 3GPP/31.102/INDEX.md

## TS 31.102 — USIM (Universal Subscriber Identity Module)

| Release | Version | Date | File | Source |
|---|---|---|---|---|
| 17 | 17.10.0 | 2023-09 | 3GPP_TS_31.102_17.10.0.pdf | Manual |
| 19 | 19.4.0 | 2025-12 | 3GPP_TS_31.102_19.4.0.docx | spec-crawler |
```

---

## 4. Влияние на другие компоненты

| Компонент | Что изменится |
|---|---|
| **Librarian** | Новая таблица маппинга: номер спецификации → директория (3GPP vs ETSI vs GSMA) |
| **SpecExtractor** | Путь к PDF вычисляется из номера спецификации, а не grep'ом |
| **Reviewer** | `specs-extracted/` повторяет новую структуру |
| **wikilinks** | `[[Specifications/3GPP/31.102/17.0/3GPP_TS_31.102_17.10.0.pdf]]` вместо `[[Specifications/ETSI_3GPP/USIM/ts_131102v171000p.pdf]]` |
| **Author** | Ссылается на спецификации по новой схеме |
| **!INCOMING pipeline** | Flatten маппит `Specs/archive/31_series/31.102/` → `3GPP/31.102/<release>/` |

---

## 5. Оценка усилий

| Фаза | Файлов | Время | Риск |
|---|---|---|---|
| 1: Новые файлы | ∞ | 0 (встроено в Librarian) | Нет |
| 2: 3GPP/ETSI миграция | 26 | 15 мин | Низкий (wikilinks сломаются) |
| 3: Не-3GPP миграция | 13 | 5 мин | Низкий |
| 4: Очистка | 3 | 2 мин | Нет |
| 5: README.md + .index.json | — | 10 мин | Нет |
| **Итого** | **42** | **~30 мин** | + время на обновление wikilinks |

---

## 6. Рекомендация

**Начать с Фазы 1 (новые файлы)** — это бесплатно и сразу даёт выгоду:
- SpecDownloader → `!INCOMING/` → Librarian flatten в `3GPP/N.N/REL/`
- Не трогает существующие файлы и wikilinks
- Все новые спецификации сразу в правильной структуре

**Фазы 2-5 отложить** до момента когда:
- Docling-миграция завершена (меньше хождений туда-сюда)
- Есть скрипт для батч-обновления wikilinks (сейчас 129 страниц ссылаются на старые пути)
- Пользователь подтвердил что готов к реструктуризации

---

*Анализ создан 2026-06-12. Структура проверена на 65 файлах.*
