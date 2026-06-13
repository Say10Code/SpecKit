---
tags: [USIM, UICC, 3GPP, application, authentication]
type: concept
level: intermediate
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_131102]]"
  - "[[wiki/summaries/ts_131101]]"
---

# USIM — Universal Subscriber Identity Module

## Определение

**USIM** (Universal Subscriber Identity Module) — это **3GPP-приложение** на UICC, обеспечивающее идентификацию абонента, аутентификацию и доступ к сетям 3GPP (UMTS, LTE, 5G). ^[extracted]

Это эволюция SIM (GSM): USIM добавляет mutual authentication, integrity protection, поддержку множественных контекстов безопасности и поколений сети (3G→4G→5G).

## Место USIM в архитектуре

```
┌──────────────────────────────────────┐
│ Мобильное устройство (ME)            │
│ ┌──────────────────────────────────┐ │
│ │ NAS (Non-Access Stratum)         │ │
│ │   ├─ MM (Mobility Management)    │ │
│ │   └─ SM (Session Management)     │ │
│ └──────────────┬───────────────────┘ │
│                │ APDU                │
├────────────────┼─────────────────────┤
│ UICC           │                     │
│ ┌──────────────┴───────────────────┐ │
│ │ ADF.USIM                         │ │
│ │   ├─ EF_IMSI                     │ │
│ │   ├─ EF_Keys (CK, IK)            │ │
│ │   ├─ EF_UST (Service Table)      │ │
│ │   ├─ EF_SPN (Operator Name)      │ │
│ │   └─ ... ещё ~150 EF             │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

## Эволюция: SIM → USIM

| Свойство | SIM (GSM) | USIM (3G+) |
|---|---|---|
| Стандарт | GSM 11.11, TS 51.011 | TS 31.102 |
| Аутентификация | Односторонняя (сеть→терминал) | **Взаимная** (mutual AKA) |
| Шифрование | A5/1, A5/2 | UEA1, UEA2 (SNOW 3G, AES) |
| Integrity | ❌ | ✅ (UIA1, UIA2) |
| AID | `A0 00 00 00 09 00 01` | `A0 00 00 00 87 10 02` |
| EF-идентификаторы | Фиксированные (6Fxx) | Фиксированные (6Fxx), больше файлов |
| 5G Security | ❌ | ✅ (5G AKA, EAP-AKA', SUCI) |
| Service Table | Не было | EF_UST (100+ сервисов) |

## Идентификация абонента

### IMSI (EF_IMSI)
Главный идентификатор: MCC (3 digits) + MNC (2-3 digits) + MSIN (до 10 digits)

### SUPI/SUCI (5G)
- **SUPI** (Subscription Permanent Identifier) — 5G-версия IMSI
- **SUCI** (Subscription Concealed Identifier) — шифрованный SUPI (privacy!)
- Расчёт SUCI через EF_SUCI_Calc_Info в DF_5GS

## Аутентификация по поколениям

### 2G (GSM)
- Терминал → сеть: IMSI
- Сеть → UICC: RAND
- UICC → сеть: SRES (COMP128) + Kc (для шифрования)

### 3G (UMTS AKA)
- Взаимная аутентификация
- UICC → сеть: RES, CK, IK
- Сеть проверяет RES; оба вычисляют CK/IK

### 4G (EPS AKA)
- Расширенная UMTS AKA
- CK + IK → KASME (для EPS security context)

### 5G (5G AKA / EAP-AKA')
- **5G AKA**: primary authentication (UMTS-style)
- **EAP-AKA'**: secondary authentication (EAP-based)
- K_AUSF, K_SEAF — иерархия ключей
- **SUCI** для защиты идентификатора

## USIM Service Table (EF_UST)

EF_UST — битовая маска, которая определяет, какие сервисы USIM поддерживает. Это центральный механизм конфигурации.

Каждый бит соответствует сервису:
```
Service 1:  Local Phone Book
Service 2:  Fixed Dialling Numbers (FDN)
Service 12: Service Provider Name (SPN)
Service 14: Administrative Data
Service 27: USIM Service Table itself (!)
Service 38: BIP (Bearer Independent Protocol)
Service 68: USAT (USIM Application Toolkit)
Service 99: 5GS (5G Support)
...
```

Если бит = 1 → сервис доступен (и EF есть); бит = 0 → сервис не доступен (EF может отсутствовать).

## Ключевые сервисы USIM

### Регистрация в сети
- **PLMN Selection**: EF_PLMNwAcT, EF_OPLMNwACT, EF_HPLMNwAcT
- **Forbidden PLMNs**: EF_FPLMN (сети, куда нельзя подключаться)
- **Location**: EF_LOCI (3G), EF_EPSLOCI (4G), EF_5GS3GPPLOCI (5G)
- **Equivalent HPLMN**: EF_EHPLMN (группа домашних сетей)

### Безопасность
- **EF_Keys**: CK + IK для 3G/4G
- **EF_KeysPS**: CK + IK для PS domain
- **DF_5GS**: все 5G-ключи и контексты
- **EF_ACC**: Access Control Class (11-15 для спецслужб)

### Телефония и контакты
- **EF_ADN**: Телефонная книга (в DF_PHONEBOOK)
- **EF_FDN**: Fixed Dialling Numbers (только разрешённые номера)
- **EF_BDN**: Barred Dialling Numbers (запрещённые номера)
- **EF_SDN**: Service Dialling Numbers (сервисные номера)
- **EF_ECC**: Emergency Call Codes
- **EF_SMS**: Хранилище SMS
- **EF_ACM**: Счётчик звонков

### Отображение оператора
- **EF_SPN**: Service Provider Name (имя оператора, UCS2) ^[extracted]
- **EF_PNN**: PLMN Network Name (имя сети)
- **EF_OPL**: Operator PLMN List (MCC→имя)
- Иконки: [[wiki/research/operator_icons_on_sim|EF_SPNI, EF_PNNI, DF_GRAPHICS]]
- Подробно: [[notes/EF_SPN_PNN]]

## USIM и CAT/USAT

USIM поддерживает **USAT** (USIM Application Toolkit) — адаптацию CAT для 3GPP:
- STK-меню (SET UP MENU, SELECT ITEM)
- Proactive commands через CAT
- Контролируется через EF_UST (service 68)
- EF_UFC (USAT Facility Control)

## Связи

- Базовое приложение: [[wiki/concepts/UICC]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
- Безопасность: [[wiki/concepts/UICC_Security]]
- CAT/STK: [[wiki/concepts/CAT_STK]]
- Specifications: [[wiki/summaries/ts_131102|TS 31.102]], [[wiki/summaries/ts_131101|TS 31.101]]
