---
tags: [STK, SIM-Toolkit, thesis, MITM, JavaCard, summary]
source: "[[Specifications/Papers/Sjors_Gielen_SIM_Toolkit_In_Practice.pdf]]"
type: thesis
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# SIM Toolkit in Practice (Sjors Gielen, BSc Thesis, 2012)

> **Автор**: Sjors Gielen, Radboud University Nijmegen
> **Научные руководители**: Erik Poll, Fabian van den Broek
> **Дата**: 27 августа 2012
> **Страниц**: 32

## Обзор

Бакалаврская работа (Honours Programme), дающая практический обзор SIM Toolkit (STK) с фокусом на реальные данные, инструменты MITM-анализа и безопасность. Уникальна тем, что содержит **сырые байты** реального STK-трафика и код для его перехвата/модификации. ^[extracted]

## Ключевые разделы

### 1. SIM card background (§2)
- Коммуникация смарт-карт: APDU модель, C-APDU → R-APDU
- GSM SELECT: CLA=A0, INS=A4
- ATR (Answer to Reset) при включении
- Карта всегда secondary role (отвечает, не инициирует)

### 2. SIM Toolkit инициализация (§3) — детальный разбор

#### Чтение SIM Service Table (EF_SST, 6F38)
```
ME: 00 A4 00 04 02     ← SELECT file
SIM: A4                  ← ACK
ME: 6F 38               ← FID = SIM Service Table
SIM: 61 1E               ← 30 bytes available (GET RESPONSE)
ME: 00 B0 00 00 07      ← READ BINARY (Le=7)
SIM: 9E EF 1F 1C FF 3E 04 90 00
```

Расшифровка: Service 1 (CHV1 disable), Service 2 (ADN), Service 17 (SPN), ...

#### Terminal Profile
```
ME: 80 10 00 00 14     ← TERMINAL PROFILE
DATA: FF FF FF FF 1F 00 00 DF D7 03 0A 00 00 00 00 06 00 00 00 00
```
Capabilities: DISPLAY TEXT, GET INKEY, SET UP MENU, SEND SHORT MESSAGE, CALL CONTROL, LAUNCH BROWSER...

#### SET UP MENU (proactive command)
```
SIM → ME: D0 26 81 03 01 25 00 82 02 81 82 85 09 4D 65 6E 75 ...
  Command: SET UP MENU
  Alpha ID: "Menu name"
  Items: '80'="Item 1", '81'="Item 2"
```

#### Menu Selection → GET INPUT
```
ME: 80 C2 00 00 09     ← ENVELOPE (Menu Selection)
     D3 07 02 02 01 81 10 01 80   ← Item '80' selected

SIM: 91 25              ← Proactive command pending (37 bytes)
ME: 80 12 00 00 25     ← FETCH
SIM: D0 23 81 03 01 23 01 82 02 81 82 8D 14 F4 "Give me some input!" ...
     GET INPUT (1-10 chars, SMS default alphabet)
```

### 3. MITM-инструменты (§4)

| Инструмент | Возможности | Ограничения |
|---|---|---|
| **RebelSIM** ($25) | Прослушивание трафика SIM↔ME | Только чтение, нет направления |
| **SIMparser.pl** (авторский) | Парсинг и объяснение сырых байт | Автор: Sjors Gielen (github.com/sgielen/simparser) |
| **SmartLogicTool** | Активный MITM, Java-код для модификации | Сбоит на высоких скоростях |
| **Bladox TurboSIM** | Тонкий чип поверх SIM, меняет трафик | Не показывает изменения, код на C |

### 4. Метод активного MITM (§4.5)
1. Перехватить TERMINAL PROFILE → заменить `90 00` на `91 XX`
2. Перехватить FETCH → подменить proactive command
3. Перехватить TERMINAL RESPONSE → обработать результат
4. Перехватить ENVELOPE → свои обработчики событий
5. Модифицировать SIM Service Table на лету
6. Синхронизация: `91 XX` от реальной SIM → `90 00` (предотвратить конфликт)

### 5. Возможности STK (§5) — с реальными байтами

#### DISPLAY TEXT (raw bytes)
```
D0 3F 81 03 01 21 81 82 02 81 02 8D 34 04
"Hello world! I am an alternative SIM Toolkit stack."
```
Qualifier: high priority + wait for user (`81`)

#### SELECT ITEM
```
D0 1B 81 03 01 24 00 82 02 81 02
8F 07 AB "Item 1" 8F 07 AC "Item 2"
```

#### PROVIDE LOCAL INFORMATION
- Network info (MCC, MNC, LAC, Cell ID)
- IMEI number
- Результат в TERMINAL RESPONSE

#### SEND SHORT MESSAGE (с SMS TPDU!)
```
D0 2D 81 03 05 13 00 82 02 81 82
85 0F "Visible message"
8B 11 31 00 0B 91 13 16 32 54 76 F8 00 00 AA 03 C8 77 1A
  ↑ SMS-SUBMIT, TP-DA=+31612345678, TP-VP=4 days, TP-UD="Hoi"
```

#### SET UP CALL (Bladox TurboSIM, код на C)
```c
u8 *address = str2msisdn(t_ms, MSISDN_ADN, MEM_R);
set_up_call(address, MSISDN_ADN, "");
```

#### Call Control (блокировка вызовов)
```c
// Bladox TurboSIM:
// Заменить EF_SST → service 28 (Call Control) = enabled
// Перехватить ENVELOPE → retval(0x9f09) → "не разрешаю"
```

#### Events (Location Changed)
```c
reg_action(ACTION_EVENT_LOCATION_STATUS);
// При изменении LAC: display_text_raw("Location changed", ...)
```

### 6. Безопасность (§6) — реальные атаки через STK

| Атака | Механизм | Реализуемость |
|---|---|---|
| **DoS** | DISPLAY TEXT в цикле (high prio + wait) | TurboSIM / MITM |
| **Отслеживание** | PROVIDE LOCAL INFO + SEND SMS | TurboSIM |
| **MITM на звонки** | Call Control → reroute | TurboSIM |
| **Кража денег** | SEND SHORT MESSAGE в цикле | TurboSIM |
| **Перехват SMS-кодов** | Event MT + SEND SMS forward | TurboSIM |

### 7. Код STK-стека (Appendix A, ~500 строк Java)
Полная реализация `SimToolkitStack` со всеми константами:
- `STK_CMD_*`: коды всех proactive команд (40+ констант)
- `STK_TAG_*`: теги COMPREHENSION-TLV (50+ констант)
- `STK_DEVICE_*`: device identities
- `buildNextMessage()`, `addDeviceIdentities()`, `addTextTag()`, `addAlphaIdentifier()`, `addItemTag()` — построитель proactive команд
- `SimToolkitStackMessage` — пример: DISPLAY TEXT в цикле (DoS)

## Ценность для проекта

**Лучший практический источник по STK** в нашей коллекции:
- Сырые байты реальных STK-команд (можно использовать для отладки)
- MITM-методология для тестирования
- Java-код STK-стека (можно адаптировать для своих апплетов)
- Реальные уязвимости (важно для security testing)

## Связи

- CAT/STK: [[wiki/concepts/CAT_STK]]
- STK Applet: [[wiki/concepts/STK_Applet]]
- JavaCard: [[wiki/concepts/JavaCard]]
- CAT спецификация: [[wiki/summaries/ts_102223]]
