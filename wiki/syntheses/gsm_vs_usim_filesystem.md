---
tags: [synthesis, GSM, USIM, file-system, comparison]
created: 2026-06-10
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/summaries/gsm_1111]]"
  - "[[wiki/summaries/ts_131102]]"
  - "[[wiki/concepts/UICC_File_System]]"
  - "[[wiki/concepts/USIM]]"
---

# GSM SIM vs 3G USIM: Сравнение файловых систем

> **Synthesis** — эволюция от фиксированной SIM-файловой системы к гибкой много-приложенческой UICC с ADF.

---

## 1. Архитектурная эволюция

```
GSM SIM (1995)                    UICC/USIM (3G+ 2000+)
══════════════                    ═══════════════════
MF (3F00)                         MF (3F00)
├── EF_ICCID (2FE2)              ├── EF_ICCID (2FE2)
├── DF_GSM (7F20) ← ОДНО прил.  ├── EF_DIR (2F00) ← ✨ НОВОЕ: каталог AID!
│   ├── EF_IMSI                  ├── EF_PL (2F05)
│   ├── EF_Kc                    ├── EF_ARR (2F06)
│   ├── EF_SPN                   ├── EF_UMPC
│   └── ... (~15 EF)             ├── DF_CD (config data)
└── DF_TELECOM (7F10)            │
    ├── EF_ADN                   ├── ADF.USIM ✨ ← По AID!
    ├── EF_SMS                   │   ├── EF_IMSI
    └── ...                      │   ├── EF_SPN (тот же FID!)
                                 │   └── ... (100+ EF + 12+ DF)
                                 ├── ADF.ISIM ✨
                                 └── ADF.GSM ✨ (для обратной совместимости)
```

---

## 2. Сравнение: key metrics

| Метрика | GSM SIM | USIM (ADF.USIM) |
|---|---|---|
| **Спецификация** | GSM 11.11 | 3GPP TS 31.102 |
| **Стандарт** | GSM Phase 2+ | Release 17+ |
| **Приложений** | 1 (только GSM) | Множественные (USIM, ISIM, свои) |
| **Выбор приложения** | Фиксированный DF_GSM | По AID (SELECT по DF Name) |
| **EF на уровне приложения** | ~15 EF | ~100 EF |
| **DF внутри приложения** | 0 | 12+ DF (5GS, PHONEBOOK, WLAN, ...) |
| **Таблица сервисов** | EF_SST (~35 сервисов) | EF_UST (100+ сервисов) |
| **Логические каналы** | 1 | 0-19 |
| **Протоколы** | T=0 | T=0, T=1, USB |
| **Типы EF** | Transparent, Linear, Cyclic | Те же + BER-TLV ✨ |
| **Access Control** | ALW, CHV1, CHV2, ADM | ALW, PIN, ADM + ARR (EF_ARR) ✨ |
| **PIN-терминология** | CHV (Card Holder Verification) | PIN (Personal Identification Number) |

---

## 3. Сравнение ключевых EF: одинаковый FID, разное наполнение

### EF_IMSI (6F07)
| | GSM SIM | USIM |
|---|---|---|
| **FID** | 0x6F07 | 0x6F07 (тот же!) |
| **Размер** | 9 байт | 9 байт |
| **Формат** | 3 bytes MCC+MNC + MSIN | Тот же |

### EF_SPN (6F46)
| | GSM SIM | USIM |
|---|---|---|
| **FID** | 0x6F46 | 0x6F46 (тот же!) |
| **Кодировка** | SMS 7-bit default alphabet | UCS2 ✨ (TS 102 221 Annex A) |
| **Display Condition** | byte 1: 0/1 | byte 1: 0/1 |

### EF_ACM (6F39)
| | GSM SIM | USIM |
|---|---|---|
| **FID** | 0x6F39 | 0x6F39 |
| **Тип** | Cyclic | Cyclic |

### EF_ADN (6F3A)
| | GSM SIM (DF_TELECOM) | USIM (DF_PHONEBOOK) |
|---|---|---|
| **FID** | 0x6F3A | 0x6F3A |
| **Структура** | Record: Alpha ID + Number + CCP | Record: Alpha ID + Number + CCP + EXT1 + Email + ANR + ... ✨ |

---

## 4. Новые файлы в USIM (не существовали в GSM)

### Аутентификация и keys (расширение)

| EF | FID | Почему не было в GSM |
|---|---|---|
| **EF_Keys** | 6F08 | В GSM: только Kc (64 bit); нужно CK + IK (128+128) |
| **EF_KeysPS** | 6F09 | PS-domain ключи — не было GPRS |
| **EF_5GAUTHKEYS** | 6FF3 | 5G K (256 bit) |
| **EF_SUCI_Calc_Info** | 6FF6 | 5G privacy — несуществующая концепция в 1995 |

### Работа с сетью и роуминг

| EF | Почему не было в GSM |
|---|---|
| **EF_PLMNwAcT** (6F60) | GSM: только EF_PLMNsel (простой список, без Access Technology) |
| **EF_OPLMNwACT** (6F61) | Роуминг-политики оператора — не было |
| **EF_EHPLMN** (6FD9) | Equivalent HPLMN — не было в GSM |
| **EF_EPSLOCI** (6FE3) | 4G location — не было LTE |
| **EF_5GS3GPPLOCI** (6FF0) | 5G location — не существовало |

### Мультимедиа и сервисы

| EF | Почему не было |
|---|---|
| **EF_MMSN** | MMS — не было в 1995 |
| **EF_GBABP** | Generic Bootstrapping — не было |
| **EF_SPNI, EF_PNNI** | Иконки операторов — не было |
| **EF_URSP** | 5G slicing policy — несуществующая концепция |

---

## 5. Эволюция Service Tables

### GSM: EF_SST (SIM Service Table)
- 1 байт на service
- ~35 сервисов максимум
- Простые биты: ADN, FDN, SMS, AoC, CCP

### USIM: EF_UST (USIM Service Table)
- Минимум 1 байт, может расширяться
- 100+ сервисов
- Каждый бит = сервис с детальной функциональностью

| SST # | Сервис GSM | UST # | Сервис USIM |
|---|---|---|---|
| 1 | CHV1 Disable | 1 | Local Phone Book |
| 2 | ADN | 2 | FDN |
| 4 | SMS | 4 | SMS |
| — | (нет) | 12 | Service Provider Name |
| — | (нет) | 68 | USAT (USIM Toolkit) |
| — | (нет) | 86 | ProSe |
| — | (нет) | 99 | 5GS |

---

## 6. Эволюция безопасности файлов

### GSM (GSM 11.11)
```
Access Byte: AM + SC (2 байта compact)
AM: READ/UPDATE/INVALIDATE/REHABILITATE
SC: ALW (0), CHV1 (1), CHV2 (2), ADM (4), NEV(F)
```

### USIM (TS 102 221)
```
Security Attributes в FCP (3 формата):
1. Compact (AM + SC) — как GSM
2. Expanded (AM_DO + SC_DO) — BER-TLV
3. Referenced (Tag '8B' → EF_ARR) ✨
   → не надо дублировать security в каждом EF
   → указатель на запись в EF_ARR (0x2F06)
```

---

## 7. Совместимость: почему старые FID работают

```
КЛЮЧЕВОЙ ДИЗАЙН-ПРИНЦИП:
┌────────────────────────────────────────────┐
│ ETSI/3GPP СОХРАНИЛИ FID между поколениями │
│                                            │
│ EF_IMSI  = 6F07 в GSM, 3G, 4G, 5G         │
│ EF_SPN   = 6F46 во всех                   │
│ EF_ADN   = 6F3A во всех                   │
│ EF_SMS   = 6F3C во всех                   │
│                                            │
│ → Телефон может читать IMSI               │
│   не зная, SIM это или USIM!               │
└────────────────────────────────────────────┘
```

Это обеспечило **backward compatibility**: старые телефоны (GSM) читают IMSI, SPN, ADN из USIM теми же командами и FID, что и из SIM.

---

## 8. Итоги: что изменилось

| Измерение | GSM → USIM |
|---|---|
| **Гибкость** | Фиксированная → Много-приложений + ADF |
| **Масштаб** | ~20 EF → ~150 EF + 12 DF |
| **Сервисы** | ~35 → 100+ |
| **Безопасность** | Simple → ARR, SE, multi-PIN |
| **Интероперабельность** | FID сохранены (!) |
| **Кодирование** | SMS 7-bit → UCS2 |
| **Расширяемость** | Phase ID byte → EF_DIR + AID + UST |

## Ссылки на источники

- GSM 11.11: [[wiki/summaries/gsm_1111]]
- USIM: [[wiki/summaries/ts_131102]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
- EF типы: [[wiki/concepts/EF_Types]]
- Аутентификация: [[wiki/syntheses/auth_evolution]]
