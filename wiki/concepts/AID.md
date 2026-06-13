---
tags: [AID, ISO7816, RID, PIX, EF_DIR, application]
type: concept
level: foundation
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md]]"
  - "[[wiki/summaries/ts_101_220|TS 101 220]]"
  - "[[wiki/concepts/UICC_File_System]]"
---

# AID — Application Identifier

## Определение

> [!abstract] Определение
> **AID (Application Identifier)** — это 5–16 байтовый идентификатор, глобально уникально определяющий приложение на смарт-карте. Состоит из **RID** (5 байт, идентификатор провайдера) и **PIX** (0–11 байт, расширение провайдера). Стандартизирован в ISO/IEC 7816-5. ^[extracted]

## Структура AID

```
┌──────────────────────────────────────────────────────────┐
│               Application IDentifier (AID)               │
│                    5–16 байт                             │
├────────────────────┬─────────────────────────────────────┤
│   RID (5 байт)     │         PIX (0–11 байт)            │
│   RID (5 байт)     │         PIX (0–11 байт)            │
├────────────────────┴─────────────────────────────────────┤
│  RID = Registered Application Provider Identifier        │
│        выдаётся ISO/IEC 7816-5 Registration Authority    │
│                                                          │
│  PIX = Proprietary Application Identifier Extension      │
│        определяется владельцем RID                       │
└──────────────────────────────────────────────────────────┘
```

## RID (Registered Application Provider Identifier)

Классифицируются по первому полубайту:

| Первый полубайт | Категория | Описание | Пример |
|---|---|---|---|
| `'0'–'9'` | ISO 7812 (IIN-based) | Организация имеет Issuer Identification Number | Visa, MasterCard |
| **`'A'`** | **International registration** | Глобальная регистрация через ISO RA | ETSI, 3GPP |
| `'D'` | National registration | Через национальный орган | G&D: `D2 76 00 01 18` |
| **`'F'`** | **Proprietary (unregistered)** | Не требует регистрации; для тестов | `F0 70 02 CA 44` |

### Зарегистрированные RID в телекоме

| RID | Владелец | Область |
|---|---|---|
| `A0 00 00 00 09` | **ETSI** | Телекоммуникации, GSM, UICC API |
| `A0 00 00 00 87` | **3GPP** | USIM, ISIM, (U)SIM API |
| `A0 00 00 00 03` | Visa | Платёжные системы |
| `A0 00 00 00 04` | MasterCard | Платёжные системы |
| `A0 00 00 00 62` | Oracle / Sun | Java Card API пакеты |
| `A0 00 00 00 76` | 3GPP/ETSI | SIM Toolkit API пакеты |
| `A0 00 00 03 43` | 3GPP2 | CDMA (CSIM) |
| `A0 00 00 06 45` | oneM2M | M2M/IoT |
| `A0 00 00 04 12` | OMA | Smart Card Web Server |
| `A0 00 00 04 24` | WiMAX Forum | WiMAX (информационно) |

## PIX (Proprietary Application Identifier Extension)

Структура PIX для ETSI/3GPP приложений (из TS 101 220):

```
Digits 1–4:   Application code  (напр. '1002' = USIM)
Digits 5–8:   Country code      (ITU-T E.164, right-justified, 'F'-padded)
Digits 9–14:  Provider code     (Industry '89' + Card Issuer, E.118)
Digits 15–22: Provider field    (версия, TAR, произвольные данные)
```

### AID телеком-приложений

| Приложение | Полный AID (базовый) |
|---|---|
| GSM SIM | `A0 00 00 00 09 00 01` |
| GSM SIM Toolkit | `A0 00 00 00 09 00 02` |
| 3G USIM | `A0 00 00 00 87 10 02 FF FF FF ...` |
| ISIM (IMS) | `A0 00 00 00 87 10 04 FF FF FF ...` |
| CSIM (CDMA) | `A0 00 00 03 43 10 02 FF FF FF ...` (3GPP2 RID!) |

### AID Java Card API пакетов

| Пакет | AID |
|---|---|
| `javacard.framework` | `A0 00 00 00 62 01 01` |
| `javacardx.crypto` | `A0 00 00 00 62 02 01` |
| `sim.toolkit` (2G) | `A0 00 00 00 76 01 01` |
| `uicc.toolkit` (3G+) | `A0 00 00 00 76 02 01` |

## AID в Java Card

```java
public class MyApplet extends Applet {
    public static void install(byte[] bArray, short bOffset, byte bLength) {
        MyApplet applet = new MyApplet();
        // Вариант 1: AID из CAP-файла (build.xml)
        applet.register();
        // Вариант 2: AID из Install Parameters
        // applet.register(bArray, (short)(bOffset + 1), bArray[bOffset]);
    }
}
```

> [!tip] Практический совет
> Для тестовых проектов используйте RID категории `'F'` (например, `F0 70 02 CA 44`). Для production **обязательна** регистрация RID через ISO/IEC 7816-5 RA. Стоимость: ~€1500–3000, срок: 1–4 недели.

## AID в UICC: EF_DIR

На UICC список всех AID хранится в **EF_DIR** (0x2F00). Телефон читает EF_DIR при старте и строит список доступных приложений. Подробнее: [[wiki/concepts/EF_DIR]].

## Связи

- Файловая система UICC: [[wiki/concepts/UICC_File_System]]
- EF_DIR: [[wiki/concepts/EF_DIR]]
- Нумерация ETSI: [[wiki/summaries/ts_101_220|TS 101 220]]
- Методическое пособие: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
- JavaCard: [[wiki/concepts/JavaCard]]
