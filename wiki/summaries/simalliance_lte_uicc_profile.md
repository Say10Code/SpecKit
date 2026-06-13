---
tags: [SIMalliance, LTE, UICC, profile, interoperability, eSIM, specification, summary]
type: summary
created: 2026-06-12
updated: 2026-06-12
status: reviewed
source: "[[Specifications/eSIM/SIMalliance_LTE_UICC_Profile_V1.0.pdf]]"
---

# SIMalliance LTE UICC Profile V1.0

> **Версия**: V1.0
> **Организация**: SIMalliance (ныне Trusted Connectivity Alliance — TCA)
> **Статус**: Промышленный профиль (industry profile)

## Обзор

**SIMalliance LTE UICC Profile** — спецификация промышленного профиля UICC для LTE-сетей. Документ определяет, какие файлы (EF), сервисы и параметры обязательны или опциональны для UICC, работающей в LTE-окружении. Это не стандарт ETSI/3GPP, а индустриальный guidance по интероперабельности. ^[inferred]

> Цель: гарантировать, что UICC от любого производителя будет корректно работать с LTE-терминалом и сетью любого оператора. Профиль сужает выбор из множества опций, допускаемых 3GPP-спецификациями.

## Ключевое содержание

### 1. Обязательные и опциональные EF
Документ определяет **минимальный набор файлов** для LTE-карты:

| Категория | Примеры файлов | Статус |
|---|---|---|
| Идентификационные | EF_ICCID, EF_IMSI | Обязательно |
| Ключи безопасности | EF_K, EF_OPc, EF_Keys | Обязательно |
| USIM Service Table | EF_UST (LTE-сервисы: 4, 25, 26, 31, 33, 37) | Обязательно |
| PLMN-селекция | EF_PLMNsel, EF_OPLMNwAcT, EF_FPLMN | Обязательно |
| NAS-конфигурация | EF_NASConfig, EF_EPSLOCI, EF_EPSNSC | Обязательно |
| Сервисные файлы | EF_SPN (имя сети), EF_SPDI, EF_ECC | Опционально |
| Адресная книга | EF_PBR, EF_ADN, EF_EXT1, EF_PSC | Опционально |

### 2. Требования к USAT (USIM Application Toolkit)
- Минимальный набор proactive commands для LTE
- TERMINAL PROFILE: какие биты должны поддерживаться
- BIP (Bearer Independent Protocol): поддержка для IMS/VoLTE
- Event download: какие события обязательны

### 3. Интероперабельность
- Тестовые сценарии для проверки совместимости карты и терминала
- Ожидаемые значения Status Words при стандартных операциях
- Граничные значения для полей (макс. длина IMSI, ICCID и т.д.)
- Требования к памяти для файлов (размер записей, количество записей)

### 4. Связь с eSIM Profile Package
Профиль, описанный в этом документе, представляет собой контентную часть **eSIM Profile Package** (по GSMA SGP.02/SGP.22):

```
eSIM Profile Package
  ├── Profile Header (ISD-P AID, Profile Name)
  ├── Profile Metadata (версии, ICCID, оператор)
  ├── File System ← Содержимое соответствует SIMalliance LTE UICC Profile
  ├── Security Domain (ISD с ключами)
  └── Toolkit-апплеты (опционально)
```

Профиль определяет **что должно быть** в файловой системе и приложениях UICC для LTE. eSIM Profile Package определяет **как это упаковать и доставить** на eUICC.

## Значение для проекта

- Используется как **чек-лист** при разработке профилей SIM-карт для LTE
- Позволяет понять, какие EF минимально необходимы для LTE-совместимой карты
- Служит мостом между абстрактными требованиями 3GPP и конкретной имплементацией
- Организация SIMalliance → TCA: [[wiki/entities/TCA]]

## Связи

- eSIM и RSP: [[wiki/concepts/eSIM]]
- eSIM White Paper: [[wiki/summaries/esim_whitepaper]]
- SGP.02 (M2M RSP): [[wiki/summaries/sgp02|SGP.02 v4.1]]
- Файловая система USIM: [[wiki/concepts/UICC_File_System]]
- Базовый стандарт UICC: [[wiki/summaries/ts_102221|TS 102 221]]
- USIM: [[wiki/summaries/ts_131102|TS 31.102]]
- Сертификация: [[wiki/concepts/Certification_GCF_PTCRB]]
- USIM EF Table: [[wiki/reference/USIM_EF_Table]]
