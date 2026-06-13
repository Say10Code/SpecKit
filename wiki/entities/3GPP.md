---
tags: [entity, standards-body, 3GPP]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
aliases: [3rd Generation Partnership Project]
---

# 3GPP — 3rd Generation Partnership Project

## Общие сведения

**3GPP** — консорциум организаций по стандартизации, разрабатывающий протоколы для мобильных сетей: UMTS (3G), LTE (4G) и 5G NR (5G). Specifications 3GPP публикуются через региональные SDO, включая [[wiki/entities/ETSI]].

## Организационная структура

- **TSG RAN** (Radio Access Network) — радиоинтерфейс
- **TSG SA** (Service & System Aspects) — архитектура, сервисы
- **TSG CT** (Core Network & Terminals) — ядро сети и терминалы
  - **CT6**: UICC, смарт-карты (ранее T3)

## Ключевые спецификации UICC (CT6)

| 3GPP TS | ETSI TS | Название |
|---|---|---|
| TS 31.101 | [[wiki/summaries/ts_131101\|TS 131 101]] | UICC-Terminal I/F для 3GPP |
| TS 31.102 | TS 131 102 | USIM характеристики |
| TS 31.103 | TS 131 103 | ISIM характеристики |
| TS 31.111 | TS 131 111 | USIM Application Toolkit (USAT) |
| TS 31.115 | TS 131 115 | Secured packet structure для UICC |
| TS 31.116 | TS 131 116 | Remote APDU structure для UICC |
| TS 31.124 | TS 131 124 | UICC API для JavaCard |

## Релизы и поколения

| Release | Год | Поколение |
|---|---|---|
| Rel-99 | 2000 | 3G (UMTS) |
| Rel-8 | 2008 | 4G (LTE) |
| Rel-15 | 2018 | 5G Phase 1 |
| Rel-17 | 2022 | 5G Phase 2 |
| Rel-18 | 2024 | 5G-Advanced |

## Нумерация 3GPP-спецификаций

- **TS 31.xxx** — UICC и USIM
- **TS 51.xxx** — GSM SIM
- **TS 23.xxx** — Архитектура сети
- **TS 24.xxx** — Протоколы ядра сети (NAS)

## Связи

- Specifications публикуются через [[wiki/entities/ETSI]]
- UICC базируется на ISO/IEC 7816: [[wiki/entities/ISO7816]]
- USIM приложение: [[wiki/concepts/UICC]]
