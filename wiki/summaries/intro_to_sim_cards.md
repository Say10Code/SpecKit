---
tags: [GSM, SIM, tutorial, summary]
source: "[[Specifications/Books/Introduction_to_SIM_Cards.pdf]]"
type: tutorial
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# Introduction to SIM Cards (2007)

> **Дата**: 20 сентября 2007
> **Страниц**: 64

## Обзор

Базовое введение в SIM-карты. Охватывает архитектуру GSM-сети, роль SIM, стандарт GSM 11.11, и типы SIM-приложений. Несмотря на возраст, остаётся полезным как исторический фундамент — особенно для понимания эволюции SIM→USIM. ^[inferred]

## Ключевые разделы

### 1. Обзор GSM-сетей
- GSM = Global System for Mobile communication
- Элементы сети: MS (ME + SIM), BSS (BTS + BSC), Core (HLR/VLR/AUC/EIR/MSC)

### 2. SIM в GSM
- **Идентификация**: IMSI — уникальный идентификатор абонента
- **Аутентификация**: Ki (секретный ключ) + RAND → SRES + Kc
- **Хранение данных**: телефонная книга, SMS, PLMN-списки
- SIM = ROM (OS) + EEPROM (данные) + CPU

### 3. GSM 11.11
Стандарт, определяющий:
- Файловую систему SIM (MF/DF/EF)
- Формат APDU-команд
- Интерфейс SIM-ME

### 4. Типы приложений
- **Anti-Cloning** — защита от клонирования
- **Local Applications** — локальная обработка (SMS-сервисы)
- **Point-to-Point Applications** — обмен данными с сетью

### 5. Производство SIM
- Input file → Data Generation → Personalization → Output file
- IMSI, ICCID, Ki генерируются оператором
- Transport Key для защищённой персонализации

## Актуальность

Материал 2007 года: GSM-центричный (нет 3G/4G), но ценен как введение в концепции, которые лежат в основе [[wiki/concepts/UICC]].

## Связи

- UICC: [[wiki/concepts/UICC]]
- Более новый учебник: [[wiki/summaries/sim_cards_thesis]]
- GSM 11.11: `[[Specifications/ETSI_3GPP/GSM_Legacy/gsm11-11.pdf]]`
