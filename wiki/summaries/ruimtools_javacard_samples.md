---
tags: [RuimTools, JavaCard, STK, examples, code, summary]
source: "[[Clippings/RuimTools JavaCard source samples.md]]"
type: code-samples
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# RuimTools: JavaCard Source Samples (STK)

> **Источник**: http://www.ruimtools.com/doc.php?doc=javacard
> **Извлечено**: 2026-05-31

## Обзор

Коллекция примеров кода для Java Card STK-апплетов. Каждая команда сопровождается кодом на Java Card и списком параметров/qualifier'ов. ^[extracted]

## Охваченные Proactive Commands

| Команда | Код | Ключевые особенности |
|---|---|---|
| REFRESH | `0x01` | File Change Notification; qualifiers: `00`-`06` |
| PROVIDE LOCAL INFORMATION | `0x0A` | Location, IMEI, IMEISV, язык, время, battery |
| SELECT ITEM | `0x0C` | Список выбора; мягкие клавиши |
| SEND SHORT MESSAGE | `0x0E` | SMS-packing; SMSC адрес |
| DISPLAY TEXT | `0x15` | Приоритет; WAIT_FOR_USER опасность reentrance |
| SET UP CALL | `0x10` | Hold/Disconnect с redial |
| GET INPUT | `0x0B` | Цифры/алфавит; скрытый ввод; SMS-packed |
| SET UP MENU | — | `ToolkitRegistry.initMenuEntry()` |
| PLAY TONE | `0x0F` | Vibrate alert |
| LAUNCH BROWSER | `0x15` | URL-тег |
| SEND USSD | — | USSD-строка → UICC → ответ через DisplayText |
| DES Calculation | — | `DESKey` + `Cipher` для crypto |

## Важные замечания из источника

- **DISPLAY TEXT с WAIT_FOR_USER**: может вызвать reentrance конфликты с другими апплетами
- **Location Information**: ненадёжно, не всегда возвращает одинаковый ответ
- **Network Measurements**: не поддерживается многими терминалами
- **SMS Sending**: убедитесь, что сервер справится с объёмом сообщений
- **Menu limits**: длина и количество записей не могут превысить install parameters + размер EF_MENU_ITEMS

## Связи

- STK-апплеты: [[wiki/concepts/STK_Applet]]
- CAT-команды: [[wiki/concepts/CAT_STK]]
- Best practices: [[wiki/summaries/ruimtools_javacard_guidelines]]
- HelloSTK: [[wiki/entities/Osmocom]]
