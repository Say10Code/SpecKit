---
tags: [ISO7816, ATR, PPS, T0, deep-dive, summary]
sources:
  - "[[Specifications/ISO7816_Analysis/ISO7816-1_ATR_analysis.pdf]]"
  - "[[Specifications/ISO7816_Analysis/ISO7816-2_PPS_analysis.pdf]]"
  - "[[Specifications/ISO7816_Analysis/ISO7816-3_T0_analysis.pdf]]"
type: analysis
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# ISO 7816 In-Depth Analysis — Углублённый анализ (серия !recheck)

> **Статус извлечения**: PDF-файлы защищены (не извлекаются через PyPDF2/pikepdf). Требуется ручной анализ или OCR.
> **Помечены**: `!recheck` — запланированы на Фазу 2.

## Состав серии

| # | Файл | Тема | Стр. |
|---|---|---|---|
| 1 | ISO7816-1 analysis... ATR | Reset, Character Frame, ATR | 12 |
| 2 | ISO7816-2 analysis... PPS | PPS (Protocol and Parameter Selection) | 4 |
| 3 | ISO7816-3 analysis... T0 | T=0 протокол | 5 |

## Ожидаемое содержание (на основе названий)

### 1. ISO 7816-1: Reset, Character Frame, ATR
— Детальный анализ холодного и тёплого сброса (Cold/Warm Reset)
— Структура Character Frame: стартовый бит, биты данных, parity, guard time
— ATR (Answer To Reset) — структура байтов:
  - TS (Initial Character): `0x3B` (direct) / `0x03F` (inverse)
  - T0 (Format Byte): маска TAi/TBi/TCi/TDi + K (historical bytes count)
  - Interface Bytes: Fi/Di, Extra Guard Time, Protocol Type
  - Historical Bytes: идентификация карты
  - TCK (Check Byte): XOR checksum

### 2. ISO 7816-2: PPS
— Protocol and Parameter Selection
— Согласование скорости после ATR
— Структура PPS: PPSS (`0xFF`) + PPS0 + PPS1 (Fi/Di) + PPS2 (spare) + PCK
— Когда PPS нужен, а когда нет

### 3. ISO 7816-3: T=0
— Байт-ориентированный полудуплексный протокол
— Procedure Bytes: ACK, NULL, SW1 (`60xx`, `61xx`, `6Cxx`, `90 00`)
— Обработка ошибок: parity check, retransmission
— Case 1-4 APDU в T=0
— GET RESPONSE для Case 2/4

## Текущий статус знаний по ISO 7816

Имеющиеся концепты wiki/ покрывают эти темы:
- [[wiki/concepts/ATR]] — ATR и PPS
- [[wiki/concepts/Transmission_Protocols]] — T=0 и T=1
- [[wiki/entities/ISO7816]] — стандарт ISO/IEC 7816

## План действий

1. Попробовать альтернативные PDF-ридеры (pdfminer, OCR)
2. При невозможности извлечения — использовать другие источники:
   - ISO/IEC 7816-3 (публичная спецификация)
   - ETSI TS 102 221 (адаптирует ISO 7816 для UICC)
   - Smart Card Tutorial ([[wiki/summaries/smart_card_tutorial]])
3. Обновить wiki/concepts/ATR и concepts/Transmission_Protocols с более глубокими деталями

## Связи

- ATR/PPS: [[wiki/concepts/ATR]]
- T=0/T=1: [[wiki/concepts/Transmission_Protocols]]
- Базовый стандарт: [[wiki/entities/ISO7816]]
- UICC-адаптация: [[wiki/summaries/ts_102221]]
