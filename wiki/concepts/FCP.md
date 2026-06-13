---
tags: [UICC, FCP, file-system, BER-TLV, SELECT]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_102221]]"
---

# FCP — File Control Parameters

## Определение

**FCP (File Control Parameters)** — это BER-TLV структура, возвращаемая UICC в ответ на команду SELECT. FCP содержит **метаданные файла**: размер, тип, идентификаторы, security attributes, и другие параметры. ^[extracted]

## Структура FCP

FCP возвращается в теле ответа R-APDU при успешном SELECT (SW1SW2 = `'90 00'`).

```
┌──────────────────────────────────────────────────────────┐
│ FCP Template (Tag '62')                                  │
├──────────────────────────────────────────────────────────┤
│  ├─ File Descriptor (Tag '82')                           │
│  ├─ File Identifier (Tag '83')                           │
│  ├─ DF Name / AID (Tag '84')          ← ADF только      │
│  ├─ Proprietary Information (Tag 'A5')                   │
│  │   ├─ SFI (Tag '88')                                   │
│  │   ├─ Life Cycle Status (Tag '8A')                    │
│  │   ├─ PIN Status Template DO (Tag '8B'/'8C')          │
│  │   └─ Minimum Clock Frequency (Tag '82' in 'A5')      │
│  ├─ Security Attributes (Tag '8B'/'8C'/'AB')            │
│  ├─ File Size (Tag '80')                                 │
│  ├─ Total File Size (Tag '81')                           │
│  └─ Short File Identifier (Tag '88')   ← если SFI есть  │
└──────────────────────────────────────────────────────────┘
```

## Основные Data Objects в FCP

| Tag | Имя | Описание | Обязательность |
|---|---|---|---|
| `82` | File Descriptor | Тип EF (см. [[wiki/concepts/EF_Types#File Descriptor Byte]]) | ✅ для EF |
| `83` | File Identifier | FID файла (2 байта) | ✅ |
| `84` | DF Name / AID | Имя DF (5-16 байт) | ✅ для DF/ADF |
| `80` | File Size | Размер данных файла | ✅ для EF |
| `81` | Total File Size | Размер данных + structural info | Опционально |
| `88` | Short File Identifier | SFI (1 байт) | Если поддерживается |
| `8A` | Life Cycle Status | Состояние файла (created/activated/deactivated) | Опционально |
| `A5` | Proprietary Info | Дополнительные параметры (внутри — sub-TLVs) | Опционально |
| `8B`/`8C`/`AB` | Security Attributes | Access conditions (см. [[wiki/concepts/UICC_Security]]) | Опционально |

## Proprietary Information (Tag `A5`)

Внутри `A5` могут быть:

| Tag | Имя | Описание |
|---|---|---|
| `82` | Minimum Clock Frequency | Мин. частота для приложения (≤3 MHz для 3GPP) ^[extracted] |
| `88` | SFI (внутри A5) | Альтернативное размещение SFI |
| `8A` | Life Cycle Status Integer | `00`=нет информации, `01`=creation, `03`=activated, `0C`=deactivated |
| `8B`/`8C` | PIN Status Template DO | Состояние PIN (см. [[wiki/concepts/UICC_Security#PIN Status]]) |

## Пример FCP (для EF)

```
SELECT 0x2FE2  (EF_ICCID)
→ '90 00', FCP:

62 1C                             ← FCP Template (28 bytes)
   82 01 01                       ← File Descriptor: Transparent
   83 02 2F E2                    ← File Identifier: 0x2FE2
   80 02 00 0A                    ← File Size: 10 bytes
   8A 01 03                       ← Life Cycle: activated
   8B 03 2F 06 04                 ← Security: EF_ARR record 4
```

## FCP для DF/ADF

При выборе DF/ADF в FCP включаются:
- **DF Name** (Tag `84`) — AID приложения
- **PIN Status** (Tag `8B`/`8C`) — состояние PIN-верификации
- Без File Size и File Descriptor (это директория, а не файл данных)

## Связи

- Типы EF (File Descriptor): [[wiki/concepts/EF_Types]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
- Безопасность: [[wiki/concepts/UICC_Security]]
- Команда SELECT: [[wiki/concepts/APDU#SELECT]]
