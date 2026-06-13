---
tags: [synthesis, security, side-channel, CPA, DPA, STK, JavaCard]
type: synthesis
created: 2026-06-10
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/summaries/outsmarting_smart_cards|Outsmarting Smart Cards]]"
  - "[[wiki/summaries/java_card_stepping_stones|TCA Stepping Stones §7]]"
  - "[[wiki/concepts/UICC_Security]]"
  - "[[wiki/summaries/ruimtools_javacard_guidelines|RuimTools Guidelines]]"
  - "[[wiki/concepts/SCP]]"
---

# UICC Smart Card Security Landscape: угрозы, атаки и защита

> **Synthesis** — полный обзор угроз для смарт-карт UICC/SIM и методов защиты, от физических атак до логических уязвимостей STK.

---

## 1. Карта угроз

```
                ┌─────────────────────────────────┐
                │     УГРОЗЫ СМАРТ-КАРТ           │
                └───────────┬─────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Физические   │   │ Side-Channel │   │ Логические   │
│ атаки        │   │ атаки        │   │ атаки        │
├──────────────┤   ├──────────────┤   ├──────────────┤
│• Microprobing│   │• SPA (Simple │   │• STK MITM    │
│• FIB         │   │  Power)      │   │• False BTS   │
│• Decapsulation│  │• DPA (Diff.) │   │• Replay      │
│• Reverse Eng.│   │• Timing      │   │• Fuzzing     │
│• Glitching   │   │• EM analysis │   │• Logical flaw │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 2. Side-Channel атаки (из Outsmarting Smart Cards)

### SPA/DPA (Simple/Differential Power Analysis)

```
Принцип:
┌──────────┐         ┌──────────────┐
│ Смарт-   │────────→│ Осциллограф  │──→ Профиль мощности
│ карта    │  I(t)   │ (потребление)│    за N выполнений
└──────────┘         └──────────────┘
                              │
                     Статистический анализ
                     (корреляция, t-test)
                              │
                     ▼
              Извлечение ключа 🔑
```

**Уязвимые операции**: DES/3DES/AES (S-box lookup), RSA (modular exponentiation), COMP128.

**Защита**: маскировка (masking), случайные задержки, dual-rail logic, constant-time алгоритмы.

### Timing Attacks

Измерение времени выполнения → корреляция с секретными данными.

**Защита**: constant-time реализации, отсутствие conditional branches в crypto.

### EM Analysis

Электромагнитное излучение чипа коррелирует с операциями.

**Защита**: EM shielding, balanced layout, noise injection.

## 3. Физические атаки

| Атака | Описание | Защита |
|---|---|---|
| **Microprobing** | Иглы на шины чипа | Active shield, glue logic |
| **FIB** (Focused Ion Beam) | Изменение проводников | Active shield, sensors |
| **Decapsulation** | Химическое вскрытие корпуса | Tamper-proof coating |
| **Glitching** | Сбой питания/тактовой частоты | Voltage/temp/freq sensors |
| **Reverse Engineering** | Снятие слоёв чипа | Scrambled layout, dummy structures |

> [!info] Ключевая идея
> eUICC для eSIM сертифицируется по **Common Criteria EAL4+**, что включает защиту от всех перечисленных физических атак. Это значительно дороже чем защита обычной UICC.

## 4. Логические атаки через STK (из Sjors Gielen)

### MITM на SIM↔ME

```
Телефон ←── TurboSIM ──→ SIM-карта
              │
         Изменение трафика:
         • Подмена DISPLAY TEXT
         • Перехват SMS
         • Блокировка вызовов
         • Подмена LOCI
```

### Конкретные атаки

| Атака | STK-механизм | Риск | Реализуемость |
|---|---|---|---|
| **DoS** | DISPLAY TEXT в цикле (high prio + wait) | Блокировка экрана | TurboSIM / вредоносный апплет |
| **Слежка** | PROVIDE LOCAL INFO + SEND SMS | Отслеживание местоположения | TurboSIM / вредоносный апплет |
| **MITM звонков** | Call Control → reroute | Перехват разговоров | TurboSIM |
| **Кража денег** | SEND SHORT MESSAGE в цикле | Опустошение счёта | TurboSIM / вредоносный апплет |
| **Перехват 2FA** | Event MT + SEND SMS forward | Обход двухфакторной аутентификации | TurboSIM |

### Защита от MITM

- **PIN-верификация** перед выполнением критических STK-команд
- **Signed SIM Toolkit commands** (TS 102 225 security)
- **Ограничение прав апплетов** (Access Domain в Install Parameters)
- **Аудит установленных апплетов** (GET STATUS)

## 5. Лучшие практики безопасности (TCA Stepping Stones §7)

### Для всех апплетов

- ✅ Изолировать crypto-операции в отдельный класс
- ✅ Использовать native crypto API (не самодельное!)
- ✅ Fixed-size PIN (предотвращает timing attacks)
- ✅ Проверять RSA подписи перед отправкой (anti-DFA)
- ✅ Минимизировать EEPROM-записи (side-channel поверхности)

### Для чувствительных апплетов (банкинг, аутентификация)

- ✅ Дополнительная верификация через `VERIFY PIN` перед каждой операцией
- ✅ Логирование попыток (EF с счётчиком)
- ✅ Блокировка после N неудачных попыток
- ✅ Secure Messaging для всех критических APDU
- ✅ Common Criteria сертификация (EAL4+)

## 6. Модель нарушителя

| Нарушитель | Возможности | Инструменты | Цель |
|---|---|---|---|
| **Remote attacker** | Только OTA (SMS-PP) | SDR, SS7 | Массовая атака |
| **Local attacker** | Физический доступ к телефону | TurboSIM, кард-ридер | Конкретная жертва |
| **Malicious applet** | Выполняется на карте | STK API | Другие апплеты / телефон |
| **Lab attacker** | Полный доступ, бюджет | Electron microscope, FIB | Клонирование / reverse engineering |
| **Nation-state** | Неограниченные ресурсы | Всё выше + 0-day exploits | Массовый перехват |

---

## 7. Эволюция защиты по поколениям

| | GSM | UMTS | LTE | 5G |
|---|---|---|---|---|
| **Аутентификация** | COMP128 (broken) | MILENAGE | MILENAGE + KDF | 5G AKA + SUCI |
| **Шифрование** | A5/1 (broken) | UEA1/UEA2 | AES/SNOW/ZUC | AES-256 |
| **Integrity** | ❌ | ✅ UIA | ✅ NAS+RRC | ✅ NAS+RRC |
| **IMSI protection** | ❌ | ❌ | ❌ | ✅ SUCI |
| **Side-channel HW** | Минимальная | Базовая | Улучшенная | EAL4+ для eUICC |
| **Secure Channel** | Нет | SCP02 | SCP03 | SCP03/SCP11 |

---

## 8. Рекомендации для разработчика

| Слой | Рекомендация |
|---|---|
| **Код апплета** | Constant-time операции, native crypto, no secrets in RAM дольше необходимого |
| **APDU-интерфейс** | Проверять CLA, INS, P1, P2. Не доверять входным данным. |
| **STK** | PIN перед критическими proactive commands, Access Domain = минимальный |
| **Память** | Ключи только в EEPROM (не в transient). Очищать APDU buffer после crypto. |
| **Сборка** | Verifier + off-card проверка, минимизация CAP размера |
| **Тестирование** | TCA Loader, pySim-trace, fuzzing, interoperability testing |

## Ссылки на источники

- Outsmarting Smart Cards: [[wiki/summaries/outsmarting_smart_cards|PhD Thesis, 2013]]
- TCA Security: [[wiki/summaries/java_card_stepping_stones|JC Stepping Stones §7]]
- RuimTools Security: [[wiki/summaries/ruimtools_javacard_guidelines|JC Best Practices]]
- UICC Security: [[wiki/concepts/UICC_Security]]
- SCP: [[wiki/concepts/SCP]]
- Sjors Gielen MITM: [[wiki/summaries/sjors_gielen_stk|SIM Toolkit in Practice]]
