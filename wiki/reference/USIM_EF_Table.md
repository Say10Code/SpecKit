---
tags: [reference, USIM, EF, table]
type: reference
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_131102]]"
---

# USIM EF Reference — Ключевые элементарные файлы

Быстрая справочная таблица ключевых EF в ADF.USIM. Полный список (200+ EF) — в [[wiki/summaries/ts_131102|TS 31.102]].

> [!seealso] Исчерпывающий каталог
> Детальный разбор каждого EF с байт-в-байт структурами, hex-примерами, access conditions и инструментами — в [[wiki/research/usim_ef_catalog|EF-каталог USIM Research]] (120+ EF, 80 KB).

## Аутентификация и идентификация

| EF | FID | Тип | Размер | Описание |
|---|---|---|---|---|
| EF_IMSI | `6F07` | Transparent | 9 байт | IMSI абонента |
| EF_Keys | `6F08` | Transparent | 33 байт | CK + IK (CS/PS) |
| EF_KeysPS | `6F09` | Transparent | 33 байт | CK + IK (PS domain) |
| EF_MSISDN | `6F40` | Linear Fixed | n×14 | Номер телефона |
| EF_UST | `6F38` | Transparent | ≥1 байт | USIM Service Table |
| EF_EST | `6F56` | Transparent | ≥1 байт | Enabled Services Table |
| EF_ACC | `6F78` | Transparent | 2 байта | Access Control Class |
| EF_AD | `6FAD` | Transparent | 4+N байт | Administrative Data |

## PLMN и роуминг

| EF | FID | Тип | Описание |
|---|---|---|---|
| EF_PLMNwAcT | `6F60` | Transparent | User PLMN selector |
| EF_OPLMNwACT | `6F61` | Transparent | Operator PLMN selector |
| EF_HPLMNwAcT | `6F62` | Transparent | HPLMN selector |
| EF_FPLMN | `6F7B` | Transparent | Forbidden PLMNs |
| EF_EHPLMN | `6FD9` | Transparent | Equivalent HPLMN |
| EF_LOCI | `6F7E` | Transparent | 3G Location Info |
| EF_EPSLOCI | `6FE3` | Transparent | 4G Location Info |
| EF_5GS3GPPLOCI | `4F01` | Transparent | 5G 3GPP Location |
| EF_PSLOCI | `6F73` | Transparent | PS Location Info |

## Имя оператора

| EF | FID | Тип | Описание |
|---|---|---|---|
| EF_SPN | `6F46` | Transparent | Service Provider Name |
| EF_PNN | `6FC5` | Linear Fixed | PLMN Network Name |
| EF_OPL | `6FC6` | Linear Fixed | Operator PLMN List |

## Телефония

| EF | FID | Тип | Описание |
|---|---|---|---|
| EF_ADN | `6F3A` | Linear Fixed | Abbreviated Dialling Numbers |
| EF_FDN | `6F3B` | Linear Fixed | Fixed Dialling Numbers |
| EF_SDN | `6F49` | Linear Fixed | Service Dialling Numbers |
| EF_BDN | `6FDB` | Linear Fixed | Barred Dialling Numbers |
| EF_ECC | `6FB7` | Linear Fixed | Emergency Call Codes |
| EF_SMS | `6F3C` | Linear Fixed | Short Messages |
| EF_ACM | `6F39` | Cyclic | Accumulated Call Meter |

## 5G Security (DF_5GS)

| EF | FID | Описание |
|---|---|---|
| EF_5GAUTHKEYS | `6FF3` | 5G Auth Keys (K, RIN) |
| EF_5GS3GPPNSC | `6FF1` | Cyclic | 5G 3GPP NAS Security Context |
| EF_5GSN3GPPNSC | `6FF2` | Linear Fixed | 5G non-3GPP NAS Security Context |
| EF_SUCI_Calc_Info | `6FF6` | SUCI Calc Info (Home Network PK) |
| EF_UAC_AIC | `6FF5` | UAC Access Identities |
| EF_URSP | `6FFA` | UE Route Selection Policy |
| EF_KAUSF_Derivation | `6FFC` | K_AUSF derivation config |

## Другие

| EF | FID | Описание |
|---|---|---|
| EF_SPN_Icon | `6FD7` | SPN Icon (PNG/JPEG) [[wiki/research/operator_icons_on_sim\|📄]] |
| EF_PNN_Icon | `6FD8` | PNN Icon (PNG/JPEG) [[wiki/research/operator_icons_on_sim\|📄]] |
| EF_SMSP | `6F42` | SMS Parameters |
| EF_ARR | `6F06` | Access Rule Reference |

## Directory Structure внутри ADF.USIM

```
ADF.USIM
├── DF_5GS              ← 5G Security
├── DF_PHONEBOOK        ← Телефонная книга
├── DF_GSM-ACCESS       ← Legacy GSM ключи (Kc, KcGPRS)
├── DF_WLAN             ← Wi-Fi offloading
├── DF_ProSe            ← Proximity Services
├── DF_HNB              ← Home NodeB / CSG
├── DF_TV               ← TV конфигурация
├── DF_ACDC             ← Application Data Connectivity
├── DF_SNPN             ← Stand-alone Non-Public Networks
├── DF_5G_ProSe         ← 5G Proximity Services
├── DF_V2X              ← C-V2X (автомобили)
└── DF_MCS              ← Mission Critical Services
```

## Типы файлов (легенда)

| Код | Тип |
|---|---|
| T | Transparent (поток байт) |
| LF | Linear Fixed (записи) |
| Cy | Cyclic (кольцо записей) |

## Связанные

- Платформа: [[wiki/concepts/UICC_File_System]]
- Типы EF: [[wiki/concepts/EF_Types]]
- SPN/PNN детали: [[notes/EF_SPN_PNN]]
- Иконки оператора (research): [[wiki/research/operator_icons_on_sim]]
- Полный список: [[wiki/summaries/ts_131102|TS 31.102 Clause 4]]
