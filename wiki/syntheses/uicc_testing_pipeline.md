---
tags: [synthesis, testing, pySim, gp, TCA-Loader, conformance, TS-31.124]
type: synthesis
created: 2026-06-11
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/summaries/osmopysim_usermanual|pySim User Manual]]"
  - "[[wiki/summaries/ts_31124|TS 31.124 — USAT Conformance]]"
  - "[[wiki/summaries/java_card_stepping_stones|TCA Stepping Stones]]"
  - "[[wiki/concepts/JavaCard_Applet_Development]]"
  - "[[wiki/concepts/GlobalPlatform_Card]]"
---

# Тестирование UICC: от pySim до TS 31.124 Conformance

> **Synthesis** — полный обзор инструментов и методик тестирования UICC/SIM: от бытового чтения файлов до сертификационных тестов.

---

## 1. Пирамида тестирования UICC

```
        ┌──────────────┐
        │ Conformance  │  GCF / PTCRB / TS 31.124
        │ (Formal)     │  Сертификационные лаборатории
        ├──────────────┤
        │Interoperability│ TCA Interop / GSMA LITE
        │   Testing    │  Разные карты × разные телефоны
        ├──────────────┤
        │  Automated   │  pySim-trace / shadysim / gp.jar
        │  Testing     │  Скрипты, CI/CD
        ├──────────────┤
        │  Manual      │  pySim-shell / GlobalPlatformPro
        │  Testing     │  Интерактивная работа
        └──────────────┘
```

---

## 2. Инструменты — обзор

### pySim (Osmocom)

```bash
pySim-shell -p 0                    # PCSC reader #0
pySIM-shell> select MF               # Выбрать корень
pySIM-shell> select ADF.USIM         # Выбрать USIM
pySIM-shell> read EF.IMSI            # Прочитать IMSI (декодирован)
pySIM-shell> verify_chv              # Проверить PIN
pySIM-shell> ust_service_activate 99 # Активировать 5GS
pySIM-shell> export                  # Дамп всей ФС в JSON
```

**Покрытие**:
- Полный доступ к файловой системе (MF/DF/ADF/EF)
- Декодирование значений (IMSI, ICCID, SPN — human-readable)
- GP-команды (list, install, delete)
- Кардирование (card profiles для разных типов UICC)

### GlobalPlatformPro (gp.jar)

```bash
# Список объектов
java -jar gp.jar --list

# Установка апплета
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK \
  --install applet.cap --params $PARAMS

# Удаление
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK \
  --uninstall applet.cap
```

**Покрытие**: GP-управление (LOAD, INSTALL, DELETE), GET STATUS, Secure Channel.

### TCA Loader

Альтернатива gp.jar от Trusted Connectivity Alliance:
- Установка апплетов с проверкой интероперабельности
- Поддержка eUICC (ISD-P)
- Автоматическое тестирование

### shadysim

Python-инструмент для программирования SIM:
```bash
python2 shadysim_isim.py --pcsc --kic $KIC --kid $KID --list-applets
```

### pySim-trace

Сниффер APDU-обмена ME↔UICC:
```bash
pySim-trace --pcsc 0
# Захват и декодирование APDU в реальном времени
```

Полезен для:
- Отладки STK-апплетов
- Reverse engineering поведения телефона
- Верификации TERMINAL PROFILE

---

## 3. Уровни тестирования

### Уровень 1: Файловая система

| Что тестируем | Инструмент | Команда |
|---|---|---|
| Чтение EF_ICCID | pySim-shell | `read EF.ICCID` |
| Чтение EF_IMSI | pySim-shell | `select ADF.USIM; read EF.IMSI` |
| Запись EF_SPN | pySim-shell | `update EF.SPN` |
| Чтение USIM Service Table | pySim-shell | `read EF.UST` |
| Создание EF | pySim-shell | `create EF` |

### Уровень 2: APDU-команды

| Что тестируем | Сырая APDU |
|---|---|
| SELECT MF | `00 A4 00 00 02 3F 00` |
| SELECT EF_ICCID | `00 A4 00 00 02 2F E2` |
| READ BINARY | `00 B0 00 00 0A` |
| VERIFY PIN | `00 20 00 01 08 <PIN>` |
| AUTHENTICATE | `00 88 00 81 22 <RAND+AUTN>` |

### Уровень 3: STK / CAT

```java
// Проверка что апплет получает ENVELOPE (Menu Selection)
// 1. Установить апплет
// 2. Открыть SIM-меню телефона
// 3. Выбрать пункт меню апплета
// 4. Убедиться что processToolkit() вызван с EVENT_MENU_SELECTION
// 5. Проверить что DISPLAY TEXT показан

// Автоматизация через pySim-trace:
pySim-trace --pcsc 0 | grep "DISPLAY TEXT"
```

### Уровень 4: Conformance (TS 31.124)

Формальное тестирование для сертификации:
- **GCF** (Global Certification Forum) — для 3GPP устройств
- **PTCRB** — для североамериканского рынка
- **TS 31.124** — 1341 страница тест-кейсов

Каждый тест-кейс определяет:
- Pre-conditions (состояние UICC)
- Test procedure (последовательность APDU)
- Expected result (ожидаемые SW и данные)

---

## 4. Практический тестовый сценарий

### Сценарий: «Новый STK-апплет на карте»

```bash
# 1. Проверить начальное состояние
pySim-shell -p 0 --script pre_test.txt

# 2. Установить апплет
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK \
  --install applet.cap --params $PARAMS

# 3. Проверить установку
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --list
# PKG: F07002CA44 (LOADED)
#   Applet: F07002CA44900101

# 4. Проверить EF_DIR
pySim-shell -p 0
pySIM-shell> select MF
pySIM-shell> select EF.DIR
pySIM-shell> read_record 1..N  # Должен быть новый AID

# 5. Проверить меню (на телефоне)
# Открыть SIM-меню → должен быть пункт "My STK App"

# 6. Проверить proactive commands (pySim-trace)
pySim-trace --pcsc 0 &
# На телефоне: выбрать пункт меню
# В логе: ENVELOPE (D3) → DISPLAY TEXT (D0)

# 7. Проверить удаление
java -jar gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK \
  --uninstall applet.cap

# 8. Проверить что удалён
java -jar gp.jar --list  # PKG F07002CA44 не должно быть
```

---

## 5. Автоматизация тестирования

### CI/CD для STK-апплетов

```yaml
# .github/workflows/test.yml
steps:
  - name: Build CAP
    run: ant build
  - name: Test on SIM card
    run: |
      java -jar gp.jar --install bin/applet.cap --params $PARAMS
      python3 test_stk.py --verify-menu
      java -jar gp.jar --uninstall bin/applet.cap
```

### Smoke-тесты

```python
# test_stk.py
import pySim
# 1. Connect
card = pySim.connect(pcsc=0)
# 2. Verify card present
assert card.select_mf() == '90 00'
# 3. Verify USIM
assert card.select_adf_usim() == '90 00'
# 4. Read IMSI
imsi = card.read_binary(0x6F07)
assert len(imsi) == 9
# 5. Verify service table
ust = card.read_binary(0x6F38)
assert ust[0] & 0x80  # Service 1 = available
print("Smoke test PASSED")
```

---

## 6. Инструментальная матрица

| Инструмент | Файловая система | GP-управление | APDU-сниффер | Conformance |
|---|---|---|---|---|
| **pySim-shell** | ✅ Полный | ✅ Базовый | ❌ | ❌ |
| **pySim-trace** | ❌ | ❌ | ✅ Полный | ❌ |
| **gp.jar** | ❌ | ✅ Полный | ❌ | ❌ |
| **TCA Loader** | ❌ | ✅ + Interop | ❌ | ❌ |
| **shadysim** | ✅ Legacy | ✅ | ❌ | ❌ |
| **TS 31.124** | ❌ | ❌ | ❌ | ✅ Formal |

---

## 7. Чек-лист тестирования STK-апплета

- [ ] CAP загружается без ошибок (gp.jar --install)
- [ ] Апплет виден в GET STATUS (gp.jar --list)
- [ ] AID добавлен в EF_DIR (pySim read EF.DIR)
- [ ] Меню отображается на телефоне (manual check)
- [ ] При выборе пункта меню — ENVELOPE доставлен (pySim-trace)
- [ ] Proactive команда выполнена (DISPLAY TEXT / SEND SMS / ...)
- [ ] TERMINAL RESPONSE получен и обработан
- [ ] Апплет удаляется без остатка (gp.jar --uninstall + --list)
- [ ] Повторная установка работает (нет конфликта AID)
- [ ] На 2 разных телефонах (interoperability: Android + Nokia)
- [ ] На 2 разных SIM-картах (разные производители)

## Ссылки на источники

- pySim Manual: [[wiki/summaries/osmopysim_usermanual]]
- TS 31.124: [[wiki/summaries/ts_31124]]
- TCA Stepping Stones: [[wiki/summaries/java_card_stepping_stones]]
- GP: [[wiki/concepts/GlobalPlatform_Card]]
- STK Applet: [[wiki/concepts/STK_Applet]]
