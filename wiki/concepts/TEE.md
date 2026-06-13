---
tags: [GlobalPlatform, TEE, security, trusted-execution]
type: concept
level: advanced
created: 2026-06-11
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/concepts/GlobalPlatform_Card|GP Card Architecture]]"
  - "[[wiki/concepts/SCP|Secure Channel Protocol]]"
---

# GlobalPlatform TEE — Trusted Execution Environment

## Определение

> [!abstract] Определение
> **TEE (Trusted Execution Environment)** — изолированная безопасная область процессора устройства (не смарт-карты!), определённая GlobalPlatform. TEE выполняет код в隔离рованном контексте, отделённом от Rich OS (Android/iOS). На смарт-картах TEE используется для операций, требующих UI (например, подтверждение платежа). ^[inferred]

## TEE vs UICC/SE

```
┌─────────────────────────────────────────────────┐
│              Устройство (телефон)                │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Rich OS  │  │ TEE      │  │ UICC / SE    │  │
│  │ (Android)│  │ (Trusted │  │ (SIM-карта)  │  │
│  │          │  │  Apps)   │  │              │  │
│  │ • Apps   │  │ • Wallet │  │ • USIM       │  │
│  │ • Browser│  │ • FIDO   │  │ • ISIM       │  │
│  │ • Games  │  │ • DRM    │  │ • STK Applet │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│       │              │               │          │
│       ▼              ▼               ▼          │
│  ┌──────────────────────────────────────────┐   │
│  │          Hardware (SoC)                  │   │
│  │  ARM TrustZone / Intel SGX / ...        │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## TEE vs UICC Security

| Свойство | UICC (SIM) | TEE |
|---|---|---|
| **Где находится** | Внешний чип (SIM-карта) | Внутри SoC устройства |
| **Изоляция** | Физическая (отдельный чип) | Логическая (TrustZone) |
| **Память** | Ограничена (KB-MB) | Десятки MB |
| **CPU** | Слабый (8-32-bit) | Мощный (ARM Cortex-A) |
| **Дисплей** | Через STK (DISPLAY TEXT) | Прямой доступ к экрану |
| **Сеть** | Через BIP (медленно) | Прямой TCP/IP |
| **Стандарт** | ETSI/3GPP | GlobalPlatform |
| **Сертификация** | CC EAL4+ для eUICC | CC EAL2+-EAL4+ |

## TEE и UICC: совместная работа

### Сценарий: Платёж с подтверждением

```
1. П платёжный апплет (UICC) получает транзакцию через NFC
2. Апплет формирует запрос на подтверждение
3. Запрос передаётся в TEE через Trusted UI
4. TEE показывает диалог «Подтвердить платёж 100 EUR?»
5. Пользователь вводит PIN / биометрию
6. TEE верифицирует → возвращает OK апплету
7. Апплет завершает транзакцию
```

### GP TEE API

GlobalPlatform определяет API для взаимодействия UICC ↔ TEE:
- **TEE Client API** — для Rich OS приложений
- **TEE Internal API** — для Trusted Applications внутри TEE
- **TEE Secure Element API** — для UICC/SE взаимодействия

## GlobalPlatform TEE Specifications

| Спецификация | Версия | Назначение |
|---|---|---|
| **TEE System Architecture** | v1.3 | Общая архитектура TEE |
| **TEE Client API** | v1.0 | API для приложений Rich OS |
| **TEE Internal Core API** | v1.3.1 | API для Trusted Applications |
| **TEE Secure Element API** | v1.1.3 | Взаимодействие TEE ↔ UICC/SE |
| **TEE Protection Profile** | v1.3 | Common Criteria PP для TEE |

## Связи

- GP Card Architecture: [[wiki/concepts/GlobalPlatform_Card|GP Card]]
- SCP: [[wiki/concepts/SCP|Secure Channel Protocol]]
- Безопасность: [[wiki/concepts/UICC_Security]]
- eSIM: [[wiki/concepts/eSIM]]
