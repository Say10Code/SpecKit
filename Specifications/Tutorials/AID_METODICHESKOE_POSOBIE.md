
# AID (Application Identifier) в SIM/UICC и JavaCard — Методическое пособие

## Полный разбор: от ISO до установки апплета на SIM-карту

**Версия 1.0 • 31 мая 2026**

---

<div style="page-break-after: always;"></div>

## Оглавление

1. [Введение](#1-введение)
2. [Стек спецификаций](#2-стек-спецификаций)
3. [Структура AID: RID + PIX](#3-структура-aid-rid--pix)
   - [3.1 ISO/IEC 7816-5: фундамент](#31-isoiec-7816-5-фундамент)
   - [3.2 RID: категории и процедура получения](#32-rid-категории-и-процедура-получения)
   - [3.3 PIX: Proprietary Application Identifier Extension](#33-pix-proprietary-application-identifier-extension)
   - [3.4 Примеры из индустрии](#34-примеры-из-индустрии)
4. [AID в Java Card](#4-aid-в-java-card)
   - [4.1 Класс `javacard.framework.AID`](#41-класс-javacardframeworkaid)
   - [4.2 `install()` и `register()`](#42-install-и-register)
   - [4.3 Различия JavaCard 2.2.1 и 3.0.5](#43-различия-javacard-221-и-305)
5. [AID в GlobalPlatform](#5-aid-в-globalplatform)
   - [5.1 Трёхуровневая иерархия AID](#51-трёхуровневая-иерархия-aid)
   - [5.2 Команда INSTALL [for install]](#52-команда-install-for-install)
   - [5.3 Команда SELECT (by AID)](#53-команда-select-by-aid)
   - [5.4 GPC Registry — GET STATUS](#54-gpc-registry--get-status)
6. [AID в SIM/UICC (ETSI/3GPP)](#6-aid-в-uicc-etsi3gpp)
   - [6.1 EF_DIR — каталог приложений на UICC](#61-ef_dir--каталог-приложений-на-uicc)
   - [6.2 Формат записи в EF_DIR](#62-формат-записи-в-ef_dir)
   - [6.3 Связь с SIM Toolkit (STK)](#63-связь-с-sim-toolkit-stk)
7. [Как AID задаётся в build-системах](#7-как-aid-задаётся-в-build-системах)
   - [7.1 build.xml (ant-javacard)](#71-buildxml-ant-javacard)
   - [7.2 Аннотация @AID](#72-аннотация-aid)
   - [7.3 GlobalPlatformPro](#73-globalplatformpro)
8. [Как сформирован AID проекта stk-test](#8-как-сформирован-aid-проекта-stk-test)
9. [Практические рекомендации](#9-практические-рекомендации)
10. [Список источников](#10-список-источников)

---

<div style="page-break-after: always;"></div>

## 1. Введение

**AID (Application Identifier)** — это центральное понятие экосистемы смарт-карт, связывающее стандарты ISO, GlobalPlatform, ETSI/3GPP и Java Card в единую систему идентификации приложений.

AID — это 5–16-байтовый идентификатор, который:
- **Глобально уникально** идентифицирует приложение на смарт-карте (SIM/UICC)
- Используется для **SELECT (выбора)** приложения терминалом/ME
- Определяет **принадлежность** приложения конкретному поставщику
- Задаётся на этапе **сборки** CAP-файла и **установки** на карту
- Участвует в **маршрутизации OTA-сообщений** (в связке с TAR)

Данное пособие последовательно разбирает AID на всех уровнях: от международного стандарта ISO 7816-5 до практической установки апплета на SIM-карту.

---

## 2. Стек спецификаций

AID определён и используется в следующей иерархии стандартов (сверху вниз):

```
┌────────────────────────────────────────────────────────────┐
│                   Стек спецификаций AID                     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ISO/IEC 7816-5 §8.2  ← Определение структуры RID + PIX   │
│        │                                                    │
│        ▼                                                    │
│  GlobalPlatform 2.3.1 §11.5   ← Load File → Module →       │
│                                   Instance AID иерархия     │
│        │                                                    │
│        ▼                                                    │
│  Java Card 2.2.1 §6.4        ← install() + register()     │
│  Java Card 3.0.5 §6.4        ← AID в JCRE и CAP            │
│        │                                                    │
│        ▼                                                    │
│  ETSI TS 102 226 §8.2.1.3    ← CA TLV (STK params с AID)  │
│  ETSI TS 102 221 §13.2       ← EF_DIR (каталог AID на UICC)│
│        │                                                    │
│        ▼                                                    │
│  3GPP TS 31.101 §8.3         ← UICC Application Selection  │
│  3GPP TS 31.102 §l.2         ← USIM AID selection procedure │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

| # | Спецификация | Роль | Текущая версия |
|---|-------------|------|----------------|
| 1 | **ISO/IEC 7816-5** | Структура AID (RID+PIX), регистрация | 2019 |
| 2 | **GlobalPlatform Card Spec v2.3.1** | AID в командах установки и registry | 2025 |
| 3 | **Java Card 2.2.1** | `javacard.framework.AID`, `register()` | 2006 |
| 4 | **Java Card 3.0.5** | То же + аннотации, новые API | 2015 |
| 5 | **ETSI TS 102 226** | CA TLV для SIM Toolkit параметров | v16.3.0 (2025) |
| 6 | **ETSI TS 102 221** | UICC-Terminal интерфейс, EF_DIR | v17.4.0 (2023) |
| 7 | **3GPP TS 31.101** | UICC-terminal interface for 3GPP | v19.1.0 |
| 8 | **3GPP TS 31.102** | USIM application characteristics | v14.7.0 |

---

## 3. Структура AID: RID + PIX

### 3.1 ISO/IEC 7816-5: фундамент

**ISO/IEC 7816-5** — «Registration of application providers» — определяет:

> AID состоит из двух частей: **RID** (Registered Application Provider Identifier) длиной **5 байт**, за которым следует **PIX** (Proprietary Application Identifier Extension) длиной **0–11 байт**.

```
┌────────────────────────────────────────────────────────────┐
│                  Application IDentifier (AID)               │
│                    5–16 байт (всегда)                        │
├───────────────┬────────────────────────────────────────────┤
│   RID (5)     │              PIX (0–11)                     │
│   RID (5)     │              PIX (0–11)                     │
│   RID (5)     │              PIX (0–11)                     │
├───────────────┴────────────────────────────────────────────┤
│  RID = Registered Application Provider Identifier           │
│        назначается ISO Registration Authority                │
│                                                             │
│  PIX = Proprietary Application Identifier Extension         │
│        назначается владельцем RID                            │
└────────────────────────────────────────────────────────────┘
```

### 3.2 RID: категории и процедура получения

RID классифицируется по **первому полубайту** (4 старших бита первого байта):

| Первый полубайт | Категория | Описание | Пример |
|:---:|-----------|----------|--------|
| `'0'–'9'` | ISO 7812 (IIN-based) | Организация имеет Issuer Identification Number | Visa, MasterCard |
| **`'A'`** | **International registration** | Глобальная регистрация через ISO/IEC 7816-5 RA | ETSI, 3GPP, Gemalto |
| `'D'` | National registration | Регистрация через национальный орган (напр. DIN в Германии) | G&D: `D2 76 00 01 18` |
| **`'F'`** | **Proprietary (unregistered)** | Не требует регистрации; уникальность не гарантируется | Тестовые проекты |

#### Процедура получения RID (категория A)

```
Податель заявки
      │
      ▼
Национальный спонсорский орган
(напр. ANSI в США, DIN в Германии)
      │
      ▼
ISO/IEC 7816-5 Registration Authority
(TDC Services A/S, Дания — http://www.ds.dk)
      │
      ▼
Выдача 5-байтового RID, начинающегося с 'A'
```

**Важно:** Регистрация RID — платная. Стоимость: ~€1500–3000 (зависит от страны). Срок ожидания: 1–4 недели.

#### Широко известные RID

| RID | Владелец | Область |
|-----|----------|---------|
| `A0 00 00 00 09` | **ETSI** | Телекоммуникации |
| `A0 00 00 00 87` | **3GPP** | Мобильная связь (USIM, ISIM) |
| `A0 00 00 00 03` | **Visa** | Платёжные системы |
| `A0 00 00 00 04` | **MasterCard** | Платёжные системы |
| `A0 00 00 00 62` | **Oracle / Sun** | Java Card API пакеты |
| `A0 00 00 00 18` | Gemplus | SIM/UICC |
| `A0 00 00 00 30` | Gemalto / Axalto | SIM/UICC |
| `A0 00 00 00 77` | Oberthur (Idemia) | SIM/UICC |
| `D2 76 00 01 18` | Giesecke & Devrient | SIM/UICC |
| `A0 00 00 04 12` | OMA (Open Mobile Alliance) | Smart Card Web Server и др. |

### 3.3 PIX: Proprietary Application Identifier Extension

PIX — 0–11-байтовое расширение, определяемое **владельцем RID** по своему усмотрению.

#### Ограничения PIX:

- **Максимальная длина:** 11 байт (результирующий AID ≤ 16 байт)
- **Последний байт ≠ `FF`:** ISO/IEC 7816-5 резервирует `FF` в качестве последнего байта для будущих целей
- **Формат:** не стандартизован — каждый RID-holder определяет свою схему (см. EF_DIR ниже)

#### Типичные схемы структурирования PIX:

**1. Простая нумерация (проекты):**
```
A0 00 00 00 62  01 01     ← javacard.framework v1.0
                 ^^ ^^
                 Major.Minor версия
```

**2. ETSI/3GPP — многоуровневая схема (см. TS 101 220 §7.2):**
```
A0 00 00 00 09  XX XX  XX…           ← ETSI
A0 00 00 00 87  10 02  04 FF FF FF  … ← USIM (3GPP)
                 ^^ ^^  ^^ ^^ ^^ ^^
                  │  │   │
                  │  │   └─ Country Code (ITU-T E.164, RJP, 'F'-padded)
                  │  └───── Application Code (напр. 10 = 3G, 10.02 = USIM)
                  └──────── PIX sub-field 1: Application Family
```

### 3.4 Примеры из индустрии

#### Телеком (ETSI/3GPP):

| Приложение | Полный AID |
|-----------|-----------|
| GSM SIM | `A0 00 00 00 09 00 01` |
| GSM SIM Toolkit (STK) | `A0 00 00 00 09 00 02` |
| 3G USIM | `A0 00 00 00 87 10 02` |
| ISIM (IMS) | `A0 00 00 00 87 10 04` |
| CSIM (CDMA) | `A0 00 00 00 87 10 06` |
| AKA (Authentication) | `A0 00 00 00 87 10 08` |

#### Платежи:

| Приложение | Полный AID |
|-----------|-----------|
| Visa Credit/Debit | `A0 00 00 00 03 10 10` |
| Visa Electron | `A0 00 00 00 03 20 10` |
| MasterCard Credit/Debit | `A0 00 00 00 04 10 10` |
| Maestro (UK) | `A0 00 00 00 05 00 01` |

#### Java Card API пакеты:

| Пакет | AID |
|-------|-----|
| `javacard.framework` | `A0 00 00 00 62 01 01` |
| `javacardx.crypto` | `A0 00 00 00 62 02 01` |
| `sim.toolkit` (2G) | `A0 00 00 00 76 01 01` |
| `uicc.toolkit` (3G) | `A0 00 00 00 76 02 01` |

---

## 4. AID в Java Card

### 4.1 Класс `javacard.framework.AID`

В Java Card 2.2.1 и 3.0.5 класс `javacard.framework.AID` инкапсулирует идентификатор приложения в соответствии с ISO 7816-5:

```java
public class AID {
    // Длина AID: 5–16 байт
    // Первые 5 байт = RID
    // Остальные 0–11 байт = PIX

    public boolean equals(byte[] bArray, short offset, byte length);
    public boolean partialEquals(byte[] bArray, short offset, byte length);
    public boolean RIDEquals(AID otherAID);  // сравнение только RID
    public byte getBytes(byte[] dest, short offset);
    public byte getPartialBytes(short aidOffset, byte[] dest, short o, byte len);
}
```

#### Правила экземпляров `AID`:

| Правило | Пояснение |
|---------|----------|
| **JCRE создаёт AID** | Апплеты не должны создавать экземпляры AID через конструктор |
| **Permanent Entry Point** | AID-объекты, принадлежащие JCRE, доступны из любого контекста |
| **`JCSystem.getAID()`** | Возвращает AID текущего апплета |
| **`JCSystem.lookupAID()`** | Ищет AID другого установленного апплета по байтам |

### 4.2 `install()` и `register()`

Процесс создания экземпляра апплета и назначения AID:

```java
public class MyApplet extends Applet implements ToolkitInterface {
    
    // static метод install называется JCRE во время INSTALL [for install]
    public static void install(byte[] bArray, short bOffset, byte bLength) {
        
        // bArray содержит Installation Parameters (из тега C9):
        // ┌────┬───────────────────┬────┬──────────────┬────┬──────────┐
        // │ Li │ Instance AID      │ Lc │ Control Info │ La │ App Data │
        // └────┴───────────────────┴────┴──────────────┴────┴──────────┘
        // Li  = длина Instance AID (5–16)
        // Lc  = длина Control Info (может быть 0)
        // La  = длина Application Data (может быть 0)
        
        MyApplet applet = new MyApplet();  // конструктор вызывает ToolkitRegistry
        
        // Вариант 1: регистрация с AID из CAP-файла
        applet.register();
        
        // Вариант 2: регистрация с пользовательским AID из bArray
        applet.register(bArray, (short)(bOffset + 1), bArray[bOffset]);
    }
}
```

#### Два способа задать Instance AID:

```
Способ 1 (build.xml):         Способ 2 (install bArray):
┌─────────────────────┐        ┌──────────────────────┐
│ build.xml:           │        │ INSTALL [for install] │
│   <applet class=...  │        │   C9 <len>           │
│     aid="D0:70:02:   │        │     [Li][AID bytes]  │
│          CA:44:90:   │ ───────▶ [Lc][Control]       │
│          03:01"/>    │        │     [La][App Data]   │
└─────────────────────┘        └──────────────────────┘
         │                              │
         ▼                              ▼
   AID запекается               AID передаётся
   в CAP-файл                   в install(bArray, ...)
         │                              │
         └──────────┬──────────────────┘
                    ▼
            applet.register()
                    │
                    ▼
         JCRE Registry:
         Instance AID = D0:70:02:CA:44:90:03:01
```

#### Исключения:

| Исключение | Причина |
|-----------|---------|
| `SystemException.ILLEGAL_AID` | AID уже используется другим апплетом, или `register()` вызван дважды, или вызван НЕ из `install()` |
| `SystemException.ILLEGAL_VALUE` | Длина AID < 5 или > 16 байт |

### 4.3 Различия JavaCard 2.2.1 и 3.0.5

| Аспект | JavaCard 2.2.1 | JavaCard 3.0.5 |
|--------|---------------|----------------|
| **AID API** | `javacard.framework.AID` — идентичен | `javacard.framework.AID` — идентичен |
| **Регистрация** | Только `register()` | `register()` + `Applet.register(bArray, off, len)` |
| **Аннотации** | Не поддерживаются | `@AID(...)` — доступна в некоторых SDK |
| **Install Parameters** | Через `bArray` (до 127 байт) | Через `bArray` (до 127 байт) |
| **Поток INSTALL** | Один апплет на `install()` | Один апплет на `install()` (ограничение то же) |
| **SIM API** | `sim.toolkit.*` | `uicc.toolkit.*` (новый API) |

**Вывод:** С точки зрения AID, JavaCard 2.2.1 и 3.0.5 **совместимы**. Различия — в toolkit API (`sim.toolkit` vs `uicc.toolkit`) и дополнительных возможностях JC3.

---

## 5. AID в GlobalPlatform

### 5.1 Трёхуровневая иерархия AID

**GlobalPlatform Card Specification** (§11.5.2.3.2) определяет трёхуровневую иерархию AID:

```
┌─────────────────────────────────────────────────────────────┐
│               GlobalPlatform AID Hierarchy                   │
│                                                              │
│  Executable Load File AID (5–16 bytes)                       │
│    │   Идентифицирует пакет/ELF при загрузке                  │
│    │                                                         │
│    ├── Executable Module AID (5–16 bytes)                    │
│    │     Идентифицирует модуль (класс апплета) внутри пакета   │
│    │                                                         │
│    └──── Application Instance AID (5–16 bytes)               │
│            Идентифицирует экземпляр апплета                   │
│            Используется в SELECT для выбора приложения        │
└─────────────────────────────────────────────────────────────┘
```

| Уровень | GP-термин | Назначение | Пример (stk-test) |
|---------|-----------|-----------|-------------------|
| 1 | **Executable Load File AID** | ID пакета при загрузке CAP на карту | `D0:70:02:CA:44` (первые 5 байт) |
| 2 | **Executable Module AID** | ID конкретного модуля в пакете | `D0:70:02:CA:44` (обычно = Load File AID) |
| 3 | **Application (Instance) AID** | ID экземпляра, через который SELECT'ят апплет | `D0:70:02:CA:44:90:03:01` |

### 5.2 Команда INSTALL [for install]

В команде INSTALL [for install] (§11.5.2.3.2) AID передаются в формате Length-Value:

```
┌─────────┬─────────────────┬─────────┬────────────────┬─────────┬─────────────────┐
│ L_ELF   │ Load File AID   │ L_EM    │ Module AID     │ L_App   │ Application AID │
│ 1 байт  │ 0/5-16 байт     │ 1 байт  │ 0/5-16 байт    │ 1 байт  │ 5-16 байт       │
└─────────┴─────────────────┴─────────┴────────────────┴─────────┴─────────────────┘
         Загруженный ранее          Модуль в этом                  Экземпляр —
         CAP-файл (0 =              Load File                      будет SELECT'иться
         не требуется)
```

**Затем следуют:**
```
Длина Privileges (1) + Privileges (1-3)
Длина Install Parameters (1-3) + Install Parameters (TLV с C9, C7, C8, EF, CA/EA)
Длина Install Token (0-3) + Install Token
```

#### GPC Install Parameters TLV (полная структура):

```
C9 <len>                         ← Application Specific Parameters (идёт в bArray)
  EF <len>                       ← System Specific Parameters
    C8 02 <NVM>                  ← Non-Volatile Memory Quota (2 байта, big-endian)
    C7 02 <VM>                   ← Volatile Memory Quota (2 байта, big-endian)
  CA <len> <CA_data>             ← SIM Toolkit Parameters (только sim.toolkit)
      ├─ 01 <AccessDomainLen>    ← 1 + AccessDomain
      ├─ 00 <AccessDomain>
      ├─ 01 <Priority>
      ├─ 00 <MaxTimers>
      ├─ XX <MaxMenuTextLen>
      ├─ YY <MaxMenuEntries>
      ├─ ... MenuEntries × Y
      ├─ 01 <MaxChannels>
      ├─ 00 <MSL_Len> [MSL_Data]  ← опционально
      └─ ZZ <TAR_Len> [TAR_Data]  ← 0 или 3×n
```

### 5.3 Команда SELECT (by AID)

Команда `SELECT [by AID]` — это способ, которым терминал (телефон, OTA-платформа) выбирает приложение на карте:

```
CLA  INS  P1  P2   Lc    Data           Le
00   A4   04  00   <Lc>  <Instance AID>  <Le>
```

| Поле | Значение | Примечание |
|------|----------|-----------|
| CLA | `00` | ISO inter-industry |
| INS | `A4` | SELECT |
| P1 | `04` | Select by AID |
| P2 | `00` | First or only occurrence |
| Lc | `05–10`h | Длина AID (5–16) |
| Data | `<AID bytes>` | Instance AID апплета |
| Le | `00` или absent | Ожидаемый ответ |

**SELECT — первая команда, которую отправляет терминал.** Возвращаемые данные содержат FCI (File Control Information) — описание приложения (пин-коды, файловая система, и т.д.).

### 5.4 GPC Registry — GET STATUS

GET STATUS (команда 0x80 0xF2) возвращает реестр всех установленных объектов на карте. Каждый объект идентифицируется своим AID:

| Registry Tag | Объект |
|-------------|--------|
| `4F` | AID (приложение, ELF, SSD, ISD) |
| `84` | Executable Module AID(s) (только ELF) |
| `C4` | Load File AID, к которому привязано приложение |
| `CC` | AID ассоциированного Security Domain |

---

## 6. AID в UICC (ETSI/3GPP)

### 6.1 EF_DIR — каталог приложений на UICC

**ETSI TS 102 221** §13.2 определяет **EF_DIR** (Application Directory) — элементарный файл под MF, содержащий **список AID всех приложений** на UICC.

```
MF (Master File — 0x3F00)
├── EF_DIR (0x2F00)   ← Список приложений: AID₁, AID₂, ..., AIDₙ
├── DF_GSM (0x7F20)   ← GSM Application
├── ADF_USIM           ← USIM Application
│   ├── EF_IMSI
│   ├── EF_ACC
│   └── ...
└── ADF_CUSTOM         ← Пользовательское STK-приложение
    └── ...
```

**EF_DIR** — линейно-фиксированный файл. Каждая запись содержит:
```
┌───────┬─────────────────────┬───────────────────────────────┐
│ Tag   │ Length (1 byte)     │ AID (5–16 bytes)              │
│ '61'  │ 0x05–0x10           │ <RID + PIX>                   │
└───────┴─────────────────────┴───────────────────────────────┘
        + опционально:
┌────────┬──────────────────────┐
│ '50'   │ Application Label    │  ← Человеко-читаемое имя
└────────┴──────────────────────┘
```

### 6.2 Формат записи в EF_DIR

```
61 1C                   ← Application Template (len=28)
  4F 0A                 ← AID tag (len=10)
    A0 00 00 00 87 10 02 FF FF FF FF   ← USIM AID
  50 0A                 ← Label tag (len=10)
    55 53 49 4D 20 41 70 70 6C 65       ← "USIM Apple" в ASCII
  73 06                 ← Non-tag discretionary data
    ...
```

**Важно:** EF_DIR — это то, что видит телефон при старте. На основе EF_DIR строится **SIM Menu** и список доступных приложений.

### 6.3 Связь с SIM Toolkit (STK)

Когда апплет реализует `ToolkitInterface`, JCRE автоматически:
1. Добавляет AID апплета в **EF_DIR**
2. Связывает TAR (`BF FF FF` или пользовательский) с этим AID
3. Регистрирует меню (set-up menu) для этого апплета — телефон видит пункты меню

**Связка AID ↔ TAR** — критична для OTA-маршрутизации:

```
OTA Push (SMS-PP)
      │
      ▼
Security Domain проверяет TAR в SMS
      │
      ├── TAR = BF FF FF → широковещательно всем STK-апплетам
      ├── TAR = XX YY ZZ → конкретному апплету c данным TAR
      │
      ▼
Sim Toolkit Framework доставляет ENVELOPE апплету
      │
      ▼
processToolkit(event) — апплет обрабатывает событие
```

---

## 7. Как AID задаётся в build-системах

### 7.1 build.xml (ant-javacard)

В `build.xml` AID задаётся атрибутом `aid` элемента `<applet>`:

```xml
<javacard>
  <cap targetsdk="oracle_javacard_sdks/jc221_kit"
       jckit="oracle_javacard_sdks/jc305u3_kit"
       output="bin/stk-test.cap"
       sources="src"
       classes="bin"
       version="1.0">
    <applet class="com.say10.stktest.StkTestApplet"
            aid="d0:70:02:ca:44:90:03:01"/>   ← Здесь задаётся AID
    <import exps="exp" jar="lib/sim.jar"/>
  </cap>
</javacard>
```

**Что происходит при сборке:**
1. Ant компилирует `StkTestApplet.java` → bytecode
2. **Конвертер JavaCard** вшивает AID в CAP-файл в двух местах:
   - **Package AID** = первые 5 байт AID (Load File AID)
   - **Applet AID** = полный AID (Instance AID)
3. CAP содержит оба AID в компоненте `Applet.cap`

### 7.2 Аннотация `@AID`

В Java Card 3.0.5 (и некоторых версиях 2.2.1 SDK с поддержкой аннотаций через ant-javacard) можно использовать аннотацию:

```java
@AID("D0:70:02:CA:44:90:03:01")
public class StkTestApplet extends Applet implements ToolkitInterface {
    // AID задаётся декларативно, без build.xml
    // build.xml для ant-javacard всегда имеет приоритет
}
```

### 7.3 GlobalPlatformPro (`gp.jar`)

При установке через `gp.jar` AID передаётся опционально:

```bash
# Взять AID из CAP-файла (исходный)
gp -install stk-test.cap

# Явно указать Instance AID
gp -install stk-test.cap --create <AID>
```

---

## 8. Как сформирован AID проекта stk-test

AID проекта **stk-test** сформирован по следующей схеме:

```
D0 : 70 : 02 : CA : 44  :  90 : 03 : 01
└────────RID──────────┘  └─────PIX─────┘
      5 байт                  3 байта
```

| Байт | Значение | Расшифровка |
|------|----------|-------------|
| `D0 70 02 CA 44` | RID (5 байт) | Зарезервирован для проектов **mrlnc**. RID категории `'D'` (= национальная регистрация, страна `070`). **Неофициальный RID — только для закрытого тестирования!** |
| `90 03 01` | PIX (3 байта) | `90` = префикс STK-проекта; `03` = номер проекта в серии; `01` = версия/вариант |

**Важное предупреждение:**

> ⚠️ `D0 70 02 CA 44` — **условно-свободный RID**, выбранный для тестовых целей. Он **НЕ зарегистрирован** в ISO/IEC 7816-5 Registration Authority. Для production-использования необходимо получить легитимный RID через процедуру регистрации (см. раздел 3.2). Незарегистрированный RID может конфликтовать с другими приложениями при установке на коммерческие SIM-карты.

---

## 9. Практические рекомендации

### 9.1 Выбор RID для тестирования

| Тип проекта | Рекомендуемый RID | Пояснение |
|------------|-------------------|-----------|
| **Закрытое тестирование** | `F0 00 …` (proprietary) | Не гарантирует уникальность, но формально допустимо ISO |
| **Закрытое тестирование** | `D0 XX …` (national, test) | Условно — страна 0XX не занята |
| **Открытое тестирование** | `A0 …` (зарегистрированный) | Полная уникальность — требует платной регистрации |
| **Commercial product** | `A0 …` (зарегистрированный) | **Требуется регистрация.** Без неё — юридический риск |

### 9.2 Формирование PIX

```
Схема:  <type> <app_id> <version>

type    = 1 байт: 90 = STK applet, 80 = JavaCard library, 70 = service
app_id  = 1–2 байта: порядковый номер проекта
version = 1 байт:  01 = v1.0, 02 = v2.0, ...

Примеры:
  D0:70:02:CA:44:90:03:01   ← STK aplet #3, v1.0
  D0:70:02:CA:44:90:03:02   ← STK aplet #3, v2.0 (обновление)
  D0:70:02:CA:44:80:01:01   ← JC library #1, v1.0
```

### 9.3 Проверка уникальности AID

Перед установкой проверьте:

```bash
# pySim-shell
pySIM-shell> select ADF.ISD
pySIM-shell> get_status

# GlobalPlatformPro
gp -list

# shadysim_isim.py
python2 shadysim_isim.py --pcsc --kic <KIC> --kid <KID> --list-applets
```

### 9.4 Совместимость AID при обновлении

- **Обновление апплета на SIM-карте невозможно.** Нужно: удалить → установить заново
- **Load File AID (первые 5 байт) должен оставаться неизменным** для одной и той же «линейки» продукта
- **Instance AID можно менять** между версиями (но тогда SELECT-команда изменится)
- **Пакет с тем же Load File AID не может быть загружен дважды** — сначала нужно удалить старый

---

## 10. Список источников

### Первичные спецификации

| # | Спецификация | Версия | Название | Файл в `.doc/` |
|---|-------------|--------|----------|----------------|
| 1 | **ISO/IEC 7816-5** | 2019 | Identification cards — Registration of application providers | — (доступен платно на iso.org) |
| 2 | **GlobalPlatform Card Spec** | v2.3.1 (2025) | GPC Card Specification | `GPC_CardSpecification_v2.3.1.pdf` |
| 3 | **Java Card 2.2.1** | 2006 | Runtime Environment Specification §6.4 | — (Oracle JCDK 2.2.1 docs) |
| 4 | **Java Card 3.0.5** | 2015 | Runtime Environment Specification §6.4 | `JavaCard_3.0.5_AID_API.html` |
| 5 | **ETSI TS 102 226** | v16.3.0 (2025-01) | Remote APDU structure for UICC based applications (§8.2) | `ETSI_TS_102_226_v16.03.00.pdf` |
| 6 | **ETSI TS 102 221** | v17.4.0 (2023-02) | UICC-Terminal interface; Physical and logical characteristics (§13) | `ETSI_TS_102_221_v17.04.00.pdf` |
| 7 | **ETSI TS 101 220** | v15.1.0 | Conformance specification for UICC — AID numbering | `ETSI_TS_101_220_v15.01.00.pdf` |
| 8 | **3GPP TS 31.101** | v19.1.0 | UICC-terminal interface for 3GPP | — |
| 9 | **3GPP TS 31.102** | v14.7.0 | USIM application characteristics (§l.2) | — |

### Дополнительные источники

| # | Источник | Описание | Файл в `.doc/` |
|---|----------|----------|----------------|
| 10 | **TCA Stepping Stones R7** | Методическое пособие по Java Card и STK | `Java_Card_Stepping_Stones.txt` |
| 11 | **ANSI RID Program** | Описание процедуры регистрации RID через ANSI | — (ans.org/rid) |
| 12 | **Oracle Java Card API** | Документация `javacard.framework.AID` | `JavaCard_3.0.5_AID_API.html` |
| 13 | **javacardos.com** | Wiki-справочник по Java Card API (AID) | — |
| 14 | **TDC Services (ISO RA)** | Registration Authority ISO/IEC 7816-5 | — (ds.dk) |

### Ключевые цитаты

> **ISO/IEC 7816-5 §8.2:** «An AID consists of two parts: an RID of 5 bytes, followed by a PIX of up to 11 bytes. The total AID length is between 5 and 16 bytes.»
>
> **GlobalPlatform 2.3.1 §11.5.2.3.2:** «The Application AID is the AID by which the installed Application instance will be selected on the card. Length: 5–16 bytes.»
>
> **Java Card 2.2.1 §6.4:** «The instance AID is used by an off-card client to select the applet for APDU communication. The applet must call register() exactly once during install().»
>
> **ETSI TS 102 226 §8.2.1.3.2.1:** «The CA tag carries SIM file access and toolkit application specific parameters. If both CA and EA tags are present in the INSTALL [for install] command, the card shall return SW '6A80'.»

---

## Приложение А: Схема потоков AID при установке

```
                         ┌─────────────┐
                         │  build.xml  │
                         │ aid="..."   │
                         └──────┬──────┘
                                │ ant-javacard
                                ▼
                         ┌──────────────┐
                         │  CAP-файл    │
                         │  содержит:   │
                         │  • Package AID│
                         │  • Applet AID │
                         └──────┬──────┘
                                │ LOAD
                                ▼
┌───────────────────────────────────────────────────┐
│               SIM-карта (UICC)                     │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │          ISD (Security Domain)            │     │
│  │  AID: A0 00 00 01 51 00 00               │     │
│  │  ┌─────────────────────────────────────┐  │     │
│  │  │        INSTALL [for install]         │  │     │
│  │  │                                      │  │     │
│  │  │  Load File AID: D0 70 02 CA 44      │  │     │
│  │  │  Module AID:    D0 70 02 CA 44      │  │     │
│  │  │  Instance AID:  D0 70 02 CA 44 90   │  │     │
│  │  │                  03 01               │  │     │
│  │  │                                      │  │     │
│  │  │  C9: [Li][AID][Lc][Ctrl][La][Data]  │  │     │
│  │  │  EF: C8(NVM) + C7(VM)               │  │     │
│  │  │  CA: STK Parameters (menu, TAR…)     │  │     │
│  │  └─────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────┘     │
│                       │                            │
│                       ▼                            │
│  ┌──────────────────────────────────────────┐     │
│  │           JCRE (Runtime)                   │     │
│  │                                            │     │
│  │  1. Регистрирует Load File                │     │
│  │  2. Регистрирует Module                   │     │
│  │  3. Вызывает MyApplet.install(bArray)     │     │
│  │  4. Внутри install(): register()          │     │
│  │  5. AID → JCRE Registry                   │     │
│  └──────────────────────────────────────────┘     │
│                       │                            │
│                       ▼                            │
│  ┌──────────────────────────────────────────┐     │
│  │           EF_DIR (0x2F00)                  │     │
│  │                                            │     │
│  │  61 0D                                     │     │
│  │    4F 0B  D0 70 02 CA 44 90 03 01 00 00  │     │
│  │    50 02  "STK Test"                       │     │
│  │                                            │     │
│  │  Телефон читает EF_DIR → SIM Menu         │     │
│  └──────────────────────────────────────────┘     │
└───────────────────────────────────────────────────┘
```

---

## Приложение Б: Ключевые байты в hex

### RID по первому байту

```
A0 XX XX XX XX → ISO International Registration (нужен платёж)
D0 XX XX XX XX → ISO National Registration (нужен спонсор)
D2 76 XX XX XX → Germany (DIN) National
D8 40 XX XX XX → Russia (GOST) National
F0 XX XX XX XX → Proprietary (не регистрируется)
```

### AID пакетов Java Card API

```
A0 00 00 00 62 01 01 → javacard.framework 1.0  (2.2.1)
A0 00 00 00 62 01 01 → javacard.framework 1.0  (3.0.5 — совпадает!)
A0 00 00 00 62 02 01 → javacardx.crypto 1.0
A0 00 00 00 76 01 01 → sim.toolkit (2G STK)
A0 00 00 00 76 02 01 → uicc.toolkit (3G STK)
A0 00 00 00 09 00 01 → GSM SIM
A0 00 00 00 09 00 02 → GSM SIM Toolkit (STK)
```

---

<div align="center">

**© 2026 say10 • Подготовлено на основе спецификаций ISO, ETSI, 3GPP, GlobalPlatform и Oracle Java Card**

</div>
