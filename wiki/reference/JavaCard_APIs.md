---
tags: [reference, JavaCard, API, AID, GP-commands]
type: reference
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/concepts/JavaCard]]"
  - "[[wiki/summaries/gpc_card_spec_2_3_1]]"
---

# JavaCard API & GP Commands — Справочник

## Java Card API пакеты и их AID

| Пакет                        | AID                    | Версия | Назначение                                           |
| ---------------------------- | :--------------------- | ------ | ---------------------------------------------------- |
| `javacard.framework`         | `A0 00 00 00 62 01 01` | 1.0    | Базовое API: Applet, APDU, AID, JCSystem, PIN        |
| `javacardx.crypto`           | `A0 00 00 00 62 02 01` | 1.0    | Расширенное crypto: Cipher (DES, AES, RSA)           |
| `javacard.security`          | `A0 00 00 00 62 03 01` | 1.0    | Базовое crypto: KeyBuilder, Signature, MessageDigest |
| `javacard.framework.service` | —                      | 1.0    | Service framework: dispatcher                        |
| `java.rmi`                   | —                      | 1.0    | Java Card RMI (Remote Method Invocation)             |
| `sim.toolkit`                | `A0 00 00 00 76 01 01` | 2G     | STK API для GSM SIM                                  |
| `uicc.toolkit`               | `A0 00 00 00 76 02 01` | 3G+    | STK API для UMTS/LTE/5G UICC                         |
| `sim.access`                 | —                      | 2G     | Доступ к файловой системе SIM                        |
| `uicc.access`                | —                      | 3G+    | Доступ к файловой системе USIM                       |

## GlobalPlatform AID

| AID | Назначение |
|---|---|
| `A0 00 00 01 51 00 00` | ISD (Issuer Security Domain) |
| `A0 00 00 01 51 41 4D` | RAM (Remote Application Management) |
| `A0 00 00 01 51 52 46 4D` | RFM (Remote File Management) |

## ETSI/3GPP AID (телеком)

| Приложение | AID (базовый) |
|---|---|
| GSM SIM | `A0 00 00 00 09 00 01` |
| GSM STK | `A0 00 00 00 09 00 02` |
| 3G USIM | `A0 00 00 00 87 10 02 FF FF FF ...` |
| ISIM (IMS) | `A0 00 00 00 87 10 04 FF FF FF ...` |
| CSIM (CDMA) | `A0 00 00 00 87 10 06 FF FF FF ...` |
| AKA Auth | `A0 00 00 00 87 10 08` |

## Основные GP команды

| Команда | CLA INS | P1 P2 | Описание |
|---|---|---|---|
| **SELECT** | `00 A4` | `04 00` | Выбрать SD по AID |
| **INITIALIZE UPDATE** | `80 50` | `00 00` + host challenge | Начать SCP-сессию |
| **EXTERNAL AUTHENTICATE** | `84 82` | `00 00` | Аутентификация SCP |
| **INSTALL [for load]** | `80 E6` | `02 00` | Подготовка загрузки CAP |
| **LOAD** | `80 E8` | `00 00` | Загрузить CAP-файл |
| **INSTALL [for install]** | `80 E6` | `0C 00` | Установить экземпляр апплета |
| **INSTALL [for delete]** | `80 E6` | `04 00` | Удалить апплет/пакет |
| **DELETE** | `80 E4` | `00 00` | Удалить объект |
| **GET STATUS** | `80 F2` | вар. | Список объектов на карте |
| **GET DATA** | `80 CA` | вар. | Прочитать данные SD |
| **SET STATUS** | `80 F0` | вар. | Изменить состояние |

## GET STATUS P1P2

| P1 | P2 | Что возвращает |
|---|---|---|
| `02` | `00` | ISD (Issuer Security Domains) |
| `20` | `00` | Applications + SSDs |
| `40` | `00` | Executable Load Files (пакеты) |
| `10` | `00` | Executable Modules |
| `80` | `00` | Все объекты |

## Proactive Command коды (STK)

| Команда | Код | Tag в структуре |
|---|---|---|
| DISPLAY TEXT | `0x21` | `D0` |
| GET INKEY | `0x22` | `D0` |
| GET INPUT | `0x23` | `D0` |
| MORE TIME | `0x24` | `D0` |
| PLAY TONE | `0x25` | `D0` |
| POLL INTERVAL | `0x26` | `D0` |
| REFRESH | `0x27` | `D0` |
| SET UP MENU | `0x28` | `D0` |
| SELECT ITEM | `0x29` | `D0` |
| SEND SHORT MESSAGE | `0x2A` | `D0` |
| SET UP CALL | `0x2C` | `D0` |
| POLLING OFF | `0x2E` | `D0` |
| PROVIDE LOCAL INFO | `0x2F` | `D0` |
| SET UP EVENT LIST | `0x30` | `D0` |
| PERFORM CARD APDU | `0x31` | `D0` |
| TIMER MANAGEMENT | `0x35` | `D0` |
| SET UP IDLE MODE TEXT | `0x36` | `D0` |
| RUN AT COMMAND | `0x37` | `D0` |
| SEND DTMF | `0x38` | `D0` |
| LANGUAGE NOTIFICATION | `0x39` | `D0` |
| LAUNCH BROWSER | `0x3A` | `D0` |
| OPEN CHANNEL | `0x3B` | `D0` |
| CLOSE CHANNEL | `0x3C` | `D0` |
| RECEIVE DATA | `0x3D` | `D0` |
| SEND DATA | `0x3E` | `D0` |
| ACTIVATE | `0x40` | `D0` |

## Связи

- JavaCard: [[wiki/concepts/JavaCard]]
- GP-архитектура: [[wiki/concepts/GlobalPlatform_Card]]
- STK-команды: [[wiki/concepts/STK_Applet]], [[wiki/concepts/CAT_STK]]
- AID-гид: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
- USIM EF: [[wiki/reference/USIM_EF_Table]]
- Нумерация ETSI: [[wiki/summaries/ts_101_220|TS 101 220]]
