---
tags: [JavaCard, GlobalPlatform, specification, summary]
source: "[[Specifications/GlobalPlatform/GPC_CardSpecification_v2.3.1.pdf]]"
type: specification
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# GlobalPlatform Card Specification v2.3.1

> **Издатель**: GlobalPlatform Inc.
> **Версия**: v2.3.1 (2025)
> **Страниц**: ~300

## Обзор

**GlobalPlatform Card Specification** — основной стандарт управления смарт-картами. Определяет:
- Архитектуру Security Domains (ISD, SSD)
- Команды управления приложениями (LOAD, INSTALL, DELETE)
- Secure Channel Protocols (SCP02, SCP03)
- Карточный реестр (Registry) и команду GET STATUS
- Трёхуровневую иерархию AID

## Ключевые разделы

### 1. Security Domains (§11.5)
- **ISD** (Issuer Security Domain) — обязательный, владелец карты
- **SSD** (Supplementary Security Domain) — провайдеры услуг
- Привилегии: SecurityDomain, CardLock, CardTerminate, DAP Verification

### 2. Управление приложениями (§11.5.2)
- INSTALL [for load] — подготовка к загрузке CAP
- LOAD — передача CAP-файла
- INSTALL [for install] — создание экземпляра апплета (передаёт AID + Install Parameters)
- INSTALL [for delete] — удаление
- DELETE — удаление объекта

### 3. Install Parameters (§11.5.2.3.2)
Полная структура для INSTALL [for install]:
```
L_ELF + Load File AID + L_EM + Module AID + L_App + Instance AID
+ Privileges + Install Parameters (C9, EF) + Install Token
```

### 4. Secure Channel Protocols

| SCP | Базовые алгоритмы | Применение |
|---|---|---|
| **SCP02** | 3DES-CBC, DES-MAC | Legacy |
| **SCP03** | AES-128/256, AES-CMAC | Современные карты |
| **SCP80** | По TS 102 225 | OTA |
| **SCP81** | TLS/PSK | Удалённый доступ |

### 5. GET STATUS (§11.11)
- `80 F2 P1 P2` — запрос реестра карты
- P1P2 = `02 00`: список ISD
- P1P2 = `20 00`: список приложений + SSD
- P1P2 = `40 00`: список ELF
- Возврат: TLV с AID'ами и статусами

## Применение к SIM-картам

На SIM-картах GPC 2.3.1 работает совместно с:
- **ETSI TS 102 226**: определяет UICC-специфичные Install Parameters (`CA`, `TA`, `EA` теги)
- **ETSI TS 102 225**: Secured APDU (SCP80)
- **Java Card**: платформа исполнения апплетов

## Связи

- GP архитектура: [[wiki/concepts/GlobalPlatform_Card]]
- Установка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- STK install params: [[wiki/summaries/ts_102_226|TS 102 226]]
- Организация: [[wiki/entities/GlobalPlatform]]
