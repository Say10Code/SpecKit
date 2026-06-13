---
tags: [UICC, EF, file-system, BER-TLV]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_102221]]"
---

# Elementary File Types — Типы элементарных файлов UICC

## Определение

**EF (Elementary File)** — конечный файл данных в файловой системе UICC. EF содержит данные и access conditions, но не может содержать другие файлы. ^[extracted]

## Четыре типа EF

### 1. Transparent EF
**Поток байт**, неструктурированный.

```
┌─────────────────────────────────┐
│ Byte 0 │ Byte 1 │ ... │ Byte N-1 │
└─────────────────────────────────┘
```

- **Доступ**: READ BINARY / UPDATE BINARY (по смещению)
- **Примеры**: EF_IMSI, EF_ICCID, EF_SPN, ключи
- **FCP File Descriptor**: `01` (transparent)
- **Размер**: до 65535 байт (но обычно меньше — ограничено памятью UICC)

### 2. Linear Fixed EF
**Записи фиксированной длины**, доступ по номеру записи.

```
┌──────────────────────┐  ← Record 1
│ Field A │ Field B │...│
├──────────────────────┤  ← Record 2
│ Field A │ Field B │...│
├──────────────────────┤  ← Record 3
│ ...                  │
└──────────────────────┘
```

- **Доступ**: READ RECORD / UPDATE RECORD (по record number)
- **SEARCH RECORD** — поиск по шаблону в записях
- **Примеры**: EF_PBR (phonebook), EF_AD (administration data)
- **FCP File Descriptor**: `02` (linear fixed)
- **Типы адресации**: absolute (номер записи), next, previous, current

### 3. Cyclic EF
**Кольцевой буфер** записей фиксированной длины.

```
┌──────┐
│Rec 1 │ ←── Запись 1..N, после N снова 1
├──────┤
│Rec 2 │
├──────┤
│ ...  │
├──────┤
│Rec N │
└──────┘
```

- **Доступ**: READ RECORD / UPDATE RECORD
- При записи после последней — перезаписывает первую (FIFO)
- **Примеры**: EF_LND (last numbers dialled), логи
- **FCP File Descriptor**: `06` (cyclic)

### 4. BER-TLV EF
**Набор BER-TLV объектов** (Tag-Length-Value), переменная длина.

```
┌──────────────────────────────────────────┐
│ Tag (1-2B) │ Length (1-3B) │ Value (L)    │
│ Tag (1-2B) │ Length (1-3B) │ Value (L)    │
│ ...                                      │
└──────────────────────────────────────────┘
```

- **Доступ**: READ BINARY / UPDATE BINARY (по смещению)
  - *Примечание*: для поиска конкретного TLV используется смещение по байтам, SEARCH RECORD не работает
- **Примеры**: EF с TLV-конфигурацией (файлы DF_5GS, EF_SUCI_Calc_Info)
- **Примечание**: EF_DIR и EF_ARR — Linear Fixed по структуре, но содержат BER-TLV данные внутри записей
- **FCP File Descriptor**: `04` (BER-TLV)
- **Сложность**: парсинг TLV-структуры требует знания формата

## Сравнительная таблица

| Свойство | Transparent | Linear Fixed | Cyclic | BER-TLV |
|---|---|---|---|---|
| Структура | Байтовый поток | Записи | Кольцо записей | TLV-объекты |
| Длина записей | Н/П | Фиксированная | Фиксированная | Переменная |
| Команды чтения | READ BINARY | READ RECORD | READ RECORD | READ BINARY |
| Команды записи | UPDATE BINARY | UPDATE RECORD | UPDATE RECORD | UPDATE BINARY |
| SEARCH RECORD | ❌ | ✅ | ✅ | ❌ |
| INCREASE | ❌ | ❌ | ❌ | ❌ (только Transparent для счётчиков) |
| File Descriptor | `01` | `02` | `06` | `04` |

## File Descriptor Byte (из FCP)

Байт дескриптора (Tag `82`) в FCP-ответе:

| Биты | Значение |
|---|---|
| b8-b6 | RFU = 000 |
| b5-b4 | **00** = RFU |
| b3-b1 | **001** = Transparent, **010** = Linear Fixed, **100** = BER-TLV, **110** = Cyclic |

## INCREASE и Transparent EF

Команда INCREASE работает только с Transparent EF, где последний байт содержит счётчик:
- Применяется для monotonic counters
- После `0xFF` → сброс в `0x00`

## Связи

- Родительский концепт: [[wiki/concepts/UICC_File_System|UICC File System]]
- FCP (как узнать тип EF): [[wiki/concepts/FCP]]
- Команды: [[wiki/concepts/APDU]]
- Пример файла: [[notes/EF_SPN_PNN]]
