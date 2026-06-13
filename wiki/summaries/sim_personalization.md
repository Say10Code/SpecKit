---
tags: [SIM, personalization, manufacturing, A-MEN, summary]
source: "[[Specifications/Manuals/SIM_Cards_personalization.pdf]]"
type: technical-document
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# SIM Card Personalization Document (A-MEN, 2005)

> **Автор**: Otto Hung, A-MEN Technology Corporation
> **Дата**: 2004-2005, версия 2.0
> **Страниц**: 35

## Обзор

Технический документ по персонализации 16K SIM-карт. Детально описывает файловую систему GSM SIM, интерфейсные команды и процесс персонализации. Ценен как практический пример реальной структуры SIM-карты с конкретными FID и параметрами. ^[extracted]

## Ключевое содержание

### 1. Структура файловой системы (реальная карта)

#### Системные EF
| EF | FID | Назначение |
|---|---|---|
| EF_PIN | — | PIN, PUK, PIN2, PUK2 |
| EF_Key | — | Транспортные ключи, Ki |
| EF_ICCID | 0x2FE2 | Серийный номер |
| EF_IMSI | 0x6F07 | Идентификатор абонента |

#### Toolkit Framework (STK)
| EF | Назначение |
|---|---|
| EF_AP_xx | Toolkit Applet — апплеты STK |
| EF_VP_xx | Variable Pool — переменные апплетов |

#### STK Setting Files
| EF | Назначение |
|---|---|
| EF_ENVELOPE | Буфер ENVELOPE команд |
| EF_COMM | Common Variable Pool |
| EF_MENUS | Menu Items — пункты меню |
| EF_Event | Event List — список событий |
| EF_Poll | Poll Duration Interval |
| EF_LAC | Local Area Code |

#### RFM (Remote File Management)
| EF | Назначение |
|---|---|
| EF_TAR | Toolkit Application Reference |
| EF_SMSH | SMS Header (OTA) |
| EF_CNTR | GSM 03.48 Counter |
| EF_CMSB | Short-Message Buffer |

### 2. Анти-клонирование
- EF_AlgorithmCounter: счётчик использований GSM-алгоритма
- EF_AntiClone: защита от клонирования
- Проверка через алгоритм Anti-Cloning

### 3. Команды персонализации
Проприетарные команды A-MEN:
- **VERIFY Transport Key** — аутентификация перед персонализацией
- **ERASE ALL** — очистка EEPROM
- **WRITE MEMORY** / **READ MEMORY** — прямой доступ к памяти
- **PUT KEY** — запись ключей
- **ACTIVE FILE SYSTEM** — активация после персонализации
- **VERIFY ICCID** — проверка ICCID

### 4. Процесс персонализации
```
1. VERIFY Transport Key → аутентификация
2. ERASE ALL → очистка
3. WRITE MEMORY / PUT KEY → запись данных
4. READ MEMORY → верификация
5. ACTIVE FILE SYSTEM → активация
```

### 5. Интересные детали
- Поддержка множественных STK-апплетов (EF_AP_01, EF_AP_02, ... EF_AP_NN)
- Variable Pool — shared переменные между апплетами
- RFM через SMS (GSM 03.48) с буфером для OTA-сообщений

## Связи

- Файловая система SIM: [[wiki/concepts/UICC_File_System]]
- OTA/RFM: [[wiki/concepts/OTA_Remote_Management]]
- AID: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
