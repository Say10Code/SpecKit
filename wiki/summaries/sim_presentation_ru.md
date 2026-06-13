---
tags: [SIM, presentation, Russian, form-factors, summary]
source: "[[Specifications/Tutorials/SIM_презентация_RU.pdf]]"
type: presentation
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# SIM-карта — Презентация (русский, 62 слайда)

> **Язык**: Русский
> **Формат**: 62 слайда
> **Темы**: Форм-факторы, контакты, электрический интерфейс, файловая система, команды

## Обзор

Презентация на русском языке, охватывающая SIM-карты «снаружи внутрь»: от физических форм-факторов до APDU-команд и аутентификации. Хорошо структурирована, подходит как введение для начинающих. ^[inferred]

## Ключевые разделы

### 1. Форм-факторы SIM-карт (слайды 2-4)
- **1FF** (Full-size, ISO ID-1): 1991
- **2FF** (Mini-SIM / Plug-in): 1996
- **3FF** (Micro-SIM): 2003, ETSI TS 102 221 V9.0.0 (Mini-UICC)
- **4FF** (Nano-SIM): 2012, ETSI TS 102 221 V11.0.0
- **MFF2** (Embedded / eSIM): 2016, JEDEC Design Guide + GSMA SGP.22

### 2. Контакты и интерфейс (слайды 5-8)
- **Vcc**: питание (5V, 3V, 1.8V)
- **CLK**: тактовые импульсы (1-5 MHz)
- **Reset**: сброс
- **I/O**: последовательная передача (полудуплекс)
- **C6**: исторически Vpp (программирование EPROM) → CLF (contactless) → USB D-
- **C4/C8**: USB Data+/Data- (TS 102 600)

### 3. Внутренняя архитектура (слайды 8-12)
- CPU (8/16/32-bit)
- ROM (ОС + фиксированные данные)
- EEPROM (файловая система, изменяемые данные)
- RAM (временные данные при работе)

### 4. Файловая система (слайды 15-30)
- MF (3F00) → DF → EF
- Ключевые EF: ICCID, IMSI, SPN, ADN, SMS
- Типы: Transparent, Linear Fixed, Cyclic

### 5. Команды APDU (слайды 35-45)
- Структура C-APDU и R-APDU
- Примеры команд: SELECT, READ BINARY, UPDATE BINARY, VERIFY CHV
- Status Words: 90 00, 6C XX, 69 82, ...

### 6. Аутентификация (слайды 46-55)
- GSM AUTH: RAND → SRES + Kc (COMP128)
- PIN/PUK: CHV1/CHV2
- ATR: начальный ответ карты

### 7. eSIM (слайды 56-62)
- Переход к eUICC
- Remote SIM Provisioning
- GSMA SGP.02 / SGP.22

## Ценность для проекта

Единственная презентация на русском языке. Полезна как введение для русскоязычных читателей. Изложение «от простого к сложному»: форма → электричество → логика → команды.

## Связи

- UICC платформа: [[wiki/concepts/UICC]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
- eSIM: [[wiki/concepts/eSIM]]
- APDU: [[wiki/concepts/APDU]]
