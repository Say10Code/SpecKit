---
tags: [pySim, Osmocom, tool, SIM, USIM, summary]
source: "[[Specifications/Manuals/osmopysim-usermanual.pdf]]"
type: tool-manual
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# pySim — User Manual (Osmocom, 2023)

> **Авторы**: Sylvain Munaut, Harald Welte, Philipp Maier и др.
> **Дата**: Октябрь 2023
> **Страниц**: 75

## Обзор

**pySim** — Python-библиотека для управления SIM/USIM/ISIM картами. Основной инструмент Osmocom для чтения, программирования и тестирования UICC. Состоит из: pySim-shell (интерактивная оболочка), pySim-trace (сниффер APDU), pySim-prog/read (legacy CLI). ^[extracted]

## Компоненты

### pySim-shell
Интерактивная оболочка с полным доступом к файловой системе UICC:

```bash
$ pySim-shell -p 0
pySIM-shell (00:01:02:03:04:05)> select MF
pySIM-shell (00:01:02:03:04:05)> select ADF.USIM
pySIM-shell (00:01:02:03:04:05)> read EF.IMSI
```

#### Группы команд

| Группа | Команды | Назначение |
|---|---|---|
| **ISO7816** | `select`, `read_binary`, `update_binary`, `read_record`, `update_record` | Базовые APDU |
| **TS 102 221** | `verify_adm`, `authenticate`, `suspend_uicc` | UICC-специфичные |
| **pySim** | `export`, `bulk_script`, `echo`, `verify_chv` | Высокоуровневые |
| **Linear Fixed EF** | `read_record_decoded`, `write_record_decoded` | Декодированные записи |
| **Transparent EF** | `read_binary_decoded`, `write_binary_decoded` | Декодированные данные |
| **BER-TLV EF** | `retrieve_data`, `set_data` | TLV-структуры |
| **USIM** | `ust_service_activate`, `ust_service_deactivate` | Управление USIM |
| **GlobalPlatform** | `gp_list`, `gp_install`, `gp_delete` | GP-команды |

### pySim-trace
Сниффер APDU-обмена между ME и UICC:
- Захват и декодирование APDU в реальном времени
- Декодирование по спецификациям (не raw-байты, а осмысленные значения)
- Поддерживает PCSC

### pySim-prog / pySim-read (Legacy)
- `pySim-prog`: программирование SIM (запись IMSI, Ki, ICCID, ...)
- `pySim-read`: чтение всех EF с карты

### pySim Library
Python-библиотека, используемая всеми инструментами:
- **Файловая система**: абстракция MF/DF/ADF/EF с кардированием (card profile)
- **Команды**: абстрактный слой над APDU
- **Транспорт**: PCSC reader, serial, modem AT-команды
- **TLV/construct**: парсинг BER-TLV и других форматов

## Поддерживаемые карты

- **sysmoUSIM-SJS1** / **sysmoISIM-SJA2** / **sysmoISIM-SJA5** (Osmocom)
- Другие программируемые карты (через кардированные profiles)
- Карты с известными ADM-ключами

## Интересные возможности

- **card_handler**: автоматическое определение типа карты и загрузка соответствующего profile
- **card_key_provider**: различные источники ключей (ADM, KIC/KID, transport key)
- **export**: дамп всей файловой системы в JSON/CSV
- **bulk_script**: пакетное выполнение команд из файла
- **ARA-M**: управление Access Rule Application Master для UICC

## Связи

- Osmocom: [[wiki/entities/Osmocom]]
- STK-апплеты: [[wiki/concepts/STK_Applet]]
- GP-управление: [[wiki/concepts/GlobalPlatform_Card]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
