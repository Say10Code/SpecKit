---
tags: [synthesis, STK, sim-toolkit, uicc-toolkit, JavaCard, migration]
type: synthesis
created: 2026-06-10
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/concepts/STK_Applet]]"
  - "[[wiki/concepts/CAT_STK]]"
  - "[[wiki/summaries/ts_102241|TS 102 241 — UICC API]]"
  - "[[wiki/summaries/ts_143019|TS 143 019 — SIM API]]"
  - "[[wiki/summaries/ts_131130|TS 131 130 — (U)SIM API]]"
---

# Сравнение sim.toolkit vs uicc.toolkit: Миграция 2G → 5G

> **Synthesis** — практическое руководство по миграции STK-апплетов с GSM SIM на современные UICC.

---

## 1. Два поколения API

```
2G (GSM):                    3G/4G/5G (UICC):
═══════════                  ════════════════
sim.toolkit                  uicc.toolkit
sim.access                   uicc.access
─                            uicc.usim.access  (NEW!)
SIM API (TS 143 019)         UICC API (TS 102 241)
                             (U)SIM API (TS 131 130)
```

## 2. Сравнение импортов

| | `sim.toolkit` | `uicc.toolkit` |
|---|---|---|
| **Import** | `import sim.toolkit.*;` | `import uicc.toolkit.*;` |
| **Файловый доступ** | `import sim.access.*;` | `import uicc.access.*;` |
| **USIM-доступ** | ❌ | `import uicc.usim.access.*;` |
| **build.xml import JAR** | `sim.jar` | `uicc.jar` |
| **Пакет AID** | `A0 00 00 00 76 01 01` | `A0 00 00 00 76 02 01` |
| **Спецификация** | TS 143 019, TS 101 476 | TS 102 241, TS 131 130 |

## 3. Сравнение ключевых классов

| Класс | `sim.toolkit` | `uicc.toolkit` | Изменения |
|---|---|---|---|
| **ProactiveHandler** | ✅ | ✅ | Идентичен |
| **ProactiveResponseHandler** | ✅ | ✅ | Идентичен |
| **ToolkitRegistry** | ✅ | ✅ | + eCAT, + SEID |
| **ToolkitConstants** | ✅ | ✅ | + новые константы |
| **ToolkitInterface** | ✅ | ✅ | Идентичен |
| **ViewHandler** | `sim.access` | `uicc.access` | + USIM-методы |
| **FileView** | `sim.access` | `uicc.access.usim` | + ADF.USIM |

## 4. Функциональные различия

| Возможность | `sim.toolkit` | `uicc.toolkit` |
|---|---|---|
| **Логические каналы** | 0 | 0–19 |
| **Multi-verification** | ❌ | ✅ (Universal PIN) |
| **SEID (Security Environment)** | ❌ | ✅ |
| **eCAT (extended CAT)** | ❌ | ✅ |
| **Contactless events** | ❌ | ✅ (HCI) |
| **BIP/channels** | Базовый | Расширенный |
| **Proactive commands** | ~20 | ~40+ |
| **USIM файлы** | ❌ | ✅ |
| **5G NAS контекст** | ❌ | ✅ |
| **Envelope Container** | ❌ | ✅ |
| **LSI Command** | ❌ | ✅ |
| **SUCI API** | ❌ | ✅ |

## 5. Миграция: пошаговый план

### Шаг 1: Заменить импорты

```java
// Было (2G):
import sim.toolkit.*;
import sim.access.*;

// Стало (3G+):
import uicc.toolkit.*;
import uicc.access.*;
```

### Шаг 2: Заменить JAR в build.xml

```xml
<!-- Было (2G): -->
<import exps="exp" jar="lib/sim.jar"/>

<!-- Стало (3G+): -->
<import exps="exp" jar="lib/uicc.jar"/>
```

### Шаг 3: Обновить Install Parameters

```diff
- CA tag: sim.toolkit параметры
+ CA tag: uicc.toolkit параметры (могут быть шире)
```

### Шаг 4: Добавить поддержку логических каналов (если нужно)

```java
// uicc.toolkit поддерживает каналы 0-19
// Если апплет должен работать на канале >0:
// Ничего специально делать не нужно — JCRE управляет
```

### Шаг 5: Использовать новые API где полезно

```java
// uicc.usim.access — прямой доступ к USIM-файлам
USIMFileView usimView = ...;
// sim.access такого не имел
```

## 6. Обратная совместимость

> [!tip] Практический совет
> Большинство карт с `uicc.toolkit` **обратно совместимы** с `sim.toolkit` на уровне APDU. Но новые карты (5G, eUICC) могут **не поддерживать** `sim.toolkit`. Для новых проектов всегда используйте `uicc.toolkit`.

## 7. Сравнительная таблица Install Parameters

| Параметр | `sim.toolkit` (CA) | `uicc.toolkit` (CA или TA) |
|---|---|---|
| **Access Domain** | 1 байт | 1 байт |
| **Priority** | 1 байт | 1 байт |
| **Max Timers** | 1 байт | 1 байт |
| **Max Menu Text Length** | 1 байт | 2 байта (до 255) |
| **Max Menu Entries** | 1 байт | 1 байт |
| **TAR** | 3 байта | 3×N байт (несколько TAR) |
| **MSL** | опционально | опционально |
| **SEID** | ❌ | ✅ |

## 8. Когда мигрировать обязательно

| Ситуация | Действие |
|---|---|
| Новый проект (2024+) | Всегда `uicc.toolkit` |
| 5G-специфичные функции | Только `uicc.toolkit` |
| eUICC / Consumer eSIM | Только `uicc.toolkit` |
| Старый апплет на GSM SIM | Оставить `sim.toolkit` |
| Апплет на USIM 3G/4G карте | Мигрировать на `uicc.toolkit` |
| Multi-operator / Multi-SIM | `uicc.toolkit` + SEID |

## Ссылки на источники

- UICC API: [[wiki/summaries/ts_102241|TS 102 241]]
- SIM API (legacy): [[wiki/summaries/ts_143019|TS 143 019]]
- (U)SIM API: [[wiki/summaries/ts_131130|TS 131 130]]
- STK Applet: [[wiki/concepts/STK_Applet]]
