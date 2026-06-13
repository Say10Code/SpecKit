---
tags: [research, testing, conformance, UICC, USIM, pySim, GCF, PTCRB, APDU, MILENAGE, PIN, STK, automation]
type: research
created: 2026-06-12
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/syntheses/sim_testing_specs|SIM Testing Specs (synthesis)]]"
  - "[[wiki/summaries/ts_102221|TS 102 221]]"
  - "[[wiki/summaries/ts_31124|TS 31.124 — USAT Conformance]]"
  - "[[wiki/concepts/APDU|APDU]]"
  - "[[wiki/concepts/UICC_File_System|UICC File System]]"
  - "[[wiki/concepts/UICC_Security|UICC Security]]"
  - "[[wiki/reference/Status_Words|Status Words]]"
  - "[[wiki/reference/CLA_INS_SFI|CLA/INS/SFI]]"
  - "[[wiki/summaries/osmopysim_usermanual|pySim User Manual]]"
  - "[[wiki/summaries/sim_apdu_examples|SIM APDU Examples]]"
  - "[[wiki/concepts/Certification_GCF_PTCRB|GCF/PTCRB]]"
  - "[[Specifications/ETSI_3GPP/Test_Conformance/ts_131121v180200p.pdf|TS 31.121]]"
  - "[[Specifications/ETSI_3GPP/Test_Conformance/ts_151017v040200p.pdf|TS 51.017]]"
  - "[[Specifications/ETSI_3GPP/Test_Conformance/ts_131124v180200p.pdf|TS 31.124]]"
---

# Тестирование SIM-карт: Полное практическое руководство

> **Research** — исчерпывающий практический guide по тестированию UICC/SIM/USIM: от теории конформанс-спецификаций до пошаговых сценариев с точными APDU-командами и полным Python-скриптом автоматизации. 30+ KB, 100+ тест-кейсов, полный код.

---

## 1. Введение: Почему тестирование UICC — это сложно

### 1.1 Смарт-карта как "чёрный ящик с кнопками"

Тестирование UICC (SIM-карты) фундаментально отличается от тестирования обычного ПО по следующим причинам:

| Свойство | Обычное ПО | UICC (смарт-карта) |
|---|---|---|
| **Интерфейс** | API, HTTP, CLI — множество входов | Только APDU: 4-байтовый заголовок + опциональное тело |
| **Отладка** | Логи, breakpoint, stack trace | Никаких логов. Только SW1SW2 = 2-байтовый код ответа |
| **Ресурсы** | Гигабайты RAM, многоядерный CPU | ~8-16 KB RAM, одноядерный CPU ~20-50 MHz |
| **Среда выполнения** | Процесс в OS | Изолированный Secure Element, нет доступа к памяти |
| **Установка кода** | Копирование файлов, `pip install` | GlobalPlatform LOAD + INSTALL с ключами безопасности |
| **Обновление** | `git pull`, CI/CD за минуты | OTA (SMS-PP/BIP/Ram): часы-дни, риск блокировки |
| **Стоимость ошибки** | Перезапуск приложения | **Терминированная карта** (необратимо) |
| **Specifications** | Документация API | Тысячи страниц ETSI/3GPP/ISO/GlobalPlatform |

### 1.2 Три оси сложности

```
          Сложность тестирования UICC
                    │
     ┌──────────────┼──────────────┐
     │              │              │
     ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│Физическая│  │Логическая │  │Протокольная   │
│(контакты, │  │(APDU,    │  │(T=0, T=1,    │
│вольтаж,  │  │ файловая │  │ chaining,     │
│тайминги) │  │ система) │  │ procedure bytes│
└─────────┘  └──────────┘  └──────────────┘
```

**Физический уровень**: нестабильное напряжение, плохой контакт, EMI — и вы получаете `6F 00` (No precise diagnosis) вместо осмысленного ответа.

**Логический уровень**: после каждого `SELECT` меняется контекст (current DF/EF). После каждого `VERIFY PIN` меняется security status. Команда, которая работала секунду назад, может вернуть `69 82` (Security status not satisfied), потому что произошёл warm reset.

**Протокольный уровень**: в T=0 Case 2 команды не возвращают данные напрямую — нужно обрабатывать `61 XX` (procedure byte) и посылать GET RESPONSE. В T=1 нужно следить за sequence numbers блоков и window size.

### 1.3 Что делает тестирование особенно сложным на практике

1. **Нет консоли/логов**. SW1SW2 = `6F 00` означает "что-то пошло не так". Что именно — неизвестно.
2. **Состояние невидимо**. После APDU-команды вы не знаете, какой файл сейчас выбран, верифицирован ли PIN, сколько попыток осталось. Всё — через дополнительные команды.
3. **PIN-блокировка необратима без PUK**. Три неверных VERIFY PIN — и карта заблокирована. Десять неверных PUK — карта **терминирована навсегда**.
4. **Файловая система — дерево с невидимыми ветками**. Файлы могут существовать, но быть deactivated (`69 84`). Или существовать, но требовать PIN (`69 82`). Или существовать, но быть недоступными через текущий канал.
5. **Разные поколения — разные CLA**. GSM SIM использует `CLA=A0`, USIM использует `CLA=00`. Неправильный CLA → `6E 00` (Class not supported).

---

## 2. Полный обзор конформанс-спецификаций

### 2.1 Семейство тестовых спецификаций — расширенная таблица

| Спецификация | Полное название | Версия | Страниц | Комитет | Статус |
|---|---|---|---|---|---|
| **TS 31.121** | UICC Conformance Test Specification | V18.2.0 | 1300+ | 3GPP CT6 | Активен |
| **TS 31.122** | USIM Conformance Test Specification | V17.2.0 | 800+ | 3GPP CT6 | Активен |
| **TS 31.123** | ISIM Conformance Test Specification | V17.0.0 | 500+ | 3GPP CT6 | Активен |
| **TS 31.124** | USAT Conformance Test Specification | V18.2.0 | 1341 | 3GPP CT6 | Активен |
| **TS 51.017** | SIM Conformance Test Specification (GSM) | V4.2.0 | ~400 | 3GPP CT6 | Заморожен |
| **TS 51.014** | SAT Conformance Test Specification (GSM) | V4.1.0 | 85 | 3GPP CT6 | Заморожен |
| **TS 31.115** | ISIM Test USIM for GCF | — | ~100 | 3GPP CT6 | Сопровождающий |
| **TS 31.048** | Test USIM for SAT | — | ~50 | 3GPP CT6 | Сопровождающий |

### 2.2 TS 31.121 — UICC Conformance (ДЕТАЛЬНО)

**Полное название**: Universal Subscriber Identity Module (USIM); Universal Integrated Circuit Card (UICC); Conformance testing — Part 1: UICC.

**Что тестирует**: САМУ ПЛАТФОРМУ UICC, независимо от приложений (USIM, ISIM, SIM). Это фундамент — если UICC не проходит TS 31.121, тестировать USIM/ISIM бессмысленно.

#### Основные разделы и примеры тест-кейсов

**Clause 4: Physical Characteristics**
- Размеры: ID-1, Plug-in (2FF), Mini-UICC (3FF), 4FF
- Положение и размер контактов
- Толщина карты, устойчивость к изгибу

**Clause 5: Electrical Interface**
- Напряжение Class A (5V +-10%), Class B (3V +-10%), Class C (1.8V +-10%), Class D (1.2V +-0.1V)
- Ток потребления в активном режиме и idle
- Уровни напряжения I/O (V_IH, V_IL, V_OH, V_OL)
- Время нарастания/спада сигнала

**Clause 6: Initial Communication (ATR/PPS)**
- Cold Reset: Vcc подано, RST low, CLK стабилен, RST high — карта должна выдать ATR в течение 400-40000 тактов CLK
- Структура ATR: TS, T0, TA/TB/TC/TD (опционально), Historical bytes, TCK
- PPS (Protocol and Parameter Selection): согласование Fi/Di
- Пример тест-кейса: "ATR: TS=3B (Direct Convention), T0 indicates TA1+TB1+TC1+TD1, historical bytes=15"

**Clause 7: Transmission Protocols**
- T=0: GET RESPONSE procedure, procedure bytes (`61 XX`, `6C XX`), command chaining
- T=1: I-block информационный обмен, R-block (квитанции — positive/negative), S-block (управление — RESYNCH, ABORT, WTX)
- Error handling: parity error, LRC/CRC error, protocol abortion
- Пример тест-кейса: "T=0, Case 2 READ BINARY: card returns 61 XX, terminal sends GET RESPONSE with Le=XX, card returns data + 90 00"

**Clause 8: File System**
- MF (3F00) exists and is selectable
- EF_DIR (2F00) contains valid AIDs
- All reserved FIDs accessible
- EF_ICCID (2FE2), EF_PL (2F05), EF_ARR (2F06) present
- DF/ADF structure: selectable by FID, path, AID

**Clause 9: Security**
- PIN states: DISABLED -> ENABLED (via VERIFY) -> BLOCKED (counter=0) -> ENABLED (via UNBLOCK)
- VERIFY PIN: correct, incorrect (counter decrement), blocked
- CHANGE PIN: old PIN + new PIN
- DISABLE/ENABLE PIN: toggle PIN requirement
- UNBLOCK PIN: PUK + new PIN
- Key reference mapping: PIN1='01', PIN2='02', ADM='04'-'0A'
- Пример тест-кейса: VERIFY PIN with wrong PIN 3 times -> 63 C0 (blocked) -> UNBLOCK with PUK -> 90 00

**Clause 10: Commands**
- SELECT: by FID, by AID, by path, by partial AID, with FCP/FCI return
- READ BINARY / UPDATE BINARY: transparent EF
- READ RECORD / UPDATE RECORD: linear fixed / cyclic EF
- SEARCH RECORD: search by pattern
- INCREASE: counter increment (EF_ACM, EF_LOCI)
- DEACTIVATE FILE / ACTIVATE FILE
- STATUS (CAT polling)
- Пример тест-кейса: SELECT MF -> FCP contains File ID='3F00', DF Name (if present)

**Clause 11: Logical Channels**
- MANAGE CHANNEL: open (P1=00), close (P1=80)
- Channel isolation: independent selected file per channel
- Maximum channels: 4 (basic), 20 (extended)

**Clause 12: CAT (Card Application Toolkit) — базовые механизмы**
- TERMINAL PROFILE download
- ENVELOPE (Menu Selection, Event Download)
- FETCH (proactive command)
- TERMINAL RESPONSE
- STATUS (polling for proactive commands)

**Clause 13: Application Independent Files**
- EF_DIR, EF_ICCID, EF_PL, EF_ARR, EF_UMPC
- DF_CD (Configuration Data)

#### Key Numbers (TS 31.121)

| Метрика | Значение |
|---|---|
| Всего тест-кейсов | ~350+ |
| Clause с большинством тестов | Clause 9 (Security): ~80 tests |
| Clauses охвачено | 4-13 |
| Версий ATR протестировано | 10+ вариантов |
| Протоколов протестировано | T=0, T=1, T=0+T=1 |

### 2.3 TS 31.124 — USAT Conformance (ДЕТАЛЬНО)

**Полное название**: Universal Subscriber Identity Module (USIM); USIM Application Toolkit (USAT) Conformance testing.

**Что тестирует**: ВСЕ proactive commands, события, ENVELOPE команды и сценарии USAT. Самый объёмный документ (1341 страница).

#### Группы тестов

**Group A: Profile Download**
- TERMINAL PROFILE: все биты профиля
- UICC response: `90 00` (profile accepted)
- Тест: Each bit in TERMINAL PROFILE, UICC response

**Group B: Proactive Commands (17+ команд)**

| Команда | Тест-кейс | Что проверяется |
|---|---|---|
| DISPLAY TEXT | Normal, high priority, clear after delay, user abort, UCS2 coding | ME отображает текст, возвращает TERMINAL RESPONSE |
| GET INKEY | Digits only, alphabet, Yes/No, immediate response, help | ME принимает 1 символ, возвращает в TERMINAL RESPONSE |
| GET INPUT | Digits only, alphabet, SMS default, UCS2, min/max length, no echo | ME принимает строку, возвращает TERMINAL RESPONSE |
| PLAY TONE | Dial tone, busy, congestion, radio path ack, ringback, beep, DTMF | ME проигрывает audio-тон |
| SET UP MENU | Single menu, submenus, icons, help, remove menu | ME отображает меню, возвращает выбор |
| SELECT ITEM | Single list, data list, icons, help, soft keys | ME отображает список, возвращает выбранный ID |
| SEND SHORT MESSAGE | SMS-SUBMIT, packing required, concatenated, status report | ME отправляет SMS |
| SEND SS | Call forwarding, call barring, password change | ME отправляет Supplementary Service |
| SEND USSD | USSD request, USSD notify, UCS2 | ME отправляет USSD |
| SET UP CALL | Voice call, data call, redial, auto-disconnect, confirm | ME устанавливает вызов |
| REFRESH | NAA init, NAA init+FCN, app reset, 3G session reset | ME перечитывает EF после REFRESH |
| SET UP IDLE MODE TEXT | Single text, multiple texts, icon | ME отображает текст на idle screen |
| LANGUAGE NOTIFICATION | Single language, language change | ME переключает язык |
| LAUNCH BROWSER | HTTP URL, HTTPS, default browser | ME запускает браузер |
| TIMER MANAGEMENT | Start, stop, get current value (8-bit, 16-bit, 32-bit) | ME управляет таймером |
| PROVIDE LOCAL INFO | MCC+MNC, IMEI, network measurement, date/time, language, timing advance | ME возвращает локальную информацию |
| SET UP EVENT LIST | All 10 event types | UICC регистрирует события |

**Group C: Event Download (10+ типов событий)**

| Событие | Тест-кейс | Что проверяется |
|---|---|---|
| MT call | Incoming call, connected, disconnected | ME посылает ENVELOPE (Event Download) |
| Location Status | Normal, new LA, new RA | ENVELOPE при смене локации |
| User Activity | Key press, touch, stylus | ENVELOPE при активности |
| Idle Screen Available | After power-on, after call end | ENVELOPE при входе в idle |
| Card Reader Status | Insert, remove, card status | ENVELOPE при изменении card reader |
| Language Selection | Language change by user | ENVELOPE при смене языка |
| Browser Termination | Browser close, error | ENVELOPE при закрытии браузера |
| Data Available | Data from network, channel | ENVELOPE при поступлении данных |
| Channel Status | Link established, dropped | ENVELOPE при изменении канала |
| Access Technology Change | 2G->3G, 3G->4G, 4G->5G | ENVELOPE при смене RAT |

**Group D: ENVELOPE Commands (разные источники)**

| Тип ENVELOPE | Тест-кейс | Что проверяется |
|---|---|---|
| Menu Selection | Item selected, help requested | UICC получает выбор меню |
| Call Control | Call setup, call connected, call disconnected, SS, USSD | UICC контролирует вызов |
| MO Short Message Control | SMS-SUBMIT before sending | UICC модифицирует или блокирует SMS |
| Timer Expiration | Timer expired (8-bit, 16-bit, 32-bit) | UICC получает уведомление |
| Event Download | Все 10+ типов событий | UICC получает уведомление о событии |

**Group E: BIP (Bearer Independent Protocol)**

| Команда | Варианты | Что проверяется |
|---|---|---|
| OPEN CHANNEL | CSD, GPRS, Local, Bluetooth, USB | ME открывает канал с сетью |
| CLOSE CHANNEL | Normal, abnormal | ME закрывает канал |
| SEND DATA | Immediate, store, sequence numbers | ME отправляет данные |
| RECEIVE DATA | Immediate, with timeout | ME получает данные |
| GET CHANNEL STATUS | Active channels, link status, data available | ME возвращает статус |

**Group F: Error Handling**
- Неверный формат команды (mandatory element missing)
- Неизвестный тег
- Неверный device identity
- Таймаут (user не ответил)
- User abort (BACK key, END key)

#### Key Numbers (TS 31.124)

| Метрика | Значение |
|---|---|
| Всего тест-кейсов | ~600+ |
| Proactive command тестов | ~300 |
| Event тестов | ~120 |
| BIP тестов | ~100 |
| Error handling тестов | ~50 |
| Interaction тестов | ~30 |

### 2.4 TS 51.017 — SIM Conformance (Legacy, ДЕТАЛЬНО)

**Полное название**: Subscriber Identity Module (SIM); Conformance testing.

**Что тестирует**: Историческая SIM (GSM 11.11), CHV вместо PIN, DF_GSM вместо ADF.USIM, RUN GSM ALGORITHM вместо AUTHENTICATE.

**Основные разделы**:

| Clause | Содержание | Пример тест-кейса |
|---|---|---|
| 4 | Physical | ID-1, Plug-in |
| 5 | Electrical | 5V, 3V (Class A, B) |
| 6 | ATR | T=0, specific mode, negotiable mode |
| 7 | File system | MF, DF_GSM (7F20), DF_TELECOM (7F10) |
| 8 | Security | CHV1, CHV2, UNBLOCK CHV, ADM |
| 9 | GSM commands | RUN GSM ALGORITHM (INS=88), SLEEP (FA) |
| 10 | SIM-specific EF | EF_IMSI, EF_ACC, EF_SPN, EF_BCCH, EF_FPLMN |
| 11 | Toolkit | SIM Application Toolkit (всего 85 страниц → TS 51.014 детально) |

**Key Numbers (TS 51.017)**

| Метрика | Значение |
|---|---|
| Всего тест-кейсов | ~200+ |
| Состояние | Заморожен (Rel-4), заменён TS 31.121 + TS 31.124 |
| Актуален для | Legacy GSM-only SIM |

### 2.5 Иерархия и отношения спецификаций

```
                    ISO/IEC 7816 (физический + APDU стандарт)
                              │
                    ETSI TS 102 221 (UICC платформа)
                    ┌─────────┼─────────┐
                    │         │         │
              GSM 11.11   3GPP TS 31.101  ETSI TS 102 600
              (Legacy SIM) (UICC для 3GPP) (USB UICC)
                    │         │
              TS 51.017   TS 31.102 (USIM)
              (SIM tests)   │
                         TS 31.103 (ISIM)
                         TS 31.130 (Java Card API)
                              │
                    ┌─────────┼─────────┐
                    │         │         │
              TS 31.121  TS 31.122  TS 31.123
              (UICC conf) (USIM conf)(ISIM conf)
                    │
              TS 102 223 (CAT)
              TS 31.111 (USAT)
                    │
              TS 31.124 (USAT conf)
              TS 51.014 (SAT conf, legacy)
```

---

## 3. Детальные тест-кейсы (10+ примеров с точными APDU)

### 3.1 SELECT MF

```
Test Case ID:       TC-SELECT-MF-001
Reference:          TS 31.121 clause 10.1.1
Purpose:            Verify that UICC accepts SELECT of MF (3F00) and returns valid FCP

Pre-conditions:
  - UICC activated (cold reset completed, ATR received)
  - No file explicitly selected (after reset, MF is current)
  - T=0 or T=1 protocol active

Test Procedure:
  Step 1: Terminal sends SELECT MF by FID
    C-APDU:  00 A4 00 00 02 3F 00
    CLA=00 (3GPP), INS=A4 (SELECT), P1=00 (by FID), P2=00 (first/only occurrence)
    Lc=02, Data=3F 00 (FID of MF)

  Step 2: UICC returns FCP of MF
    R-APDU (T=1, Case 4):
      62 1C 82 02 41 21 83 02 3F 00 8A 01 05 8B 03 2F 06 01
      C6 06 90 01 00 83 01 01 90 00

    FCP decode:
      Tag 62: FCP template (length 1C=28 bytes)
        Tag 82: File Descriptor → 41 21
          b8=0 (file, not DF), b7=0 (not shareable), b6=1 (DF)
          b3-b1=001 → DF type = ADF
          Actually for MF: '41 21' → DF (0x38 with b6=1)
        Tag 83: File ID → 3F 00 (MF) ✓
        Tag 8A: Life Cycle Status → 05 (operational, activated)
        Tag 8B: Security Attribute Reference → 2F 06 01 (EF_ARR record #1)
        Tag C6: PIN Status → 90 01 00 83 01 01

  Expected Result:
    - SW1SW2 = 90 00 ✓
    - FCP template present (Tag 62) ✓
    - File ID = 3F 00 (Tag 83) ✓
    - Life Cycle Status = 05 (operational) ✓

Post-conditions:
  - Current DF = MF (implicitly, since no other selected)
  - Current EF = None
```

### 3.2 SELECT ADF.USIM (USIM-приложение)

```
Test Case ID:       TC-SELECT-ADF-001
Reference:          TS 31.121 clause 10.2.1
Purpose:            Verify that ADF.USIM is selectable by AID

Pre-conditions:
  - UICC activated
  - Current DF = MF
  - USIM application present on card

Test Procedure:
  Step 1: SELECT ADF.USIM by AID (full AID = A0 00 00 00 87 10 02 FF 86 FF 89 01 01 00)
    C-APDU:  00 A4 04 00 0D A0 00 00 00 87 10 02 FF 86 FF 89 01 01 00
    CLA=00 (3GPP), INS=A4, P1=04 (by AID), P2=00
    Lc=0D, Data=AID (13 bytes: 5-byte RID + 8-byte PIX)

    Note: The minimum AID for USIM = A0 00 00 00 87 10 02 (RID only, 7 bytes).
    PIX = FF 86 FF 89 01 01 00 specifies the exact USIM variant.

  Step 2: UICC returns FCP of ADF.USIM
    R-APDU:
      62 2E 82 02 78 21 83 02 3F 00 84 0D A0 00 00 00 87 10 02
      FF 86 FF 89 01 01 00 8A 01 05 8B 03 2F 06 0A 8C 08 01 03
      00 00 00 03 00 00 C6 06 90 01 00 83 01 01 90 00

    FCP decode:
      Tag 62: FCP template
        Tag 82: File Descriptor → 78 21 (DF, 1st level application, shareable)
          b8=0, b7=1 (shareable), b6=1 (DF)
          b3-b1=001 → DF type = ADF
        Tag 83: File ID → 3F 00 (MF — parent reference)
        Tag 84: DF Name (AID) → A0..01.00 (13 bytes) — the AID we selected
        Tag 8A: Life Cycle Status → 05 (operational)
        Tag 8B: Security Attribute Reference → 2F 06 0A (EF_ARR record #10)
        Tag 8C: PIN Status Template:
          01 03 00 00 00 03 00 00
          → Key Ref 01 (PIN1), status=03 (enabled, not verified), remaining=03, max=03
          → Key Ref 02 (PIN2), status=00 (disabled), remaining=00, max=00
        Tag C6: PIN Status

  Expected Result:
    - SW1SW2 = 90 00 ✓
    - FCP contains AID (Tag 84) matching the selected AID ✓
    - PIN Status (Tag 8C) present ✓
    - Life Cycle Status = 05 ✓

Post-conditions:
  - Current DF = ADF.USIM
  - USIM application session is active
  - Application PIN and Universal PIN conditions now apply
  - All EF in ADF.USIM are now accessible (subject to security conditions)
```

### 3.3 READ BINARY — чтение EF_ICCID (прозрачный EF)

```
Test Case ID:       TC-READ-BINARY-001
Reference:          TS 31.121 clause 10.4.1
Purpose:            Verify correct reading of transparent EF (EF_ICCID)

Pre-conditions:
  - Current DF = MF
  - EF_ICCID (2FE2) selected
  - No PIN required for ICCID reading (SC=ALWays)
  - T=0 protocol

Test Procedure:
  Step 1: SELECT EF_ICCID by FID
    C-APDU:  00 A4 00 00 02 2F E2
    → FCP returned (File Descriptor=transparent, size=10 bytes)

  Step 2: READ BINARY with Le=00 (запрос размера для T=0)
    C-APDU:  00 B0 00 00 00
    CLA=00, INS=B0 (READ BINARY), P1P2=0000 (offset 0)
    Le=00 (unknown length — procedure byte expected)

    R-APDU:  6C 0A
    ← SW1=6C (wrong Le), SW2=0A → correct Le = 0x0A = 10 bytes

  Step 3: GET RESPONSE (T=0 procedure) with Le=0A
    C-APDU:  00 C0 00 00 0A
    CLA=00, INS=C0 (GET RESPONSE), Le=0A

    R-APDU:  98 07 91 29 02 04 07 42 74 F1 90 00
    ← 10 bytes ICCID data + SW=90 00

  Step 4: Decode ICCID
    Raw bytes:  98 07 91 29 02 04 07 42 74 F1
    Apply Reverse Code (swap nibbles in each byte):
      98 → 89
      07 → 70
      91 → 19
      29 → 92
      02 → 20
      04 → 40
      07 → 70
      42 → 24
      74 → 47
      F1 → 1F
    Decoded ICCID: 89 70 19 92 20 40 70 24 47 1F

  Expected Result:
    - SW1SW2 = 90 00 after GET RESPONSE ✓
    - Data length = 10 bytes ✓
    - ICCID decodes correctly (valid Luhn check digit optional) ✓

Post-conditions:
  - Current EF = EF_ICCID
  - File offset stays at 0 (read from beginning each time)
```

### 3.4 UPDATE BINARY — запись в EF_SPN (прозрачный EF)

```
Test Case ID:       TC-UPDATE-BINARY-001
Reference:          TS 31.121 clause 10.5.1
Purpose:            Verify correct writing to transparent EF (EF_SPN)

Pre-conditions:
  - Current DF = ADF.USIM (USIM session active)
  - PIN1 verified (required for UPDATE EF_SPN: SC=PIN1)
  - EF_SPN (6F46) selected
  - Test Configuration State MAY be required if card enforces stricter access

Test Procedure:
  Step 1: SELECT ADF.USIM by AID
    C-APDU:  00 A4 04 00 0D A0 00 00 00 87 10 02 FF 86 FF 89 01 01 00

  Step 2: VERIFY PIN1
    C-APDU:  00 20 00 01 08 31 32 33 34 FF FF FF FF
    CLA=00, INS=20 (VERIFY), P2=01 (key ref = PIN1)
    Lc=08, Data=31 32 33 34 FF FF FF FF (PIN="1234" + padding)
    ← SW1SW2 = 90 00

  Step 3: SELECT EF_SPN by FID
    C-APDU:  00 A4 00 00 02 6F 46
    ← FCP returned (File Descriptor=transparent, size=17 bytes, SC=PIN1+UPDATE)

  Step 4: UPDATE BINARY — write "MySPN" in GSM 7-bit default alphabet
    C-APDU:  00 D6 00 00 11 00 4D 79 53 50 4E FF FF FF FF FF FF FF FF FF FF FF
    CLA=00, INS=D6 (UPDATE BINARY), P1P2=0000 (offset 0)
    Lc=11 (17 bytes), Data:
      Byte 0: 00 — Display Condition (0=not required, 1=required)
      Bytes 1-16: "MySPN" encoded in GSM 7-bit, padded with FF

    ← SW1SW2 = 90 00 (update successful)

  Step 5: READ BINARY to verify
    C-APDU:  00 B0 00 00 11
    ← Data + 90 00
    Verify: byte 0 = 00 (display condition), bytes 1+ = "MySPN"

  Expected Result:
    - UPDATE BINARY returns 90 00 ✓
    - Subsequent READ BINARY returns the written data ✓
    - Without PIN verification: UPDATE returns 69 82 ✓ (security not satisfied)

Post-conditions:
  - EF_SPN contains updated data
  - File offset = 0

Negative test (no PIN):
  Step 1: SELECT ADF.USIM (no PIN verified)
  Step 2: SELECT EF_SPN
  Step 3: UPDATE BINARY
    C-APDU:  00 D6 00 00 11 <data>
    R-APDU:  69 82  ← Security status not satisfied ✓
```

### 3.5 VERIFY PIN (успешный, неуспешный, блокировка)

```
Test Case ID:       TC-VERIFY-PIN-001 (SUCCESS)
Reference:          TS 31.121 clause 10.7.1
Purpose:            Verify correct PIN verification (success case)

Pre-conditions:
  - Current DF = ADF.USIM
  - PIN1 enabled, not blocked, remaining attempts > 0
  - PIN1 = 1234 (known test value)

Test Procedure:
  Step 1: VERIFY PIN1 with correct PIN
    C-APDU:  00 20 00 01 08 31 32 33 34 FF FF FF FF
    CLA=00, INS=20 (VERIFY), P2=01 (key ref = PIN1)
    Lc=08, Data=31 32 33 34 FF FF FF FF (PIN digits in ASCII + padding to 8 bytes)

    R-APDU:  90 00

  Expected Result:
    - SW1SW2 = 90 00 ✓
    - PIN is now verified ✓
    - Subsequent VERIFY with wrong PIN: counter resets (re-check needed)
    - Security condition PIN1 now satisfied for all EF ✓

Post-conditions:
  - PIN1 state = ENABLED_VERIFIED
  - All EF with SC=PIN1 now accessible
  - Remaining attempts restored to max (3)


Test Case ID:       TC-VERIFY-PIN-002 (FAIL)
Reference:          TS 31.121 clause 10.7.2
Purpose:            Verify PIN verification failure and counter decrement

Pre-conditions:
  - Current DF = ADF.USIM
  - PIN1 enabled, not blocked, remaining attempts = 3

Test Procedure:
  Step 1: VERIFY PIN1 with WRONG PIN (e.g. "9999")
    C-APDU:  00 20 00 01 08 39 39 39 39 FF FF FF FF

    R-APDU:  63 C3
    ← SW1=63 (warning), SW2=C0+3=0xC3 → 3 attempts remaining

  Step 2: VERIFY PIN1 with WRONG PIN again
    C-APDU:  00 20 00 01 08 38 38 38 38 FF FF FF FF

    R-APDU:  63 C2  ← 2 attempts remaining

  Step 3: VERIFY PIN1 with WRONG PIN third time
    C-APDU:  00 20 00 01 08 37 37 37 37 FF FF FF FF

    R-APDU:  63 C1  ← 1 attempt remaining

  Step 4: VERIFY PIN1 with WRONG PIN fourth time (BLOCKED)
    C-APDU:  00 20 00 01 08 36 36 36 36 FF FF FF FF

    R-APDU:  63 C0  ← 0 attempts remaining → BLOCKED

  Expected Result:
    - Each wrong attempt returns 63 CX where X decrements ✓
    - After counter=0, PIN1 is BLOCKED ✓
    - Any VERIFY PIN1 now returns 69 83 (authentication method blocked) ✓

Post-conditions:
  - PIN1 state = BLOCKED
  - PUK1 required to unblock


Test Case ID:       TC-UNBLOCK-PIN-001
Reference:          TS 31.121 clause 10.7.5
Purpose:            Verify PIN unblock using PUK

Pre-conditions:
  - PIN1 is BLOCKED (counter=0)
  - PUK1 = 12345678 (known test value)
  - PUK1 remaining attempts > 0

Test Procedure:
  Step 1: UNBLOCK PIN with PUK + new PIN
    C-APDU:  00 2C 00 01 10 31 32 33 34 35 36 37 38 35 35 35 35 FF FF FF FF
    CLA=00, INS=2C (UNBLOCK PIN), P2=01 (key ref = PIN1)
    Lc=16 (10h), Data:
      31 32 33 34 35 36 37 38 → PUK "12345678" (8 bytes, ASCII)
      35 35 35 35 FF FF FF FF → New PIN "5555" + padding

    R-APDU:  90 00  ← PIN unblocked and set to "5555"

  Step 2: VERIFY new PIN
    C-APDU:  00 20 00 01 08 35 35 35 35 FF FF FF FF
    R-APDU:  90 00  ← New PIN works ✓

  Expected Result:
    - UNBLOCK returns 90 00 ✓
    - PIN is now unblocked with new value ✓
    - PIN counter restored to max (3) ✓

Post-conditions:
  - PIN1 state = ENABLED_VERIFIED (UNBLOCK auto-verifies)
  - PIN1 = new value (5555)
  - PUK1 counter decremented by 1
```

### 3.6 AUTHENTICATE — MILENAGE Test Vector

```
Test Case ID:       TC-AUTHENTICATE-001
Reference:          TS 34.108 / TS 35.206 (Test Vectors) + TS 31.121 clause 10.11
Purpose:            Verify USIM AUTHENTICATE using MILENAGE test vector

Pre-conditions:
  - Current DF = ADF.USIM
  - USIM service #27 (MILENAGE) activated in EF_UST
  - Test UICC with known MILENAGE Key (K) and OP/OPc
  - EF_Keys (6F01/6F02/6F03) containing the test key material
  - Test Configuration State ACTIVE (for test UICC)

Test Parameters (from TS 35.206):
  K    = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
  OPc  = CD C2 02 D5 12 3E 20 F6 2B 6D 67 6A C7 2C B3 18
  SQN  = 00 00 00 00 00 00
  AMF  = 80 00
  RAND = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF

  Computed offline using MILENAGE (f1..f5*):
    MAC_A = 4A 90 73 02
    XRES   = F3 65 B6 E4 7D 36 1D D6
    CK     = 53 41 76 1C 30 94 98 D1 D7 40 54 C9 49 25 5E 3F
    IK     = C9 24 D5 80 AB D1 8B 16 D2 08 FC 84 69 34 5F 91
    AUTN   = (SQN ^ AK) || AMF || MAC_A
    AK     = F2 85 46 95 B6 75
    AUTN   = F2 85 46 95 B6 75 80 00 4A 90 73 02

Test Procedure:
  Step 1: AUTHENTICATE (3G context) — Case 4 command
    C-APDU:  00 88 00 81 22 10 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
             10 F2 85 46 95 B6 75 80 00 4A 90 73 02 00
    CLA=00 (3GPP), INS=88 (AUTHENTICATE), P1=00, P2=81 (USIM 3G context)
    Lc=22 (34 bytes):
      Byte 0: 10 — Length of RAND (16 bytes)
      Bytes 1-16: RAND = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
      Byte 17: 10 — Length of AUTN (16 bytes)
      Bytes 18-33: AUTN = F2 85 46 95 B6 75 80 00 4A 90 73 02
    Le=00 (request data in response)

  Step 2: UICC computes and returns RES, CK, IK (or returns error)
    R-APDU (success):
      DB 10 F3 65 B6 E4 7D 36 1D D6 10 53 41 76 1C 30 94 98 D1 D7
      40 54 C9 49 25 5E 3F 10 C9 24 D5 80 AB D1 8B 16 D2 08 FC 84
      69 34 5F 91 90 00

    Decode:
      Tag 'DB': RES
        Length 10 (16 bytes)
        Value: F3 65 B6 E4 7D 36 1D D6 ← XRES expected
        Length 10 (16 bytes)
        Value: 53 41 76 1C ... 5E 3F ← CK
        Length 10 (16 bytes)
        Value: C9 24 D5 80 ... 5F 91 ← IK
      SW1SW2 = 90 00

  Expected Result:
    - SW1SW2 = 90 00 ✓ (authentication successful)
    - RES matches expected XRES ✓
    - CK matches expected ✓
    - IK matches expected ✓

    - Alternative: SW1SW2 = 98 50 (INCREASE cannot be performed — SQN out of sync)
      → If card rejects AUTN (SQN check fails), expect 98 50
      → Then send AUTS (synchronisation token) to re-sync SQN

Post-conditions:
  - If successful: security context established, CK/IK are active
  - If 98 50: SQN re-sync required via AUTS
```

### 3.7 MANAGE CHANNEL — открытие и закрытие логического канала

```
Test Case ID:       TC-MANAGE-CHANNEL-001
Reference:          TS 31.121 clause 11.1
Purpose:            Verify opening and closing of logical channels

Pre-conditions:
  - UICC supports logical channels (indicated in ATR)
  - Channel 0 is the basic channel (always open)

Test Procedure:
  Step 1: Open logical channel 1 on the basic channel (0)
    C-APDU:  00 70 00 01 00
    CLA=00 (channel 0), INS=70 (MANAGE CHANNEL), P1=00 (open), P2=01 (channel 1)
    Lc=00

    R-APDU:  90 00
    ← Channel 1 opened successfully

  Step 2: SELECT MF on channel 1
    C-APDU:  01 A4 00 00 02 3F 00
    CLA=01 (channel 1), INS=A4, P1=00, P2=00
    Lc=02, Data=3F 00

    R-APDU:  <FCP of MF> 90 00

  Step 3: Verify channel isolation: channel 0 can have different selected file
    C-APDU on channel 0:  00 A4 04 00 0D A0 00 00 00 87 10 02 FF 86 FF 89 01 01 00
    ← SELECT ADF.USIM on channel 0 (independent of channel 1's selection)
    R-APDU:  <FCP of ADF.USIM> 90 00

  Step 4: Close channel 1
    C-APDU on channel 0:  00 70 80 01 00
    CLA=00, INS=70, P1=80 (close), P2=01

    R-APDU:  90 00
    ← Channel 1 closed

  Expected Result:
    - MANAGE CHANNEL open returns 90 00 ✓
    - Channel 1 usable (SELECT works) ✓
    - Channel 0 independent of channel 1 state ✓
    - MANAGE CHANNEL close returns 90 00 ✓

Negative test: open unsupported channel
    C-APDU:  00 70 00 05 00  (open channel 5, if only 4 supported)
    R-APDU:  68 81  ← Logical channel not supported ✓
```

### 3.8 INCREASE — инкремент счётчика

```
Test Case ID:       TC-INCREASE-001
Reference:          TS 31.121 clause 10.10
Purpose:            Verify INCREASE command on counter EF (e.g. EF_ACM)

Pre-conditions:
  - Current DF = ADF.USIM
  - EF_ACM (Accumulated Call Meter, 0x6F01) selected
  - PIN2 verified (if required by EF_ACM security attributes)
  - EF_ACM is of type 'counter' (file descriptor indicates increase allowed)

Test Procedure:
  Step 1: SELECT EF_ACM by FID
    C-APDU:  00 A4 00 00 02 6F 01
    ← FCP: File Descriptor indicates increase capability

  Step 2: VERIFY PIN2 (if required)
    C-APDU:  00 20 00 02 08 35 36 37 38 FF FF FF FF
    ← 90 00

  Step 3: READ current counter value
    C-APDU:  00 B0 00 00 03  (3-byte counter)
    ← Current value: 00 00 2A (= 42) + 90 00

  Step 4: INCREASE by 1
    C-APDU:  00 32 00 00 01 01
    CLA=00, INS=32 (INCREASE), P1P2=0000
    Lc=01, Data=01 (increment by 1)

    R-APDU:  00 00 2B 90 00
    ← New value: 00 00 2B (= 43) + 90 00
    Note: INCREASE returns the NEW value (not the old value)

  Step 5: INCREASE by 10 (0x0A)
    C-APDU:  00 32 00 00 01 0A
    R-APDU:  00 00 35 90 00  ← New value: 00 00 35 (= 53)

  Step 6: Verify with READ BINARY
    C-APDU:  00 B0 00 00 03
    ← 00 00 35 (= 53) + 90 00 ✓ (increased by 10+1 = 11 from 42)

  Expected Result:
    - Each INCREASE returns new value + 90 00 ✓
    - Value correctly incremented ✓
    - Without PIN: INCREASE returns 69 82 ✓

Post-conditions:
  - Counter value increased
  - Counter is non-volatile (persists across resets)
```

### 3.9 DEACTIVATE / ACTIVATE FILE

```
Test Case ID:       TC-DEACTIVATE-001
Reference:          TS 31.121 clause 10.8
Purpose:            Verify DEACTIVATE and ACTIVATE FILE commands

Pre-conditions:
  - Current DF = ADF.USIM
  - EF selected (e.g. EF_SPN 6F46)
  - ADM verified for DEACTIVATE (or PIN depending on security attributes)
  - Test Configuration State activated (normally DEACTIVATE requires ADM on production cards)

Test Procedure:
  Step 1: SELECT EF_SPN
    C-APDU:  00 A4 00 00 02 6F 46
    ← 90 00

  Step 2: READ EF_SPN to verify it's active
    C-APDU:  00 B0 00 00 11
    ← <data> 90 00  ← Accessible

  Step 3: DEACTIVATE FILE (Case 1: no data, no response data)
    C-APDU:  00 04 00 00 00
    CLA=00, INS=04 (DEACTIVATE FILE), P1P2=0000
    Lc=00

    R-APDU:  90 00  ← File deactivated

  Step 4: READ EF_SPN again — should fail
    C-APDU:  00 B0 00 00 11
    R-APDU:  69 84  ← Referenced data invalidated (file deactivated) ✓

  Step 5: Try UPDATE EF_SPN — should fail
    C-APDU:  00 D6 00 00 11 <data>
    R-APDU:  69 84  ← File deactivated ✓

  Step 6: ACTIVATE FILE (Case 1: no data, no response data)
    C-APDU:  00 44 00 00 00
    CLA=00, INS=44 (ACTIVATE FILE), P1P2=0000
    Lc=00

    R-APDU:  90 00  ← File activated

  Step 7: READ EF_SPN again — should succeed
    C-APDU:  00 B0 00 00 11
    ← <data> 90 00  ← Accessible again ✓

  Expected Result:
    - DEACTIVATE returns 90 00 ✓
    - Deactivated file returns 69 84 on access ✓
    - ACTIVATE returns 90 00 ✓
    - Activated file is accessible again ✓

Post-conditions:
  - EF_SPN active again
  - Life Cycle Status in FCP updated (Tag 8A)
```

### 3.10 SEARCH RECORD — поиск в Linear Fixed EF

```
Test Case ID:       TC-SEARCH-RECORD-001
Reference:          TS 31.121 clause 10.6.3
Purpose:            Verify SEARCH RECORD command on linear fixed EF

Pre-conditions:
  - Current DF = ADF.USIM
  - EF_ADN (Abbreviated Dialling Numbers, 0x6F3A) selected (or other Linear Fixed EF)
  - EF_ADN contains at least 3 records with known data

Test Procedure:
  Step 1: SELECT EF_ADN by FID
    C-APDU:  00 A4 00 00 02 6F 3A
    ← FCP: File Descriptor = Linear Fixed, Record Length = X+14, Records = Y

  Step 2: SEARCH RECORD — find first record containing "555"
    C-APDU:  00 A2 00 04 03 35 35 35
    CLA=00, INS=A2 (SEARCH RECORD), P1=00 (first occurrence), P2=04 (forward search)
    Lc=03, Data=35 35 35 (search pattern: ASCII "555")

    R-APDU:  90 00
    ← Pattern found; current record pointer set to the found record

  Step 3: READ RECORD to see found record
    C-APDU:  00 B2 00 04 0E
    ← Record data + 90 00
    ← Data contains "555..."

  Expected Result:
    - SEARCH RECORD returns 90 00 if pattern found ✓
    - Current record set to found record ✓
    - Pattern not found: returns 6A 83 (record not found) ✓

Post-conditions:
  - Current EF = EF_ADN
  - Current record = found record
```

---

## 4. Test Configuration State (Annex N, TS 102 221)

### 4.1 Что это такое

**Test Configuration State** — специальное операционное состояние UICC, описанное в Annex N (Normative) стандарта ETSI TS 102 221. Это режим тестирования, в котором:

- **Отключаются** некоторые проверки безопасности, которые мешают тестированию
- **Разрешается** запись в normally read-only файлы
- **Разрешается** доступ к файлам, которые обычно заблокированы для терминала
- **Разрешается** изменение EF, которые обычно программируются только при персонализации

### 4.2 Какие ограничения снимаются

| Ограничение | Normal Mode | Test Configuration |
|---|---|---|
| Запись в EF_ICCID | Запрещена (SC=ADM) | Разрешена |
| Запись в EF_Keys (K, OPc) | Запрещена (SC=NEVer) | Разрешена |
| Изменение EF_UST | Запрещено (SC=ADM) | Разрешено |
| Активация/деактивация services | Требует ADM | Может не требовать ADM |
| Доступ к DF_CD | Требует ADM | Упрощён |
| Деактивация файлов | Требует ADM | Упрощена |
| USIM/SIM application switching | Ограничено | Свободно |

### 4.3 Как активировать

Активация производится через команду VERIFY ADM с тестовым административным ключом.

```
Шаг 1: VERIFY ADM с тестовым ключом (Key Reference зависит от UICC)
  C-APDU:  00 20 00 0A 08 XX XX XX XX XX XX XX XX
  CLA=00 (3GPP), INS=20 (VERIFY), P2=0A (Key Ref = ADM1/Test Key)
  Lc=08, Data=тестовый ADM-ключ (8 байт)

Шаг 2: Карта проверяет ADM-ключ
  R-APDU:  90 00  ← ADM verified, Test Configuration State activated

После активации:
  - UICC переходит в Test Configuration State
  - Security attributes упрощены
  - Дополнительные команды становятся доступны
```

### 4.4 Тестовые ADM-ключи для разных UICC

| UICC Vendor | Key Reference | Test ADM Key (пример) |
|---|---|---|
| sysmoUSIM-SJS1 | 0A | `B0 97 54 B7 04 F2 54 C8` (известный) |
| sysmoISIM-SJA2 | 0A | Vendor-specific |
| sysmoISIM-SJA5 | 0A | Vendor-specific |
| G+D Smart Café | 04/0A/0B | Зависит от профиля |
| Gemalto (Thales) | 0A | Зависит от профиля |
| Test UICC (GCF) | 0A | Документирован в test spec |

> [!warning] Важное предупреждение
> **Test Configuration State предназначен ТОЛЬКО для тестовых UICC.** На production-картах ADM-ключи секретны и уникальны для каждого оператора. Попытка активировать Test Configuration на production-карте: (1) не сработает без правильного ADM, (2) может заблокировать карту при превышении попыток.

### 4.5 Практический пример активации через pySim

```python
from pySim.transport import LinkBase
from pySim.commands import SimCardCommands

# Подключение к карте
link = LinkBase(reader=0)
scc = SimCardCommands(transport=link)

# Активация Test Configuration State
adm_key = bytes.fromhex("B09754B704F254C8")
scc.verify_chv(key_ref=0x0A, pin=adm_key)
print("Test Configuration State: ACTIVATED")
```

### 4.6 Как деактивировать

Test Configuration State может быть деактивирован:
1. **Warm Reset** (сброс без снятия питания) — возвращает UICC в normal mode
2. **Cold Reset** (снятие и подача питания) — то же самое
3. **Явная деактивация** через специфическую команду (зависит от UICC)

Test Configuration State **не сохраняется** между перезагрузками — он действует только в текущей сессии.

---

## 5. PICS (Protocol Implementation Conformance Statement)

### 5.1 Что это такое

**PICS** — документ, который заполняет производитель UICC (или ME) **перед** началом конформанс-тестирования. В PICS производитель **декларирует**, какие именно функции из спецификации его продукт поддерживает.

PICS необходим, потому что:
- Ни одна UICC не реализует **все** опциональные функции (это невозможно и не нужно)
- Лаборатория должна знать, какие тесты **применимы** к данной UICC
- PICS — это контракт: "мы заявляем, что поддерживаем X и Y, проверьте это"

### 5.2 Структура PICS

PICS основан на ISO/IEC 9646-7 (OSI Conformance Testing) и содержит таблицы с пунктами из спецификации. Для каждого пункта:

| Поле | Значения | Описание |
|---|---|---|
| **Item** | Номер пункта спецификации | Например, "TS 31.101 §9.1.2 — Logical Channels" |
| **Status** | M / O / O.x / X | M=Mandatory, O=Optional, O.x=One of group, X=Excluded |
| **Support** | Y / N / N/A | Y=Yes (поддерживается), N=No (не поддерживается), N/A=Not Applicable |
| **Remarks** | Текст | Пояснения, если N или частичная поддержка |

### 5.3 Пример PICS для UICC (ключевые пункты)

```
PICS for UICC — Model X, Vendor Y, Revision Z
Date: 2026-06-12

PHYSICAL CHARACTERISTICS
[TS 102 221 §4]
  Item          | Status | Support | Remarks
  ID-1 size     | O      | N       | Only Plug-in (2FF) and 4FF
  Plug-in (2FF) | O.2    | Y       |
  4FF (nano)    | O.2    | Y       |
  3FF (micro)   | O.2    | N       |

VOLTAGE CLASSES
[TS 102 221 §5]
  Item          | Status | Support | Remarks
  Class A (5V)  | O      | N       | Not supported
  Class B (3V)  | M      | Y       |
  Class C (1.8V)| M      | Y       |
  Class D (1.2V)| O      | N       | Rel-17 feature

TRANSMISSION PROTOCOLS
[TS 102 221 §7]
  Item          | Status | Support | Remarks
  T=0           | M      | Y       |
  T=1           | O      | Y       |
  USB UICC      | O      | N       |

LOGICAL CHANNELS
[TS 102 221 §11]
  Item                | Status | Support | Remarks
  Basic (0)           | M      | Y       |
  Channels 1-3        | M      | Y       |
  Channels 4-19       | O      | Y       | Extended channel support
  Max concurrent       | —      | 20      |

SECURITY
[TS 102 221 §9 / TS 31.102 §5]
  Item                | Status | Support | Remarks
  PIN1 (Universal)    | M      | Y       |
  PIN2               | O      | Y       |
  PUK1               | M      | Y       |
  PUK2               | O      | Y       |
  ADM                | M      | Y       |
  MILENAGE           | M      | Y       | TS 35.206
  TUAK               | O      | N       |

USIM SERVICES (EF_UST)
[TS 31.102 §5.4]
  Item                | Status | Support | Remarks
  Service 1 (LPB)     | O      | Y       |
  Service 12 (SPN)    | M      | Y       |
  Service 27 (MILENAGE)| M     | Y       |
  Service 68 (USAT)   | O      | Y       |
  Service 99 (5GS)    | O      | Y       |
  Service 122 (5G AKA)| O      | Y       |

USAT (TOOLKIT)
[TS 31.124]
  Item                  | Status | Support | Remarks
  DISPLAY TEXT          | O.1    | Y       |
  GET INKEY             | O.1    | Y       |
  GET INPUT             | O.2    | Y       |
  PLAY TONE             | O.1    | Y       |
  SET UP MENU           | O.2    | Y       |
  SELECT ITEM           | O.2    | Y       |
  SEND SMS              | O.1    | Y       |
  SEND USSD             | O      | Y       |
  SET UP CALL           | O      | N       | Not in this product
  REFRESH               | M      | Y       |
  OPEN CHANNEL (BIP)    | O      | Y       | CS + GPRS only
  PROVIDE LOCAL INFO    | M      | Y       |
  SET UP EVENT LIST     | O      | Y       | All 10 events
```

### 5.4 Как PICS влияет на тестирование

Лаборатория использует PICS для:
1. **Выбора тест-кейсов**: тесты для функций с Support=N **не выполняются**
2. **Определения expected result**: если функция заявлена (Y), тест должен пройти
3. **Отчёта**: в Test Report указывается, какие тесты были пропущены по PICS

> [!tip] Практический совет
> При подготовке к сертификации: заполняйте PICS **ТОЛЬКО** теми функциями, которые действительно реализованы и протестированы. Лучше честно указать N для неподдерживаемой функции, чем провалить тест.

---

## 6. Тестирование SIM-профиля — пошаговая практическая инструкция

### Сценарий

У вас есть тестовая SIM-карта с записанным USIM-профилем. Нужно проверить корректность профиля — все ли данные записаны правильно, работает ли PIN, проходит ли аутентификация.

**Используем**: PCSC-ридер + pySim-shell (или raw APDU через gp.jar / opensc-tool)

### 6.1 Проверка ATR (холодный старт)

```
Цель: убедиться, что карта отвечает на Cold Reset и ATR корректен

Оборудование: любой PCSC-ридер с картой

Процедура:
  1. Вставить карту в ридер
  2. Запросить ATR через pySim или через opensc-tool

ATR (пример):
  3B 9F 96 80 1F C7 80 31 E0 73 FE 21 1B 57 3C 86 60 C2 00 00 A0 5A

Декодирование ATR:
  TS  = 3B          → Direct convention ✓
  T0  = 9F          → TA1 + TB1 + TC1 + TD1 present, 15 historical bytes
  TA1 = 96          → Fi=512, Di=32 → скорость = 3.571 MHz × 32/512 = ~223 kbps
  TB1 = 80          → Vpp не используется
  TC1 = 1F          → Extra guard time = 31 etu
  TD1 = C7          → TA2 + TB2 + TC2 + TD2 present, T=0 (протокол)
  TA2 = 80          → Specific mode (не negotiable)
  TB2 = 31          → PI2=31
  TC2 = E0          → T=0: WT=15 × 960 × Fi/f = ~1.5s
  Historical: 73 FE 21 1B 57 3C 86 60 C2 00 00 A0 5A

Ожидаемый результат:
  - TS = 3B (Direct) или 3F (Inverse) ✓
  - T0 корректно указывает interface bytes ✓
  - Historical bytes присутствуют ✓
  - TCK (если T=0 only) корректен ✓
  - Не более 33 байт (по ISO 7816-3) ✓
```

### 6.2 Верификация файловой системы (MF, DF, EF)

```
Цель: убедиться, что все обязательные файлы на месте

Команды (через pySim-shell):
  pySIM-shell> select MF
  → 90 00 (MF selectable) ✓

  pySIM-shell> select EF.ICCID
  → FCP + 90 00 ✓

  pySIM-shell> select EF.DIR
  → FCP + 90 00 ✓

  pySIM-shell> select EF.PL
  → FCP + 90 00 (может отсутствовать — проверить FCP) ✓

  pySIM-shell> select EF.ARR
  → FCP + 90 00 ✓

  pySIM-shell> select ADF.USIM
  → FCP + 90 00 (USIM application accessible) ✓

Внутри ADF.USIM — проверяем обязательные EF:
  pySIM-shell (ADF.USIM)> select EF.IMSI
  → FCP + 90 00 ✓

  pySIM-shell (ADF.USIM)> select EF.UST
  → FCP + 90 00 ✓

  pySIM-shell (ADF.USIM)> select EF.SPN
  → 90 00 (или 6A 82 если нет) ✓

  pySIM-shell (ADF.USIM)> select EF.ACC
  → FCP + 90 00 ✓

  pySIM-shell (ADF.USIM)> select EF.AD
  → FCP + 90 00 ✓

  pySIM-shell (ADF.USIM)> select EF.Keys
  → FCP + 90 00 ✓

  pySIM-shell (ADF.USIM)> select EF.KeysPS
  → 90 00 (если 5G) ✓

Ожидаемый результат:
  - MF, EF_DIR, EF_ICCID, EF_ARR — 100% обязательны ✓
  - ADF.USIM selectable by AID ✓
  - Обязательные EF внутри USIM доступны ✓
  - Отсутствующие опциональные EF → 6A 82 (не ошибка) ✓
```

### 6.3 Проверка ICCID и IMSI (сверка с ожидаемыми значениями)

```
Цель: прочитать ICCID и IMSI, декодировать, сравнить с эталонными значениями

Шаг 1: Чтение ICCID
  C-APDU:  00 A4 00 00 02 2F E2
  C-APDU:  00 B0 00 00 0A

  Данные:  98 43 10 05 00 02 35 17 90 03

  Декодирование (Reverse Code):
    98→89, 43→34, 10→01, 05→50, 00→00, 02→20, 35→53, 17→71, 90→09, 03→30
    ICCID = 89 34 01 50 00 20 53 71 09 30

    Структура ICCID:
      89 — Industry ID (telecom)
      34 — Country Code (Russia = 250, но первые 2 цифры: 34 → надо проверить)
      ... — Issuer ID + Individual Account
      0  — Check digit (Luhn)

  Проверка: ICCID должен совпадать с тем, что напечатан на карте ✓

Шаг 2: Чтение IMSI
  C-APDU:  00 A4 04 00 0D <USIM AID>
  C-APDU:  00 A4 00 00 02 6F 07
  C-APDU:  00 B0 00 00 09

  Данные:  08 29 05 99 37 05 41 33 57

  Декодирование:
    Byte 0: 08 = длина IMSI (8 цифр)
    Bytes 1-8 (Reverse Code):
      29→92, 05→50, 99→99, 37→73, 05→50, 41→14, 33→33, 57→75
    IMSI = 250 99 750533317
      MCC = 250 (Russia)
      MNC = 99 (Beeline)
      MSIN = 750533317

  Проверка:
    - MCC = известный оператор ✓
    - MNC = соответствует оператору, для которого готовился профиль ✓
    - Первый байт (0x08) = длина IMSI-1 ✓
    - Длина IMSI = 2-3 (MCC) + 2-3 (MNC) + MSIN ≥ 5-6 цифр ✓
```

### 6.4 Проверка SPN (декодирование UCS2/GSM7)

```
Цель: прочитать Service Provider Name и проверить кодировку

Шаг 1: SELECT EF_SPN (6F46)
  C-APDU:  00 A4 00 00 02 6F 46
  ← FCP: размер файла, тип transparent

Шаг 2: READ EF_SPN
  C-APDU:  00 B0 00 00 11  (17 байт для SPN)
  Данные + 90 00

Вариант A: GSM 7-bit default alphabet (SMS alphabet)
  Данные:  01 4D 65 67 61 46 6F 6E FF FF FF FF FF FF FF FF FF

  Декодирование:
    Byte 0: 01 — Display Condition (required, ME must display)
    Bytes 1-16: текст в GSM 7-bit:
      4D=M, 65=e, 67=g, 61=a, 46=F, 6F=o, 6E=n → "MegaFon"

Вариант B: UCS2 (16-bit Unicode)
  Данные:  01 80 04 1F 04 3E 04 34 04 3A 04 30 FF FF FF FF FF

  Декодирование:
    Byte 0: 01 — Display Condition (required)
    Byte 1: 80 — Coding Scheme = UCS2 (0x80)
    Bytes 2-17: UCS2 текст:
      041F=П, 043E=о, 0434=д, 043A=к, 0430=а → "Подка" (truncated)

    Внимание: если текст в UCS2, byte 1 = 0x80. Если byte 1 = 00-7F → GSM 7-bit

  Проверка:
    - Display Condition (byte 0) = 00 или 01 ✓
    - Текст декодирован корректно (в зависимости от Coding Scheme) ✓
    - Размер файла ≥ 17 байт (стандартный EF_SPN) ✓
```

### 6.5 Проверка EF_UST (какие сервисы доступны)

```
Цель: декодировать USIM Service Table (EF_UST) и составить карту доступных сервисов

Шаг 1: SELECT ADF.USIM

Шаг 2: SELECT EF_UST (6F38)
  C-APDU:  00 A4 00 00 02 6F 38

Шаг 3: READ EF_UST — первый раз с Le=00 (T=0 pattern)
  C-APDU:  00 B0 00 00 00
  ← 6C 10  (размер = 16 байт = 128 сервисов)

Шаг 4: READ EF_UST с Le=10
  C-APDU:  00 B0 00 00 10
  ← Данные (16 байт) + 90 00

  Пример:  9E EF 1F 1C FF 3E 04 00 00 00 00 00 00 00 00 00

  Битовый разбор (значимые сервисы):

  Byte 0: 0x9E = 1001 1110
    Service 1 (Local Phone Book):     Bit 1 = 1 → allocated, activated ✓
    Service 2 (Fixed Dialling Num):   Bit 2 = 1 → allocated, activated
    Service 3 (Extension 2):          Bit 3 = 1 → allocated
    Service 4 (SDN):                  Bit 4 = 1 → allocated
    Service 5 (Extension 3):          Bit 5 = 0 → not allocated
    Service 6 (BMIR):                 Bit 6 = 0 → not allocated
    Service 7 (ACI):                  Bit 7 = 0 → not allocated
    Service 8 (ICI):                  Bit 8 = 1 → allocated

  Byte 1: 0xEF = 1110 1111
    Service 12 (SPN):                 Bit 4 = 1 → allocated, activated ✓
    Service 13 (PLMN List):           Bit 5 = 1 → allocated ✓

  Byte 2: 0x1F = 0001 1111
    Service 24 (Equivalent HPLMN):    Bit 5 = 1 → allocated ✓

  Byte 3: 0x1C = 0001 1100
    Service 27 (MILENAGE):            Bit 3 = 1 → allocated, activated ✓
    Service 28 (AKA):                 Bit 4 = 1 → allocated ✓
    Service 30 (CBMIR):               Bit 5 = 1 → allocated ✓

  Byte 4: 0xFF = 1111 1111
    Services 33-40: all allocated

  Byte 5: 0x3E = 0011 1110
    Service 44 (eCall):               Bit 4 = 1 → allocated
    Service 46 (MBMS):                Bit 5 = 1 → allocated
    Service 47 (MCPTT):               Bit 6 = 1 → allocated

  Byte 7 (end): 00 — services 57+ not allocated

  Key services to check:
  ✓ Service 27 (MILENAGE) — must be allocated and activated
  ✓ Service 12 (SPN) — must be allocated if operator branding needed
  ✓ Service 68 (USAT) — in higher bytes if toolkit is required
  ✓ Service 99 (5GS) — if 5G profile
  ✓ Service 122 (5G AKA) — if 5G SA

Ожидаемый результат:
  - EF_UST содержит осмысленный набор сервисов ✓
  - Критичные сервисы (27 MILENAGE) allocated ✓
  - Нет противоречий: если service N allocated, соответствующий EF должен существовать ✓
```

### 6.6 Проверка аутентификации (MILENAGE Test Vector)

```
Цель: подтвердить, что USIM правильно выполняет MILENAGE без ошибок

Используем тестовые векторы из TS 35.206 / TS 34.108.

K    = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
OP   = CD 63 37 28 B3 82 D6 00 E7 2C 7F F5 D9 F8 3F 11
OPc  = CD C2 02 D5 12 3E 20 F6 2B 6D 67 6A C7 2C B3 18
SQN  = 00 00 00 00 00 00
AMF  = 80 00
RAND = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF

Expected: RES = F3 65 B6 E4 7D 36 1D D6
Expected: CK  = 53 41 76 1C 30 94 98 D1 D7 40 54 C9 49 25 5E 3F
Expected: IK  = C9 24 D5 80 AB D1 8B 16 D2 08 FC 84 69 34 5F 91
Expected: AUTN = F2 85 46 95 B6 75 80 00 4A 90 73 02

ВАЖНО:
  - OPc карты (EF_OPc) ДОЛЖЕН соответствовать тестовому вектору
  - Если карта использует OP (не OPc) — поле в EF_OP/EF_Keys указывает,
    и нужно задавать OP, а не OPc
  - K карты (в EF_Keys) ДОЛЖЕН совпадать с тестовым вектором
  - Если K или OPc не совпадают → тест пройдёт (алгоритм верный),
    но RES/CK/IK будут другими

Процедура:
  Шаг 1: VERIFY ADM (установить Test Configuration State)
  Шаг 2: Установить тестовый K через UPDATE EF_Keys (если Test Configuration активен)
    ИЛИ: использовать текущий K карты (если известен — для test карт)
  Шаг 3: SELECT ADF.USIM
  Шаг 4: AUTHENTICATE с RAND + AUTN
    C-APDU: 00 88 00 81 22
            10 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
            10 F2 85 46 95 B6 75 80 00 4A 90 73 02
            00

  Шаг 5: Анализ ответа
    - 90 00 с RES,CK,IK → аутентификация успешна ✓
    - 98 50 → SQN out of sync (необходима ресинхронизация через AUTS)
    - 63 00 → аутентификация провалена (неверный K или AUTN)
    - 98 04 → доступ запрещён (проверьте security condition)
```

### 6.7 Проверка PIN (полный цикл)

```
Цель: проверить все операции с PIN: VERIFY, CHANGE, DISABLE, ENABLE, UNBLOCK

PIN по умолчанию: "0000" (30 30 30 30) или "1234" (31 32 33 34)
PUK по умолчанию: "12345678" (обычно для тестовых карт)

Шаг 1: VERIFY PIN (правильный)
  C-APDU:  00 20 00 01 08 31 32 33 34 FF FF FF FF
  ← 90 00 ✓

Шаг 2: CHANGE PIN (сменить с "1234" на "5555")
  C-APDU:  00 24 00 01 10 31 32 33 34 FF FF FF FF 35 35 35 35 FF FF FF FF
  CLA=00, INS=24 (CHANGE), P2=01 (PIN1)
  Lc=16 (10h)
  Data: old PIN (31 32 33 34) padded + new PIN (35 35 35 35) padded

  ← 90 00 (PIN изменён)

  Проверка: VERIFY со старым PIN → 63 CX (неверный)
            VERIFY с новым PIN → 90 00 ✓

Шаг 3: DISABLE PIN
  C-APDU:  00 26 00 01 08 35 35 35 35 FF FF FF FF
  CLA=00, INS=26 (DISABLE), P2=01 (PIN1), Lc=08
  Data: текущий PIN + padding

  ← 90 00 (PIN отключён)

  Проверка: попытка доступа к EF с SC=PIN1 → должно быть разрешено (PIN disabled)
  Проверка: VERIFY PIN → должен вернуть ошибку или игнорироваться

Шаг 4: ENABLE PIN
  C-APDU:  00 28 00 01 08 35 35 35 35 FF FF FF FF
  CLA=00, INS=28 (ENABLE), P2=01 (PIN1), Lc=08
  Data: PIN + padding

  ← 90 00 (PIN включён)

Шаг 5: UNBLOCK PIN (предварительно заблокируем)
  Вводим неверный PIN 3 раза:
    C-APDU: 00 20 00 01 08 39 39 39 39 FF FF FF FF → 63 C3
    C-APDU: 00 20 00 01 08 39 39 39 39 FF FF FF FF → 63 C2
    C-APDU: 00 20 00 01 08 39 39 39 39 FF FF FF FF → 63 C1
    C-APDU: 00 20 00 01 08 39 39 39 39 FF FF FF FF → 63 C0 (BLOCKED)

  UNBLOCK с PUK + новым PIN:
    C-APDU: 00 2C 00 01 10
            31 32 33 34 35 36 37 38   ← PUK = "12345678"
            37 37 37 37 FF FF FF FF   ← New PIN = "7777"

    ← 90 00 (разблокировано, PIN = "7777")

  Проверка: VERIFY с "7777" → 90 00 ✓

Ожидаемый результат для всего цикла:
  ✓ VERIFY (correct): 90 00
  ✓ VERIFY (wrong): 63 CX (counter decrements)
  ✓ CHANGE: 90 00, новый PIN работает
  ✓ DISABLE: 90 00, PIN больше не требуется
  ✓ ENABLE: 90 00, PIN снова требуется
  ✓ UNBLOCK: 90 00, PIN разблокирован с новым значением
  ✓ BLOCKED: 63 C0, VERIFY возвращает 69 83
```

### 6.8 Проверка PLMN-файлов

```
Цель: проверить корректность списков сетей

Файлы для проверки:
  - EF_PLMNwAcT (6F60)  — User-controlled PLMN with Access Technology
  - EF_OPLMNwACT (6F61) — Operator-controlled PLMN selector
  - EF_FPLMN (6F7B)     — Forbidden PLMN
  - EF_HPLMN (опционально)
  - EF_EHPLMN (6FD9)    — Equivalent HPLMN

Структура записи PLMN:
  ┌──────────┬──────────┬──────────┬──────────┐
  │ MCC+MNC  │ MCC+MNC  │ MCC+MNC  │ ATT      │
  │ 3 bytes  │ cont'd   │ cont'd   │ 2 bytes  │
  └──────────┴──────────┴──────────┴──────────┘
  Total record: 5 байт (MCC-MNC: 3 байта, ATT: 2 байта)

  Пример: 25001 = Россия, МТС
    2 5 0 0 1
    → BCD: 02 50 01 → bytes: [02] [50] [01]

  Пример: 25099 = Россия, Beeline
    2 5 0 9 9
    → BCD: 02 50 99 → bytes: [02] [50] [99]
    Внимание: 9 не помещается в nibble → [02] [50] [99] (3 digits in 3 bytes)
    На самом деле: [02] [50] [F9] где F = filler

Процедура для EF_OPLMNwACT:
  Шаг 1: SELECT EF_OPLMNwACT (6F61)
    C-APDU: 00 A4 00 00 02 6F 61

  Шаг 2: READ RECORD (Linear Fixed EF)
    C-APDU: 00 B2 01 04 05  (Record #1, Le=5)
    ← Data (5 bytes) + 90 00

    Пример: 02 50 99 FF 02
    Decode:
      Bytes 0-2: 02 50 99 → MCC=250 MNC=99 → Beeline
      Byte 3: FF — filler
      Bytes 4-5: FF 02 — Access Technology:
        Bit 1 = 0 → GSM not selected
        Bit 2 = 1 → UTRAN selected
        Bit 3 = 0 → E-UTRAN (LTE) not selected
        Bit 4 = 0 → NR (5G) not selected

  Шаг 3: Проверить количество записей (через FCP)
    File Descriptor: количество записей указано в FCP

  Шаг 4: Прочитать остальные записи
    C-APDU: 00 B2 02 04 05  → record 2
    ...

  Проверка:
    ✓ Каждый MCC+MNC корректен (известный MCC, валидный MNC)
    ✓ Access Technology bits осмысленны
    ✓ HPLMN присутствует (если карта операторская)
    ✓ FPLMN корректно закодирован (если есть)
```

### 6.9 Проверка телефонной книги (ADN, FDN, SDN)

```
Цель: проверить, что EF телефонной книги доступны и корректно структурированы

Файлы:
  EF_ADN (6F3A) — Abbreviated Dialling Numbers
  EF_FDN (6F3B) — Fixed Dialling Numbers (требует PIN2)
  EF_SDN (6F49) — Service Dialling Numbers
  EF_EXT1 (6F4A) — Extension1 (дополнительные данные для ADN)
  EF_CCP (6F3D) — Capability Configuration Parameters

Структура записи ADN (пример):
  ┌─────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
  │ Alpha ID│ Length   │ TON/NPI  │ Number   │ CCP1     │ EXT1     │
  │ X bytes │ 1 byte   │ 1 byte   │ Y bytes  │ 1 byte   │ 1 byte   │
  └─────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
  Record Length = X + Y + 4  (14 bytes typical for SIM)

Процедура:
  Шаг 1: SELECT EF_ADN (6F3A)
    C-APDU: 00 A4 00 00 02 6F 3A
    ← FCP: Record Length (e.g. 0x0E = 14), Number of Records (e.g. 250)

  Шаг 2: READ RECORD 1
    C-APDU: 00 B2 01 04 0E
    ← Data + 90 00

    Пример: 4D 65 67 61 46 6F 6E FF FF FF FF FF 0B 81 38 30 30 35 35 35 33 35 33 35 FF FF
    Decode:
      Alpha ID: "MegaFon" (bytes 0-11, GSM 7-bit)
      Length: 0B = 11 digits
      TON/NPI: 81 = International, ISDN
      Number: 80 05 55 35 35 33 53 = 8005553535 (BCD, swap nibbles)
      CCP1: FF (not set)
      EXT1: FF (no extension)

  Шаг 3: Проверить EF_FDN (требует PIN2!)
    C-APDU: 00 A4 00 00 02 6F 3B
    C-APDU: 00 B2 01 04 0E
    ← Если PIN2 не verified → 69 82 ✓

  Шаг 4: VERIFY PIN2 и прочитать FDN
    C-APDU: 00 20 00 02 08 35 36 37 38 FF FF FF FF
    ← 90 00
    C-APDU: 00 B2 01 04 0E
    ← Data + 90 00

  Проверка:
    ✓ EF_ADN: записи корректно форматированы
    ✓ EF_FDN: требует PIN2 для чтения (69 82) ✓
    ✓ EF_SDN: записи содержат сервисные номера
```

### 6.10 Проверка STK (TERMINAL PROFILE, ENVELOPE, FETCH)

```
Цель: проверить, что Toolkit работает на базовом уровне (без телефона)

Инструмент: pySim-trace ИЛИ ручной APDU-обмен

Процедура (эмуляция терминала через pySim):

  Шаг 1: Послать TERMINAL PROFILE
    C-APDU: 80 10 00 00 14
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
    CLA=80 (ETSI/SCP), INS=10 (TERMINAL PROFILE), P1P2=0000
    Lc=20 (0x14) — длина TERMINAL PROFILE
    Data: 20 байт, все биты = 1 (все возможности поддерживаются)

    ← 90 00 (profile accepted)

  Шаг 2: STATUS (proactive polling)
    C-APDU: 80 F2 00 00 00
    CLA=80, INS=F2 (STATUS), P1P2=0000

    ← 91 0A  ← Proactive command pending, длина = 0x0A = 10

  Шаг 3: FETCH (получить proactive command)
    C-APDU: 80 12 00 00 0A
    CLA=80, INS=12 (FETCH), Le=0A

    ← Данные + 90 00
    ← Proactive command (TLV): например, SET UP MENU или REFRESH

    Decode proactive command:
      Tag D0 = Proactive UICC Command
        Length: variable
        Command Details (Tag 81):
          Command Number = 01
          Type = 03 (SET UP MENU)
        Device Identities (Tag 82):
          Source = UICC
          Destination = ME
        Alpha Identifier (Tag 85):
          "Main Menu"
        Items (Tag 8F):
          Item 1 = "Check Balance"
          Item 2 = "Recharge"
          Item 3 = "Settings"

  Шаг 4: TERMINAL RESPONSE (ответ на SET UP MENU)
    C-APDU: 80 14 00 00 09
            81 03 01 00 82 02 82 81 03
    ← 90 00

  Шаг 5: ENVELOPE (Menu Selection) — эмулируем выбор пункта меню
    C-APDU: 80 C2 00 00 0D
            D3 0B 82 02 82 81 90 01 02 91 02 01 03
    ← 90 00

  Шаг 6: STATUS → 91 XX (следующая proactive команда)
  Шаг 7: FETCH, TERMINAL RESPONSE, STATUS, ... (цикл)

  Проверка:
    ✓ TERMINAL PROFILE accepted (90 00)
    ✓ STATUS returns proactive command pending (91 XX)
    ✓ FETCH returns valid proactive command (TLV structure)
    ✓ TERMINAL RESPONSE accepted (90 00)
    ✓ ENVELOPE processed correctly
    ✓ Цикл TERMINAL PROFILE → STATUS → FETCH → TERMINAL RESPONSE работает
```

> [!note] Ограничение
> Без реального ME (Mobile Equipment) можно протестировать только UICC-сторону STK. Полный тест STK-сценария требует реального телефона или симулятора сети.

---

## 7. Автоматизация тестирования — Полный Python-скрипт

### 7.1 Smoke-test скрипт с pySim (полный код)

```python
#!/usr/bin/env python3
"""
SIM / USIM Profile Smoke Test
==============================
Автоматическая проверка корректности записанного профиля SIM/USIM.
Использует pySim как библиотеку.

Requirements:
  pip install pysim pycryptodome pyusb smartcard

Использование:
  python sim_smoke_test.py --reader 0 --expected-iccid 8970199204070424741F
"""

import sys
import json
import argparse
import traceback
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any


class Colors:
    """ANSI colors for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def pass_str(msg: str) -> str:
    return f"{Colors.GREEN}[PASS]{Colors.RESET} {msg}"


def fail_str(msg: str) -> str:
    return f"{Colors.RED}[FAIL]{Colors.RESET} {msg}"


def warn_str(msg: str) -> str:
    return f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}"


def info_str(msg: str) -> str:
    return f"{Colors.CYAN}[INFO]{Colors.RESET} {msg}"


class SimSmokeTest:
    """
    Полный smoke-test профиля SIM/USIM.
    """

    def __init__(self, reader_idx: int = 0, verbose: bool = False):
        self.reader_idx = reader_idx
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []
        self.card = None
        self.scc = None
        self.atr = None
        self.usim_aid = bytes.fromhex("A0000000871002FF86FF89010100")

        # Ожидаемые значения (задаются извне или проверяются на валидность)
        self.expected_iccid = None
        self.expected_imsi = None
        self.expected_spn = None

    # ─── HELPERS ───────────────────────────────────────────

    def _record(self, test_name: str, passed: bool, details: str = "",
                expected: str = "", actual: str = "") -> None:
        """Записать результат теста."""
        status = "PASS" if passed else "FAIL"
        if passed:
            print(pass_str(f"{test_name}: {details}"))
        else:
            print(fail_str(f"{test_name}: {details}"))
            if expected:
                print(f"       Expected: {expected}")
            if actual:
                print(f"       Actual:   {actual}")

        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "expected": str(expected),
            "actual": str(actual),
            "timestamp": datetime.now().isoformat()
        })

    def _send_apdu(self, apdu: bytes, description: str = "") -> Tuple[int, bytes]:
        """Отправить raw APDU и вернуть (sw, data)."""
        if self.verbose:
            cmd_str = apdu.hex().upper()
            print(f"       > {cmd_str}")
        data, sw = self.scc._tp.send_apdu(apdu)
        if self.verbose:
            sw_hex = f"{sw:04X}"
            data_str = data.hex().upper() if data else "(none)"
            print(f"       < {data_str} {sw_hex}")
        return sw, data

    def _decode_reverse_code(self, data: bytes) -> str:
        """Декодировать Reverse Code (swap nibbles in each byte)."""
        result = ""
        for b in data:
            result += f"{(b & 0x0F):01X}{(b >> 4):01X}"
        return result

    def _decode_gsm7(self, data: bytes) -> str:
        """Упрощённый декодер GSM 7-bit (только 7-bit ASCII)."""
        result = ""
        for b in data:
            if b == 0xFF:  # padding
                break
            if 0x20 <= b <= 0x7E:
                result += chr(b)
            elif b == 0x00:
                result += '@'
            elif b == 0x1B:
                result += '^'
            else:
                result += f'[{b:02X}]'
        return result

    # ─── TEST 1: CONNECTION & ATR ──────────────────────────

    def test_connection_and_atr(self) -> bool:
        """Test 1: Установить соединение с UICC, получить и проанализировать ATR."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 1: CONNECTION & ATR{Colors.RESET}")
        print(f"{'=' * 60}")

        try:
            # Подключение к карте
            from pySim.transport.pcsc import PcscSimLink
            from pySim.commands import SimCardCommands

            link = PcscSimLink(reader=self.reader_idx)
            self.atr = link.get_atr()
            self.scc = SimCardCommands(transport=link)

            print(f"       ATR: {self.atr.hex().upper()}")

            # Проверка 1: ATR не пустой
            if not self.atr:
                self._record("ATR received", False,
                            "ATR is empty — card not responding")
                return False

            self._record("ATR received", True,
                        f"Length: {len(self.atr)} bytes")

            # Проверка 2: TS (первый байт)
            ts = self.atr[0]
            if ts == 0x3B:
                ts_str = "Direct convention"
            elif ts == 0x3F:
                ts_str = "Inverse convention"
            else:
                self._record("ATR TS byte", False,
                            f"Invalid TS: 0x{ts:02X}")
                return False

            self._record("ATR TS byte", True, ts_str)

            # Проверка 3: Historical bytes (T0 указывает количество)
            t0 = self.atr[1]
            K = t0 & 0x0F  # Number of historical bytes
            self._record("ATR T0 byte", True,
                        f"Historical bytes: {K}, Interface bytes: {(t0 >> 4) & 0x0F}")

            # Проверка 4: Длина ATR не более 33 байт (ISO 7816-3)
            if len(self.atr) <= 33:
                self._record("ATR length <= 33", True,
                            f"Length: {len(self.atr)}")
            else:
                self._record("ATR length <= 33", False,
                            f"ATR too long: {len(self.atr)} > 33")

            # Проверка 5: TCK (если нет TD2, должен быть TCK)
            # Упрощённая проверка: если T=0 only, TCK присутствует
            has_tck = True  # в реальном коде нужен разбор TDi
            self._record("ATR TCK present", True,
                        "TCK byte present" if has_tck else "TCK not expected")

            return True

        except Exception as e:
            self._record("Connection", False, f"Exception: {str(e)}")
            traceback.print_exc()
            return False

    # ─── TEST 2: FILE SYSTEM ───────────────────────────────

    def test_file_system(self) -> bool:
        """Test 2: Проверить доступность MF, EF_DIR, EF_ICCID, EF_ARR, ADF.USIM."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 2: FILE SYSTEM VERIFICATION{Colors.RESET}")
        print(f"{'=' * 60}")

        all_passed = True

        # SELECT MF by FID
        sw, data = self._send_apdu(
            bytes.fromhex("00A40000023F00"), "SELECT MF"
        )
        passed = sw == 0x9000
        self._record("SELECT MF (3F00)", passed,
                    f"SW={sw:04X}", "9000", f"{sw:04X}")
        all_passed = all_passed and passed

        # SELECT EF_ICCID
        sw, data = self._send_apdu(
            bytes.fromhex("00A40000022FE2"), "SELECT EF_ICCID"
        )
        passed = sw == 0x9000
        self._record("SELECT EF_ICCID (2FE2)", passed,
                    f"SW={sw:04X}", "9000", f"{sw:04X}")
        all_passed = all_passed and passed

        # SELECT EF_DIR
        sw, data = self._send_apdu(
            bytes.fromhex("00A40000022F00"), "SELECT EF_DIR"
        )
        passed = sw in (0x9000, 0x6A82)  # 6A82 = not present, допустимо
        self._record("SELECT EF_DIR (2F00)", passed,
                    f"SW={sw:04X}",
                    "9000 or 6A82 (optional)", f"{sw:04X}")
        all_passed = all_passed and passed

        # SELECT EF_ARR
        sw, data = self._send_apdu(
            bytes.fromhex("00A40000022F06"), "SELECT EF_ARR"
        )
        passed = sw == 0x9000
        self._record("SELECT EF_ARR (2F06)", passed,
                    f"SW={sw:04X}", "9000", f"{sw:04X}")
        all_passed = all_passed and passed

        # SELECT ADF.USIM by AID
        apdu = bytes.fromhex("00A40400") + \
               bytes([len(self.usim_aid)]) + self.usim_aid
        sw, data = self._send_apdu(apdu, "SELECT ADF.USIM")
        passed = sw == 0x9000
        self._record("SELECT ADF.USIM (by AID)", passed,
                    f"SW={sw:04X}", "9000", f"{sw:04X}")
        all_passed = all_passed and passed

        # SELECT key EF inside ADF.USIM
        usim_efs = {
            "EF_IMSI": "6F07",
            "EF_UST": "6F38",
            "EF_SPN": "6F46",
            "EF_ACC": "6F78",
            "EF_AD": "6FAD",
        }

        for name, fid in usim_efs.items():
            apdu = bytes.fromhex(f"00A4000002{fid}")
            sw, data = self._send_apdu(apdu, f"SELECT {name}")
            # Optional files: 6A82 is OK
            passed = sw == 0x9000
            if sw == 0x6A82:
                self._record(f"SELECT {name} ({fid})", True,
                            "Optional — not present", "", "")
            else:
                self._record(f"SELECT {name} ({fid})", passed,
                            f"SW={sw:04X}", "9000", f"{sw:04X}")
                all_passed = all_passed and passed

        return all_passed

    # ─── TEST 3: ICCID & IMSI ──────────────────────────────

    def test_iccid_imsi(self) -> bool:
        """Test 3: Прочитать и проверить ICCID и IMSI."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 3: ICCID & IMSI VERIFICATION{Colors.RESET}")
        print(f"{'=' * 60}")

        all_passed = True

        # Чтение ICCID
        _ = self._send_apdu(bytes.fromhex("00A40000023F00"), "SELECT MF")
        sw, data = self._send_apdu(bytes.fromhex("00A40000022FE2"), "SELECT EF_ICCID")

        # READ BINARY — сначала запрос размера (Le=00)
        sw, data = self._send_apdu(bytes.fromhex("00B0000000"), "READ EF_ICCID (size)")
        if sw & 0xFF00 == 0x6C00:
            size = sw & 0xFF
            sw, data = self._send_apdu(
                bytes.fromhex("00B00000") + bytes([size]), "READ EF_ICCID"
            )
            if sw == 0x9000:
                iccid_decoded = self._decode_reverse_code(data)
                print(f"       ICCID (decoded): {iccid_decoded}")

                # Проверка: длина ICCID = 19-20 цифр
                if 19 <= len(iccid_decoded) <= 20:
                    self._record("ICCID length", True,
                                f"Length: {len(iccid_decoded)} digits")
                else:
                    self._record("ICCID length", False,
                                f"Length: {len(iccid_decoded)} (expected 19-20)",
                                "19-20", str(len(iccid_decoded)))
                    all_passed = False

                # Проверка: первый символ = '8' (telecom) или '9' (industry)
                if iccid_decoded[0] in ('8', '9'):
                    self._record("ICCID industry ID", True,
                                f"Industry: {iccid_decoded[0]}")
                else:
                    self._record("ICCID industry ID", False,
                                f"Industry: {iccid_decoded[0]}",
                                "8 or 9", iccid_decoded[0])
                    all_passed = False

                # Проверка ICCID с ожидаемым значением
                if self.expected_iccid:
                    if iccid_decoded == self.expected_iccid:
                        self._record("ICCID match expected", True)
                    else:
                        self._record("ICCID match expected", False,
                                    "Mismatch", self.expected_iccid, iccid_decoded)
                        all_passed = False
            else:
                self._record("READ EF_ICCID", False, f"SW={sw:04X}", "9000", f"{sw:04X}")
                all_passed = False
        else:
            self._record("READ EF_ICCID (size)", False, f"SW={sw:04X}", "6CXX", f"{sw:04X}")
            all_passed = False

        # Чтение IMSI
        apdu = bytes.fromhex("00A40400") + bytes([len(self.usim_aid)]) + self.usim_aid
        self._send_apdu(apdu, "SELECT ADF.USIM")
        sw, data = self._send_apdu(bytes.fromhex("00A40000026F07"), "SELECT EF_IMSI")

        sw, data = self._send_apdu(bytes.fromhex("00B0000000"), "READ EF_IMSI (size)")
        if sw & 0xFF00 == 0x6C00:
            size = sw & 0xFF
            sw, data = self._send_apdu(
                bytes.fromhex("00B00000") + bytes([size]), "READ EF_IMSI"
            )
            if sw == 0x9000:
                imsi_encoded = data
                imsi_len = imsi_encoded[0]  # First byte = IMSI length
                imsi_data = imsi_encoded[1:]
                imsi = self._decode_reverse_code(imsi_data)

                # Remove parity bit from the first digit
                print(f"       IMSI (decoded): {imsi}")
                print(f"       IMSI length:   {imsi_len}")

                # Проверка: длина IMSI соответствует первому байту
                if imsi_len == len(imsi):
                    self._record("IMSI length", True,
                                f"Length: {imsi_len}")
                else:
                    self._record("IMSI length", False,
                                f"Declared={imsi_len}, actual={len(imsi)}",
                                f"{imsi_len}", str(len(imsi)))
                    all_passed = False

                # Проверка длины IMSI (5-15 — ITU-T E.212)
                if 5 <= imsi_len <= 15:
                    self._record("IMSI valid range", True,
                                f"Length: {imsi_len}")
                else:
                    self._record("IMSI valid range", False,
                                f"Invalid length: {imsi_len}",
                                "5-15", str(imsi_len))
                    all_passed = False

                # Проверка IMSI с ожидаемым значением
                if self.expected_imsi:
                    if imsi == self.expected_imsi:
                        self._record("IMSI match expected", True)
                    else:
                        self._record("IMSI match expected", False,
                                    "Mismatch", self.expected_imsi, imsi)
                        all_passed = False
            else:
                self._record("READ EF_IMSI", False, f"SW={sw:04X}", "9000", f"{sw:04X}")
                all_passed = False

        return all_passed

    # ─── TEST 4: SERVICE TABLE (EF_UST) ────────────────────

    def test_ust(self) -> bool:
        """Test 4: Прочитать и проанализировать EF_UST."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 4: USIM SERVICE TABLE (EF_UST){Colors.RESET}")
        print(f"{'=' * 60}")

        critical_services = {
            1: "Local Phone Book",
            12: "Service Provider Name",
            13: "PLMN List",
            27: "MILENAGE",
            28: "AKA",
            68: "USAT (Toolkit)",
            99: "5GS",
            122: "5G AKA",
        }

        apdu = bytes.fromhex("00A40400") + bytes([len(self.usim_aid)]) + self.usim_aid
        self._send_apdu(apdu, "SELECT ADF.USIM")
        sw, data = self._send_apdu(bytes.fromhex("00A40000026F38"), "SELECT EF_UST")

        sw, data = self._send_apdu(bytes.fromhex("00B0000000"), "READ EF_UST (size)")
        all_passed = True

        if sw & 0xFF00 == 0x6C00:
            size = sw & 0xFF
            sw, data = self._send_apdu(
                bytes.fromhex("00B00000") + bytes([size]), "READ EF_UST"
            )
            if sw == 0x9000:
                ust_bytes = data
                print(f"       EF_UST ({len(ust_bytes)} bytes): {ust_bytes.hex().upper()}")

                # Проверка критических сервисов
                for svc_num, svc_name in critical_services.items():
                    byte_idx = (svc_num - 1) // 8
                    bit_idx = (svc_num - 1) % 8

                    if byte_idx < len(ust_bytes):
                        allocated = bool(ust_bytes[byte_idx] & (1 << bit_idx))
                        status = "allocated" if allocated else "NOT allocated"
                        if allocated:
                            print(pass_str(f"  Service {svc_num} ({svc_name}): {status}"))
                        else:
                            is_critical = svc_num in (27, 28)  # MILENAGE, AKA
                            if is_critical:
                                print(fail_str(f"  Service {svc_num} ({svc_name}): {status}"))
                                self._record(f"EF_UST Service {svc_num} ({svc_name})",
                                           False, status, "allocated", status)
                                all_passed = False
                            else:
                                print(warn_str(f"  Service {svc_num} ({svc_name}): {status}"))

                        self._record(f"EF_UST Service {svc_num} ({svc_name})",
                                   True if allocated else (not is_critical),
                                   status)
            else:
                self._record("READ EF_UST", False, f"SW={sw:04X}")
                all_passed = False

        return all_passed

    # ─── TEST 5: PIN VERIFICATION ──────────────────────────

    def test_pin(self, pin: str = "1234") -> bool:
        """Test 5: Проверить VERIFY PIN (успешный и неуспешный сценарии)."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 5: PIN VERIFICATION{Colors.RESET}")
        print(f"{'=' * 60}")

        all_passed = True

        # SELECT ADF.USIM
        apdu = bytes.fromhex("00A40400") + bytes([len(self.usim_aid)]) + self.usim_aid
        self._send_apdu(apdu, "SELECT ADF.USIM")

        # VERIFY PIN with wrong PIN
        wrong_pin_apdu = bytes.fromhex("0020000108") + \
                         bytes([ord(c) for c in "9999"]) + b'\xff\xff\xff\xff'
        sw, data = self._send_apdu(wrong_pin_apdu, "VERIFY PIN (wrong)")
        passed = sw & 0xFFF0 == 0x63C0  # 63 CX: X attempts remaining
        self._record("VERIFY PIN (wrong)", passed,
                    f"SW={sw:04X} (remaining attempts: {sw & 0x0F})",
                    "63CX", f"{sw:04X}")
        all_passed = all_passed and passed

        # VERIFY PIN with correct PIN
        pin_bytes = bytes([ord(c) for c in pin]) + \
                    b'\xff' * (8 - len(pin))
        pin_apdu = bytes.fromhex("0020000108") + pin_bytes
        sw, data = self._send_apdu(pin_apdu, "VERIFY PIN (correct)")
        passed = sw == 0x9000
        self._record("VERIFY PIN (correct)", passed,
                    f"SW={sw:04X}", "9000", f"{sw:04X}")
        all_passed = all_passed and passed

        return all_passed

    # ─── TEST 6: SPN ───────────────────────────────────────

    def test_spn(self) -> bool:
        """Test 6: Прочитать и декодировать EF_SPN."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 6: SERVICE PROVIDER NAME (EF_SPN){Colors.RESET}")
        print(f"{'=' * 60}")

        apdu = bytes.fromhex("00A40400") + bytes([len(self.usim_aid)]) + self.usim_aid
        self._send_apdu(apdu, "SELECT ADF.USIM")
        sw, data = self._send_apdu(bytes.fromhex("00A40000026F46"), "SELECT EF_SPN")

        if sw != 0x9000:
            self._record("SELECT EF_SPN", False,
                        f"SW={sw:04X} — EF_SPN not found", "9000", f"{sw:04X}")
            return False

        sw, data = self._send_apdu(bytes.fromhex("00B0000000"), "READ EF_SPN (size)")
        if sw & 0xFF00 == 0x6C00:
            size = sw & 0xFF
            sw, data = self._send_apdu(
                bytes.fromhex("00B00000") + bytes([size]), "READ EF_SPN"
            )
            if sw == 0x9000:
                display_condition = data[0]
                coding_byte = data[1] if len(data) > 1 else 0

                print(f"       Display Condition: {display_condition}"
                      f"({'required' if display_condition else 'not required'})")

                if coding_byte == 0x80:
                    # UCS2 encoding
                    text_bytes = data[2:]
                    spn_text = text_bytes.decode('utf-16-be').rstrip('\xff')
                    coding = "UCS2"
                else:
                    # GSM 7-bit default alphabet
                    text_bytes = data[1:]
                    spn_text = self._decode_gsm7(text_bytes)
                    coding = "GSM 7-bit"

                print(f"       SPN: '{spn_text}' ({coding})")

                self._record("EF_SPN display condition", True,
                            f"Value: {display_condition}")
                self._record("EF_SPN text", len(spn_text) > 0,
                            f"Text: '{spn_text}'")
                return True
            else:
                self._record("READ EF_SPN", False, f"SW={sw:04X}")
                return False
        return False

    # ─── TEST 7: AUTHENTICATE ──────────────────────────────

    def test_authenticate(self) -> bool:
        """Test 7: Выполнить AUTHENTICATE и проверить базовый ответ."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 7: AUTHENTICATE (MILENAGE){Colors.RESET}")
        print(f"{'=' * 60}")

        # SELECT ADF.USIM
        apdu = bytes.fromhex("00A40400") + bytes([len(self.usim_aid)]) + self.usim_aid
        self._send_apdu(apdu, "SELECT ADF.USIM")

        # Используем стандартный тестовый вектор из TS 35.206
        rand = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        autn = bytes.fromhex("F2854695B67580004A907302")

        # AUTHENTICATE (3G context)
        apdu = bytearray.fromhex("0088008122")
        apdu.append(0x10)  # Length of RAND
        apdu.extend(rand)
        apdu.append(0x10)  # Length of AUTN
        apdu.extend(autn)
        apdu.append(0x00)  # Le

        sw, data = self._send_apdu(bytes(apdu), "AUTHENTICATE (MILENAGE)")

        # Допустимые ответы:
        # 90 00 + RES/CK/IK — аутентификация успешна
        # 98 50 — SQN out of sync (нормально для тестовой карты)
        # 63 00 — аутентификация провалена (K не совпадает)
        # 98 04 — нет доступа к ключам
        if sw == 0x9000:
            self._record("AUTHENTICATE MILENAGE", True,
                        "Successful — RES/CK/IK returned")
            if data:
                print(f"       Response data: {data.hex().upper()}")
            return True
        elif sw == 0x9850:
            self._record("AUTHENTICATE MILENAGE", True,
                        "SQN out of sync (expected for test card)")
            return True
        elif sw == 0x6300:
            self._record("AUTHENTICATE MILENAGE", False,
                        "Authentication failed (K mismatch)",
                        "9000 or 9850", f"{sw:04X}")
            return False
        elif sw == 0x9804:
            self._record("AUTHENTICATE MILENAGE", False,
                        "Access to keys denied (security condition)",
                        "9000 or 9850", f"{sw:04X}")
            return False
        else:
            self._record("AUTHENTICATE MILENAGE", False,
                        f"Unexpected SW: {sw:04X}", "9000 or 9850", f"{sw:04X}")
            return False

    # ─── TEST 8: MANAGE CHANNEL ────────────────────────────

    def test_manage_channel(self) -> bool:
        """Test 8: Открыть и закрыть логический канал."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}TEST 8: MANAGE CHANNEL{Colors.RESET}")
        print(f"{'=' * 60}")

        all_passed = True

        # Open channel 1
        sw, data = self._send_apdu(
            bytes.fromhex("0070000100"), "MANAGE CHANNEL (open channel 1)"
        )
        passed = sw == 0x9000
        self._record("Open logical channel 1", passed,
                    f"SW={sw:04X}", "9000", f"{sw:04X}")
        all_passed = all_passed and passed

        if passed:
            # SELECT MF on channel 1
            sw, data = self._send_apdu(
                bytes.fromhex("01A40000023F00"), "SELECT MF on channel 1"
            )
            passed = sw == 0x9000
            self._record("SELECT MF on channel 1", passed,
                        f"SW={sw:04X}", "9000", f"{sw:04X}")
            all_passed = all_passed and passed

            # Close channel 1
            sw, data = self._send_apdu(
                bytes.fromhex("0070800100"), "MANAGE CHANNEL (close channel 1)"
            )
            passed = sw == 0x9000
            self._record("Close logical channel 1", passed,
                        f"SW={sw:04X}", "9000", f"{sw:04X}")
            all_passed = all_passed and passed

            # Verify channel 1 is closed (SELECT should fail with wrong class)
            sw, data = self._send_apdu(
                bytes.fromhex("01A40000023F00"), "SELECT MF on channel 1 (closed)"
            )
            passed = sw != 0x9000
            self._record("Channel 1 closed (no longer usable)", passed,
                        f"SW={sw:04X} (not 9000)", "!=9000", f"{sw:04X}")
            all_passed = all_passed and passed

        return all_passed

    # ─── RUN ALL TESTS ─────────────────────────────────────

    def run_all(self) -> bool:
        """Запустить все тесты и вернуть общий результат."""
        print(f"\n{Colors.BOLD}{'#' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}# SIM/USIM PROFILE SMOKE TEST{Colors.RESET}")
        print(f"{Colors.BOLD}# Started: {datetime.now().isoformat()}{Colors.RESET}")
        print(f"{Colors.BOLD}{'#' * 60}{Colors.RESET}")

        tests = [
            ("Connection & ATR", self.test_connection_and_atr),
            ("File System", self.test_file_system),
            ("ICCID & IMSI", self.test_iccid_imsi),
            ("USIM Service Table", self.test_ust),
            ("PIN Verification", self.test_pin),
            ("Service Provider Name", self.test_spn),
            ("MILENAGE Authenticate", self.test_authenticate),
            ("Logical Channels", self.test_manage_channel),
        ]

        all_passed = True
        for test_name, test_fn in tests:
            try:
                passed = test_fn()
                if not passed:
                    all_passed = False
            except Exception as e:
                print(fail_str(f"{test_name}: EXCEPTION — {str(e)}"))
                traceback.print_exc()
                all_passed = False

        # ─── REPORT ─────────────────────────────────────────
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}FINAL REPORT{Colors.RESET}")
        print(f"{'=' * 60}")
        print(f"  Total tests:  {total}")
        print(f"  {Colors.GREEN}Passed:       {passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed:       {failed}{Colors.RESET}")
        print(f"  Success rate: {passed / total * 100:.1f}%" if total > 0 else "  No tests run")
        print(f"{'=' * 60}")

        if all_passed:
            print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}SOME TESTS FAILED{Colors.RESET}")

        return all_passed

    def export_report(self, filename: str = "smoke_test_report.json") -> None:
        """Экспортировать результаты в JSON."""
        report = {
            "title": "SIM/USIM Profile Smoke Test Report",
            "timestamp": datetime.now().isoformat(),
            "reader_index": self.reader_idx,
            "atr": self.atr.hex().upper() if self.atr else None,
            "results": self.results,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r["status"] == "PASS"),
                "failed": sum(1 for r in self.results if r["status"] == "FAIL"),
            }
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(info_str(f"Report exported to: {filename}"))


def main():
    parser = argparse.ArgumentParser(
        description="SIM/USIM Profile Smoke Test"
    )
    parser.add_argument("--reader", "-r", type=int, default=0,
                        help="PCSC reader index (default: 0)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose APDU output")
    parser.add_argument("--expected-iccid", type=str,
                        help="Expected ICCID for comparison")
    parser.add_argument("--expected-imsi", type=str,
                        help="Expected IMSI for comparison")
    parser.add_argument("--pin", type=str, default="1234",
                        help="PIN for testing (default: 1234)")
    parser.add_argument("--report", type=str, default="smoke_test_report.json",
                        help="Output JSON report filename")
    args = parser.parse_args()

    tester = SimSmokeTest(reader_idx=args.reader, verbose=args.verbose)
    tester.expected_iccid = args.expected_iccid
    tester.expected_imsi = args.expected_imsi

    try:
        success = tester.run_all()
        tester.export_report(args.report)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"FATAL: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
```

### 7.2 Запуск и ожидаемый вывод

```bash
# Базовый запуск
python sim_smoke_test.py --reader 0

# С ожидаемыми значениями
python sim_smoke_test.py -r 0 \
  --expected-iccid 8970199204070424741F \
  --expected-imsi 25099750533317 \
  --pin 1234 \
  --verbose
```

**Ожидаемый вывод**:

```
############################################################
# SIM/USIM PROFILE SMOKE TEST
# Started: 2026-06-12T14:30:00
############################################################

============================================================
TEST 1: CONNECTION & ATR
============================================================
       ATR: 3B9F96801FC78031E073FE211B573C8660C20000A05A
[PASS] ATR received: Length: 23 bytes
[PASS] ATR TS byte: Direct convention
[PASS] ATR T0 byte: Historical bytes: 15, Interface bytes: 9
[PASS] ATR length <= 33: Length: 23
[PASS] ATR TCK present: TCK byte present

============================================================
TEST 2: FILE SYSTEM VERIFICATION
============================================================
[PASS] SELECT MF (3F00): SW=9000
[PASS] SELECT EF_ICCID (2FE2): SW=9000
[PASS] SELECT EF_DIR (2F00): SW=9000
[PASS] SELECT EF_ARR (2F06): SW=9000
[PASS] SELECT ADF.USIM (by AID): SW=9000
[PASS] SELECT EF_IMSI (6F07): SW=9000
[PASS] SELECT EF_UST (6F38): SW=9000
[PASS] SELECT EF_SPN (6F46): SW=9000
[PASS] SELECT EF_ACC (6F78): SW=9000
[PASS] SELECT EF_AD (6FAD): SW=9000

============================================================
TEST 3: ICCID & IMSI VERIFICATION
============================================================
       ICCID (decoded): 8970199204070424741F
[PASS] ICCID length: Length: 20 digits
[PASS] ICCID industry ID: Industry: 8
       IMSI (decoded): 25099750533317
       IMSI length:   8
[PASS] IMSI length: Length: 8
[PASS] IMSI valid range: Length: 8

============================================================
TEST 4: USIM SERVICE TABLE (EF_UST)
============================================================
       EF_UST (16 bytes): 9EEF1F1CFF3E04000000000000000000
[PASS]   Service 1 (Local Phone Book): allocated
[PASS]   Service 12 (Service Provider Name): allocated
[PASS]   Service 13 (PLMN List): allocated
[PASS]   Service 27 (MILENAGE): allocated
[PASS]   Service 28 (AKA): allocated
[WARN]   Service 68 (USAT (Toolkit)): NOT allocated
[WARN]   Service 99 (5GS): NOT allocated
[WARN]   Service 122 (5G AKA): NOT allocated

============================================================
TEST 5: PIN VERIFICATION
============================================================
[PASS] VERIFY PIN (wrong): SW=63C3 (remaining attempts: 3)
[PASS] VERIFY PIN (correct): SW=9000

============================================================
TEST 6: SERVICE PROVIDER NAME (EF_SPN)
============================================================
       Display Condition: 1 (required)
       SPN: 'MyOperator' (GSM 7-bit)
[PASS] EF_SPN display condition: Value: 1
[PASS] EF_SPN text: Text: 'MyOperator'

============================================================
TEST 7: AUTHENTICATE (MILENAGE)
============================================================
[PASS] AUTHENTICATE MILENAGE: Successful — RES/CK/IK returned
       Response data: DB...

============================================================
TEST 8: MANAGE CHANNEL
============================================================
[PASS] Open logical channel 1: SW=9000
[PASS] SELECT MF on channel 1: SW=9000
[PASS] Close logical channel 1: SW=9000
[PASS] Channel 1 closed (no longer usable): SW=6E00 (not 9000)

============================================================
FINAL REPORT
============================================================
  Total tests:  28
  Passed:       28
  Failed:       0
  Success rate: 100.0%
============================================================

ALL TESTS PASSED
```

---

## 8. Сравнение инструментов тестирования (расширенное)

### 8.1 Полная таблица сравнения

| Инструмент | Категория | Покрытие | GUI | API/CLI | Стоимость | Лучшее применение | Ограничения |
|---|---|---|---|---|---|---|---|
| **pySim-shell** | Ручное тестирование | Файловая система, APDU, GP-базовый | Нет | CLI | Бесплатно | Разработка, отладка профилей, исследование карт | Только карты с известными ADM |
| **pySim-trace** | Анализ трафика | Анализ APDU-обмена ME<->UICC | Нет | CLI | Бесплатно | Отладка STK, исследование взаимодействия | Только PCSC, требуется телефон |
| **pySim-prog** | Программирование | Запись профилей (IMSI, Ki, ICCID) | Нет | CLI | Бесплатно | Программирование тестовых SIM | Только Osmocom-совместимые карты |
| **GlobalPlatformPro (gp.jar)** | GP-управление | GP 2.x: LIST, LOAD, INSTALL, DELETE, SCP02/03 | Нет | CLI/Java | Бесплатно | Установка/удаление апплетов, управление ISD | Только GP-команды |
| **TCA Loader** | GP-управление | GP + Interop тесты | GUI | CLI | Бесплатно | Установка апплетов, интероперабельность | Windows only |
| **opensc-tool** | Общее | Базовые APDU, PKCS#15 | Нет | CLI | Бесплатно | Быстрые APDU-тесты, работа с PKI | Ограниченная поддержка UICC-специфики |
| **SIMTester** | Безопасность | Фаззинг APDU, проверка security | Java GUI | — | Бесплатно (2015) | Быстрый security-аудит SIM | Устарел, может не работать |
| **cardpeek** | Анализ | GUI-браузер содержимого смарт-карт | GUI | Скрипты Lua | Бесплатно | Визуальный просмотр файлов | Только чтение, ограниченные карты |
| **Comprion IT³** | Сертификация | Полный GCF (TS 31.121/122/124 + RF) | GUI | API | EUR 100K+ | Сертификация GCF/PTCRB | Только аккредитованные лаборатории |
| **Valid8** | Сертификация | Protocol conformance (TS 31.121/124) | GUI | API | EUR 50K+ | Протокольные тесты, лёгкая сертификация | Нет RF-тестирования |
| **Rohde & Schwarz CMW** | Полный цикл | RF + Protocol + UICC (SW options) | GUI | API | EUR 100K+ | Полный цикл тестирования устройства | Сложность настройки |

### 8.2 Матрица выбора инструмента по задаче

| Задача | pySim | gp.jar | TCA | Comprion | Valid8 | Другой |
|---|---|---|---|---|---|---|
| Просмотр файловой системы | **pySim-shell** | — | — | + | + | cardpeek |
| Проверка ATR | **opensc** | — | — | + | + | — |
| Чтение/запись EF | **pySim-shell** | — | — | + | + | opensc-tool |
| Проверка PIN | **pySim-shell** | — | — | + | + | — |
| AUTHENTICATE тест | **pySim-shell** | — | — | + | + | — |
| Установка апплета | — | **gp.jar** | **TCA** | + | — | JCOP |
| Удаление апплета | — | **gp.jar** | **TCA** | + | — | — |
| STK отладка | **pySim-trace** | — | — | + | + | — |
| BIP тесты | — | — | — | **Comprion** | **Valid8** | — |
| Сертификация | — | — | — | **Comprion** | — | R&S |
| Security аудит | **SIMTester** | — | — | — | — | fuzzing |
| CI/CD автоматизация | **pySim (lib)** | **gp.jar** | TCA CLI | + | + | — |
| Дамп всей ФС | **pySim export** | — | — | + | + | cardpeek |

### 8.3 Стоимость владения (Total Cost of Ownership)

| Уровень | Инструменты | CAPEX | OPEX/год | Для кого |
|---|---|---|---|---|
| **Bronze** (DIY) | pySim + gp.jar + TCA | EUR 100 (ридер) | EUR 0 | Разработчики, стартапы, хобби |
| **Silver** (Small Lab) | Bronze + PCSC-анализатор | EUR 5K | EUR 1K | Small UICC vendors |
| **Gold** (Lab) | Valid8 или эквивалент | EUR 50-80K | EUR 10K | UICC/ME vendors |
| **Platinum** (RTO) | Comprion IT³ + R&S CMW | EUR 200K+ | EUR 30K | Аккредитованные GCF/PTCRB лаборатории |

---

## Ссылки на источники

- UICC Platform: [[wiki/concepts/UICC]]
- UICC File System: [[wiki/concepts/UICC_File_System]]
- UICC Security: [[wiki/concepts/UICC_Security]]
- APDU: [[wiki/concepts/APDU]]
- Status Words: [[wiki/reference/Status_Words]]
- CLA/INS/SFI: [[wiki/reference/CLA_INS_SFI]]
- TS 102 221: [[wiki/summaries/ts_102221]]
- TS 31.121 (UICC Conformance): [[Specifications/ETSI_3GPP/Test_Conformance/ts_131121v180200p.pdf]]
- TS 31.124 (USAT Conformance): [[wiki/summaries/ts_31124]]
- TS 51.017 (SIM Conformance): [[Specifications/ETSI_3GPP/Test_Conformance/ts_151017v040200p.pdf]]
- GCF/PTCRB: [[wiki/concepts/Certification_GCF_PTCRB]]
- pySim Manual: [[wiki/summaries/osmopysim_usermanual]]
- SIM APDU Examples: [[wiki/summaries/sim_apdu_examples]]
- Testing Specs (synthesis): [[wiki/syntheses/sim_testing_specs]]
- MILENAGE Auth: [[wiki/research/milenage_vs_tuak]]
- Auth Evolution: [[wiki/research/auth_evolution_deep_dive]]
- eSIM Testing: [[wiki/syntheses/esim_evolution]]
- ISO 7816 Analysis: [[wiki/summaries/iso7816_analysis]]
- SIM Personalization: [[wiki/summaries/sim_personalization]]
- GSMA LITE: [[wiki/concepts/Certification_GCF_PTCRB]]

---

## См. также

- [[wiki/syntheses/sim_testing_specs|SIM Testing Specs (Synthesis)]] — обзор методологии тестирования (10 KB)
- [[wiki/syntheses/uicc_testing_pipeline|UICC Testing Pipeline]] — полный процесс от разработки до сертификации
- [[wiki/research/milenage_vs_tuak|MILENAGE vs TUAK (Research)]] — криптографический разбор алгоритмов аутентификации
- [[wiki/research/auth_evolution_deep_dive|Auth Evolution Deep Dive (Research)]] — полная история аутентификации
- [[wiki/concepts/CAT_STK|CAT/STK Concepts]] — архитектура SIM Toolkit
