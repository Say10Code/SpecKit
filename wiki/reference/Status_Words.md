---
tags: [reference, APDU, SW1SW2, table]
type: reference
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_102221]]"
  - "[[wiki/summaries/gsm_1111]]"
  - "[[wiki/concepts/APDU]]"
---

# Status Words (SW1 SW2) — Коды ответов APDU

Пара байт `SW1 SW2` возвращается UICC в каждом Response APDU. Источник: ETSI TS 102 221 §10.2, ISO 7816-4.

## Нормальное завершение

| SW1 SW2 | Категория | Значение |
|---|---|---|
| `90 00` | Normal | OK — команда выполнена успешно |
| `91 XX` | Normal | Proactive command pending (CAT), XX = длина команды |
| `9F XX` | Normal | XX байт данных доступны (GET RESPONSE) |
| `61 XX` | Normal | XX байт данных доступны (T=0 GET RESPONSE) |
| `62 00` | Warning | No information given |
| `62 81` | Warning | Часть данных повреждена |
| `62 82` | Warning | Конец файла/записи до чтения Le байт |
| `62 83` | Warning | Выбранный файл invalidated |
| `62 84` | Warning | FCI не отформатирован по ISO |
| `63 00` | Warning | Аутентификация провалена |
| `63 CX` | Warning | Проверка не удалась, осталось X попыток |
| `63 81` | Warning | Файл полон (для EF_LND) |
| `64 00` | Execution Error | Состояние non-volatile памяти не изменилось |
| `65 00` | Execution Error | Состояние non-volatile памяти изменилось |
| `65 81` | Execution Error | Memory failure |
| `66 00` | Security | Зарезервировано для security-related |
| `67 00` | Checking Error | Wrong length (Lc или Le) |

## Checking Errors

| SW1 SW2 | Категория | Значение |
|---|---|---|
| `68 00` | Checking | Функции в CLA не поддерживаются |
| `68 81` | Checking | Logical channel не поддерживается |
| `68 82` | Checking | Secure messaging не поддерживается |
| `69 00` | Checking | Command not allowed |
| `69 81` | Checking | Command incompatible with file structure |
| `69 82` | Checking | Security status not satisfied |
| `69 83` | Checking | Authentication method blocked |
| `69 84` | Checking | Referenced data invalidated |
| `69 85` | Checking | Conditions of use not satisfied |
| `69 86` | Checking | Command not allowed (no current EF) |
| `69 87` | Checking | Expected SM data objects missing (ISO 7816-4) |
| `69 88` | Checking | SM data objects incorrect (ISO 7816-4) |

## Checking Errors (продолжение)

| SW1 SW2 | Категория | Значение |
|---|---|---|
| `6A 00` | Checking | Wrong parameters P1-P2 |
| `6A 80` | Checking | Incorrect parameters in the data field |
| `6a 81` | Checking | Function not supported |
| `6A 82` | Checking | **File not found** ⭐ |
| `6A 83` | Checking | Record not found |
| `6A 84` | Checking | Not enough memory space in file |
| `6A 85` | Checking | Lc inconsistent with TLV structure |
| `6A 86` | Checking | Incorrect parameters P1-P2 |
| `6A 87` | Checking | Lc inconsistent with P1-P2 |
| `6A 88` | Checking | **Referenced data not found** ⭐ |
| `6A 89` | Checking | File already exists |
| `6A 8A` | Checking | DF name already exists |
| `6B 00` | Checking | Wrong parameters P1-P2 (offset outside EF) |
| `6C XX` | Checking | Wrong Le; XX = exact length ⭐ |
| `6D 00` | Checking | Instruction code not supported or invalid |
| `6E 00` | Checking | **Class not supported** ⭐ |
| `6F 00` | Checking | No precise diagnosis |

## Application Errors

| SW1 SW2 | Значение |
|---|---|
| `90 01` | Transport key not verified |
| `90 02` | Card terminated |
| `98 00` | RFM: No SM exception |
| `98 02` | Security status not satisfied (RAM) |
| `98 04` | Access condition not fulfilled |
| `98 08` | RFM: Counter exceeded |
| `98 50` | INCREASE cannot be performed |

## GSM 11.11 специфичные

| SW1 SW2 | Значение |
|---|---|
| `92 00` | Update successful but after using an internal retry routine |
| `92 40` | Memory problem — EEPROM failure |
| `94 00` | No EF selected |
| `94 02` | Out of range (invalid address) |
| `94 04` | File ID not found |
| `94 08` | File inconsistent with command |
| `98 04` | Access condition not fulfilled / CHV not verified |
| `98 40` | GSM authentication failure |

## Наиболее частые на практике

| SW | Причина | Типичное решение |
|---|---|---|
| `6A 82` | Неправильный FID | Проверить FID в SELECT |
| `6A 88` | Неправильный TAR или ссылка | Проверить EF_ARR record или TAR |
| `69 82` | PIN не проверен | VERIFY PIN сначала |
| `6E 00` | Неправильный CLA (GSM vs 3GPP) | Проверить CLA: 00=3GPP, A0=GSM |
| `6C XX` | Неправильный Le | Повторить с Le=XX |
| `69 84` | Файл деактивирован | ACTIVATE FILE сначала |
| `63 CX` | Неверный PIN, X попыток | Проверить PIN; PUK при X=0 |

## Связанные

- APDU: [[wiki/concepts/APDU]]
- GSM 11.11: [[wiki/summaries/gsm_1111]]
