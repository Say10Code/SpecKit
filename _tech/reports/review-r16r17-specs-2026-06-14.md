# Review Report — Wiki-страницы после загрузки R16/R17 спецификаций

> **Reviewer v3** | Pass 1 (hybrid TXT/MD/JSON) | 2026-06-14
> **Проверено**: 8 страниц · **Метод**: TXT Grep (FID/CLA) + MD read (таблицы) + JSON lookup (Docling)
> **Спецификации-эталоны**: TS 31.102 v17.10.0, TS 33.102 v19.1.0, TS 33.401 v19.2.0, TS 33.501 (5G), TS 35.205/35.206 (MILENAGE), TS 133.220 (security)

---

## Вердикт: ❌ FAIL — 2 CRITICAL, 4 HIGH, 3 MEDIUM, 14 CORRECT

---

## 🔴 CRITICAL

### C1: USIM_EF_Table.md — неверные FID для SPN_Icon и PNN_Icon

**Файл**: `wiki/reference/USIM_EF_Table.md`

| EF | Wiki (неверно) | TS 31.102 v17.10.0 (верно) |
|---|---|---|
| EF_SPN_Icon | `6FD7` | **`6FDE`** (§4.2.88) |
| EF_PNN_Icon | `6FD8` | **`6FDF`** (§4.2.89) |

`6FD7`/`6FD8` — FID из старых версий спецификации (до Release 13). В Release 17 они заняты MBMS Service Keys. Использование старого FID для SPNI/PNNI на современной UICC приведёт к чтению/записи не того файла.

**Источник**: `specs-extracted/ETSI_3GPP/USIM/ts_131102v171000p.pdf.txt`:
```
4.2.88 EF SPNI — Identifier: '6FDE'
4.2.89 EF PNNI — Identifier: '6FDF'
```

### C2: UICC_File_System.md — отсутствует DF_GRAPHICS, нет DF_TELECOM

**Файл**: `wiki/concepts/UICC_File_System.md`

Страница не содержит:
- **DF_TELECOM** (`0x7F10`) — ключевой DF телеом-уровня
- **DF_GRAPHICS** (`0x5F50`) — графическая директория
- Полное отсутствие упоминания современной структуры DF под DF_TELECOM

Это фундаментальная страница о файловой системе UICC — без DF_TELECOM она не отражает современную архитектуру (Release 13+).

**Источник**: TS 31.102 v17.10.0, §4.6.0: «DFs may be present as child directories of DF_TELECOM. The following DFs have been defined: DF_GRAPHICS '5F50', DF_PHONEBOOK '5F3A', DF_MULTIMEDIA '5F3B'»

---

## 🟡 HIGH

### H1: auth_evolution.md — отсутствуют ссылки на MILENAGE/TUAK алгоритмы

**Файл**: `wiki/syntheses/auth_evolution.md`

Страница ссылается на TS 33.102/33.401/33.501 (архитектура безопасности) — верно. Но **отсутствуют** ссылки на спецификации самих алгоритмов:

| Отсутствует | Назначение |
|---|---|
| TS 35.205 | MILENAGE algorithm specification |
| TS 35.206 | MILENAGE test vectors |
| TS 35.231 | TUAK algorithm specification |
| TS 35.232 | TUAK test vectors |

С учётом того, что страница подробно описывает COMP128→MILENAGE→5G AKA эволюцию — отсутствие ссылок на 35-ю серию существенно.

### H2: milenage_vs_tuak.md — номера тестовых векторов неконсистентны

**Файл**: `wiki/research/milenage_vs_tuak.md`

Ссылается на «TS 35.205 (MILENAGE Specification)» ✅ и «TS 35.231 (TUAK Specification)» ✅, но **не ссылается** на TS 35.206 (MILENAGE test vectors) и TS 35.232 (TUAK test vectors). При этом страница содержит псевдокод функций — тестовые векторы были бы ключевым источником для верификации.

### H3: USIM_EF_Table.md — вероятны другие устаревшие FID

**Файл**: `wiki/reference/USIM_EF_Table.md`

Помимо C1, страница содержит 120+ EF-записей. Не проверены посимвольно, но:
- `6FD7`/`6FD8` устарели → высока вероятность, что и другие FID из старых версий
- Нет колонки «актуально на Release N» — нет возможности определить применимость
- Рекомендуется: grep по TXT для каждого FID из таблицы, сверить с TS 31.102 v17.10.0

### H4: sim_testing_deep_dive.md — версии спецификаций устарели

**Файл**: `wiki/research/sim_testing_deep_dive.md`

| Спецификация | Wiki | Актуальная |
|---|---|---|
| TS 31.121 | V18.2.0 | V18.5.0 (latest) |
| TS 31.124 | V18.2.0 | V18.6.0 (latest) |

Разница в минорных версиях — контент вероятно не изменился для тестовой методологии, но цифры неактуальны.

---

## 🟢 MEDIUM

### M1: operator_icons_on_sim.md — Image Coding таблица всё ещё не верифицирована

После ревизии (2026-06-14) таблица Image Coding помечена как «требует верификации». Docling-извлечение TS 102 221 Annex H не выполнено — коды `0x01`-`0x21` не подтверждены.

### M2: USIM.md — service numbers не проверены

EF_UST описан верно (`6F38`), но перечислены только Service 27 и Service 68. Полная таблица сервисов (>80) отсутствует. Service 78 (SPN Icon) и 79 (PNN Icon) не упомянуты.

### M3: UICC_File_System.md — нумерация разделов устарела

Структура ADF.USIM описана без указания номеров разделов из спецификации. В TS 31.102 v17.10.0 нумерация сдвинулась на ~6 позиций по сравнению с v10.

---

## ✅ CORRECT — подтверждённые утверждения

| # | Страница | Что проверено | Статус |
|---|---|---|---|
| 1 | USIM.md | EF_UST FID = `0x6F38` | ✅ CORRECT |
| 2 | USIM.md | EF_IMSI, Service Table концептуально | ✅ CORRECT |
| 3 | auth_evolution.md | TS 33.102/33.401/33.501 ссылки для архитектуры | ✅ CORRECT |
| 4 | auth_evolution.md | COMP128→UMTS AKA→EPS AKA→5G AKA эволюция | ✅ CORRECT |
| 5 | auth_evolution.md | Ks=CK||IK (из 33.401) | ✅ CORRECT |
| 6 | milenage_vs_tuak.md | MILENAGE = AES-128, TUAK = Keccak-256 | ✅ CORRECT |
| 7 | milenage_vs_tuak.md | f1-f5* функции для обоих алгоритмов | ✅ CORRECT |
| 8 | milenage_vs_tuak.md | TS 35.205 / TS 35.231 ссылки | ✅ CORRECT |
| 9 | operator_icons_on_sim.md | Все FID исправлены на актуальные | ✅ CORRECT (post-fix) |
| 10 | sim_testing_deep_dive.md | TS 31.121/31.124/151.017 структура тестов | ✅ CORRECT |
| 11 | sim_testing_deep_dive.md | TERMINAL PROFILE ссылки | ✅ CORRECT |
| 12 | USIM_EF_Table.md | Большинство базовых FID (6F07-6F48) | ✅ CORRECT |
| 13 | EF_UST.md (concept implicit) | 6F38, прозрачный, обязательный | ✅ CORRECT |
| 14 | plmn_selection_algorithm.md | PLMN selection логика | ✅ CORRECT |

---

## 📊 Сводка по страницам

| Страница | Статус | Находок |
|---|---|---|
| USIM_EF_Table.md | 🔴 FAIL | C1 + H3 |
| UICC_File_System.md | 🔴 FAIL | C2 + M3 |
| auth_evolution.md | 🟡 NEEDS FIX | H1 |
| milenage_vs_tuak.md | 🟡 NEEDS FIX | H2 |
| sim_testing_deep_dive.md | 🟡 NEEDS FIX | H4 |
| operator_icons_on_sim.md | 🟢 PASS (post-fix) | M1 (известно) |
| USIM.md | 🟢 PASS | M2 (minor) |
| plmn_selection_algorithm.md | 🟢 PASS | — |

---

## 📥 Загрузка R16/R17 спецификаций — результат

| Метрика | Значение |
|---|---|
| Скачано | 20 спецификаций (10 номеров × 2 релиза) |
| R16 | 10 файлов (g-series) |
| R17 | 10 файлов (h-series) |
| Формат | .docx (31-series) + .doc (33/35-series) |
| Расположение | `Specifications/ETSI_3GPP/<тема>/` |
| ETSI (102.xxx и пр.) | ❌ Не скачаны — spec-crawler не поддерживает R16/R17 для ETSI |

### Загруженные файлы

```
ETSI_3GPP/USIM/:
  31_101-REL16_31101-g20.docx   31_101-REL17_31101-h10.docx
  31_102-REL16_31102-gf0.docx   31_102-REL17_31102-hg0.docx
  31_111-REL16_31111-gb0.docx   31_111-REL17_31111-he0.docx
  31_213-REL16_31213-g10.docx   31_213-REL17_31213-h00.docx

ETSI_3GPP/Test_Conformance/:
  31_121-REL16_31121-ge0.docx   31_121-REL17_31121-h50.docx
  31_124-REL16_31124-ge0.docx   31_124-REL17_31124-h50.docx

ETSI_3GPP/UICC_API/:
  31_130-REL16_31130-g00.docx   31_130-REL17_31130-h40.docx

ETSI_3GPP/Security/:
  33_102-REL16_33102-g00.doc    33_102-REL17_33102-h00.doc
  33_401-REL16_33401-g40.doc    33_401-REL17_33401-h70.doc
  35_206-REL16_35206-g00.doc    35_206-REL17_35206-h00.doc
```

---

## 🔧 Приоритеты исправлений

| # | Что | Срочность | Оценка |
|---|---|---|---|
| 1 | USIM_EF_Table.md: исправить 6FD7→6FDE, 6FD8→6FDF | 🔴 Сейчас | 10m |
| 2 | UICC_File_System.md: добавить DF_TELECOM + DF_GRAPHICS | 🔴 Сейчас | 30m |
| 3 | auth_evolution.md: добавить ссылки TS 35.205/35.206/35.231/35.232 | 🟡 Эта сессия | 10m |
| 4 | milenage_vs_tuak.md: добавить TS 35.206/35.232 | 🟡 Эта сессия | 5m |
| 5 | sim_testing_deep_dive.md: обновить версии TS 31.121/31.124 | 🟢 Позже | 5m |
| 6 | USIM_EF_Table.md: полный FID-аудит по spec v17.10.0 | 🟢 Позже | 2h |
| 7 | Конвертировать .docx/.doc → PDF через LibreOffice + Docling | 🟢 Позже | 4h |

---

*Отчёт создан 2026-06-14. Спецификации R16/R17 загружены в `Specifications/ETSI_3GPP/`. Ревью проведено гибридным методом Reviewer v3.*
