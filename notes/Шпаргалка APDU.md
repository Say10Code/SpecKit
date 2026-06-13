---
tags: [note, cheat-sheet, APDU, quick-reference]
type: note
created: 2026-06-11
updated: 2026-06-11
---

# Шпаргалка APDU — Быстрый справочник

## Структура C-APDU

```
CLA INS P1 P2 [Lc] [Data] [Le]
```

## Основные команды

| INS | Команда | Пример |
|---|---|---|
| `A4` | **SELECT** | `00 A4 00 00 02 3F 00` (MF) |
| `B0` | **READ BINARY** | `00 B0 00 00 0A` |
| `D6` | **UPDATE BINARY** | `00 D6 00 00 08 ...` |
| `B2` | **READ RECORD** | `00 B2 01 04 1A` |
| `DC` | **UPDATE RECORD** | `00 DC 01 04 1A ...` |
| `20` | **VERIFY PIN** | `00 20 00 01 08 ...` |
| `88` | **AUTHENTICATE** | `00 88 00 81 22 ...` |
| `F2` | **STATUS** | `80 F2 00 00 00` |
| `C0` | **GET RESPONSE** | `00 C0 00 00 1E` |

## Частые SW1 SW2

| SW | Значение | Действие |
|---|---|---|
| `90 00` | OK | ✅ |
| `61 XX` | Готово XX байт | GET RESPONSE |
| `6C XX` | Неправильный Le | Повторить с Le=XX |
| `69 82` | PIN не проверен | VERIFY PIN |
| `6A 82` | Файл не найден | Проверить FID |
| `6A 88` | Referenced data not found | Проверить TAR/ARR |
| `6E 00` | Class not supported | Проверить CLA |
| `63 CX` | PIN неверен, X попыток | Проверить PIN |

## CLA по приложению

| CLA | Приложение |
|---|---|
| `00` | 3GPP (USIM/ISIM) |
| `A0` | GSM (SIM) |
| `80` | ETSI/GP |

## Путь к популярным файлам

```
MF (3F00) → EF_ICCID (2FE2)
MF (3F00) → DF_GSM (7F20) → EF_IMSI (6F07)
MF (3F00) → DF_GSM (7F20) → EF_SPN (6F46)
MF (3F00) → ADF.USIM (A0..87.10.02...) → EF_IMSI (6F07)
```

## Типовой сеанс чтения

```
1. SELECT MF         00 A4 00 00 02 3F 00    → 90 00
2. SELECT EF_ICCID   00 A4 00 00 02 2F E2    → 90 00
3. READ BINARY       00 B0 00 00 00          → 6C 0A
4. READ BINARY       00 B0 00 00 0A          → ... 90 00
```

## См. также

- [[wiki/reference/Status_Words|Полная таблица SW]]
- [[wiki/reference/CLA_INS_SFI|CLA/INS/SFI справочник]]
- [[wiki/concepts/APDU|APDU — полный разбор]]
