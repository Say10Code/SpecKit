---
tags: [GlobalPlatform, card-management, ISD, SSD, security-domain]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/gpc_card_spec_2_3_1|GlobalPlatform Card Spec v2.3.1]]"
---

# GlobalPlatform — Архитектура управления картой

## Определение

**GlobalPlatform (GP)** — это стандарт, определяющий архитектуру управления смарт-картой: загрузку, установку и удаление приложений, управление security domains, secure channel протоколы (SCP). ^[extracted]

Если Java Card — платформа **исполнения** апплетов, то GlobalPlatform — платформа **управления** ими. На SIM-картах GP работает поверх Java Card.

## Архитектура GlobalPlatform

```
┌──────────────────────────────────────────────────────────┐
│                    SIM-карта (UICC)                       │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  ISD (Issuer Security Domain)                         │ │
│  │  AID: A0 00 00 01 51 00 00                           │ │
│  │  • Владелец карты (оператор)                         │ │
│  │  • Обязательный, всегда присутствует                 │ │
│  │  • Privileges: SecurityDomain, CardLock, CardTerminate│ │
│  │  • Имеет ключи KIC/KID/KIK для аутентификации        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────┐  ┌────────────────────────────┐ │
│  │  SSD 1               │  │  SSD 2                     │ │
│  │  (Supplementary SD)  │  │  (Trusted Service Manager) │ │
│  │  AID: ...            │  │  AID: ...                  │ │
│  │  • Content Provider  │  │  • TSM (OTA-provisioning) │ │
│  └──────────────────────┘  └────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Executable Load Files (ELF / CAP packages)           │ │
│  │  ┌──────────┬──────────┬──────────────────────────┐  │ │
│  │  │ Package1 │ Package2 │ Applet A, B, C...         │  │ │
│  │  └──────────┴──────────┴──────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Трёхуровневая иерархия AID в GP

```
Executable Load File AID (5-16 байт)
  └── Executable Module AID (5-16 байт)
       └── Application Instance AID (5-16 байт)
```

| Уровень | Что это | Когда используется |
|---|---|---|
| **Load File AID** | Идентификатор пакета/CAP | LOAD, DELETE |
| **Module AID** | Класс апплета внутри пакета | INSTALL (обычно = Load File AID) |
| **Instance AID** | Экземпляр апплета | SELECT, INSTALL [for install] |

## Ключи и аутентификация GP

Каждый Security Domain имеет 3 ключа (2-key или 3-key SCP):

| Ключ | Назначение | Длина |
|---|---|---|
| **KIC** (Key Encryption) | Шифрование C-APDU | 16 байт (AES-128) |
| **KID** (Key MAC) | Integrity / MAC | 16 байт |
| **KIK** (Key DEK) | Data Encryption Key | 16 байт |
| **KVN** | Key Version Number | 1 байт |

## Основные команды GlobalPlatform

| Команда | CLA+INS | Описание |
|---|---|---|
| **SELECT [by AID]** | `00 A4 04 00` | Выбрать Security Domain |
| **INITIALIZE UPDATE** | `80 50` | Начать SCP-сессию |
| **EXTERNAL AUTHENTICATE** | `82` | Завершить SCP-аутентификацию |
| **INSTALL [for install]** | `80 E6` | Установить экземпляр апплета |
| **INSTALL [for load]** | `80 E6` | Подготовить к загрузке CAP |
| **LOAD** | `80 E8` | Загрузить CAP-файл |
| **INSTALL [for delete]** | `80 E6` | Удалить апплет/пакет |
| **GET STATUS** | `80 F2` | Список установленных объектов |
| **GET DATA** | `80 CA` | Прочитать информацию о карте |
| **SET STATUS** | `80 F0` | Изменить состояние (lock/unlock) |
| **DELETE** | `80 E4` | Удалить объект |

## GET STATUS — реестр объектов

Команда `80 F2` возвращает все установленные объекты на карте:

```
ISD: A000000003000000 (SECURED)
     Privs: SecurityDomain, CardLock, CardTerminate
APP: A0000000871002FFFFFFFF8907090000 (SELECTABLE)    ← USIM
APP: A0000000871004FFFFFFFF8907090000 (SELECTABLE)    ← ISIM
PKG: A0000000620001 (LOADED)                          ← javacard.framework
PKG: A0000000620101 (LOADED)                          ← javacard.framework 1.0
PKG: D07002CA44 (LOADED)                              ← пользовательский пакет
     Applet: D07002CA44900101                          ← экземпляр апплета
```

## SCP (Secure Channel Protocol)

GlobalPlatform определяет несколько версий защищённых каналов:

| SCP | Шифрование | MAC | Keyset |
|---|---|---|---|
| **SCP02** | 3DES | 3DES | 3-key (KIC, KID, KIK) |
| **SCP03** | AES-128/256 | AES-CMAC | 3-key |
| **SCP80** | Secured APDU (TS 102 225) | — | OTA |
| **SCP81** | TLS/PSK | — | Remote |

На современных SIM-картах: **SCP03** для локального управления, **SCP80** для OTA.

## Привилегии Security Domain

| Привилегия | Описание |
|---|---|
| **SecurityDomain** | Может быть родителем для других SD |
| **CardLock** | Может заблокировать карту |
| **CardTerminate** | Может терминировать карту |
| **CardReset** | Может сбросить карту |
| **TrustedPath** | Доступ к доверенному пути ввода/вывода |
| **DAP Verification** | Проверка DAP (Data Authentication Pattern) |

## GlobalPlatform и UICC/SIM

На SIM-картах:
- **ISD** = оператор (MNO), владеет картой
- Пользовательские апплеты устанавливаются под ISD (тот же Security Domain)
- OTA-сообщения проходят через ISD → RAM → апплет
- TS 102 226 определяет специфичные для UICC install parameters (теги `CA`, `EA`, `TA`)

## Связи

- Платформа: [[wiki/concepts/JavaCard]]
- Разработка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- STK-апплеты: [[wiki/concepts/STK_Applet]]
- OTA: [[wiki/concepts/OTA_Remote_Management]]
- AID-инфраструктура: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
- Спецификация: [[wiki/summaries/gpc_card_spec_2_3_1]]
- PC/SC и Linux HOWTO: [[wiki/summaries/smart_card_howto|Smart Card HOWTO]]
- Contactless Services (CRS, CREL, Multi-SE): [[wiki/research/sim_nfc_contactless|SIM и NFC — SWP, HCI, CLF]]
