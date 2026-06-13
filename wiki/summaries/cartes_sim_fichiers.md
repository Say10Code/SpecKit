---
tags: [SIM, French, academic, CNAM, summary]
source: "[[Specifications/Tutorials/CartesSIM_Fichiers_Anglais.pdf]]"
type: slides
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# Cartes SIM/USIM — Fichiers (Samia Bouzefrane, CNAM)

> **Автор**: Samia Bouzefrane, CEDRIC Lab, CNAM (Paris)
> **Формат**: 49 слайдов на французском
> **Темы**: GSM-сеть, SIM-карты, файловая система, безопасность

## Обзор

Академические слайды курса CNAM по SIM/USIM-картам. На французском языке. Охватывают: введение в GSM, архитектуру SIM, файловую систему, сервисы SIM, безопасность. Полезны как педагогический материал — упрощённое объяснение сложных тем. ^[inferred]

## Ключевые темы

### 1. GSM-сеть (слайды 1-15)
- Эволюция GSM (1982 → 1991)
- Архитектура: BTS → BSC → MSC → HLR/VLR/AUC
- Идентификация: IMSI, TMSI, MSISDN
- Аутентификация: RAND → COMP128 → SRES + Kc

### 2. SIM-карты (слайды 16-28)
- Форм-факторы: ID-1, Plug-in, Mini-UICC
- Физические характеристики ISO 7816
- ATR и PPS
- Файловая система: MF/DF/EF
- Команды: SELECT, READ BINARY, UPDATE BINARY, READ RECORD...

### 3. Файловая система (слайды 29-38)
- MF (3F00) как корень
- DF_GSM (7F20) и DF_TELECOM (7F10)
- EF с фиксированными FID
- Типы файлов: Transparent, Linear Fixed, Cyclic

### 4. Сервисы SIM (слайды 39-43)
- SMS-хранение
- Телефонная книга (ADN, FDN)
- STK-меню
- OTA-обновление

### 5. Безопасность (слайды 44-49)
- CHV1/CHV2 (PIN1/PIN2)
- Аутентификация GSM
- COMP128 алгоритм
- Ключи Ki, Kc

## Ценность для проекта

Французский материал, но структурирован и педагогичен. Дополняет [[wiki/summaries/intro_to_sim_cards|Intro to SIM Cards (2007)]] как альтернативный взгляд на те же темы.

## Связи

- UICC: [[wiki/concepts/UICC]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
- GSM 11.11: [[wiki/summaries/gsm_1111]]
- Введение в SIM: [[wiki/summaries/intro_to_sim_cards]]
