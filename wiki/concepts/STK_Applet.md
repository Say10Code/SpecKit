---
tags: [JavaCard, STK, applet, ToolkitInterface, ProactiveHandler]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
sources:
  - "[[wiki/summaries/ts_102223|ETSI TS 102 223 — CAT]]"
  - "[[wiki/summaries/java_card_stepping_stones|Java Card Stepping Stones]]"
  - "[[wiki/summaries/ruimtools_javacard_samples|RuimTools JavaCard Samples]]"
---

# STK Applet — SIM Toolkit Applet Development

## Определение

**STK-апплет** — это Java Card приложение, реализующее интерфейс `ToolkitInterface` (`sim.toolkit` или `uicc.toolkit`). Такой апплет получает события от терминала через ENVELOPE и может отправлять **proactive commands** через `ProactiveHandler`. ^[inferred]

## Архитектура STK-апплета

```
┌──────────────────────────────────────────────────────────┐
│  Терминал (ME)                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  DISPLAY TEXT, SET UP MENU, GET INPUT, ...          │  │
│  └────────────┬───────────────────────────────────────┘  │
│               │ ENVELOPE                                  │
└───────────────┼──────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────┐
│  UICC / Java Card                                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  ToolkitInterface.processToolkit(APDU apdu)        │  │
│  │     ↓                                              │  │
│  │  ProactiveHandler.send()                           │  │
│  │     ↓                                              │  │
│  │  ProactiveResponseHandler (результат команды)      │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Базовый STK-апплет (шаблон)

```java
public class StkApplet extends Applet implements ToolkitInterface {

    private static final short PRO_CMD_DISPLAY_TEXT = 0x21;
    private static final byte  DEV_ID_DISPLAY = (byte)0x02;
    private static final byte  DEV_ID_ME     = (byte)0x81;
    private static final byte  TAG_ALPHA_IDENTIFIER = 0x05;
    private static final byte  TAG_TEXT_STRING = (byte)0x0D;
    private static final byte  DCS_8_BIT_DATA = 0x04;

    // Статический install — точка входа при установке
    public static void install(byte[] bArray, short bOffset, byte bLength) {
        StkApplet applet = new StkApplet();
        applet.register(bArray, (short)(bOffset + 1), bArray[bOffset]);
    }

    // Конструктор — регистрируем меню
    private StkApplet() {
        ToolkitRegistry tr = ToolkitRegistry.getEntry();
        byte[] menuText = {'M','y',' ','M','e','n','u'};
        tr.initMenuEntry(menuText, (short)0, (short)7,
                         (byte)0, false, (byte)0, (byte)0);
    }

    // APDU-диспетчер
    public void process(APDU apdu) {
        byte[] buf = apdu.getBuffer();
        if (buf[ISO7816.OFFSET_INS] == (byte)0xD0) {
            processToolkit(apdu);  // ENVELOPE → к ToolkitInterface
        } else {
            ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

    // Обработчик ENVELOPE
    public void processToolkit(APDU apdu) {
        byte[] buf = apdu.getBuffer();

        byte event = buf[ISO7816.OFFSET_P1];  // тип события
        switch (event) {
            case ToolkitConstants.EVENT_MENU_SELECTION:
                onMenuSelection();
                break;
            case ToolkitConstants.EVENT_TIMER_EXPIRATION:
                onTimerExpiration();
                break;
            default:
                // неизвестное событие
                break;
        }
    }

    // Обработчик выбора меню
    private void onMenuSelection() {
        ProactiveHandler ph = ProactiveHandler.getTheHandler();

        ph.init(PRO_CMD_DISPLAY_TEXT,
                (byte)0x00,         // normal priority, no user wait
                DEV_ID_DISPLAY);

        byte[] text = {'H','e','l','l','o',' ','S','T','K','!'};
        ph.appendTLV((byte)(TAG_TEXT_STRING | 0x80), DCS_8_BIT_DATA,
                     text, (short)0, (short)text.length);

        ph.send();
    }
}
```

## Ключевые API-классы STK

| Класс | Пакет 2G | Пакет 3G+ | Назначение |
|---|---|---|---|
| **`ProactiveHandler`** | `sim.toolkit` | `uicc.toolkit` | Формирование и отправка proactive команд |
| **`ProactiveResponseHandler`** | `sim.toolkit` | `uicc.toolkit` | Получение ответа (TERMINAL RESPONSE) |
| **`ToolkitRegistry`** | `sim.toolkit` | `uicc.toolkit` | Регистрация меню, заголовка, событий |
| **`ToolkitConstants`** | `sim.toolkit` | `uicc.toolkit` | Константы (коды команд, событий, теги) |
| **`ToolkitInterface`** | `sim.toolkit` | `uicc.toolkit` | Интерфейс обработчика ENVELOPE |
| **`ViewHandler`** | `sim.access` | `uicc.access` | Доступ к файловой системе UICC |

## ProactiveHandler — формирование команд

```java
ProactiveHandler ph = ProactiveHandler.getTheHandler();

// Инициализация команды
ph.init(commandType, qualifier, deviceId);
// commandType: PRO_CMD_DISPLAY_TEXT, PRO_CMD_SET_UP_MENU, ...
// qualifier: битовые флаги (приоритет, алфавит, ...)
// deviceId:   DEV_ID_ME (UICC→ME), DEV_ID_DISPLAY, DEV_ID_NETWORK

// Добавление TLV-полей
ph.appendTLV(tag, value, offset, length);

// Отправка
ph.send();
```

## События (Events) — что может получить STK-апплет

| Константа | Событие |
|---|---|
| `EVENT_MENU_SELECTION` | Пользователь выбрал пункт меню |
| `EVENT_CALL_CONTROL_BY_NAA` | Контроль исходящего вызова |
| `EVENT_TIMER_EXPIRATION` | Таймер истёк |
| `EVENT_MT_CALL` | Входящий звонок |
| `EVENT_CALL_CONNECTED` / `CALL_DISCONNECTED` | Состояние звонка |
| `EVENT_LOCATION_STATUS` | Изменение LAC/TAC |
| `EVENT_IDLE_SCREEN_AVAILABLE` | Экран ожидания свободен |
| `EVENT_LANGUAGE_SELECTION` | Смена языка телефона |
| `EVENT_ACCESS_TECHNOLOGY_CHANGE` | Смена RAT |
| `EVENT_BROWSER_TERMINATION` | Браузер закрыт |
| `EVENT_HCI_CONNECTOR_EVENT` | Contactless-событие |

## Регистрация на события

```java
private StkApplet() {
    // Регистрация на события — через ToolkitRegistry
    ToolkitRegistry tr = ToolkitRegistry.getEntry();

    // Подписка на location status
    tr.setEvent((byte)ToolkitConstants.EVENT_LOCATION_STATUS);

    // Подписка на call control
    tr.setEvent((byte)ToolkitConstants.EVENT_CALL_CONTROL_BY_NAA);

    // Подписка на change of Access Technology
    tr.setEvent((byte)ToolkitConstants.EVENT_ACCESS_TECHNOLOGY_CHANGE);
}
```

## Практические примеры (из RuimTools / HelloSTK)

### DISPLAY TEXT
```java
ph.init(PRO_CMD_DISPLAY_TEXT, (byte)0x00, DEV_ID_DISPLAY);
ph.appendTLV((byte)(TAG_TEXT_STRING | 0x80), DCS_8_BIT_DATA,
             text, (short)0, (short)text.length);
ph.send();
```

### SELECT ITEM (список выбора)
```java
ph.init(PRO_CMD_SELECT_ITEM, (byte)0x00, DEV_ID_ME);
ph.appendTLV(TAG_ALPHA_IDENTIFIER, "Выберите:", (short)0, (short)9);
ph.appendTLV(TAG_ITEM_CR, (byte)1, item1, (short)0, (short)item1.length);
ph.appendTLV(TAG_ITEM_CR, (byte)2, item2, (short)0, (short)item2.length);
ph.send();
```

### SEND SHORT MESSAGE (отправка SMS)
```java
ph.init(PRO_CMD_SEND_SHORT_MESSAGE, (byte)0x00, DEV_ID_NETWORK);
ph.appendTLV(TAG_ADDRESS, smscAddress, (short)1, (short)smscAddress[0]);
ph.appendTLV(TAG_SMS_TPDU, smsTPDU, (short)0, (short)smsTPDU.length);
ph.send();
```

### LAUNCH BROWSER (открыть браузер)
```java
byte[] url = {'h','t','t','p',':','/','/','m','y','.','c','o','m','/'};
ph.init(0x15, (byte)0x00, DEV_ID_ME);
ph.appendTLV(0x31, url, (short)0, (short)url.length);
ph.send();
```

### REFRESH (уведомить терминал об изменении файлов)
```java
ph.init(PRO_CMD_REFRESH, (byte)0x00, DEV_ID_ME);
// '00' = NAA Initialization and Full File Change Notification
// '01' = File Change Notification
ph.send();
```

## Два поколения API: sim.toolkit vs uicc.toolkit

| Особенность | `sim.toolkit` (2G) | `uicc.toolkit` (3G+) |
|---|---|---|
| Применение | GSM SIM | UMTS/LTE/5G UICC |
| AID пакета | `A0 00 00 00 76 01 01` | `A0 00 00 00 76 02 01` |
| Логические каналы | Базовый (0) | Множественные (0-19) |
| ProactiveHandler | `sim.toolkit.ProactiveHandler` | `uicc.toolkit.ProactiveHandler` |
| Install parameters | `CA` tag | `CA` or `TA` tag |
| Доступ к файлам | `sim.access` | `uicc.access` + `uicc.usim.access` |

## Важные ограничения

1. **Одна proactive команда за раз**: Второй `ph.send()` без завершения сессии → ошибка
2. **Reentrance**: Пока DISPLAY TEXT с `WAIT_FOR_USER` активен, другие proactive команды блокированы
3. **Menu entry limits**: Длина и количество записей меню ограничены install parameters (`CA`)
4. **Stack danger**: Не вызывай proactive команды внутри `processToolkit()` глубже 2-3 уровней
5. **Terminal может отвергнуть**: Не все терминалы поддерживают все proactive команды (см. TERMINAL PROFILE)

## Связи

- CAT/STK механизмы: [[wiki/concepts/CAT_STK]]
- Платформа JavaCard: [[wiki/concepts/JavaCard]]
- Разработка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- GlobalPlatform установка: [[wiki/concepts/GlobalPlatform_Card]]
- Примеры кода: [[wiki/summaries/ruimtools_javacard_samples]]
- MITM-анализ STK: [[wiki/summaries/sjors_gielen_stk|SIM Toolkit in Practice]]
- UICC API спецификация: [[wiki/summaries/ts_102241|TS 102 241]]
- SIM API (legacy): [[wiki/summaries/ts_143019|TS 143 019]]
- SAT (GSM STK): [[wiki/summaries/ts_151014|TS 51.014]]
- Миграция 2G→5G: [[wiki/syntheses/sim_vs_uicc_toolkit|sim.toolkit vs uicc.toolkit]]
- AID-гид: `Specifications/Tutorials/AID_METODICHESKOE_POSOBIE.md`
