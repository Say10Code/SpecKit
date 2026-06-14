> **📦 АРХИВ** | 2026-06-14 | Исследовательский документ. Заменён на `_pipeline/` (speckit).

---
tags: [plan, integration, 3gpp-crawler, automation]
type: synthesis
created: 2026-06-12
updated: 2026-06-12
status: draft
sources:
  - "[[3gpp-crawler]]"
---

# 🔗 Как `3gpp-crawler` может усилить `ObsidianDB`

> **Анализ**: 2026-06-12 | **Источник**: https://forge.3gpp.org/rep/reimes/3gpp-crawler/

---

## Сначала — текущее состояние ObsidianDB

ObsidianDB — это **зрелая, структурированная база знаний** на 130+ страниц по UICC/SIM/JavaCard/eSIM/5G, с 7 sub-agents, 62 PDF-спецификациями, 100% reviewed. Но при этом есть **цепочка ручных операций**, которая сдерживает масштабирование:

```
Текущий процесс:
  🔍 Найти спецификацию вручную (3GPP portal, ETSI, GSMA...)
  📥 Скачать PDF вручную
  📂 Переместить в Specifications/!INCOMING/
  🤖 Librarian сортирует → Author пишет summary
  🤖 SpecExtractor: PyPDF2 → TXT (плоское, без структуры)
  🤖 Reviewer сверяет с TXT
```

---

## 🎯 5 ключевых точек интеграции

### 1. Автоматическая загрузка спецификаций (вместо ручного поиска)

**Проблема сейчас**: Ты вручную ищешь и скачиваешь спецификации. В Roadmap'е: SGP.22, SGP.32, ISO 7816-5, TS 35.206, TS 23.501, TS 24.229 — всё ждут «добыть PDF».

**Решение через 3gpp-crawler**:

```bash
# Автоматически найти и скачать ЛЮБУЮ спецификацию
spec-crawler checkout 23.501     # 5G Core
spec-crawler checkout 24.229     # SIP/IMS
spec-crawler checkout 35.206     # MILENAGE vectors
spec-crawler checkout 31.102     # USIM (обновлённая версия!)
```

**Выгода**: `!INCOMING` наполняется автоматически, не вручную. Librarian получает стабильный поток новых версий.

### 2. Docling-извлечение вместо PyPDF2 (ключевое улучшение SpecExtractor)

**Проблема сейчас**: `SpecExtractor` использует PyPDF2 — извлекает голый текст, теряя:
- Структуру таблиц (критично для EF-таблиц!)
- Иерархию разделов
- Изображения и диаграммы
- Позиционирование элементов на странице

**Решение**: Заменить PyPDF2 на пайплайн извлечения `3gpp-crawler`:

```bash
# Создать workspace для ObsidianDB
3gpp-crawler workspace create obsidiandb-specs
3gpp-crawler workspace activate obsidiandb-specs

# Добавить все ключевые спецификации
3gpp-crawler workspace add 31.102 31.101 22.101 --kind spec
3gpp-crawler workspace add 102.221 102.223 102.225 102.226 --kind spec

# Извлечь с Docling (структурированный .md + .json!)
3gpp-crawler workspace process --profile default
```

**Результат**: `~/.3gpp-crawler/wiki/obsidiandb-specs/sources/` содержит для каждой спецификации:
- `*.md` — структурированный Markdown с таблицами, заголовками, изображениями
- `*.json` — канонический JSON с координатами provenance (страница/параграф/таблица)

Сравнение качества:

| Аспект | PyPDF2 (сейчас) | Docling (через 3gpp-crawler) |
|--------|-----------------|------------------------------|
| Таблицы | Разрушены в строки | Сохранены как таблицы Markdown |
| EF-списки | Теряют FID, размер, тип | Сохранены структурно |
| Диаграммы | Потеряны | Извлечены как изображения |
| Provenance | Только страница | Страница + параграф + элемент |
| JSON | Нет | Полный канонический JSON |

### 3. Workspace'ы как исследовательские проекты

**Проблема сейчас**: Research-темы (auth evolution, MILENAGE vs TUAK, operator icons) требуют ручного подбора источников.

**Решение**: Workspace на каждую research-тему:

```bash
# Исследование аутентификации
3gpp-crawler workspace create auth-evolution
3gpp-crawler workspace activate auth-evolution
3gpp-crawler workspace add 33.102 33.401 33.501 35.206 --kind spec
3gpp-crawler workspace add --agenda "*AKA*"    # TDoc'и по AKA!
tdoc-crawler crawl -w SA -s S3                 # SA3 = security WG
3gpp-crawler workspace process --profile advanced --device cuda

# Исследование eSIM
3gpp-crawler workspace create esim-deep
3gpp-crawler workspace add 31.102 --release 19  # 5G USIM
3gpp-crawler workspace add --agenda "*eSIM* OR *RSP* OR *SGP*"
3gpp-crawler workspace process --profile default
```

**Выгода**: Researcher получает workspace с уже извлечёнными структурированными артефактами, а не начинает с нуля.

### 4. TDoc-поток: свежие документы рабочих групп

**Проблема сейчас**: В ObsidianDB нет TDoc'ов — временных документов рабочих групп. Это самые свежие обсуждения ещё до того, как они станут спецификациями.

**Решение**:

```bash
# Подписаться на рабочие группы по UICC/SIM тематике
tdoc-crawler crawl-meetings -s CP      # CT Plenary = UICC решения
tdoc-crawler crawl-meetings -s C6      # CT6 = Smart Card Application

# Регулярно обновлять
tdoc-crawler crawl --start-date 2024   # TDoc'и за последние 2 года

# Искать по темам
tdoc-crawler query --agenda "*USIM* OR *UICC*"
tdoc-crawler query --title "*Java*Card* AND *API*"
tdoc-crawler query --agenda "*eSIM*"
```

**Выгода**: ObsidianDB получает **поток актуальных обсуждений** — можно писать summaries по свежим TDoc'ам ещё до выхода спецификаций. Это то, что делает базу знаний **живой**.

### 5. Автоматизация пайплайна «загрузка → извлечение → wiki»

**Проблема сейчас**: 5 ручных шагов от PDF до wiki-страницы.

**Решение**: Единый пайплайн:

```bash
# ==========================================
# ObsidianDB Pipeline v2 (с 3gpp-crawler)
# ==========================================

# Шаг 1: Обновить метаданные встреч
tdoc-crawler crawl-meetings -s CP C6

# Шаг 2: Скачать свежие спецификации
spec-crawler crawl
spec-crawler checkout 31.102 102.221 102.223

# Шаг 3: Извлечь в workspace (→ .md + .json)
3gpp-crawler workspace process obsidiandb-specs --profile default

# Шаг 4: Скопировать артефакты в ObsidianDB
# .md → specs-extracted/ (замена TXT!)
# .json → для машинной обработки

# Шаг 5: Author создаёт/обновляет summary на основе структурированного .md
# (вместо плоского .txt!)
```

---

## 📊 Сравнительная таблица: до и после

| Измерение | ObsidianDB сейчас | ObsidianDB + 3gpp-crawler |
|-----------|-------------------|---------------------------|
| **Поиск спецификаций** | Ручной (portal → download) | `spec-crawler checkout <номер>` |
| **Версионирование** | Нет (имя файла) | Release-aware (REL17/18/19) |
| **Извлечение текста** | PyPDF2 (плоский TXT) | Docling (структурированный MD + JSON) |
| **Таблицы EF** | Разрушены, Reviewer правит вручную | Сохранены структурно |
| **TDoc'и** | Отсутствуют | Полный доступ через `tdoc-crawler` |
| **Research workspace** | Ручной подбор PDF | `workspace add` + `workspace process` |
| **Provenance** | `^[extracted]` без координат | Страница/параграф/элемент из JSON |
| **Инкрементальность** | Ручная проверка новых версий | `spec-crawler crawl` автообновление |
| **Изображения** | Потеряны | Извлечены (embed или reference) |

---

## 🗺️ План внедрения

### Фаза 1: Установка и верификация ✅ ВЫПОЛНЕНО

```bash
cd D:\!Projects\3gpp-crawler\3gpp-crawler
uv sync
uv run pytest -v                     # Убедиться, что всё работает
uv tool install .                    # Установить как CLI-инструмент
```

**Результат**: `spec-crawler` доступен глобально. Кэш: `D:\ObsidianDB\.3gpp-crawler\`.
**Агент создан**: `SpecDownloader` (`.claude/agents/specdownloader.md`).
**CLAUDE.md обновлён**: добавлена секция «Интеграция с 3gpp-crawler».

### Фаза 2: Замена SpecExtractor на Docling-пайплайн ⬜ (P0)

1. Создать workspace `obsidiandb-specs`
2. Добавить 5 ключевых спецификаций (TS 31.102, TS 102 221, TS 102 223, GSM 11.11, GPC 2.3.1)
3. `workspace process --profile default`
4. Сравнить качество `.md` вывода с текущими `.txt` из `specs-extracted/`
5. Если качество выше (а оно будет) — обновить SpecExtractor для использования `3gpp-crawler` workspace process вместо PyPDF2

### Фаза 3: Автоматическая загрузка недостающих спецификаций

Из Roadmap'а ObsidianDB — добыть:

- `spec-crawler checkout 35.206` — MILENAGE vectors
- `spec-crawler checkout 23.501` — 5G Core (расширить concept)
- `spec-crawler checkout 24.229` — SIP/IMS (расширить concept)

> **Примечание**: для SGP.22/SGP.32 `3gpp-crawler` не поможет (это GSMA, не 3GPP).

### Фаза 4: Интеграция TDoc-потока

1. `tdoc-crawler crawl-meetings -s C6` — CT6 WG (Smart Card Application)
2. `tdoc-crawler crawl --start-date 2024`
3. Запросы по темам (`--agenda`, `--title`) → новые summaries
4. Настроить периодическое обновление (cron / ручной запуск)

### Фаза 5: Research-автоматизация

Для каждой research-темы (Фаза 5 Roadmap'а):

```bash
3gpp-crawler workspace create <research-topic>
3gpp-crawler workspace add <specs> <tdocs>
3gpp-crawler workspace process --profile advanced
# → Researcher работает с готовыми структурированными артефактами
```

### Фаза 6: CI/CD для спецификаций

Скрипт `update_specs.py`:

```python
# Еженедельно: обновить метаданные → проверить новые версии → workspace process
# → скопировать в ObsidianDB specs-extracted/ → обновить INDEX.md
# → уведомить о новых версиях
```

---

## ⚠️ Что 3gpp-crawler НЕ решает

| Ограничение | Почему |
|-------------|--------|
| **GSMA SGP.22/SGP.32** | Это GSMA-спецификации, не 3GPP — crawler их не скачает |
| **ISO 7816** | ISO-спецификации не на 3GPP FTP |
| **GlobalPlatform** | GP-спецификации отдельный источник |
| **PDF → TXT обратная совместимость** | Docling выдаёт Markdown/JSON, не плоский TXT — нужно адаптировать Reviewer |
| **Требуется ETSI-аккаунт** | Для `crawl-meetings` и portal fallback |

---

## 🏁 Итог

**3gpp-crawler** закрывает самую трудоёмкую часть пайплайна ObsidianDB: **поиск → скачивание → извлечение структуры из PDF**. Он превращает месяцы ручного ворошения спецификаций в одну команду.

Ключевое преимущество: Docling-извлечение **на порядок качественнее** PyPDF2 для домена UICC/SIM — таблицы с FID/размерами/типами EF, структурные разделы, изображения диаграмм. Это напрямую улучшает качество summaries и снижает нагрузку на Reviewer (меньше ручных исправлений).

**Рекомендация**: начать с Фазы 1-2, сравнить качество извлечения на TS 31.102 и TS 102 221 — ты сразу увидишь разницу.

---

---
    
    ## 🔍 Техническая инспекция (Claude)
    
    ### Сильные стороны
    - **Болевая точка выбрана верно**: извлечение текста — действительно узкое место. PyPDF2 разрушает таблицы → Reviewer исправляет вручную → человеческий фактор (9 критических ошибок найдено именно так)
    - **Workspace-модель для research**: правильная абстракция, соответствует тому как Researcher уже работает (подбор N PDF → кросс-анализ)
    - **Чёткие границы применимости**: честно указано что GSMA/ISO/GP не решаются — это зрелый архитектурный подход
    
    ### Что требует уточнения
    
    #### 1. Влияние на Reviewer v2
    Самое серьёзное архитектурное последствие: если Docling выдаёт структурированный `.md` вместо плоского `.txt`, Reviewer должен **изменить свой алгоритм**. Сейчас он делает:
    ```
    Grep по TXT → Read контекст → сравнить с wiki
    ```
    Со структурированным `.json` (с координатами provenance) Reviewer мог бы:
    ```
    Запрос: EF_IMSI → JSON-поиск → точные координаты (секция/таблица/ряд) → сверка
    ```
    Это требует **адаптации Pass 1 Reviewer** — зато качество проверки вырастет на порядок.
    
    #### 2. Конфликт форматов `specs-extracted/`
    Сейчас там 63 `.txt` файла. При переходе на Docling там появятся `.md` и `.json`. Нужно:
    - Либо сосуществование (старые TXT + новые MD/JSON)
    - Либо миграция всех 63 файлов через Docling
    - Обновить `INDEX.md` (сейчас он ссылается на `.txt`)
    
    #### 3. Зависимость от внешнего инструмента
    `3gpp-crawler` — отдельный проект, не в репозитории ObsidianDB. Если он сломается или изменит API — пайплайн встанет. Рекомендации:
    - Зафиксировать версию (`uv lock`)
    - Добавить fallback на старый PyPDF2 если Docling недоступен
    - Держать скрипты интеграции в `_tech/scripts/` а не в самом ObsidianDB
    
    #### 4. Приоритет внедрения
    Предложенные 6 фаз линейны. Предлагаю переупорядочить по импакту:
    
    | Фаза | Импакт | Усилие | Приоритет |
    |---|---|---|---|
    | Фаза 2 (Docling вместо PyPDF2) | 🔴 Критический | Среднее | **P0** |
    | Фаза 3 (добыть недостающие PDF) | 🟡 Высокий | Низкое | **P1** |
    | Фаза 5 (Research workspace) | 🟢 Средний | Среднее | **P2** |
    | Фаза 4 (TDoc-поток) | 🟢 Средний | Высокое | **P3** |
    | Фаза 6 (CI/CD) | 🔵 Низкий | Высокое | **P4** |
    
    Фаза 2 должна идти первой потому что она **меняет качество фундамента** (эталонные тексты), а не просто автоматизирует существующий процесс.
    
    #### 5. Не упомянута интеграция с `!INCOMING`
    3gpp-crawler может автоматически наполнять `!INCOMING/` новыми версиями спецификаций. Это замыкает петлю автообновления:
    ```
    3gpp-crawler checkout 31.102  →  Specifications/!INCOMING/ts_131102vXXX.pdf
                                    →  Librarian сортирует
                                    →  Author создаёт/обновляет summary
    ```
    
    ### Рекомендация
    Начать с **пилота на 3 спецификациях** (TS 31.102, TS 102 221, TS 102 223):
    1. Извлечь через Docling
    2. Сравнить `.md` вывод с текущими `.txt`
    3. Прогнать Reviewer v2 на одной и той же wiki-странице → сравнить количество найденных ошибок
    4. Если Docling находит больше структурных несоответствий (таблицы EF, FID, размеры) — принимать решение о миграции
    
    *Инспекция добавлена 2026-06-12.*
