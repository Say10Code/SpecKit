---
tags: [synthesis, JavaCard, STK, tutorial, end-to-end]
created: 2026-06-10
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/concepts/JavaCard]]"
  - "[[wiki/concepts/JavaCard_Applet_Development]]"
  - "[[wiki/concepts/GlobalPlatform_Card]]"
  - "[[wiki/concepts/STK_Applet]]"
  - "[[wiki/concepts/OTA_Remote_Management]]"
  - "[[wiki/concepts/CAT_STK]]"
  - "[[wiki/summaries/java_card_stepping_stones]]"
  - "[[wiki/summaries/gpc_card_spec_2_3_1]]"
  - "[[wiki/summaries/ruimtools_javacard_guidelines]]"
  - "[[wiki/summaries/ruimtools_javacard_samples]]"
  - "[[wiki/summaries/hello_stk]]"
---

# Java Card Applet: От исходников до рабочего STK-меню за 30 минут

> **Synthesis** — объединение знаний из 11 источников (TCA, ETSI, GlobalPlatform, RuimTools, Osmocom). Практическое руководство.

---

## 1. Что мы делаем

**Цель**: написать Java Card апплет, который добавляет пункт в SIM-меню телефона. При выборе пункта — показывает сообщение «Hello STK!».

**Стек**: Java Card 2.2.1/3.0.5 + `sim.toolkit`/`uicc.toolkit` API + GlobalPlatform.

```
┌──────────────────────────────────────────────────────────┐
│  Ваш телефон                                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SIM Menu                                        │   │
│  │  ├── Услуги оператора                            │   │
│  │  ├── Мой апплет     ←── НАШЕ ПРИЛОЖЕНИЕ          │   │
│  │  └── Настройки                                   │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Инструменты (что нужно установить)

| Инструмент | Версия | Для чего |
|---|---|---|
| **JDK** | 1.8 или выше | Компиляция Java → bytecode (javac с target 1.1) |
| **ant-javacard** | последняя | Сборка: `.java` → `.cap` |
| **Oracle JCDK** | 2.2.2 или 3.0.5u3 | Java Card Development Kit |
| **GlobalPlatformPro** | v20.08.12+ | Установка/удаление апплетов с карты |
| **sim.jar / uicc.jar** | из JCDK | STK API библиотеки |

### Структура проекта

```
my-stk-applet/
├── src/
│   └── com/example/stk/
│       └── HelloStkApplet.java
├── lib/
│   ├── api.jar          ← Java Card API
│   └── sim.jar          ← sim.toolkit (2G) или uicc.jar (3G)
├── exp/                 ← export-файлы из JCDK
├── build.xml            ← ant-javacard конфигурация
└── bin/
    └── hello-stk.cap    ← результат сборки
```

---

## 3. Код апплета (полный)

```java
package com.example.stk;

import javacard.framework.*;
import sim.toolkit.*;        // 2G: sim.toolkit
// import uicc.toolkit.*;   // 3G: uicc.toolkit (выбрать один!)

public class HelloStkApplet extends Applet implements ToolkitInterface {

    // ── Константы Proactive команд ──
    private static final short PRO_CMD_DISPLAY_TEXT = 0x21;

    // ── Device Identities ──
    private static final byte DEV_ID_ME      = (byte)0x81;  // UICC → ME
    private static final byte DEV_ID_DISPLAY = (byte)0x02;  // UICC → Display
    private static final byte DEV_ID_NETWORK = (byte)0x03;  // UICC → Network

    // ── Теги TLV ──
    private static final byte TAG_ALPHA_IDENTIFIER = 0x05;
    private static final byte TAG_TEXT_STRING = (byte)0x0D;
    private static final byte DCS_8_BIT_DATA = 0x04;

    // ── Текст меню и сообщения ──
    private static final byte[] MENU_TITLE =
        {'M','y',' ','S','T','K',' ','A','p','p'};          // 10 байт
    private static final byte[] HELLO_TEXT =
        {'H','e','l','l','o',' ','S','T','K','!'};          // 10 байт

    // ── Флаг для первого запуска ──
    private boolean menuRegistered;

    // ═══════════════════════════════════════════════════════
    // install() — точка входа при INSTALL [for install]
    // ═══════════════════════════════════════════════════════
    public static void install(byte[] bArray, short bOffset, byte bLength) {
        // bArray содержит Install Parameters (тег C9):
        //   [Li][Instance AID][Lc][Control Info][La][App Data]
        //
        // Если AID передан в install parameters — используем его
        // Если нет (bArray[bOffset] == 0) — AID из CAP-файла

        HelloStkApplet applet = new HelloStkApplet();

        // Регистрация: либо из CAP, либо из install params
        if (bArray[bOffset] == 0) {
            applet.register();  // AID из CAP-файла
        } else {
            // AID из install params
            applet.register(bArray, (short)(bOffset + 1), bArray[bOffset]);
        }
    }

    // ═══════════════════════════════════════════════════════
    // Конструктор — вызывается ОДИН РАЗ при install()
    // ═══════════════════════════════════════════════════════
    private HelloStkApplet() {
        // Вся EEPROM-аллокация здесь — НЕ в process()!
        registerMenu();
    }

    // ═══════════════════════════════════════════════════════
    // Регистрация пункта меню
    // ═══════════════════════════════════════════════════════
    private void registerMenu() {
        ToolkitRegistry tr = ToolkitRegistry.getEntry();

        // initMenuEntry(text, offset, length,
        //               position, isHelpAvailable,
        //               iconId, iconQualifier)
        tr.initMenuEntry(
            MENU_TITLE,           // текст пункта меню
            (short)0,             // смещение в массиве
            (short)MENU_TITLE.length,  // длина
            (byte)0,              // позиция (0 = конец меню)
            false,                // help не нужен
            (byte)0,              // icon ID (0 = без иконки)
            (byte)0               // icon qualifier
        );

        menuRegistered = true;
    }

    // ═══════════════════════════════════════════════════════
    // process() — APDU диспетчер
    // ═══════════════════════════════════════════════════════
    public void process(APDU apdu) {
        byte[] buf = apdu.getBuffer();
        byte cla = buf[ISO7816.OFFSET_CLA];
        byte ins = buf[ISO7816.OFFSET_INS];

        if (ins == (byte)0xD0) {
            // ENVELOPE — передаём в ToolkitInterface
            processToolkit(apdu);
        } else if (ins == (byte)0xA4) {
            // SELECT — OK, апплет выбран
            return;
        } else {
            ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

    // ═══════════════════════════════════════════════════════
    // processToolkit() — обработчик ENVELOPE (STK events)
    // ═══════════════════════════════════════════════════════
    public void processToolkit(APDU apdu) {
        byte[] buf = apdu.getBuffer();
        byte event = buf[ISO7816.OFFSET_P1];

        switch (event) {
            case ToolkitConstants.EVENT_MENU_SELECTION:
                onMenuSelected();
                break;

            case ToolkitConstants.EVENT_TIMER_EXPIRATION:
                // Не используется в этом примере
                break;

            default:
                // Неизвестное событие — безопасно игнорируем
                break;
        }
    }

    // ═══════════════════════════════════════════════════════
    // onMenuSelected() — пользователь выбрал наш пункт меню
    // ═══════════════════════════════════════════════════════
    private void onMenuSelected() {
        showHelloMessage();
    }

    // ═══════════════════════════════════════════════════════
    // showHelloMessage() — DISPLAY TEXT proactive command
    // ═══════════════════════════════════════════════════════
    private void showHelloMessage() {
        ProactiveHandler ph = ProactiveHandler.getTheHandler();

        // Инициализация команды
        ph.init(
            PRO_CMD_DISPLAY_TEXT,           // тип команды
            (byte)0x00,                     // qualifier: normal priority, auto-clear
            DEV_ID_DISPLAY                  // target: дисплей
        );

        // Добавление текста
        ph.appendTLV(
            (byte)(TAG_TEXT_STRING | (byte)0x80),  // tag + CR bit
            DCS_8_BIT_DATA,                        // кодировка
            HELLO_TEXT,                            // данные
            (short)0,                              // смещение
            (short)HELLO_TEXT.length               // длина
        );

        // Отправка proactive команды
        ph.send();

        // После send() терминал покажет текст
        // Апплет возвращает управление JCRE
    }
}
```

---

## 4. build.xml (сборка)

```xml
<project default="build" basedir=".">

  <taskdef name="javacard"
           classname="pro.javacard.ant.JavaCard"
           classpath="lib/ant-javacard.jar"/>

  <target name="build">
    <mkdir dir="bin"/>

    <!-- Компиляция Java → class -->
    <javac srcdir="src" destdir="bin"
           source="1.1" target="1.1"
           bootclasspath="lib/api.jar"
           classpath="lib/sim.jar"/>

    <!-- Конвертация class → CAP -->
    <javacard>
      <cap targetsdk="oracle_javacard_sdks/jc221_kit"
           jckit="oracle_javacard_sdks/jc305u3_kit"
           output="bin/hello-stk.cap"
           sources="src"
           classes="bin"
           version="1.0">
        <applet class="com.example.stk.HelloStkApplet"
                aid="f0:70:02:ca:44:90:03:01"/>
        <import exps="exp" jar="lib/sim.jar"/>
      </cap>
    </javacard>
  </target>
</project>
```

> ⚠️ **AID**: `F0 70 02 CA 44 90 03 01` — тестовый RID `F0` (proprietary/unregistered). Для production — зарегистрировать RID через ISO.

---

## 5. Install Parameters (что передать при установке)

Install Parameters (BER-TLV hex для GlobalPlatformPro):

```
C9 00                         ← Application Parameters (пусто)
EF 1C                         ← System Parameters (28 байт)
  C8 02 01 00                 ← NVM Quota = 256 байт
  C7 02 01 00                 ← RAM Quota = 256 байт
  CA 12                       ← STK Parameters (18 байт)
    01 00                     ← Access Domain = 0x00 (доступ к ФС разрешён)
    01                        ← Priority = 1
    00                        ← Max Timers = 0
    15                        ← Max Menu Entry Length = 21 байт
    05                        ← Max Menu Entries = 5
    00 00 00 00 00 00 00 00   ← TAR placeholder (нет)
    00 00 00                  ← MSL placeholder (нет)
```

Склеенная hex-строка:
```
c900ef1cc8020100c7020100ca12010001001505000000000000000000000000
```

---

## 6. Установка на карту

```bash
# Переменные (замените на свои ключи!)
KIC="..."  # Key Encryption Key
KID="..."  # Key MAC Key
KIK="..."  # Key DEK Key
KVN="01"   # Key Version Number

# Install Parameters
PARAMS="c900ef1cc8020100c7020100ca12010001001505000000000000000000000000"

CAP="bin/hello-stk.cap"

# Шаг 1: Установка
java -jar gp.jar \
  --key-enc $KIC --key-mac $KID --key-dek $KIK --key-ver $KVN \
  --install $CAP --params $PARAMS

# Шаг 2: Проверка
java -jar gp.jar \
  --key-enc $KIC --key-mac $KID --key-dek $KIK \
  --list

# Ожидаемый результат:
# PKG: F07002CA44 (LOADED)
#      Applet: F07002CA44900301
```

---

## 7. Что происходит на телефоне

```
1. Телефон читает EF_DIR → видит новый AID F0:70:02:CA:44:90:03:01
2. Терминал отправляет TERMINAL PROFILE → UICC
3. UICC отправляет SET UP MENU (proactive) → терминал
4. Телефон добавляет "My STK App" в SIM-меню
5. Пользователь открывает SIM-меню → видит пункт
6. Пользователь выбирает пункт → терминал отправляет ENVELOPE (MENU SELECTION)
7. UICC → JCRE → processToolkit() → onMenuSelected()
8. UICC отправляет DISPLAY TEXT "Hello STK!" → телефон показывает
```

---

## 8. Типичные ошибки и их решение

| Симптом | Причина | Исправление |
|---|---|---|
| `6A88` при INSTALL | Неправильная длина Install Params или TAR | Проверить BER-TLV структуру `unber.py --hex $PARAMS` |
| `6985` при INSTALL | Не прошёл VERIFY PIN | Выполнить аутентификацию через EXTERNAL AUTHENTICATE |
| Апплет не в меню | `initMenuEntry()` не вызван или ошибка в параметрах | Проверить конструктор и длину текста меню |
| Меню есть, но не реагирует | `processToolkit()` не обрабатывает `EVENT_MENU_SELECTION` | Добавить case в switch |
| CAP не загружается | Конфликт Load File AID | Удалить старый пакет: `gp --uninstall $CAP` |
| DISPLAY TEXT не показывается | Терминал не поддерживает (terminal profile bit = 0) | Проверить TERMINAL PROFILE бит для DISPLAY TEXT |
| Stack overflow | Глубокая вложенность вызовов | Упростить call chain; не вызывать proactive из processToolkit() рекурсивно |

---

## 9. Оптимизация перед production

### Память
```java
// ПЛОХО: 6 маленьких массивов → 9×32 = 288 байт EEPROM
private byte[] a1 = new byte[8];
private byte[] a2 = new byte[12];
// ... и т.д.

// ХОРОШО: 1 массив → 5×32 = 160 байт EEPROM
private byte[] buffer = new byte[124];
// Доступ по смещениям: buffer[0..7], buffer[8..19], ...
```

### Скорость
```java
// ПЛОХО: instance field в цикле (чтение EEPROM каждый раз)
for (short i = 0; i < myArray.length; i++) { ... }

// ХОРОШО: локальная переменная (в RAM/стеке)
short len = myArray.length;
for (short i = 0; i < len; i++) { ... }
```

### EEPROM vs RAM
```java
// EEPROM (persistent, медленно): ~1-10ms/запись
private byte[] persistentData;

// RAM/transient (быстро, сброс при RESET): ~μs/запись
private byte[] temp;  // создаётся через JCSystem.makeTransientByteArray()
```

---

## 10. Следующие шаги (что добавить)

| Уровень | Функция | Как сделать |
|---|---|---|
| **Базовый** | Подменю | Несколько `initMenuEntry()` + обработка `ITEM_ID` в SELECT ITEM response |
| **Базовый** | GET INPUT | `ph.initGetInput(...)` → получить ввод пользователя |
| **Средний** | SMS-уведомление | `PRO_CMD_SEND_SHORT_MESSAGE` → отправить SMS |
| **Средний** | Таймеры | `PRO_CMD_TIMER_MANAGEMENT` → периодические действия |
| **Продвинутый** | Location-triggered | `setEvent(EVENT_LOCATION_STATUS)` → действие при смене LAC |
| **Продвинутый** | Call Control | `EVENT_CALL_CONTROL_BY_NAA` → модифицировать/блокировать вызов |
| **Продвинутый** | BIP/Интернет | `OPEN CHANNEL` → TCP/IP через терминал |
| **OTA** | Удалённое обновление | SMS-PP с TAR → `processToolkit()` → обновить файлы |

---

## 11. Сравнение: sim.toolkit (2G) vs uicc.toolkit (3G+)

| Аспект | `sim.toolkit` | `uicc.toolkit` |
|---|---|---|
| **import** | `import sim.toolkit.*;` | `import uicc.toolkit.*;` |
| **Пакет AID** | `A0 00 00 00 76 01 01` | `A0 00 00 00 76 02 01` |
| **Target** | GSM SIM (2G) | UMTS/LTE/5G UICC |
| **ProactiveHandler** | `sim.toolkit.ProactiveHandler` | `uicc.toolkit.ProactiveHandler` |
| **ToolkitRegistry** | `sim.toolkit.ToolkitRegistry` | `uicc.toolkit.ToolkitRegistry` |
| **Логические каналы** | Базовый (0) | 0-19 |
| **Install Params** | `CA` tag (TS 102 226) | `CA` или `TA` tag |
| **Доступ к файлам** | `sim.access.*` | `uicc.access.*` |
| **USIM-специфичный доступ** | ❌ | `uicc.usim.access.*` |

> **Практический совет**: для новых проектов используйте `uicc.toolkit` — он работает на всех 3G/4G/5G картах и обратно совместим с 2G в большинстве случаев.

---

## Ссылки на источники

- Спецификация CAT: [[wiki/summaries/ts_102223|ETSI TS 102 223]]
- Установка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- STK API: [[wiki/concepts/STK_Applet]]
- GP управление: [[wiki/concepts/GlobalPlatform_Card]]
- AID-гид: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
- Best Practices: [[wiki/summaries/java_card_stepping_stones]]
- RuimTools examples: [[wiki/summaries/ruimtools_javacard_samples]]
- HelloSTK: [[wiki/summaries/hello_stk|HelloSTK (Osmocom)]]
