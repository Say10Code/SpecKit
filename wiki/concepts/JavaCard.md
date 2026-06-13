---
tags: [JavaCard, platform, JCRE, JCVM, applet]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/java_card_stepping_stones|Java Card Stepping Stones]]"
  - "[[wiki/summaries/gpc_card_spec_2_3_1|GlobalPlatform Card Spec 2.3.1]]"
---

# Java Card — Платформа для смарт-карт

## Определение

**Java Card** — это стандартизированная платформа для разработки и выполнения приложений (апплетов) на смарт-картах с ограниченными ресурсами. Java Card — это урезанная версия Java для устройств с 32-128 KB EEPROM и ~4 KB RAM. ^[extracted]

На SIM/UICC-картах Java Card — основной способ создания пользовательских STK-приложений (SIM Toolkit).

## Архитектура Java Card

```
┌──────────────────────────────────────────────────────────┐
│                    Application Layer                      │
│  ┌──────────┬──────────┬──────────┬──────────────────┐   │
│  │ Applet 1 │ Applet 2 │ Applet N │ Toolkit Applet   │   │
│  │ (Wallet) │ (PKI)    │ (STK)    │ (processToolkit) │   │
│  └──────────┴──────────┴──────────┴──────────────────┘   │
├──────────────────────────────────────────────────────────┤
│              Java Card API (Framework)                    │
│  javacard.framework │ javacard.security │ javacardx.crypto│
│  sim.toolkit │ uicc.toolkit │ sim.access │ uicc.access   │
├──────────────────────────────────────────────────────────┤
│         Java Card Runtime Environment (JCRE)              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Java Card Virtual Machine (JCVM)                  │  │
│  │  • bytecode interpreter (JCVM subset)              │  │
│  │  • Firewall (applet isolation)                     │  │
│  │  • Transaction manager (atomicity)                 │  │
│  │  • Garbage Collector (optional, JC 3.0.5+)         │  │
│  └────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────┤
│         Card OS / Native Layer                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  • EEPROM/NVM driver                               │  │
│  │  • APDU transport (T=0/T=1)                        │  │
│  │  • Cryptographic coprocessor                       │  │
│  │  • GlobalPlatform Card Manager                     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Java Card 2.2.1 vs 3.0.5 vs 3.1.0

| Аспект | JC 2.2.1 (2006) | JC 3.0.5 (2017) | JC 3.1.0 (2022) |
|---|---|---|---|
| **Classic Edition** | Да | Да | Да |
| **Connected Edition** | Нет | Да (servlets, TCP/IP) | Да |
| **GC** | Нет | Опционально | Опционально |
| **Логические каналы** | 4 | 20 | 20 |
| **Toolkit API** | `sim.toolkit` (2G) | `uicc.toolkit` (3G/4G) | `uicc.toolkit` (5G) |
| **Макс. package size** | 64 KB | Без ограничений | Без ограничений |
| **Shareable Interface** | Да | Да | Да |
| **Applet deletion** | Да | Да | Да |
| **Аннотации** | Нет | `@AID` (в нек. SDK) | `@AID` |

> 💡 **На практике**: 99% SIM-карт на рынке используют **Java Card 2.2.1** или **3.0.5 Classic Edition**. Connected Edition не используется в SIM/UICC.

## JCRE (Java Card Runtime Environment)

JCRE — среда выполнения, управляющая жизненным циклом апплетов:

1. **Загрузка**: LOAD команда → CAP-файл → JCRE парсит и сохраняет
2. **Установка**: INSTALL [for install] → JCRE вызывает `Applet.install()` → `applet.register()`
3. **Выбор**: SELECT [by AID] → JCRE вызывает `applet.select()`
4. **Обработка**: APDU → JCRE вызывает `applet.process(APDU)`
5. **Деселекция**: SELECT другого апплета или reset → `applet.deselect()`
6. **Удаление**: DELETE → JCRE освобождает память

### Firewall (изоляция апплетов)

JCRE обеспечивает изоляцию через контексты безопасности:
- Каждый апплет принадлежит к контексту (группа package)
- Прямой доступ к объектам другого контекста запрещён
- **Shareable Interface** — единственный легальный способ меж-апплетной коммуникации
- **Entry Point Objects** (AID, APDU buffer, JCRE-owned) доступны из любого контекста

### Транзакции и атомарность

- `JCSystem.beginTransaction()` / `JCSystem.commitTransaction()` / `JCSystem.abortTransaction()`
- Гарантируют атомарность записи в NVM (EEPROM)
- Вложенные транзакции не поддерживаются
- Апплетные операции чтения через `Util.arrayCopyNonAtomic()` — быстрее (без транзакций)

## Java Card API — ключевые пакеты

| Пакет | AID | Содержание |
|---|---|---|
| `java.lang` | — | `Object`, `Throwable`, `Class` (урезанные) |
| `javacard.framework` | `A0 00 00 00 62 01 01` | `Applet`, `APDU`, `AID`, `JCSystem`, `Util`, `ISO7816`, PIN |
| `javacard.security` | `A0 00 00 00 62 03 01` | `KeyBuilder`, `MessageDigest`, `Signature`, ключи |
| `javacardx.crypto` | `A0 00 00 00 62 02 01` | `Cipher` (DES, AES, RSA) |
| `sim.toolkit` | `A0 00 00 00 76 01 01` | STK API для **2G/GSM** (ProactiveHandler, ToolkitRegistry) |
| `uicc.toolkit` | `A0 00 00 00 76 02 01` | STK API для **3G/4G/5G** (ProactiveHandler, ToolkitRegistry) |
| `sim.access` | — | Доступ к файловой системе SIM |
| `uicc.access` | — | Доступ к файловой системе UICC/USIM |

### Ограничения Java Card по сравнению со standard Java

- **Нет**: `float`, `double`, `String`, `Thread`, `ClassLoader`, многопоточность
- **Нет**: динамическая загрузка классов, reflection, сериализация
- **Нет**: `System.gc()`, `clone()` (на большинстве платформ)
- **Максимум**: 32 767 полей, 255 статических полей
- **Стек**: очень ограничен (обычно 2-4 KB) — глубокая вложенность вызовов опасна

## Инструменты разработки

| Инструмент | Назначение |
|---|---|
| **ant-javacard** | Сборка: `.java` → `.class` → `.cap` (build.xml) |
| **Oracle JCDK** | Java Card Development Kit (JC 2.2.2, 3.0.5) |
| **GlobalPlatformPro** (`gp.jar`) | Управление картой: LOAD, INSTALL, DELETE, LIST |
| **pySim** | Чтение/запись файлов UICC, программирование SIM |
| **shadysim** | Установка апплетов, APDU-команды |
| **TCA Loader** | Тестовый инструмент от Trusted Connectivity Alliance |
| **Gemalto Developer Suite** | Коммерческая IDE для разработки (legacy) |
| **SIMTester** | Тестирование STK-апплетов |

## Связи

- Разработка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- GlobalPlatform: [[wiki/concepts/GlobalPlatform_Card]]
- STK-апплеты: [[wiki/concepts/STK_Applet]]
- AID в JavaCard: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
- Учебник TCA: [[wiki/summaries/java_card_stepping_stones]]
- Безопасность UICC: [[wiki/concepts/UICC_Security]]
- CAT/STK: [[wiki/concepts/CAT_STK]]
- End-to-End Guide: [[wiki/syntheses/javacard_stk_end_to_end|JavaCard: от исходников до STK-меню]]
- UICC API: [[wiki/summaries/ts_102241|TS 102 241]]
- (U)SIM API: [[wiki/summaries/ts_131130|TS 131 130]]
- SIM API (legacy): [[wiki/summaries/ts_143019|TS 143 019]]
