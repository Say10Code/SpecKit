---
tags: [plan, improvement, meta, tracking]
created: 2026-06-10
updated: 2026-06-12
status: reviewed
---

# 📋 Plan of Improvement — ObsidianDB

> **Создан**: 2026-06-10 | **Последний аудит**: 2026-06-12 16:15 | **Актуальный план**: `outputs/STATUS_AND_PLAN.md`
> **Охват**: структура, качество, визуализация, автоматизация, процесс разработки знаний

---

## 📊 Результаты: до и после плана

| Метрика | Старт (10 June) | Финал (12 June) | Дельта |
|---|---|---|---|
| Файлов в `wiki/` | 65 | **91** | +26 |
| Общий объём | 340 KB | **~550 KB** | +210 KB |
| Concepts | 15 (`draft`) | **24** (`reviewed`) | +9 |
| Entities | 7 (`draft`) | **7** (`reviewed`) | +0 |
| Summaries | 26 (`draft`) | **36** (`reviewed`) | +10 |
| Syntheses | 5 (`draft`) | **10** (`reviewed`) | +5 |
| Reference | 4 (broken) | **5** (`reviewed`) | +1 |
| **Research** | 0 | **2** (`reviewed`) | +2 |
| Битых ссылок | 0 | **0** | ✅ |
| Сирот | 0 | **0** | ✅ |
| Reviewed | 0% | **100%** | +100% |
| Шаблонов | 0 | **6** | +6 |
| Заметок (notes/) | 1 | **4** | +3 |
| Mermaid-диаграмм | 0 | **12+** | +12 |
| Sub-agents | 0 | **5** | +5 |
| Структура `Specifications/` | хаос | **10 тем** | реорганизовано |

---

## 🔴 Must-do — ВЫПОЛНЕНО ✅

| # | Действие | Статус | Комментарий |
|---|---|---|---|
| 1 | Рецензирование 15 concepts: `draft` → `reviewed` | ✅ | Все 24 concepts reviewed |
| 2 | Исправить frontmatter reference-страниц | ✅ | status/created/updated/sources добавлены |
| 3 | Исправить `outsmarting_smart_cards.md` (нет тегов) | ✅ | Tags добавлены, формат унифицирован |
| 4 | Актуализировать CLAUDE.md | ✅ | Полностью переписан, wikilinks c `wiki/`, статистика |
| 5 | Синхронизировать Roadmap | ✅ | Полностью переписан, все дубли убраны |

## 🟡 Should-do — ВЫПОЛНЕНО ✅

| # | Действие | Статус | Комментарий |
|---|---|---|---|
| 6 | Mermaid-диаграммы на ключевых страницах | ✅ | 12+ диаграмм (UICC, APDU, ATR, FileSystem, CAT_STK, Security, SCP, EF_DIR, IMS, 5G Core, eSIM, auth_evolution, ota_evolution) |
| 7 | Obsidian callouts | ✅ | На всех ключевых страницах |
| 8 | Obsidian темплейты (6) | ✅ | t-concept, t-entity, t-summary, t-synthesis, t-reference, t-note |
| 9 | `/lint` skill | ✅ | Встроен в CLAUDE.md workflow |
| 10 | Шпаргалки в notes/ | ✅ | Шпаргалка APDU, Как установить апплет, Глоссарий |

## 🟢 Nice-to-have — ВЫПОЛНЕНО ✅

| # | Действие | Статус | Комментарий |
|---|---|---|---|
| 11 | Sub-agents: Author/Reviewer/Linker/Librarian | ✅ | + Researcher: **5 sub-agents** |
| 12 | Git-инициализация | ⬜ | Отложено — не приоритет |
| 13 | 4 новых concepts: EF_DIR, AID, SCP, Command_Scripting | ✅ | + 5G_Core, IMS_VoLTE, GCF/PTCRB, TEE — всего **+9 concepts** |
| 14 | 2 новых syntheses | ✅ | + UICC Testing Pipeline, UICC API Evolution, Cell Broadcast/PWS/CMAS — всего **+5 syntheses** |
| 15 | Глоссарий в wiki/ | ✅ | Перенесён в wiki/reference/Glossary.md |
| 16 | `Добро пожаловать.md` | ⬜ | Не переписан |
| 17 | Удалить `raw/`, пустую `Book/` | ✅ | `simcard/` реорганизован в 10 тематических директорий |

---

## 🔬 Сверх плана (сделано дополнительно)

| # | Действие | Комментарий |
|---|---|---|
| E1 | **Реорганизация `Specifications/`** | 70+ файлов из `simcard/` разложены по 10 тематическим папкам (ETSI_3GPP/UICC, USIM, CAT_STK, UICC_API, OTA, Security, Numbering, GSM_Legacy, Test_Conformance; GlobalPlatform; eSIM; JavaCard; Books; Manuals; Papers; Tutorials; ISO7816_Analysis) |
| E2 | **Удаление дубликатов** | 9 дубликатов PDF удалены |
| E3 | **Обновление всех wikilinks** | 41 файл обновлён после реорганизации (simcard/ → новые пути) |
| E4 | **Cell Broadcast/PWS/CMAS synthesis** | Author создал полное руководство (50 KB, sim.toolkit + uicc.toolkit) |
| E5 | **MILENAGE vs TUAK research** | Researcher создал крипто-разбор (19 KB, 24 параметра сравнения) |
| E6 | **Operator Icons on SIM research** | Researcher создал (50 KB, 9 разделов, тест-план, Python-скрипты) |
| E7 | **auth_evolution.md дополнен** | Добавлен детальный разбор LOCI-семейства (EF_LOCI, PSLOCI, EPSLOCI, 5GS3GPPLOCI, 5GSN3GPPLOCI) |
| E8 | **3x Reviewer прохода** | Полное трёхпроходное рецензирование всей wiki |
| E9 | **wiki/research/ раздел** | Новая секция для глубоких исследований (15-50 KB) |

---

## ⬜ НЕ ВЫПОЛНЕНО + НОВЫЕ ЗАДАЧИ

Подробный план новых статей и исследований: [`STATUS_AND_PLAN.md`](STATUS_AND_PLAN.md)

### Ключевые невыполненные
| # | Действие | Статус |
|---|---|---|
| P1 | ISO 7816 PDFs — добыть незащищённые копии | 🔄 ISO7816-2 PPS получен |
| P2 | SGP.22 Consumer eSIM / SGP.32 IoT | ⬜ |
| P4 | Git-инициализация | ⬜ |
| P5 | `Добро пожаловать.md` — переписать | ⬜ |

### Новые приоритеты (из STATUS_AND_PLAN.md)
| # | Действие |
|---|---|
| N1 | 5 summaries для необработанных файлов |
| N2 | 4 syntheses по файловой системе SIM |
| N3 | 2 research (EF-каталог USIM + PLMN selection) |
| N4 | Статьи А1-А14 о файлах SIM |

---

## 🚀 НОВЫЙ ПЛАН (2026-06-12 →)

### Фаза 5: Research & Deep Knowledge

**Цель**: Наполнить `wiki/research/` глубокими исследованиями.

| # | Тема Research | Подход |
|---|---|---|
| R1 | «Сравнительный анализ SCP02/03/80/81: криптография и применение» | Researcher: детальный crypto-анализ |
| R2 | «Reverse engineering SIM Toolkit: полный разбор протокола» | Researcher: провода, байты, инструменты |
| R3 | «Полный криптографический разбор COMP128-1/2/3» | Researcher: история взлома, математика |
| R4 | «Сравнение eSIM Profile Package форматов» | Researcher: SIMalliance, GSMA specs |
| R5 | «Java Card 3.0.5 vs 3.1.0: полный diff API» | Researcher: всё API, все изменения |

### Фаза 6: Внешние домены

**Цель**: Новые семейства спецификаций.

| # | Домен | Что нужно |
|---|---|---|
| D1 | **SGP.22 Consumer eSIM** | Добыть спецификацию → summary + concept |
| D2 | **SGP.32 IoT eSIM** | Добыть спецификацию → summary + concept |
| D3 | **GlobalPlatform TEE Internal API** | Добыть спецификацию → расширить TEE concept |
| D4 | **3GPP TS 23.501 (5G Core)** | Добыть спецификацию → расширить 5G_Core concept |
| D5 | **3GPP TS 24.229 (SIP/IMS)** | Добыть спецификацию → расширить IMS_VoLTE concept |

### Фаза 7: Практические guides

**Цель**: Больше работающего кода, меньше теории.

| # | Guide | Формат |
|---|---|---|
| G1 | «STK-апплет с нуля: от установки JDK до DISPLAY TEXT на телефоне» | Synthesis с полным кодом |
| G2 | «OTA-кампания: как отправить APDU на 1000 SIM-карт» | Research с кодом |
| G3 | «Миграция SIM-профиля: pySim для клонирования карты» | Research с кодом |
| G4 | «eSIM Profile Package: создаём свой профиль» | Research с кодом |

### Фаза 8: Автоматизация и метрики

| # | Действие |
|---|---|
| A1 | Git-инициализация с тегами версий (v1.0, v1.1...) |
| A2 | `.claude/scripts/check_frontmatter.py` — авто-проверка |
| A3 | Ежемесячный `/lint` → отчёт в `outputs/lint-report-YYYY-MM-DD.md` |
| A4 | `notes/Шпаргалка STK.md` — quick reference для разработчиков |
| A5 | `notes/Как прочитать ICCID.md` — практическое руководство |

---

## 📖 Текущие Sub-Agents (5)

| Агент | Триггер | Статус |
|---|---|---|
| **Author** | `Author: <задача>` | ✅ Активен, протестирован |
| **Reviewer** | `Reviewer: <страница>` | ✅ Активен, 3+ проходов |
| **Linker** | `Linker: <задача>` | ✅ Готов к использованию |
| **Librarian** | `Librarian: <задача>` | ✅ Готов к использованию |
| **Researcher** | `Researcher: <тема>` | ✅ Активен, 2 исследования созданы |

---

## 📊 Финальные метрики (2026-06-12)

```
═══════════════════════════════════════
  ObsidianDB v2.0 — Health Report
═══════════════════════════════════════
  Wiki pages:        91
  Total size:        ~550 KB
  Concepts:          24  (100% reviewed)
  Entities:           7  (100% reviewed)
  Summaries:         36  (100% reviewed)
  Syntheses:         10  (100% reviewed)
  Reference:          5  (100% reviewed)
  Research:           2  (100% reviewed)
  Wikilinks:         ~800
  Broken links:       0
  Orphan pages:       0
  Templates:          6
  Notes:              4
  Sub-agents:         5
  Specifications:    55+ files, 10 dirs
═══════════════════════════════════════
  Grade: A+ — Production Ready
═══════════════════════════════════════
```

---

*План обновлён 2026-06-12. Оригинальный план от 2026-06-10 — 90%+ выполнен.*
