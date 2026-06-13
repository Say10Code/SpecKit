---
tags: [JavaCard, applet, development, build, install, GP]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/java_card_stepping_stones|Java Card Stepping Stones]]"
  - "[[wiki/summaries/ruimtools_javacard_guidelines|RuimTools JavaCard Guidelines]]"
  - "[[wiki/summaries/gpc_card_spec_2_3_1|GlobalPlatform Card Spec 2.3.1]]"
---

# Java Card Applet Development — Разработка апплетов

## Определение

Разработка апплета Java Card — это процесс от написания кода на Java (ограниченный subset) до установки готового CAP-файла на SIM-карту через GlobalPlatform. ^[inferred]

## Конвейер сборки

```
┌────────┐     javac       ┌─────────┐    converter    ┌────────┐   verifier   ┌──────────┐
│ .java  │ ──────────────→ │ .class  │ ───────────────→│ .cap   │ ───────────→│ verified │
│ source │   (Java 1.1)    │ bytecode│  (ant-javacard) │ package│  (optional) │  .cap    │
└────────┘                 └─────────┘                 └────────┘              └──────────┘
                                                                │
                                                    ┌───────────▼───────────┐
                                                    │ GlobalPlatformPro     │
                                                    │ gp.jar --install      │
                                                    └───────────┬───────────┘
                                                                │
                                                    ┌───────────▼───────────┐
                                                    │    SIM-карта (UICC)   │
                                                    └───────────────────────┘
```

### Build с ant-javacard (build.xml)

```xml
<project>
  <taskdef name="javacard" classname="pro.javacard.ant.JavaCard"/>

  <javacard>
    <cap targetsdk="jc221_kit" jckit="jc305u3_kit"
         output="bin/my-applet.cap" sources="src"
         classes="bin" version="1.0">
      <applet class="com.example.MyApplet"
              aid="f0:70:02:ca:44:90:03:01"/>
      <import exps="exp" jar="lib/sim.jar"/>
    </cap>
  </javacard>
</project>
```

- **targetsdk**: Java Card SDK цели (обычно `jc221_kit`)
- **jckit**: SDK компилятора (может быть новее)
- **applet aid**: Instance AID (5–16 hex байт, разделённых `:`)
- **import**: Импорт экспортированных пакетов (`sim.jar` — STK API)

## Жизненный цикл апплета

### 1. Конструктор: `Applet()`
```java
public class MyApplet extends Applet implements ToolkitInterface {

    private byte[] state;  // persistent (EEPROM)

    private MyApplet() {
        // Вызывается один раз — во время install()
        state = new byte[10];   // allocate EEPROM
        // Регистрация меню:
        ToolkitRegistry tr = ToolkitRegistry.getEntry();
        tr.initMenuEntry("My Menu", (short)0, (short)7,
                         (byte)0, false, (byte)0, (byte)0);
    }
}
```

### 2. `install()`: Установка
```java
public static void install(byte[] bArray, short bOffset, byte bLength) {
    MyApplet applet = new MyApplet();  // конструктор
    applet.register();  // Instance AID — из CAP
    // или: applet.register(bArray, (short)(bOffset+1), bArray[bOffset]);
}
```

**bArray** содержит Installation Parameters (тег `C9`):
```
Li (1) + Instance AID (5-16) + Lc (1) + Control Info (0-N) + La (1) + App Data (0-N)
```

### 3. `select()`: Выбор апплета
```java
public boolean select() {
    // Вызывается при SELECT [by AID]
    // Вернуть true = апплет готов принимать APDU
    return true;
}
```

### 4. `process()`: Обработка APDU
```java
public void process(APDU apdu) {
    byte[] buf = apdu.getBuffer();
    byte cla = buf[ISO7816.OFFSET_CLA];
    byte ins = buf[ISO7816.OFFSET_INS];

    switch (ins) {
        case (byte)0xA4:  // SELECT
            // ...
            break;
        case (byte)0xD0:  // ENVELOPE (STK event)
            processToolkit(apdu);
            break;
        default:
            ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
}
```

### 5. `deselect()`: Де-активация
```java
public void deselect() {
    // Очистка transient данных
}
```

## Оптимизация апплетов (ключевые правила)

### Память

| Правило | Пояснение |
|---|---|
| **Выделяй всё в конструкторе** | `new` в process() — риск исчерпания памяти и замедление |
| **Объединяй маленькие массивы** | 6 массивов по 8 байт = 9×32 = 288 байт; 1 массив 48 байт = 2×32 = 64 байта |
| **static для примитивов** | `static byte x` = 1 байт EEPROM вместо 2 |
| **RAM для временных данных** | Используй APDU buffer и transient массивы вместо EEPROM |

### Скорость

| Правило | Пояснение |
|---|---|
| **Избегай глубокой иерархии** | Виртуальные методы дороги из-за dynamic binding |
| **Favor static, private, final** | Не подвергаются dynamic binding → быстрее |
| **Используй native API** | `Util.arrayCopy()`, `Util.arrayFillNonAtomic()` — нативный код |
| **Оптимизируй циклы** | Выноси `.length` и вызовы методов за цикл |
| **Проверяй CLA+INS вместе** | `switch (Util.getShort(buf, OFFSET_CLA))` — один вызов вместо двух |

### EEPROM (Non-Volatile Memory)

- Запись в EEPROM **в ~1000 раз медленнее** чем в RAM ^[extracted]
- Используй `Util.arrayCopyNonAtomic()` вместо `Util.arrayCopy()` если не нужна транзакция
- Транзакции (`beginTransaction`/`commitTransaction`) дороги — пользуйся обоснованно

### Стек

- Избегай глубокой вложенности вызовов (стек ~2-4 KB)
- Не используй рекурсию на смарт-карте
- Локальные переменные — быстрее чем instance fields

## Установка через GlobalPlatformPro

```bash
# Переменные карты
KIC="..."  # Key Encryption
KID="..."  # Key MAC
KIK="..."  # Key DEK
KVN="01"   # Key Version Number

# Install parameters (BER-TLV hex):
PARAMS="c900ef1cc8020100c7020100ca12010001001505000000000000000000000000"

# Установка
java -jar gp.jar \
  --key-enc $KIC --key-mac $KID --key-dek $KIK --key-ver $KVN \
  --install applet.cap --params $PARAMS

# Проверка
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --list

# Удаление
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --uninstall applet.cap
```

### Install Parameters (тег `C9` + `EF` + `C8`/`C7`/`CA`)

```
C9 00                          ← Application Parameters (пусто)
EF 1C                          ← System Parameters (28 байт)
  C8 02 01 00                  ← NVM Quota = 256 bytes
  C7 02 01 00                  ← RAM Quota  = 256 bytes
  CA 12 01 00 01 00 15 05     ← STK Parameters:
    01 00                        ← Access domain = 0x00 (file system access)
    01                           ← Priority level 1
    00                           ← Max timers = 0
    15                           ← Max menu entry length = 21
    05                           ← Max menu entries = 5
    00 00 00 00 00 00 00 00     ← TAR (нет)
    00 00 00                     ← MSL (нет)
```

## Типичные ошибки

| Ошибка | Причина | Решение |
|---|---|---|
| `6A88` (Referenced data not found) | Неправильный TAR в install params | Проверить CA tag — TAR должен совпадать |
| `6985` (Conditions not satisfied) | Не прошли VERIFY PIN / AUTH | Выполнить VERIFY PIN до команды |
| CAP не загружается | Конфликт Load File AID | Удалить старый пакет перед загрузкой |
| Applet не появляется в EF_DIR | `register()` не вызван | Проверить install() и bArray |
| `ILLEGAL_AID` | AID уже занят или < 5 байт | Проверить уникальность AID |
| Menu не отображается | Нет вызова `initMenuEntry()` в конструкторе | Добавить в конструктор + переустановить |
| Stack overflow | Слишком глубокая вложенность | Упростить call chain |

## Связи

- Платформа: [[wiki/concepts/JavaCard]]
- GlobalPlatform архитектура: [[wiki/concepts/GlobalPlatform_Card]]
- STK-разработка: [[wiki/concepts/STK_Applet]]
- AID-система: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
- Примеры кода: [[wiki/summaries/ruimtools_javacard_samples]]
