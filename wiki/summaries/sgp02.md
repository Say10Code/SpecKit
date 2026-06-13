---
tags: [eSIM, GSMA, M2M, specification, summary]
source: "[[Specifications/eSIM/SGP.02-v4.1.pdf]]"
type: specification
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# GSMA SGP.02: Remote Provisioning Architecture for M2M v4.1

> **Издатель**: GSMA
> **Версия**: v4.1
> **Страниц**: 456

## Обзор

**SGP.02** — спецификация GSMA, определяющая архитектуру Remote SIM Provisioning для M2M (Machine-to-Machine). Это решение, в котором оператор управляет eSIM-профилями удалённо, без участия конечного пользователя — через SM-DP (подготовка профилей) и SM-SR (маршрутизация). ^[inferred]

## Ключевые разделы

### 1. Архитектура
- SM-DP (Subscription Manager — Data Preparation): создание и защита профилей
- SM-SR (Subscription Manager — Secure Routing): доставка профилей, управление их жизненным циклом
- eUICC: чип, хранящий ISD-P для каждого профиля

### 2. Процесс Provisioning
1. SM-DP создаёт профиль (IMSI, ICCID, ключи, файловая система)
2. SM-DP передаёт защищённый профиль в SM-SR
3. SM-SR доставляет профиль на eUICC через SMS или data-канал
4. eUICC устанавливает профиль в новый ISD-P
5. SM-SR управляет состоянием (Enable, Disable, Delete)

### 3. Безопасность
- PSK (Pre-Shared Key) между eUICC и SM-SR
- SCP03 или SCP80 для защищённого канала
- EAL4+ сертификация eUICC

### 4. SM-SR Swap
Процедура передачи группы eUICC от одного SM-SR другому (смена владельца/оператора).

## Отличия от Consumer (SGP.22)

| SGP.02 (M2M) | SGP.22 (Consumer) |
|---|---|
| Push-модель | Pull-модель |
| SM-DP + SM-SR | SM-DP+ (объединённый) |
| PSK аутентификация | PKI (сертификаты) |
| BIP транспорт | HTTPS/IP |
| Один SM-SR на группу eUICC | Любой SM-DP+ ↔ любой eUICC |

## Связи

- eSIM концепт: [[wiki/concepts/eSIM]]
- Whitepaper: [[wiki/summaries/esim_whitepaper]]
- GlobalPlatform: [[wiki/concepts/GlobalPlatform_Card]]
- Организация: [[wiki/entities/GSMA]]
