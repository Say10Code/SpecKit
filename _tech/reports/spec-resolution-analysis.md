# Spec Resolution — анализ и решение

> **Создан**: 2026-06-14 · **Вопрос**: как агент понимает какую спецификацию искать по запросу?

---

## 1. Диагноз

### Сценарий

Пользователь: «Основные проблемы ошибок регистрации 5G NR NSA»

Для ответа нужны спецификации:
- **TS 38.300** — NR overall description (RRC states, registration area)
- **TS 38.331** — RRC (connection setup, reconfiguration, error handling)
- **TS 37.340** — EN-DC (NSA architecture, secondary node addition)
- **TS 24.501** — NAS protocol (registration procedure, reject causes)
- **TS 23.502** — 5G Core procedures (UE registration, authentication)

### Что происходит сейчас

```
Агент получает запрос "5G NR NSA registration problems"
  │
  ├─[1] Смотрит .category-map.md
  │     ├─ 23.xxx → "5G Core"   ✅ попадание (частично)
  │     ├─ 38.xxx → "NR/RAN"    ✅ попадание
  │     └─ 24.xxx → "SIP/IMS"   ❌ промах (TS 24.501 — NAS, не SIP!)
  │
  ├─[2] Смотрит wiki/
  │     └─ Ищет concepts по ключевым словам
  │
  ├─[3] WebSearch ← ПОШЁЛ В ИНТЕРНЕТ
  │     └─ Нашёл бы те же номера спецификаций, но без provenance
  │
  └─[4] Что упущено:
        ❌ Не знает что TS 24.501 = NAS, а не SIP
        ❌ Не знает что TS 37.340 = EN-DC
        ❌ Не знает что TS 38.331 = RRC
        ❌ Не знает что такое NSA с точки зрения спецификаций
```

### Корень проблемы

`.category-map.md` создавался для **Librarian** (сортировка скачанных файлов), а не для **Researcher** (поиск спецификаций по теме). В нём 15 серий — только те, что мы уже скачали. Для любого нового запроса он бесполезен.

**Между запросом пользователя и номером спецификации — пропасть.** Её заполняет только опыт AI-модели (training data) или WebSearch. Но WebSearch лишает нас provenance.

---

## 2. Что есть сейчас

| Инструмент | Охват | Для чего | Ограничение |
|---|---|---|---|
| `.category-map.md` (62 строки) | 15 серий | Librarian: куда класть | Только скачанные |
| `.speckit/metadata.db` | 1 spec (31.102) | _pipeline: URL/версии | Только запрошенные |
| `specs-extracted/INDEX.md` | Извлечённые | Reviewer: форматы | Только обработанные |
| WhatTheSpec API | Все 3GPP | _pipeline: resolve | Вызывается per-spec |
| WebSearch | Весь интернет | Researcher: найти | Нет provenance |

**Пропасть**: нет файла, который агент может прочитать и сказать: «5G NR NSA registration → TS 38.300, TS 38.331, TS 37.340, TS 24.501».

---

## 3. Структура нумерации 3GPP

3GPP использует фиксированную систему серий. Каждая серия имеет свою тему. Знание этой системы — ключ к resolution:

| Серия | Тема | Ключевые спецификации |
|---|---|---|
| **21.xxx** | Requirements | 21.905 (vocabulary) |
| **22.xxx** | Service aspects | 22.011 (service accessibility), 22.101 (service principles) |
| **23.xxx** | 5G Core architecture | 23.501 (5GS), 23.502 (procedures), 23.503 (policy) |
| **24.xxx** | NAS + SIP/IMS | 24.501 (NAS), 24.301 (EPC NAS), 24.229 (SIP) |
| **25.xxx** | UTRAN (3G RAN) | 25.331 (RRC 3G) |
| **31.xxx** | UICC/SIM/USIM | 31.101, 31.102, 31.111 |
| **33.xxx** | Security | 33.401 (EPS AKA), 33.501 (5G AKA) |
| **36.xxx** | LTE/E-UTRAN | 36.300 (LTE overview), 36.331 (LTE RRC) |
| **37.xxx** | Multi-RAT | 37.340 (EN-DC) |
| **38.xxx** | NR/5G RAN | 38.300 (NR overview), 38.331 (NR RRC), 38.304 (idle) |
| ... | ... | ~200 серий всего |

**Важно**: серии не всегда интуитивны. Например:
- 24 серия = «SIP/IMS» в `.category-map.md`, но реально TS 24.501 — NAS, а не SIP
- 37 серия вообще не упомянута в `.category-map.md`, хотя TS 37.340 — критичен для NSA

---

## 4. Решение

### 4.1 Новый файл: `Specifications/.spec-registry.md`

**Назначение**: единый реестр спецификаций 3GPP/ETSI — маппинг «тема → серия → конкретные номера».

**Отличие от `.category-map.md`**:

| | `.category-map.md` | `.spec-registry.md` |
|---|---|---|
| **Для кого** | Librarian | Researcher, SpecDownloader |
| **Вопрос** | Куда положить? | Какую качать? |
| **Охват** | Только скачанные | Все relevant серии |
| **Гранулярность** | Серия → директория | Тема → серия → ключевые номера |
| **Обновляется** | При добавлении новой серии | Редко (структура 3GPP стабильна) |

### 4.2 Структура .spec-registry.md

```markdown
# Spec Registry — полный реестр спецификаций

> **Назначение**: ЕДИНСТВЕННЫЙ source of truth для маппинга «тема → номер спецификации».
> **Используется**: Researcher, SpecDownloader
> **Правило**: перед любым research'ем — проверь реестр.

## 5G / NR

### 5G System Architecture
| Номер | Название | Ключевая тема |
|---|---|---|
| TS 23.501 | System architecture for the 5GS | AMF, SMF, UPF, NFs |
| TS 23.502 | Procedures for the 5GS | Registration, PDU session, handover |
| TS 23.503 | Policy and charging control framework | PCC rules |

### NR RAN
| Номер | Название | Ключевая тема |
|---|---|---|
| TS 38.300 | NR Overall description | RRC states, architecture |
| TS 38.331 | NR RRC | Connection setup, reconfig, failure |
| TS 38.304 | NR Idle/Inactive | Cell selection, paging |
| TS 38.321 | NR MAC | Scheduling, HARQ, random access |

### Multi-RAT / NSA
| Номер | Название | Ключевая тема |
|---|---|---|
| TS 37.340 | EN-DC | NSA architecture, SgNB, SCG failure |
...
```

### 4.3 Алгоритм Researcher'а (обновлённый)

```
Researcher: получил запрос «5G NR NSA registration problems»

1. ИЗВЛЕКИ ключевые термины:
   → «NR», «NSA», «registration», «problems»
   → Домен: 5G radio access (38-я серия) + core (23-я) + multi-RAT (37-я)

2. ПРОЧИТАЙ Specifications/.spec-registry.md
   → Найди секции по домену: «5G / NR», «Multi-RAT / NSA»
   → Получи список релевантных спецификаций:
       TS 38.300, TS 38.331, TS 37.340, TS 24.501, TS 23.502

3. ПРОВЕРЬ наличие:
   ├─ Есть в specs-extracted/ → готово для Grep/Read
   ├─ Есть в Specifications/ (PDF/DOCX) → SpecExtractor: извлеки
   └─ Нет → SpecDownloader: python -m _pipeline download <номер>

4. ПРОВЕРЬ wiki/ — summaries, concepts, syntheses по номерам спецификаций

5. ТОЛЬКО ЕСЛИ спецификация отсутствует в .spec-registry.md (GSMA, ISO):
   → WebSearch
```

### 4.4 Пополнение реестра

Скрипт `_pipeline/spec_registry.py`:
- Читает `.spec-registry.md`
- Для каждого номера обращается к WhatTheSpec API
- Дополняет названием и описанием
- Выводит diff — что добавилось

Команда: `python -m _pipeline registry update`

---

## 5. Сравнение: до и после

### До (сейчас)

```
Пользователь: "5G NR NSA registration problems"
Агент: WebSearch("5G NR NSA registration 3GPP")
      → находит TS 38.300, TS 38.331...
      → ⚠️ Нет provenance — Reviewer не сможет верифицировать
      → ⚠️ Может пропустить TS 37.340 (NSA — неочевидно)
      → ⚠️ Может найти устаревшую версию
```

### После (.spec-registry.md)

```
Пользователь: "5G NR NSA registration problems"
Агент: Read Specifications/.spec-registry.md
      → «5G/NR» → TS 38.300, 38.331
      → «Multi-RAT/NSA» → TS 37.340
      → «NAS» → TS 24.501
      → «5G Core Procedures» → TS 23.502
      → Проверка specs-extracted/: TS 38.300 — нет
      → python -m _pipeline download 38.300 37.340 24.501
      → SpecExtractor: извлечь
      → ✅ Provenance: все утверждения из спецификаций
      → ✅ Полнота: ни одна спецификация не пропущена
```

---

## 6. Реализация

### Фаза 1: Создать .spec-registry.md

- Охватить все серии 3GPP, relevant для домена проекта
- Формат: тема → серия → таблица с номерами, названиями, ключевыми темами
- ~200-300 строк

### Фаза 2: Обновить Researcher agent

- Добавить шаг 0: «Прочитай .spec-registry.md»
- Приоритет: registry → specs-extracted → download → wiki → WebSearch

### Фаза 3: Скрипт пополнения

- `python -m _pipeline registry update` — дополняет названия из WhatTheSpec API
- В будущем: `python -m _pipeline registry suggest "NR NSA"` — AI-поиск по темам

---

*Анализ создан 2026-06-14. Требует утверждения перед реализацией.*
