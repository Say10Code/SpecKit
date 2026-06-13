---
tags: [synthesis, OTA, SMS-PP, CAT_TP, eSIM, RSP, evolution]
created: 2026-06-10
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/concepts/OTA_Remote_Management]]"
  - "[[wiki/summaries/ts_102_226|TS 102 226]]"
  - "[[wiki/concepts/eSIM]]"
  - "[[wiki/summaries/sgp02|SGP.02]]"
---

# OTA: От SMS-PP к eSIM RSP — Эволюция удалённого управления SIM

> **Synthesis** — как менялось удалённое управление SIM-картами: от простых SMS-команд до защищённой PKI-инфраструктуры eSIM.

---

## 1. Три эпохи OTA

```
Эпоха I: SMS-PP          Эпоха II: BIP/CAT_TP      Эпоха III: eSIM RSP
═══════════════════      ══════════════════════     ═══════════════════
1998-2005                2005-2016                  2016-настоящее

SMS-DELIVER             OPEN CHANNEL               HTTPS + PKI
9.6 kbps                2-100+ Mbps                Broadband
<140 байт/SMS          Потоковая передача         Полный профиль (KB-MB)
Симметричные ключи     Симметричные ключи         PKI + сертификаты
TAR-маршрутизация      TAR + каналы               Профиль-изоляция
```

---

## 2. Эпоха I: SMS-PP (GSM 03.48 / TS 102 225/226)

### Как работает

```
┌──────────┐    SMS-DELIVER     ┌──────────┐    ENVELOPE     ┌──────────┐
│OTA Server│ ───────→───────────│  Phone   │ ─────→───────── │   UICC   │
│          │  (Secured Packet)  │  (ME)    │  (SMS-PP)       │  (SIM)   │
└──────────┘                    └──────────┘                  └──────────┘
                                      ↑
                                 TAR (3 байта) →
                                 BF FF FF = всем STK
                                 XX YY ZZ = конкретный апплет
                                 00 00 00 = RAM (управление апплетами)
                                 00 00 01 = RFM (управление файлами)
```

### Структура Command Packet (TS 102 226)

```
┌──────────┬──────────┬────────────┬──────────────┬──────────┐
│ CPL      │ CHL(SPI) │ KIc/KID    │ Counter      │ Secured  │
│ (Length) │ (Security│ (Key IDs)  │ (anti-replay)│ Data     │
│          │  Params) │            │              │ (APDU)   │
└──────────┴──────────┴────────────┴──────────────┴──────────┘
```

### Характеристики

| Параметр | Значение |
|---|---|
| **Транспорт** | SMS (GSM) |
| **Стандарты** | GSM 03.48 → ETSI TS 102 225 (Secured Packet), TS 102 226 (Command Packet) |
| **Объём** | <140 байт полезной нагрузки на SMS |
| **Скорость** | Медленно (SMS-канал) |
| **Безопасность** | 3DES/AES, симметричные ключи (KIC/KID) |
| **Маршрутизация** | TAR (Toolkit Application Reference) |
| **Применение** | Обновление файлов, STK-команды, RAM/RFM |

### Ограничения
- Медленно (несколько секунд на SMS)
- Ограниченный объём (конкатенация SMS даёт ~1 KB)
- Надёжность зависит от SMS-центра
- Только SIM-карта (не телефон)

---

## 3. Эпоха II: BIP + CAT_TP (TS 102 127 / TS 102 223)

### Как работает

```
┌──────────┐   OPEN CHANNEL     ┌──────────┐   TCP/UDP       ┌──────────┐
│OTA Server│ ←─────→────────────│  Phone   │ ←─────→─────────│  Server  │
│   UICC   │   (Proactive cmd)  │  (ME)    │   (GPRS/3G/4G) │          │
└──────────┘                    └──────────┘                 └──────────┘
```

Процесс:
1. UICC отправляет OPEN CHANNEL (proactive) → терминал
2. Терминал открывает TCP/IP соединение через модем
3. UICC ↔ Сервер обмениваются данными через SEND/RECEIVE DATA
4. UICC отправляет CLOSE CHANNEL

### Два режима

| Режим | Кто инициирует | Пример |
|---|---|---|
| **UICC Server Mode** | UICC слушает порт | Smart Card Web Server (SCWS) |
| **Terminal Server Mode** | UICC подключается к серверу | Обновление апплета, IoT |

### Характеристики

| Параметр | Значение |
|---|---|
| **Транспорт** | GPRS/3G/LTE data (BIP) |
| **Стандарты** | ETSI TS 102 223 (OPEN CHANNEL), TS 102 127 (CAT_TP) |
| **Объём** | Неограничен (потоковая передача) |
| **Скорость** | Доступная скорость модема (100+ Mbps на 4G) |
| **Безопасность** | PSK-TLS + CAT_TP шифрование |
| **Применение** | RAM over IP, SCWS, IoT-апплеты |

### Преимущества над SMS-PP
- Намного быстрее (данные, а не SMS)
- Большие объёмы (полные апплеты, изображения для SCWS)
- Двунаправленный канал (не только push)

---

## 4. Эпоха III: eSIM RSP (GSMA SGP.02 / SGP.22)

### M2M (SGP.02) — через BIP + SMS fallback

```
SM-DP → SM-SR → eUICC (через BIP или SMS)
```

- Использует BIP как основной канал
- SMS как fallback для constrained устройств
- PSK аутентификация (симметричные ключи)

### Consumer (SGP.22) — чистый IP

```
SM-DP+ → HTTPS → LPA → eUICC
```

- Только IP (HTTPS/TLS 1.2+)
- PKI аутентификация (сертификаты X.509)
- LPA — локальный посредник в устройстве
- ES8+ (SM-DP+ ↔ eUICC) + ES9+ (SM-DP+ ↔ LPA)

### Характеристики

| Параметр | M2M (SGP.02) | Consumer (SGP.22) |
|---|---|---|
| **Транспорт** | BIP (TCP/SMS/CAT_TP) | HTTPS/IP |
| **Аутентификация** | PSK | PKI (X.509) |
| **Объём профиля** | KB-MB | KB-MB |
| **Безопасность** | SCP03/SCP80 + PSK | TLS + PKI |
| **Модель** | Push (сервер) | Pull (пользователь) |

---

## 5. Сравнение трёх эпох

| Свойство | SMS-PP | BIP/CAT_TP | eSIM RSP |
|---|---|---|---|
| **Год появления** | ~1998 | ~2005 | 2016 |
| **Транспорт** | SMS | TCP (через BIP) | HTTPS/IP |
| **Скорость** | <1 kbps | До 100+ Mbps | Широкополосный |
| **Макс. данные** | ~1 KB/SMS | Без ограничений | Без ограничений |
| **Надёжность** | Низкая (SMS) | Высокая (TCP) | Высокая (TLS) |
| **Безопасность** | 3DES/AES симметричная | PSK-TLS | PKI + сертификаты |
| **Маршрутизация** | TAR (3 байта) | TAR + канал | Профиль/AID |
| **Инициатор** | Сервер (push) | UICC (pull) | Пользователь/сервер |
| **Управление** | По-командно | Сессионно | Профилями |

---

## 6. Эволюция безопасности OTA

```
SMS-PP:                    BIP:                      eSIM RSP:
══════════                 ════════                  ════════════
3DES/DES                   TLS-PSK                   PKI (X.509)
KIC + KID                  CAT_TP security           GSMA CI
SPI (Security Params)      Channel keys              SAS сертификация
Counter anti-replay        Session keys              EAL4+ eUICC
                                                      Certificate chain
                           
  Ключи в SIM               Ключи в UICC              Ключи в eUICC + CI
  TAR = маршрутизация       TAR + Channel ID          AID + ISD-P
  Один домен                Один домен                Множественные домены
```

---

## 7. Что это значит для разработчика

| Аспект | SMS-PP OTA | BIP OTA | eSIM RSP |
|---|---|---|---|
| **STK-апплет получает** | ENVELOPE с SMS | RECEIVE DATA | Не применимо (уровень профиля) |
| **Формат команды** | Secured Packet (TS 102 225) | RAW APDU | Profile Package |
| **TAR** | Обязателен | Обязателен | Нет (профиль = AID) |
| **Установка апплета** | SMS-PP → RAM | BIP → RAM | Уровень профиля |
| **Обновление файла** | RFM SMS | BIP → UPDATE BINARY | Новый профиль |
| **Отладка** | Сложно (SMS-сниффер) | Wireshark | Логи LPA/SM-DP+ |

---

## 8. Будущее: IoT и за пределами

- **SGP.32**: eSIM IoT — лёгкий протокол без LPA, без SM-SR
- **iSIM** (Integrated SIM): чип внутри SoC (Qualcomm, Samsung)
- **nuSIM**: ещё более лёгкая альтернатива для IoT (меньше кода, меньше памяти)
- **5G**: сетевая slicing + eSIM = динамическое подключение к разным сетям

---

## Ссылки на источники

- OTA Remote APDU: [[wiki/summaries/ts_102_226|TS 102 226]]
- CAT/BIP: [[wiki/concepts/CAT_STK]]
- OTA концепт: [[wiki/concepts/OTA_Remote_Management]]
- eSIM: [[wiki/concepts/eSIM]]
- SGP.02: [[wiki/summaries/sgp02]]
- eSIM Whitepaper: [[wiki/summaries/esim_whitepaper]]
