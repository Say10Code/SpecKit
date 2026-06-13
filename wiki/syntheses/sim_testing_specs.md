---
tags: [synthesis, testing, conformance, UICC, USIM, pySim, GCF, PTCRB, TS-31.121, TS-31.124, TS-51.017]
type: synthesis
created: 2026-06-12
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/summaries/ts_31124|TS 31.124 — USAT Conformance]]"
  - "[[wiki/syntheses/uicc_testing_pipeline|UICC Testing Pipeline]]"
  - "[[wiki/concepts/Certification_GCF_PTCRB|GCF/PTCRB]]"
  - "[[wiki/concepts/UICC_File_System]]"
  - "[[wiki/summaries/ts_102221|TS 102 221]]"
  - "[[wiki/summaries/ts_131102|TS 31.102 — USIM]]"
  - "[[Specifications/ETSI_3GPP/Test_Conformance/ts_131121v180200p.pdf|TS 31.121 — UICC Conformance]]"
  - "[[Specifications/ETSI_3GPP/Test_Conformance/ts_151017v040200p.pdf|TS 51.017 — SIM Conformance]]"
---

# Тестирование SIM-карт согласно спецификациям

> **Synthesis** — обзор методологии тестирования UICC/SIM на соответствие спецификациям ETSI/3GPP: от физического уровня до протокольных тестов STK.

---

## 1. Пирамида тестирования UICC

```
        ┌──────────────────┐
        │  Сертификация     │  GCF / PTCRB
        │  (Conformance)   │  TS 31.121, TS 31.124, TS 51.017
        ├──────────────────┤
        │  Интероперабельность│ TCA Interop / GSMA LITE
        │  (Interop)       │  Разные карты × телефоны
        ├──────────────────┤
        │  Автоматизированное│ pySim-trace / gp.jar
        │  тестирование    │  CI/CD-скрипты
        ├──────────────────┤
        │  Ручное           │ pySim-shell / GlobalPlatformPro
        │  тестирование    │  Интерактивный APDU-обмен
        └──────────────────┘
```

---

## 2. Семейство конформанс-спецификаций

| Спецификация | Версия | Что тестирует | Страниц |
|---|---|---|---|
| **TS 31.121** (UICC Conformance) | V18.2.0 | Базовая UICC: файловая система, команды, безопасность, протоколы | 1300+ |
| **TS 31.122** (USIM Conformance) | V17.x | USIM-приложение: аутентификация, EF, сервисы | 800+ |
| **TS 31.123** (ISIM Conformance) | — | ISIM-приложение: IMS регистрация, IMPI/IMPU | 500+ |
| **TS 31.124** (USAT Conformance) | V18.2.0 | USIM Application Toolkit: proactive commands, events, BIP | 1341 |
| **TS 51.017** (SIM Conformance) | V4.2.0 | Legacy GSM SIM: файлы, CHV, GSM алгоритм | 400 |
| **TS 51.014** (SAT Conformance) | V4.1.0 | Legacy SIM Application Toolkit | 85 |

### Взаимосвязь спецификаций

```
TS 102 221 (базовый UICC)
  ├── TS 31.121 (UICC conformance tests)
  │     ├── TS 31.122 (USIM tests)
  │     └── TS 31.123 (ISIM tests)
  │
  ├── TS 102 223 (CAT)
  │     ├── TS 31.124 (USAT conformance tests)
  │     └── TS 51.014 (SAT conformance tests — legacy)
  │
  └── GSM 11.11 (legacy SIM)
        └── TS 51.017 (SIM conformance tests — legacy)
```

---

## 3. Что тестирует каждая спецификация

### TS 31.121 — UICC Conformance

**Базовый документ тестирования.** Проверяет саму платформу UICC, без привязки к конкретному приложению (USIM, ISIM).

| Область | Что тестируется |
|---|---|
| **Физические характеристики** | Form factor (ID-1, Plug-in, 4FF), толщина, контакты |
| **Электрический интерфейс** | Классы напряжения (A/B/C/D), ток потребления, уровни I/O |
| **ATR / PPS** | Структура ATR, historical bytes, согласование скорости |
| **Протоколы** | T=0: GET RESPONSE, procedure bytes, chaining; T=1: I-block, S-block, error handling |
| **Файловая система** | MF (3F00) обязателен, EF_DIR (2F00) корректен, все зарезервированные FID присутствуют |
| **Команды** | SELECT (по FID, по AID, по пути), READ/WRITE/SEARCH/INCREASE — все возвращают корректные SW |
| **Безопасность** | VERIFY PIN, CHANGE/DISABLE/ENABLE/UNBLOCK — все переходы состояний |
| **Логические каналы** | MANAGE CHANNEL: открыть/закрыть, изоляция каналов |

### TS 31.124 — USAT Conformance

**Наиболее объёмный документ.** Проверяет ВСЕ proactive commands и сценарии CAT/USAT.

| Группа тестов | Примеры |
|---|---|
| **Profile Download** | TERMINAL PROFILE: все биты, response `'90 00'` |
| **Proactive Commands** | DISPLAY TEXT, GET INKEY, GET INPUT, PLAY TONE, SET UP MENU, SELECT ITEM, SEND SMS, SET UP CALL, REFRESH |
| **Events** | MT call, call connected/disconnected, location status, user activity, idle screen, access technology change |
| **BIP (Bearer Independent Protocol)** | OPEN CHANNEL (CS/GPRS/Local), CLOSE CHANNEL, SEND/RECEIVE DATA, GET CHANNEL STATUS |
| **ENVELOPE** | Menu Selection, Call Control, Timer Expiration, Event Download (все типы) |
| **Ошибки** | Неверный формат, неизвестный тег, пропущенные mandatory элементы |

### TS 51.017 — SIM Conformance (Legacy)

Исторический документ для GSM SIM. Тестирует:
- GSM-специфичные команды: RUN GSM ALGORITHM (`INS=88`), SLEEP (`FA`)
- CHV (Card Holder Verification) — предшественник PIN
- SIM Service Table (EF_SST) — предшественник EF_UST
- Файловую систему DF_GSM (7F20)

---

## 4. Типовая структура тест-кейса

Каждый тест-кейс в конформанс-спецификациях имеет единую структуру:

```
Test Case: <имя>
  Reference: TS XX.XXX clause Y.Z
  Purpose: Что проверяется
  Pre-conditions:
    - Состояние UICC (PIN verified, file selected, ...)
    - Terminal capabilities (TERMINAL PROFILE bits)
  Test procedure:
    1. Terminal sends:   CLA INS P1 P2 Lc Data
    2. UICC shall return: SW1 SW2 [Data]
    3. ...
  Expected result:
    - SW = 90 00 (success)
    - Response data содержит ...
  Post-conditions:
    - UICC state after test
```

### Пример тест-кейса: SELECT MF

```
Reference: TS 31.121 clause 10.1.1
Purpose: Verify that UICC accepts SELECT of MF (3F00)
Pre-conditions: UICC activated, ATR received, no file selected
Test procedure:
  1. Terminal: 00 A4 00 00 02 3F 00
  2. UICC shall return: FCP of MF + SW=90 00
Expected result:
  - SW1SW2 = 90 00
  - Response contains FCP template (tag 62)
  - FCP contains File ID (tag 83) = 3F 00
  - FCP contains DF Name (tag 84) if MF has AID
Post-conditions: MF is selected (current directory = MF)
```

---

## 5. Инструменты тестирования

### pySim

```bash
# pySim-shell с картой
pySim-shell -p 0
pySIM-shell> select MF               # Тест: SELECT MF
pySIM-shell> select ADF.USIM         # Тест: SELECT USIM
pySIM-shell> read EF.IMSI            # Тест: READ BINARY transparent
pySIM-shell> verify_chv              # Тест: VERIFY PIN
pySIM-shell> export                  # Дамп всей ФС
```

### pySim-trace

```bash
# Сниффер APDU-обмена ME <-> UICC
pySim-trace --pcsc 0
# Выход:
#  > 00 A4 00 00 02 3F 00    SELECT MF
#  < 62 1C ... 90 00          FCP + OK
#  > 00 B0 00 00 00           READ BINARY (запрос размера)
#  < 6C 0A                    10 bytes available
```

### GlobalPlatformPro

```bash
# Тест установки/удаления апплета
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --list
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --install applet.cap --params $PARAMS
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --uninstall applet.cap
```

---

## 6. Сертификация: GCF / PTCRB

```
Разработчик UICC
      │
      ▼
Аккредитованная лаборатория (RTO)
    │  Тесты по TS 31.121 (базовая UICC)
    │  Тесты по TS 31.122 (USIM)
    │  Тесты по TS 31.124 (USAT)
    │  Декларация: PICS (Protocol Implementation Conformance Statement)
    │
    ▼
GCF / PTCRB Certification Body
    │  Валидация тест-репорта
    │
    ▼
Сертификат соответствия → Выход на рынок
```

### PICS (Protocol Implementation Conformance Statement)

Документ, в котором производитель UICC декларирует какие функции он поддерживает:
- Voltage classes (A, B, C, D — какие поддерживаются)
- Logical channels (0-3, 0-19)
- T=0 / T=1 / USB (какие протоколы)
- USAT (какие proactive commands/events)
- Каждый пункт: M (mandatory), O (optional), N/A (not applicable)

---

## 7. Тестовый профиль (Test UICC)

Для конформанс-тестирования используются **специальные тестовые UICC**:

| Свойство | Обычная UICC | Test UICC |
|---|---|---|
| **ADM-ключи** | Секретные оператора | Известные тестовые |
| **EF зарезервированы** | Частично заполнены | Все файлы доступны |
| **Test Configuration State** | Выключен | Активирован (Annex N, TS 102 221) |
| **OTA-ключи** | KIC/KID оператора | Тестовые ключи |
| **TERMINAL PROFILE** | Полный | Может быть изменён |
| **Производство** | Массовое | Мелкая серия |

### Annex N (TS 102 221) — Test Configuration State

Специальное состояние UICC для тестирования:
- Активируется через VERIFY ADM с тестовым ключом
- Отключает проверки безопасности, которые мешают тестированию
- Позволяет запись в normally read-only EF
- Обязательно для GCF/PTCRB тестовых карт

---

## 8. Практический пример: тестирование профиля SIM

### Шаг 1: Верификация АТR

```bash
# Проверяем что карта отвечает на reset
pySim-shell -p 0
# ATR: 3B 9F 96 80 1F C7 80 31 E0 73 FE 21 1B 57 3C ...
# Проверяем:
#  - TS = 3B (direct convention) ✓
#  - T0 = 9F (TA1+TB1+TC1+TD1 present, 15 historical bytes) ✓
#  - TD1 = 80 (T=0 protocol, no TA2..TD2) ✓
```

### Шаг 2: Верификация файловой системы

```bash
pySim-shell -p 0 << 'EOF'
select MF
select EF.ICCID
read_binary 0 10
select EF.DIR
read_record 1
select ADF.USIM
read EF.IMSI
read EF.UST
read EF.SPN
EOF
```

### Шаг 3: Верификация USIM Service Table

```bash
pySIM-shell> select ADF.USIM
pySIM-shell> read EF.UST
# Вывод: 9E EF 1F 1C FF 3E 04 90 00
# Декодируем bit-by-bit:
# Service 1: Local Phone Book (allocated, activated)
# Service 12: Service Provider Name (allocated, not activated)
# Service 68: USAT (allocated, activated)
# Service 99: 5GS (allocated, activated)
```

### Шаг 4: Тест AUTHENTICATE

```bash
# Тестовый вектор MILENAGE (из TS 35.206):
K    = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
OPc  = CD C2 02 D5 12 3E 20 F6 2B 6D 67 6A C7 2C B3 18
RAND = 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF

# Выполняем AUTHENTICATE:
#  00 88 00 81 22 10 <RAND> 10 <AUTN>
# Ожидаем: RES + CK + IK + SW=90 00
```

### Шаг 5: Тест TERMINAL PROFILE и STK

```bash
# Включаем pySim-trace и наблюдаем обмен при старте телефона:
pySim-trace --pcsc 0
# Ожидаем увидеть:
#  > 80 10 00 00 14 ...        TERMINAL PROFILE
#  < 91 XX                     proactive command pending
#  > 80 12 00 00 XX            FETCH
#  < D0 ...                    SET UP MENU (или другая proactive cmd)
```

---

## 9. Автоматизация тестирования

### Smoke-тест (базовый)

```python
import pySim
card = pySim.connect(pcsc=0)
assert card.select('3F00')       # MF exists
assert card.select('2FE2')       # EF_ICCID exists
iccid = card.read_binary(0, 10)
assert len(iccid) == 10           # ICCID = 10 bytes
assert card.select('A0..87.10.02...')  # ADF.USIM selectable
imsi = card.read_binary(0x6F07, 9)
assert imsi[0] < 16               # First byte of IMSI = length
print("Smoke test PASSED")
```

### Полный тест-лист профиля

| # | Тест | APDU | Ожидаемый SW |
|---|---|---|---|
| 1 | SELECT MF | `00 A4 00 00 02 3F 00` | `90 00` |
| 2 | SELECT EF_ICCID | `00 A4 00 00 02 2F E2` | `90 00` |
| 3 | READ EF_ICCID | `00 B0 00 00 0A` | `... 90 00` |
| 4 | SELECT ADF.USIM | `00 A4 04 00 0A <AID>` | `90 00` |
| 5 | READ EF_IMSI | `00 B0 00 00 09` | `... 90 00` |
| 6 | READ EF_UST | `00 B0 00 00 01` | `... 90 00` |
| 7 | VERIFY PIN (wrong) | `00 20 00 01 08 FF...` | `63 Cx` |
| 8 | VERIFY PIN (correct) | `00 20 00 01 08 <PIN>` | `90 00` |
| 9 | AUTHENTICATE | `00 88 00 81 <Lc> <data>` | `... 90 00` or `... 98 50` |
| 10 | UPDATE EF_SPN | `00 D6 00 00 <Lc> <data>` | `90 00` |
| 11 | READ EF_SPN | `00 B0 00 00 <Le>` | `... 90 00` |
| 12 | Unverified READ (after reset) | `00 B0 00 00 XX` (protected EF) | `69 82` |

---

## 10. Сравнение: ручное vs автоматизированное vs сертификационное

| Свойство | Ручное (pySim-shell) | Автоматизированное (CI) | Сертификационное (GCF) |
|---|---|---|---|
| **Скорость** | Часы-дни | Минуты | Недели |
| **Покрытие** | Выборочное | Все smoke-тесты | 100% conformance |
| **Стоимость** | $0 | $0 (свои скрипты) | $50K-200K |
| **Требует Test UICC** | Нет | Нет | Да (Annex N) |
| **Признаётся рынком** | Нет | Нет | Да |
| **Когда использовать** | Разработка, отладка | CI/CD, nightly | Выход на рынок |

---

## Ссылки на источники

- UICC Conformance: [[Specifications/ETSI_3GPP/Test_Conformance/ts_131121v180200p.pdf|TS 31.121]]
- USAT Conformance: [[wiki/summaries/ts_31124|TS 31.124]]
- SIM Conformance: [[Specifications/ETSI_3GPP/Test_Conformance/ts_151017v040200p.pdf|TS 51.017]]
- GCF/PTCRB: [[wiki/concepts/Certification_GCF_PTCRB]]
- Testing Pipeline: [[wiki/syntheses/uicc_testing_pipeline]]
- UICC Platform: [[wiki/concepts/UICC]]
- pySim Manual: [[wiki/summaries/osmopysim_usermanual]]

## См. также

- [[wiki/research/sim_testing_deep_dive|SIM Testing Deep Dive (Research)]] — исчерпывающее практическое руководство: 30+ KB, 10+ детальных тест-кейсов с APDU, полный Python-скрипт, пошаговая инструкция тестирования профиля
