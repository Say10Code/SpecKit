---
tags: [OTA, RAM, SMS-PP, CAT_TP, security]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_102_226|ETSI TS 102 226 — Remote APDU]]"
  - "[[wiki/summaries/sim_cards_thesis|SIM Cards for Cellular Networks]]"
---

# OTA — Over-the-Air / Удалённое управление SIM

## Определение

**OTA (Over-the-Air)** — механизм удалённого управления SIM/UICC-картой через мобильную сеть. Позволяет оператору отправлять APDU-команды, обновлять файлы, устанавливать/удалять апплеты без физического доступа к карте. ^[extracted]

Используется для: обновления SPN/PLMN-списков, установки STK-апплетов, конфигурации роуминга, обновления ключей безопасности.

## Транспортные механизмы OTA

### SMS-PP (SMS Point-to-Point)
```
┌─────────┐    SMS-DELIVER     ┌─────────┐    ENVELOPE    ┌─────────┐
│  OTA    │ ───────→────────── │  Phone  │ ─────→─────────│  UICC   │
│ Server  │   (TP-UD с APDU)   │  (ME)   │   (SMS-PP)     │ (SIM)   │
└─────────┘                    └─────────┘                └─────────┘
                ←── SMS-SUBMIT ─────────── ←──────────────
                   (Response, если нужен)
```

- Транспорт: GSM/3G SMS
- Каждое SMS содержит одну или несколько Secured APDU команд
- **TP-UD** (TP User Data) = Command Packet по TS 102 226

### CAT_TP (Card Application Toolkit Transport Protocol)
```
┌─────────┐    BIP (GPRS/3G/4G)  ┌─────────┐     ENVELOPE     ┌─────────┐
│  OTA    │ ←────→─────────────── │  Phone  │ ──────→──────────│  UICC   │
│ Server  │   TCP/IP connection   │  (ME)   │  (OPEN CHANNEL)  │ (SIM)   │
└─────────┘                       └─────────┘                  └─────────┘
```

- Транспорт: TCP/IP через BIP (Bearer Independent Protocol)
- Устанавливается proactive командой OPEN CHANNEL
- Более быстрый и надёжный чем SMS-PP

### HTTPS (eUICC — GSMA SGP.22)
- Используется для eSIM Remote SIM Provisioning
- ES9+ (SM-DP+ ↔ LPA) и ES8+ (SM-DP+ ↔ eUICC)
- Не рассматривается в TS 102 226 (это GSMA SGP.22 domain)

## Архитектура OTA по TS 102 226

```
┌──────────────────────────────────────────────────────────┐
│              OTA Server (Platform)                        │
│                                                           │
│  ┌─────────────┐    ┌──────────────┐   ┌──────────────┐  │
│  │ Application │    │ Secured APDU │   │ SMS/HTTP     │  │
│  │ Command     │───→│ Packets      │──→│ Transport     │  │
│  │ (APDU)      │    │ (TS 102 226) │   │ (SMSC, IP)  │  │
│  └─────────────┘    └──────────────┘   └──────────────┘  │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│               SIM-карта (UICC)                            │
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │ SMS-PP       │──→│ Secured Packet│──→│ Application   │  │
│  │ ENVELOPE     │   │ Unwrap       │   │ APDU          │  │
│  └──────────────┘   └──────────────┘   └──────────────┘  │
│                                                           │
│  Security:                                                │
│  • TAR (Toolkit Application Reference) — маршрутизация    │
│  • Secured Packet по TS 102 225 (шифрование + MAC)        │
│  • Ключи KIC/KID для OTA-сессии                           │
└──────────────────────────────────────────────────────────┘
```

## Структура Command Packet (TS 102 226)

```
┌──────────┬──────────┬────────────┬──────────────┬──────────┐
│ CPL      │ CHL      │ CPL        │ CHL          │ Secured  │
│ Length   │ SPI      │ SPI Value  │ KIc/KID      │ Data     │
│ (var)    │ (1 byte) │ (CPL-1)    │ Values       │          │
└──────────┴──────────┴────────────┴──────────────┴──────────┘
```

- **CPL** (Command Packet Length) — общая длина пакета
- **CHL** (Command Header Length) — длина заголовка безопасности
- **SPI** (Security Parameters Indicator) — тип защиты
- **KIC/KID** — индексы ключей (encryption, MAC)
- **Secured Data** — шифрованные APDU команды с MAC

## TAR (Toolkit Application Reference)

**TAR** — 3-байтовый идентификатор, маршрутизирующий OTA-сообщения конкретному апплету:

| TAR | Назначение |
|---|---|
| `BF FF FF` | Широковещательно всем STK-апплетам |
| `XX YY ZZ` | Конкретный апплет (задан в install parameters `CA`) |
| `00 00 00` | RAM (Remote Application Management) — управление приложениями |
| `00 00 01` | RFM (Remote File Management) — управление файлами |

### Маршрутизация через TAR
```
OTA Server → SMS-DELIVER (с TAR в TP-UD)
  → Карта проверяет TAR:
    • BF FF FF → всем STK-апплетам (все ToolkitInterface получат ENVELOPE)
    • XX YY ZZ → конкретному апплету с этим TAR
    • 00 00 00 → RAM → ISD
    • Неизвестный → удаление без доставки
```

## RAM (Remote Application Management)

RAM — подсистема OTA для управления приложениями (а не файлами):
- Использует TAR = `00 00 00`
- Команды адресованы ISD (Issuer Security Domain)
- Позволяет: LOAD, INSTALL, DELETE апплеты удалённо
- Используется SCP80 (Secured APDU) для шифрования + MAC

### RFM (Remote File Management)
- TAR = `00 00 01`
- Позволяет: CREATE, DELETE, UPDATE файлы EF/DF
- Доступ контролируется через RAM security domain

## Безопасность OTA

| Уровень | Стандарт | Что делает |
|---|---|---|
| Transport | GSM/3G/4G SMS | Не шифровано (само по себе) |
| **Secured Packet** | **TS 102 225** | Шифрование + MAC команд |
| **Command Packet** | **TS 102 226** | Формат пакета, TAR, SPI |
| Канал | SCP80 | Secure Channel для RAM/RFM |
| Ключи | KIC, KID, KIK | Симметричные ключи для OTA |

### Уровни безопасности SPI (TS 102 226)

| SPI | Шифрование | MAC | Counter | Применение |
|---|---|---|---|---|
| 0x00 | Нет | Нет | Нет | Тестирование |
| 0x12 | 3DES/AES | DES/AES-CBC | Да | Production |
| 0x22 | AES | AES | Да | Современный |

## Связь OTA с STK-апплетом

1. Апплет регистрирует TAR в install parameters (`CA` tag)
2. OTA-сервер отправляет SMS с этим TAR
3. UICC получает SMS-PP → проверяет TAR → формирует ENVELOPE
4. JCRE вызывает `applet.processToolkit()` с EVENT_UNRECOGNIZED_ENVELOPE
5. Апплет разбирает ENVELOPE и выполняет команду

## Связи

- Формат пакетов: [[wiki/summaries/ts_102_226|ETSI TS 102 226]]
- Secured Packet: [[wiki/summaries/ts_102225|TS 102 225]]
- TAR значения: [[wiki/summaries/ts_101_220|TS 101 220 Annex D]]
- OTA Security (GSM): [[wiki/summaries/ts_123048|TS 23.048]]
- STK-апплеты: [[wiki/concepts/STK_Applet]]
- GlobalPlatform: [[wiki/concepts/GlobalPlatform_Card]]
- Безопасность UICC: [[wiki/concepts/UICC_Security]]
- Установка апплета: [[wiki/concepts/JavaCard_Applet_Development]]
- Персонализация SIM: [[wiki/summaries/sim_personalization|SIM Personalization (A-MEN)]]
- OTA evolution: [[wiki/syntheses/ota_evolution|OTA: от SMS-PP к eSIM RSP]]
- SCWS + BIP: [[wiki/research/sim_scws_webserver|SIM как веб-сервер — SCWS + BIP]] (TAR B2 01 01, OTA-обновление контента)
