> **📦 АРХИВ** | 2026-06-14 | Все шаги выполнены. Заменён на `_pipeline/` (speckit).

# 3gpp-crawler Build & Integration Plan

> **Дата**: 2026-06-12
> **Исходники**: `D:\ObsidianDB\3gpp-crawler\` (локально в корне проекта)
> **Цель**: Встроить 3gpp-crawler как встроенный инструмент ObsidianDB с кэшем внутри проекта и нулевой авторизацией.

---

## 1. Анализ исходного кода (результаты)

### 1.1 Три точки входа (pyproject.toml)

```toml
[project.scripts]
tdoc-crawler = "tdoc_crawler.cli.tdoc_app:tdoc_app"
spec-crawler = "tdoc_crawler.cli.spec_app:spec_app"
3gpp-crawler = "tdoc_crawler.cli.mgmt_app:mgmt_app"
```

| CLI | Назначение |
|---|---|
| `spec-crawler` | Specifications: crawl (метаданные), query, checkout (скачать PDF), open |
| `tdoc-crawler` | TDoc'и: crawl, query, checkout, workspace create/process |
| `3gpp-crawler` | Управление БД, конфигурация, workspace lifecycle |

### 1.2 Критические архитектурные детали

#### Config Discovery (mise-style)
3gpp-crawler автоматически сканирует рабочую директорию в поисках конфигурационных файлов. **Высший приоритет** у проекта — `3gpp-crawler.toml` в корне CWD.

Precedence (низший → высший):
```
~/.config/3gpp-crawler/config.toml          (глобальный)
~/.config/3gpp-crawler/conf.d/*.toml
.config/.3gpp-crawler/conf.d/*.toml         (проектный, низ)
.config/.3gpp-crawler/config.toml
.config/3gpp-crawler.toml
.3gpp-crawler/config.toml
.3gpp-crawler.toml
3gpp-crawler.toml                            (проектный, ВЫСШИЙ)
```

**Вывод**: разместив `3gpp-crawler.toml` в `D:\ObsidianDB\`, мы переопределим `cache_dir` без использования env vars.

#### PathConfig — где живут кэш и БД
```python
class PathConfig(BaseSettings):
    cache_dir: Path = "~/.3gpp-crawler"         # ← переопределяем через TOML
    db_filename: str = "3gpp_crawler.db"
    checkout_dirname: str = "checkout"

    @property
    def db_file(self) -> Path:
        return self.cache_dir / "3gpp_crawler.db"

    @property
    def http_cache_file(self) -> Path:
        return self.cache_dir / "http-cache.sqlite3"

    @property
    def checkout_dir(self) -> Path:
        return self.cache_dir / "checkout"
```

**Вывод**: `cache_dir` — это корень всего. Установим в `D:\ObsidianDB\.3gpp-crawler\`.

#### SpecDownloads — как качаются спецификации
```python
# spec-crawler checkout 31.102 → SpecDownloads.checkout_specs()
# 1. Resolve URL: WhatTheSpec API (публичный JSON) + 3GPP dynareport
# 2. Если метаданных нет в БД → auto-crawl sources (fetch_threegpp_metadata + fetch_whatthespec_metadata)
# 3. Download zip с 3GPP FTP → извлечь → целевая директория
```

**Важно**: первичный `spec-crawler crawl` нужен для наполнения БД метаданными. После этого `checkout` работает быстро (берёт URL из БД).

#### Extraction Profiles (workspace process)
```
pdf-only        → Raw PDF, no extraction
markdown-only   → pymupdf4llm, layout-aware .md, no ML
default         → Docling: structured .md + .json (ТО ЧТО НАМ НУЖНО)
advanced        → Docling + picture descriptions, code/formula enrichment
```

#### Python ≥ 3.13
3gpp-crawler **требует Python 3.13+**. Нужно проверить что он доступен.

### 1.3 Что уже сделано в ObsidianDB

| Компонент | Статус |
|---|---|
| CLAUDE.md: секция «Интеграция с 3gpp-crawler» | ✅ Есть |
| Agent: SpecDownloader (`.claude/agents/specdownloader.md`) | ✅ Создан |
| `.3gpp-crawler/` директория | ❌ Не существует |
| `.gitignore` | ❌ Не существует |
| `3gpp-crawler.toml` (проектный конфиг) | ❌ Не существует |
| `spec-crawler` CLI глобально | ❓ Требует `uv tool install` |

---

## 2. План реализации

### Шаг 1: Проверка окружения

**Что**: Убедиться что Python 3.13 доступен, установить 3gpp-crawler.

```bash
python --version                                        # Должен быть ≥ 3.13
cd D:\ObsidianDB\3gpp-crawler
uv sync                                                  # Установить зависимости
uv run spec-crawler --help                               # Проверить что CLI работает
uv tool install .                                        # Глобальная установка
```

**Валидация**: `spec-crawler --help` выводит список команд (crawl, query, checkout, open).

---

### Шаг 2: Проектный конфиг `3gpp-crawler.toml`

**Что**: Создать `D:\ObsidianDB\3gpp-crawler.toml` — конфиг, который 3gpp-crawler обнаружит автоматически при запуске из `D:\ObsidianDB`.

```toml
# 3gpp-crawler project config for ObsidianDB
# Auto-discovered: highest project-level precedence (mise-style)

[path]
cache_dir = "D:\\ObsidianDB\\.3gpp-crawler"

[http]
cache_enabled = true
cache_ttl = 7200          # 2 часа

[workspace]
profile = "default"        # Docling structured extraction
figures = "reference"      # Изображения отдельными файлами
tables = "embed"           # Таблицы в markdown
device = "auto"            # Авто-детект GPU
```

**Валидация**: `cd D:\ObsidianDB && spec-crawler crawl` создаст `.3gpp-crawler\3gpp_crawler.db`.

---

### Шаг 3: `.gitignore`

**Что**: Добавить `.gitignore` в корень `D:\ObsidianDB\.gitignore`.

```gitignore
# 3gpp-crawler cache (generated, large)
.3gpp-crawler/

# Obsidian workspace
.obsidian/workspace.json
.trash/

# Session data
.claudian/sessions/

# Python bytecode and venv
__pycache__/
*.pyc
.venv/
```

---

### Шаг 4: Первичное наполнение БД метаданными

**Что**: Запустить `spec-crawler crawl` для наполнения SQLite-БД метаданными ВСЕХ спецификаций 3GPP.

```bash
cd D:\ObsidianDB
spec-crawler crawl
```

Это займёт некоторое время (~5-10 минут для полного каталога). Скачиваются только метаданные (без PDF). Результат: `3gpp_crawler.db` ~50-100 MB.

**Валидация**: `spec-crawler query 31.102` выводит метаданные USIM.

---

### Шаг 5: Тестовое скачивание спецификации

**Что**: Скачать одну спецификацию напрямую в `!INCOMING/`.

```bash
cd D:\ObsidianDB
spec-crawler checkout 31.102 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"
```

**Ожидаемый результат**: ZIP-файл TS 31.102 извлечён в `!INCOMING/Specs/archive/31_series/31.102/`.

**Валидация**: `Get-ChildItem "D:\ObsidianDB\Specifications\!INCOMING"` показывает скачанный файл.

---

### Шаг 6: Обновление SpecDownloader Agent

**Что**: Актуализировать `.claude/agents/specdownloader.md` с точными командами.

Ключевые изменения в агенте:
- Добавить Шаг 0.5: проверка что CWD = `D:\ObsidianDB` (чтобы config discovery сработал)
- Уточнить формат `--checkout-dir` (полный путь в кавычках)
- Добавить пост-проверку: перечислить что скачалось
- Добавить `--release` примеры с актуальными версиями

---

### Шаг 7: Интеграционное тестирование полного пайплайна

**Сценарий**: `spec-crawler checkout 35.206` (MILENAGE test vectors — недостающая спецификация из Roadmap)

1. `spec-crawler checkout 35.206 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"`
2. PDF появляется в `!INCOMING/`
3. Librarian сортирует → `ETSI_3GPP/Security/`
4. `/ingest` → Author создаёт summary
5. `/lint` → проверка
6. SpecExtractor: PDF → TXT в `specs-extracted/`
7. Reviewer: сверка нового summary с TXT

---

### Шаг 8 (опционально): Docling-извлечение через workspace

**Что**: Заменить PyPDF2 на Docling для извлечения текста.

```bash
cd D:\ObsidianDB

# Создать workspace для ключевых спецификаций
3gpp-crawler workspace create obsidiandb-specs

# Добавить спецификации
3gpp-crawler workspace add 31.102 --kind spec --release 18
3gpp-crawler workspace add 102.221 --kind spec
3gpp-crawler workspace add 102.223 --kind spec

# Извлечь (Docling → structured .md + .json)
3gpp-crawler workspace process obsidiandb-specs --profile default --device auto
```

Результат в `.3gpp-crawler/workspaces/obsidiandb-specs/sources/`:
- `31.102-REL18/31.102-REL18.md` — структурированный Markdown (таблицы, заголовки)
- `31.102-REL18/31.102-REL18.json` — provenance-координаты (секция/таблица/строка)

Скопировать `.md` → `specs-extracted/` вместо `.txt`. Reviewer получает таблицы вместо разрушенных строк.

**Отложить** до результатов пилота на 3 спецификациях.

---

## 3. Финальная архитектура

```
D:\ObsidianDB\
├── 3gpp-crawler.toml                ← Конфиг (авто-обнаружение)
├── .gitignore                       ← Исключает .3gpp-crawler/
├── .3gpp-crawler/                   ← Кэш и БД (в .gitignore)
│   ├── 3gpp_crawler.db             ← Метаданные ВСЕХ спецификаций 3GPP
│   ├── http-cache.sqlite3          ← HTTP-кэш (экономит трафик)
│   ├── checkout/                    ← Стандартный checkout (не используется)
│   └── workspaces/                  ← Docling workspace artifacts
├── 3gpp-crawler/                    ← Исходники (локальная копия)
└── Specifications/!INCOMING/          ← Цель для spec-crawler checkout
```

### Поток скачивания спецификации

```
spec-crawler checkout 31.102 --checkout-dir "...\!INCOMING"
        │
        ├── 1. Ищет метаданные в .3gpp-crawler/3gpp_crawler.db
        │      └── Нет? → auto-crawl (WhatTheSpec + 3GPP FTP) → БД
        │
        ├── 2. Резолвит URL: 3GPP FTP (публичный, без авторизации)
        │      https://www.3gpp.org/ftp/Specs/archive/31_series/31.102/...
        │
        ├── 3. Скачивает ZIP (использует http-cache.sqlite3)
        │      └── Повторный checkout мгновенный из кэша
        │
        └── 4. Извлекает в !INCOMING/Specs/archive/31_series/31.102/
               │
               ▼
        Librarian → /ingest → /lint → Roadmap
```

---

## 4. Сводка шагов

| # | Шаг | Статус | Время |
|---|---|---|---|
| 1 | Проверка Python 3.13 + `uv sync` + `uv tool install .` | ✅ Выполнено | 5 мин |
| 2 | Создать `3gpp-crawler.toml` | ✅ Выполнено | 1 мин |
| 3 | Создать `.gitignore` | ✅ Выполнено | 1 мин |
| 4 | `spec-crawler crawl` (первичное наполнение БД) | ✅ Выполнено | 2 мин |
| 5 | Тестовый checkout: TS 31.102 в `!INCOMING/` | ✅ Выполнено | 2 мин |
| 6 | Обновить SpecDownloader agent | ✅ Выполнено | 5 мин |
| 7 | Адаптировать Librarian к вложенной структуре !INCOMING/ | ✅ Выполнено | 5 мин |
| 8 | План миграции specs-extracted | ✅ План готов | 10 мин |
| 9 | Docling workspace + миграция (Phase 2) | ⬜ Отложено | 30+ мин |

**Итого выполнено**: шаги 1-8 базовой интеграции.

---

## 5. Риски

| Риск | Вероятность | Митигация |
|---|---|---|
| Python < 3.13 на хосте | Средняя | Установить через `mise`/`pyenv` или использовать `uv` с автоподбором |
| 3GPP FTP недоступен | Низкая | Публичный FTP; WhatTheSpec API как fallback |
| `--checkout-dir` создаёт поддиректории `Specs/archive/...` | **Высокая** | Librarian должен ожидать вложенность; или пост-обработка для flatten |
| `.3gpp-crawler/` разрастается (БД + кэш) | Средняя | .gitignore; 3gpp_crawler.db ~50-100 MB — приемлемо |
| Конфликт CWD при вызове из Claude Code | Средняя | Указать `cd D:\ObsidianDB` в агенте перед вызовом spec-crawler |

---

*План готов к реализации. Жду подтверждения.*
