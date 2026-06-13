---
tags: [reference, CLA, INS, SFI, table]
type: reference
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/concepts/APDU]]"
  - "[[wiki/summaries/ts_102221]]"
---

# CLA, INS, SFI — Кодирование байтов APDU

## CLA (Class Byte)

### По приложениям

| CLA | Приложение | Канал |
|---|---|---|
| `00` | 3GPP (USIM, ISIM) | Канал 0 |
| `01`-`03` | 3GPP | Каналы 1-3 |
| `A0` | GSM (SIM) | Канал 0 |
| `A1`-`A3` | GSM | Каналы 1-3 |
| `80` | ETSI / SCP / GP commands | Канал 0 |
| `81`-`83` | ETSI / SCP / GP | Каналы 1-3 |
| `84` | GP Secure Channel | Канал 0 |

### Битовая структура CLA

```
b8 b7 b6 b5 b4 b3 b2 b1
│  └──┴──┘ │  └──┴──┘
│  SM type │  Channel (0-3)
│          └── Command chaining (0=last, 1=more)
└── 0=inter-industry, 1=proprietary
```

### SM (Secure Messaging)

| b7 b6 | SM Type |
|---|---|
| `00` | No SM or no indication |
| `01` | Proprietary SM |
| `10` | SM per ISO |
| `11` | Authentication (CLA `0C`) |

---

## INS (Instruction Byte) — Основные команды

### File Access (TS 102 221)

| INS | Команда | Case | Где применяется |
|---|---|---|---|
| `A4` | **SELECT** | 3/4 | Выбор файла/DF/ADF |
| `B0` | **READ BINARY** | 2 | Transparent EF, BER-TLV EF |
| `D6` | **UPDATE BINARY** | 3 | Transparent EF, BER-TLV EF |
| `B2` | **READ RECORD** | 2 | Linear Fixed EF, Cyclic EF |
| `DC` | **UPDATE RECORD** | 3 | Linear Fixed EF, Cyclic EF |
| `A2` | **SEARCH RECORD** | 3 | Linear Fixed EF, Cyclic EF |
| `32` | **INCREASE** | 3 | Transparent EF (счётчик) |
| `04` | **DEACTIVATE FILE** | 1 | Блокировка EF |
| `44` | **ACTIVATE FILE** | 1 | Разблокировка EF |

### PIN Management

| INS | Команда | Описание |
|---|---|---|
| `20` | **VERIFY PIN** | Проверить PIN |
| `24` | **CHANGE PIN** | Сменить PIN |
| `26` | **DISABLE PIN** | Отключить PIN-проверку |
| `28` | **ENABLE PIN** | Включить PIN-проверку |
| `2C` | **UNBLOCK PIN** | Разблокировать (PUK) |
| `20` | **VERIFY CHV** (GSM) | GSM CHV (CLA=A0, INS=20 как в UICC) |

### Security

| INS | Команда | Описание |
|---|---|---|
| `88` | **AUTHENTICATE** | GSM/UMTS/LTE/5G аутентификация |
| `89` | **AUTHENTICATE** (odd INS) | ISO-совместимый AUTHENTICATE |
| `84` | **GET CHALLENGE** | Получить случайное число |
| `82` | **EXTERNAL AUTHENTICATE** | GP взаимная аутентификация |
| `70` | **MANAGE CHANNEL** | Открыть/закрыть логический канал |
| `73` | **MANAGE SECURE CHANNEL** | GP SCP управление |

### Data Access

| INS | Команда | Описание |
|---|---|---|
| `CA` | **GET DATA** | Чтение data object |
| `DA` | **PUT DATA** | Запись data object |
| `CB` | **RETRIEVE DATA** | CAT Retrieve Data |
| `DB` | **SET DATA** | CAT Set Data |
| `EA` | **SUSPEND UICC** | Приостановка UICC |
| `EB` | **RESUME UICC** | Возобновление UICC |

### GSM 11.11 специфичные

| INS | Команда | Описание |
|---|---|---|
| `88` | **RUN GSM ALGORITHM** | GSM AUTH (вместо AUTHENTICATE) |
| `FA` | **SLEEP** | Спящий режим SIM |

### CAT / STK

| INS | Команда | Описание |
|---|---|---|
| `C0` | **GET RESPONSE** | T=0: получить данные |
| `C2` | **ENVELOPE** | CAT: данные/события → UICC |
| `C3` | **FETCH** | CAT: получить proactive command |
| `F2` | **STATUS** | CAT: проактивный поллинг |
| `10` | **TERMINAL PROFILE** | CAT: профиль терминала (CLA=80) |

### GlobalPlatform

| INS | Команда | Описание |
|---|---|---|
| `50` | **INITIALIZE UPDATE** | Начало SCP сессии |
| `E4` | **DELETE** | Удалить объект |
| `E6` | **INSTALL** | Установить апплет |
| `E8` | **LOAD** | Загрузить CAP |
| `F2` | **GET STATUS** | Список объектов |

---

## SFI (Short File Identifier)

5-битный идентификатор для быстрого доступа к EF без полного SELECT. Tag `88` в FCP.

### SFI на уровне MF (Annex H, TS 102 221)

| SFI | EF | Назначение |
|---|---|---|
| `01` | EF_ICCID | ICC Identification |
| `02` | EF_PL | Preferred Languages |
| `03` | EF_ARR | Access Rule Reference |
| `04` | EF_UMPC | UICC Max Power Consumption |

### Использование SFI

```
READ BINARY с SFI:
  P1[7] = 1 → SFI mode
  P1[6:1] = SFI value (1-30)
  P1[0] = 0 (RFU)

Пример: READ EF_ICCID по SFI
  00 B0 81 00 0A → P1 = 0x81 (SFI=1, bit7=1)
```

---

## TERMINAL PROFILE — Ключевые биты (первые 10 байт)

| Байт | Бит | Функция |
|---|---|---|
| 1 | 1 | Profile download |
| 1 | 2 | SMS-PP data download |
| 2 | 1 | DISPLAY TEXT |
| 2 | 2 | GET INKEY |
| 2 | 3 | GET INPUT |
| 2 | 6 | PLAY TONE |
| 2 | 7 | SET UP MENU |
| 2 | 8 | SELECT ITEM |
| 3 | 3 | SEND SHORT MESSAGE |
| 3 | 4 | SET UP CALL |
| 4 | 1 | PROVIDE LOCAL INFO |
| 4 | 2 | SET UP EVENT LIST |
| 4 | 6 | TIMER MANAGEMENT |
| 4 | 8 | SEND DTMF |
| 5 | 1 | CALL CONTROL |
| 5 | 3 | LAUNCH BROWSER |
| 8 | 1 | OPEN CHANNEL (BIP) |
| 8 | 2 | CLOSE CHANNEL |
| 8 | 4 | SEND DATA |
| 8 | 5 | RECEIVE DATA |
| 10 | 1 | ACTIVATE |

## Связанные

- APDU: [[wiki/concepts/APDU]]
- Status Words: [[wiki/reference/Status_Words]]
- CAT/STK: [[wiki/concepts/CAT_STK]]
- JavaCard APIs: [[wiki/reference/JavaCard_APIs]]
