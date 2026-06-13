---
tags: [entity, standards-body, GlobalPlatform, card-management]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
aliases: [GP, GlobalPlatform Inc.]
---

# GlobalPlatform — Стандарт управления смарт-картами

## Общие сведения

**GlobalPlatform** — международная организация по стандартизации, определяющая архитектуру управления смарт-картами и secure elements. GP-стандарты используются для загрузки, установки и управления приложениями на UICC/SIM, eSIM, платежных картах, eUICC.

## Ключевые спецификации

| Спецификация | Версия | Назначение |
|---|---|---|
| **Card Specification** | v2.3.1 | Управление картой: LOAD, INSTALL, DELETE, SCP |
| **Card Specification** | v3.0+ | Поддержка eUICC, IoT, дополнительных SCP |
| **Secure Channel Protocol 03** | 1.2 | SCP03: AES-128/256 secure channel |
| **TEE Specification** | — | Trusted Execution Environment |
| **Secure Element Configuration** | — | SE provisioning |

## GP Card Architecture

- **ISD** (Issuer Security Domain) — обязательный домен владельца карты
- **SSD** (Supplementary Security Domain) — домены контент-провайдеров
- **SCP** (Secure Channel Protocol) — защищённый канал (SCP02, SCP03, SCP80, SCP81)
- **DAP** (Data Authentication Pattern) — проверка подлинности загружаемого кода

## Применение в проекте

- Управление апплетами на SIM-картах через GP-команды
- Инструмент GlobalPlatformPro (`gp.jar`) для LOAD/INSTALL/DELETE
- Install Parameters для STK-апплетов по GP + TS 102 226

## Связи

- GP Card Architecture: [[wiki/concepts/GlobalPlatform_Card]]
- Разработка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- Спецификация: [[wiki/summaries/gpc_card_spec_2_3_1]]
- Связанные: [[wiki/entities/ETSI]], [[wiki/entities/3GPP]], [[wiki/entities/TCA]]
