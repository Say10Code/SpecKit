---
tags: [eSIM, eUICC, GSMA, RSP, profile]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/esim_whitepaper|eSIM Whitepaper]]"
  - "[[wiki/summaries/sgp02|SGP.02 v4.1]]"
---

# eSIM / eUICC — Embedded SIM и Remote SIM Provisioning

## Определение

**eSIM** (embedded SIM) — технология, позволяющая загружать профили операторов на встроенный чип (eUICC) удалённо, без физической замены SIM-карты. Стандартизирована GSMA в спецификациях SGP.02 (M2M) и SGP.22 (Consumer). ^[extracted]

## Ключевые понятия

| Термин | Определение |
|---|---|
| **eUICC** | Embedded UICC — физический чип (может быть встроенным или съёмным), поддерживающий множественные профили |
| **Профиль** | Данные оператора + подписка: IMSI, ICCID, ключи, файловая система, приложения |
| **RSP** | Remote SIM Provisioning — технология удалённой загрузки профилей |
| **eSIM** | Общий термин для технологии; часто путают с eUICC |

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                 GSMA eSIM Ecosystem                      │
│                                                          │
│  ┌─────────────┐    ┌──────────────┐   ┌─────────────┐  │
│  │ SM-DP(+)    │───→│ SM-SR /      │──→│ eUICC       │  │
│  │ (Profile    │    │ SM-DS        │   │ (встроенный │  │
│  │  Factory)   │    │ (Router /    │   │  чип)       │  │
│  └─────────────┘    │  Discovery)  │   └─────────────┘  │
│                     └──────────────┘                     │
│  ┌─────────────┐    ┌──────────────┐                    │
│  │ LPA         │    │ CI           │                    │
│  │ (Local      │    │ (Certificate │                    │
│  │  Profile    │    │  Issuer)     │                    │
│  │  Assistant) │    └──────────────┘                    │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

## Два решения GSMA

### M2M (SGP.02)

| Свойство | Значение |
|---|---|
| **Рынок** | IoT, промышленные устройства, automotive |
| **Модель** | Push — сервер управляет профилями |
| **Пользователь** | Не взаимодействует |
| **Ключевые стандарты** | SGP.02 (архитектура), SGP.05 (безопасность eUICC), SAS-UP (производство) |
| **SM-DP** | Готовит и защищает профили |
| **SM-SR** | Маршрутизирует профили на eUICC, управляет их состоянием |
| **eUICC** | Содержит ISD-P (Issuer Security Domain Profile) для каждого профиля |
| **Аутентификация** | PSK (Pre-Shared Key) между eUICC и SM-SR |
| **Транспорт** | SMS, CAT_TP, TCP/IP (через BIP) |
| **SM-SR Swap** | Процедура передачи группы eUICC другому SM-SR |

### Consumer (SGP.22)

| Свойство | Значение |
|---|---|
| **Рынок** | Смартфоны, планшеты, умные часы |
| **Модель** | Pull — пользователь инициирует загрузку профиля |
| **Пользователь** | Управляет через UI устройства (LPA) |
| **Ключевые стандарты** | SGP.22 (архитектура), SGP.23 (тесты), SGP.25 (безопасность) |
| **SM-DP+** | Объединяет функции SM-DP и SM-SR |
| **SM-DS** | Discovery Server — «доска объявлений» для уведомлений |
| **LPA** | Local Profile Assistant — интерфейс в устройстве (LPAe в eUICC + LPAd в device) |
| **Аутентификация** | PKI (сертификаты X.509) — любой eUICC с любым SM-DP+ |
| **Транспорт** | Только HTTPS/IP |
| **Совместимые устройства** | Primary (телефон) + Companion (часы, планшет) |

## Профиль (Profile)

Структура профиля аналогична содержимому физической SIM:

```
Profile:
├── ISD-P (Issuer Security Domain - Profile)
├── File System (MF, DF, EF)
│   ├── EF_ICCID
│   ├── EF_IMSI
│   └── ... все EF из ADF.USIM ...
├── Security Keys (Ki, K, OPc)
├── Applications (USIM, ISIM, STK-апплеты)
└── Profile Metadata (имя, оператор, политики)
```

Профили создаются по спецификации **SIMalliance eUICC Profile Package** (Interoperable Profile).

## Состояния профиля

```
Created → Disabled → Enabled → Disabled → Deleted
```

- **Disabled**: профиль есть на eUICC, но не активен
- **Enabled**: профиль активен — устройство в сети этого оператора
- Только один профиль может быть Enabled одновременно
- Пользователь переключает профили через LPA (Consumer) или сервер (M2M)

## Безопасность

### eUICC (чип)
- Common Criteria EAL4+ (Protection Profile)
- Защита от физических атак, side-channel
- ISD-P для каждого профиля (изоляция)

### Производство
- GSMA SAS-UP (Site Accreditation for UICC Personalization)
- Сертификация производственных площадок

### Платформы
- GSMA SAS-SM (Subscription Manager)
- Сертификация SM-DP/SM-DP+ хостинга

### Функциональная совместимость
- Тесты GlobalPlatform для eUICC
- Тесты GCF/PTCRB для устройств
- Тесты GSMA для SM-DP/SM-DP+

## eSIM vs UICC: сравнение

| Свойство | UICC (классическая) | eUICC (eSIM) |
|---|---|---|
| **Форм-фактор** | Съёмная (2FF/3FF/4FF) | Встроенная (MFF2) или съёмная |
| **Профили** | 1 профиль | Множественные профили |
| **Смена оператора** | Физическая замена SIM | Удалённая загрузка профиля |
| **Управление** | Физическое | Удалённое (OTA) |
| **Применение** | Телефоны | Телефоны, IoT, автомобили |
| **Стандарт** | ETSI TS 102 221 | GSMA SGP.02 / SGP.22 |

## Связи

- Платформа UICC: [[wiki/concepts/UICC]]
- Whitepaper: [[wiki/summaries/esim_whitepaper]]
- M2M спецификация: [[wiki/summaries/sgp02|SGP.02 v4.1]]
- GP архитектура: [[wiki/concepts/GlobalPlatform_Card]]
- Организация: [[wiki/entities/GSMA]]
- eSIM evolution: [[wiki/syntheses/esim_evolution|eSIM: от UICC к профилю]]
