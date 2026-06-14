# План консолидации: `speckit` — свой пайплайн вместо 3gpp-crawler

> **Создан**: 2026-06-14 · **Обновлён**: 2026-06-14 (v3 — аудит состояния реализации)
> **Статус**: 🔄 Частично реализован (70%) · **Название проекта**: `speckit` (specification kit)
> **Реализовано**: `_pipeline/` (10 модулей), `pyproject.toml`, `.venv` с CUDA, CLI: `python -m _pipeline`
> **НЕ реализовано**: `speckit.toml` (конфиг захардкожен), Этап 7 (декомиссия 3gpp-crawler), `speckit status/index`

---

## 1. Диагноз проблем

### 1.1 GPU не работает в uv tool

| Окружение | Python | Torch | CUDA |
|---|---|---|---|
| Системный (`python`) | WindowsApps 3.13.13 | `torch-2.12.0+cu126` | ✅ RTX 3060 |
| uv tool (`spec-crawler`) | Тот же exe, другой `sys.prefix` | `torch-2.12.0+cu126` | ❌ |

**Корень**: `uv tool install` создаёт изолированный venv в `%APPDATA%/uv/tools/`. PyTorch внутри него не находит CUDA-рантайм DLL — пути DLL изолированы от системных. Системный Python (WindowsApps) имеет доступ к `C:\Windows\System32\nvcuda.dll` и **видит CUDA**.

**Следствие**: Docling-миграция P3-5 обрабатывает 33 PDF на CPU (в 2.4–4.2× медленнее).

**Решение**: `uv sync` с `.venv` в корне ObsidianDB. venv наследует системный PATH → CUDA DLL доступны.

### 1.2 Внешняя зависимость

ObsidianDB использует **2 из 8 команд** 3gpp-crawler (`crawl`, `checkout`). 37 пакетов-зависимостей, из которых ~8 реально нужны. Upstream может изменить API.

---

## 2. Глубокий анализ: что оставить, что выбросить

### 2.1 Методология

Каждый компонент 3gpp-crawler проанализирован через три вопроса:
1. **Что делает?** — функциональное назначение
2. **Нужно ли ObsidianDB?** — да/нет/частично
3. **Если да — берём логику или код?** — переписываем (своя реализация) или адаптируем (с изменениями)

---

### 2.2 БЛОК Α: Скачивание спецификаций (Specs)

#### `specs/downloads.py` — `SpecDownloads` (295 строк)

**Что делает**: Оркестрирует полный цикл скачивания спецификации с 3GPP FTP:
- Разрешает URL из метаданных БД
- Скачивает .docx напрямую из ZIP-архива через `RemoteZipFile` (без скачивания всего ZIP — экономия трафика)
- Fallback: полное скачивание ZIP + извлечение
- Формирует путь: `{checkout_dir}/Specs/archive/{series}/{normalized}/`

**Вердикт**: ✅ **НУЖНО — переписываем**

Нам нужны две вещи:
- `RemoteZipFile` логика (doc-only download) — ключевая оптимизация
- URL resolution с выбором версии по релизу

**Что берём**: Алгоритм doc-only download + структуру URL.
**Что пишем сами**: Реализацию на `httpx` + `zipfile` (без `unzip-http`, без `niquests`).

#### `specs/sources/whatthespec.py` — WhatTheSpec API (70 строк)

**Что делает**: Запрашивает JSON API `whatthespec.net` для получения метаданных спецификации (версии, URL, статус). Публичный, без авторизации.

**Вердикт**: ✅ **НУЖНО — переписываем**

Самый ценный источник метаданных. Протокол простой:
```
GET /api/specs/{номер} → JSON с версиями и FTP URL
```

**Что берём**: Протокол (эндпоинты, формат ответа).
**Что пишем сами**: Клиент на `httpx` (20-30 строк).

#### `specs/sources/threegpp.py` — 3GPP Dynareport (55 строк)

**Что делает**: Идёт на `SPEC_DYNAREPORT_URL_TEMPLATE` (legacy 3GPP portal), следует редиректу, парсит JSON с `specificationId`.

**Вердикт**: ⚠️ **ОПЦИОНАЛЬНО — берём как fallback**

WhatTheSpec — основной источник. Dynareport — запасной, если WhatTheSpec недоступен.
Реализация тривиальная: HTTP GET → редирект → JSON.

#### `specs/sources/base.py` — SpecSource Protocol (15 строк)

**Что делает**: Определяет структурный тип (`Protocol`) для источников метаданных: `name: str` + `fetch(spec_number) -> dict`.

**Вердикт**: ✅ **НУЖНО — паттерн сохраняем**

Идея Protocol для взаимозаменяемых источников — правильная. В нашей реализации — абстрактный класс или Protocol с двумя имплементациями (WhatTheSpec + 3GPP).

---

### 2.3 БЛОК Β: База данных

#### `database/specs.py` — `SpecDatabase` (555 строк)

**Что делает**: Асинхронная БД спецификаций поверх Oxyde ORM:
- `upsert_specification()` — вставка/обновление метаданных спека
- `crawl_specs()` — параллельный обход источников для нескольких спеков
- `get_spec_versions()` — запрос версий с фильтрацией по релизу
- `_build_source_differences()` — сравнение метаданных между источниками

**Вердикт**: ✅ **НУЖНО — сильно упрощаем**

Нам нужна только малая часть:
- Сохранение метаданных спека + версий (2 таблицы)
- Запрос: дай последнюю версию спека X
- Запрос: дай URL для версии X.Y

Что НЕ нужно:
- Oxyde ORM (async SQLite) → синхронный `sqlite3` из stdlib
- Source comparison → у нас один источник (WhatTheSpec)
- Параллельный crawl → мы качаем по одному спеку за раз
- 555 строк → хватит ~80 строк на сыром SQL

#### `database/base.py` — `DocDatabase` (315 строк)

**Что делает**: Фасад над Oxyde `AsyncDatabase`. Миграции, сидирование справочников (working groups), контекстный менеджер.

**Вердикт**: ❌ **НЕ НУЖНО**

Свой слой на чистом sqlite3 без ORM: `CREATE TABLE IF NOT EXISTS`, никаких миграций, никакого сидирования.

#### `database/oxyde_models.py` — Oxyde ORM модели (228 строк)

**Что делает**: Девять моделей: WorkingGroup, SubWorkingGroup, CrawlLog, Meeting, TDoc, Specification, SpecificationSource, SpecificationVersion, SpecificationDownload.

**Вердикт**: ❌ **НЕ НУЖНО**

Нам нужны 2 таблицы из 9. Без ORM: простые dataclass'ы → строки через `sqlite3.Row`.

#### `database/tdocs.py`, `database/meetings.py`

**Вердикт**: ❌ **НЕ НУЖНО**

TDoc и Meetings — для встреч 3GPP, не для спецификаций.

---

### 2.4 БЛОК C: Извлечение (Extraction)

#### `extraction/convert.py` — `convert_for_wiki()` (608 строк)

**Что делает**: Главный оркестратор конвертации документа в Markdown+JSON:
1. Разрешает исходный файл (SPEC → checkout, TDOC → download, OTHER → локальный путь)
2. Для Office-форматов: конвертирует в PDF через LibreOffice
3. Выбирает профиль: pdf-only / markdown-only (pymupdf4llm) / default (Docling) / advanced (Docling+)
4. Пишет YAML frontmatter с метаданными
5. Кэширует: не перегоняет, если выходные файлы уже есть

**Вердикт**: ✅ **НУЖНО — переписываем, сохраняя все профили**

Это **ядро** extraction-пайплайна. Но текущая реализация завязана на:
- `SourceKind` enum (TDOC/SPEC/OTHER) → нам нужен только SPEC + OTHER
- Workspace checkout logic → заменяем на прямые пути в `Specifications/`
- niquests/asyncio → заменяем на httpx/синхронный

**Что сохраняем**:
- 4 профиля (`pdf-only`, `markdown-only`, `default`, `advanced`)
- Кэширование: проверка выходных файлов перед конвертацией
- YAML frontmatter с метаданными
- pymupdf4llm fallback для markdown-only
- Картинки: `ImageRefMode.PLACEHOLDER` для Docling, base64-embed для pymupdf4llm

**Что выбрасываем**:
- `_resolve_source_files()` — ObsidianDB работает с путями файлов, а не с идентификаторами в БД
- TDOC support
- `convert_for_wiki()` как единая функция с 15 параметрами → разбиваем на композицию функций

#### `extraction/docling/converter.py` — Docling converter (96 строк)

**Что делает**: Создаёт и кэширует `DocumentConverter` (700 MB модель), экспортирует .md + .json, опционально .csv таблиц.

Ключевые детали:
- Кэш из одного элемента: `_converter_cache.clear()` при смене профиля — никогда не держит >1 модели в памяти
- `TQDM_DISABLE=1` — глушит прогресс-бары загрузки весов
- `TablesMode.CSV` → `_export_tables_as_csv()` — итерация по `result.document.tables`

**Вердикт**: ✅ **НУЖНО — адаптируем**

Логика кэширования конвертера и CSV-экспорта — готовая и правильная. Адаптируем под нашу структуру.

#### `extraction/docling/pipeline.py` — Pipeline options (52 строки)

**Что делает**: Строит `PdfPipelineOptions` для Docling с ограничениями под 8 GB VRAM:
- `images_scale=1.5`, `layout_batch_size=2`, `table_batch_size=2`
- `do_ocr=False` (документы born-digital, не сканы)
- `generate_picture_images=True`
- Advanced: `do_picture_description`, `do_code_enrichment`, `do_formula_enrichment`

**Вердикт**: ✅ **НУЖНО — переносим с донастройкой**

Эти параметры — результат экспериментов на RTX 3060 12 GB. Сохраняем как базовые, с возможностью тюнинга. **Критично**: `do_ocr=False` сильно ускоряет (OCR не нужен для born-digital PDF).

#### `extraction/docling/filter.py` — bad_alloc filter (35 строк)

**Что делает**: `logging.Filter`, который глушит `std::bad_alloc` от C++ бэкенда Docling (RockHopper). Известный баг: пытается обработать фантомные страницы за пределами PDF.

**Вердикт**: ✅ **НУЖНО — переносим как есть**

Без этого фильтра Docling спамит ERROR-сообщениями, которые выглядят как фатальные, но не являются.

#### `extraction/fetch_spec.py` — Spec download for extraction (125 строк)

**Что делает**: Скачивает спецификацию по номеру + релизу, возвращает пути к файлам. Использует `SpecDownloads` внутри.

**Вердикт**: ⚠️ **ЧАСТИЧНО — логика входит в downloader**

Функция `fetch_spec_files()` делает download + scan файлов. В нашей архитектуре это разделено:
- Download: `_pipeline/download.py`
- Scan: `_pipeline/files.py` (найти .docx/.pdf в скачанном)

#### `extraction/fetch_tdoc.py` — TDoc download

**Вердикт**: ❌ **НЕ НУЖНО**

Только для meeting documents.

#### `extraction/profiles.py` — ExtractionProfile enum

**Вердикт**: ✅ **НУЖНО — 15 строк, переносим**

```python
class ExtractionProfile(StrEnum):
    PDF_ONLY = "pdf-only"
    MARKDOWN_ONLY = "markdown-only"
    DEFAULT = "default"
    ADVANCED = "advanced"
```

Плюс `FiguresMode`, `TablesMode`, `DeviceType` — все нужны.

#### `extraction/errors.py`, `extraction/metrics.py`

**Вердикт**: ✅ **НУЖНО — оба**

- `ConversionError` — своё исключение для ошибок конвертации
- `timed_operation()` — контекстный менеджер для замеров времени этапов

---

### 2.5 БЛОК D: Workspaces

#### `workspaces/` — весь модуль

**Что делает**: Управление именованными коллекциями документов (workspace = набор TDocs + Specs + Other), с регистрацией в JSON-файле, отслеживанием состояния обработки, и batch-конвертацией через `workspace process`.

**Вердикт**: ❌ **НЕ НУЖНО — но паттерн "membership tracking" заимствуем**

ObsidianDB имеет свою структуру: `Specifications/` + `specs-extracted/`. Workspace-концепция 3gpp-crawler (логические группы документов) избыточна, НО:

- **Идея tracking'а состояния** полезна: знать, для каких PDF уже есть .md/.json, для каких нет
- Реализуем через **файловую систему**: `specs-extracted/INDEX.md` + `.meta.json`

Самый полезный кусок — `workspaces/utils.py` (`checkout_spec_to_workspace()`, `resolve_spec_release_from_db()`) — но его логика уже учтена в Блоке Α (downloader).

---

### 2.6 БЛОК E: Инфраструктура

#### `config/settings.py` — `ThreeGPPConfig` (310 строк)

**Что делает**: Pydantic-settings модель с четырьмя вложенными конфигами (Path, Http, Credentials, Crawl), поддержка переменных окружения (`TDC_*`), загрузка из TOML/YAML/JSON.

**Вердикт**: ❌ **НЕ НУЖНО — заменяем на простой `speckit.toml`**

ObsidianDB нужен один конфиг-файл с путями и настройками Docling. Не нужно:
- pydantic-settings (тяжёлая зависимость)
- mise-style cascade (4 уровня конфигов)
- Env-var маппинг (`TDC_*`)
- Credentials (всё публичное)
- Crawl config (не качаем meeting-данные)

Замена: `speckit.toml` в корне ObsidianDB, читается через `tomllib` (stdlib Python 3.11+).

#### `config/cache_manager.py` — CacheManager singleton (132 строки)

**Что делает**: Синглтон, хранящий пути к БД, HTTP-кэшу, checkout-директории, workspace-файлам. Регистрируется при старте CLI, разрешается глобально.

**Вердикт**: ❌ **НЕ НУЖНО — заменяем на module-level config**

Паттерн «singleton для путей» имеет смысл в большом CLI с subcommands. В нашем случае пути читаются из `speckit.toml` один раз и хранятся в модуле.

#### `config/sources.py` — Config file discovery (260 строк)

**Что делает**: mise-style обход директорий: `~/.config/3gpp-crawler/` → `.config/.3gpp-crawler/` → `.3gpp-crawler/` → `3gpp-crawler.toml`. Поддержка `${ENV_VAR}`, deep merge нескольких файлов.

**Вердикт**: ❌ **НЕ НУЖНО**

Один файл `speckit.toml` в корне ObsidianDB. Никакого cascade, никакого `${ENV_VAR}`.

---

### 2.7 БЛОК F: HTTP-клиент

#### `http_client/session.py` — niquests + hishel (346 строк)

**Что делает**:
- Создаёт `niquests.Session` (requests-форк с HTTP/3)
- Оборачивает в `hishel.CacheTransport` с SQLite-бэкендом
- Ретраи с экспоненциальной задержкой (429, 5xx)
- Browser-like заголовки для обхода 403 от 3GPP-серверов
- Адаптер для совместимости niquests и hishel (типы не совпадают)

**Вердикт**: ❌ **НЕ НУЖНО как код, но паттерны заимствуем**

Что нам реально нужно:
- **Browser-заголовки**: 3GPP FTP отклоняет запросы без User-Agent → **переносим константы**
- **Ретраи**: 3 повтора с backoff для 5xx → **5 строк с httpx**
- **HTTP-кэш**: SQLite-кэш для повторных запросов → **опционально**, файлы маленькие
- **HTTP/3**: не нужен, 3GPP FTP не поддерживает
- **niquests/hishel bridge**: самый сложный кусок → не нужен

Замена: `httpx` (30 строк настройки сессии).

---

### 2.8 БЛОК G: CLI (Typer)

#### `cli/` — три Typer-приложения

**Что делает**: Три отдельных CLI (tdoc-crawler, spec-crawler, 3gpp-crawler) на Typer с Rich-форматированием, панелями команд, progress-bar'ами.

**Вердикт**: ❌ **НЕ НУЖНО как фреймворк, но CLI-интерфейс нужен**

Наш CLI будет **один**: `python -m speckit <команда>`. Вместо Typer — `argparse` stdlib (или лёгкий `click`). Команды: `download`, `extract`, `status`, `metadata`.

Rich-прогресс-бары оставляем для визуализации Docling-конвертации.

---

### 2.9 БЛОК H: Модели и константы

#### `models/` — Pydantic модели + Enums

**Что делает**: Доменные типы: WorkingGroup, SubWorkingGroup, CrawlLogEntry, TDocCrawlConfig, MeetingCrawlConfig, Workspace, ExtractedTableElement, OutputFormat, SortOrder.

**Вердикт**: ⚠️ **ЧАСТИЧНО**

Что нужно:
- `ExtractionProfile`, `FiguresMode`, `TablesMode`, `DeviceType` — из `extraction/profiles.py`
- `WorkingGroup` enum — для серия→тема mapping
- `ExtractedTableElement` — модель таблицы для JSON-экспорта

Что НЕ нужно:
- `TDocCrawlConfig`, `MeetingCrawlConfig` — только для TDoc
- `OutputFormat` (ISON, TOON, YAML) — неиспользуемые форматы вывода
- `PortalCredentials` — без авторизации
- `Workspace`, `DocumentClassification` — своя модель

#### `constants/urls.py` — URL-шаблоны (47 строк)

**Что делает**: Все URL-константы для 3GPP FTP, портала, WhatTheSpec, заголовки браузера.

**Вердикт**: ✅ **ЦЕННО — переносим как данные**

Эти константы — результат знания поведения 3GPP-серверов:
- `BROWSER_HEADERS` — без них 403
- `SPEC_URL_TEMPLATE` — структура FTP-пути (стабильна 20+ лет)
- `SPEC_DYNAREPORT_URL_TEMPLATE` — legacy-источник
- `WHATSPEC_*_URL_TEMPLATE` — API-эндпоинты

#### `constants/patterns.py` — Regex (28 строк)

**Вердикт**: ⚠️ **ЧАСТИЧНО**

Нужно: `TDOC_PATTERN` — если будем парсить имена файлов.
Не нужно: `DATE_PATTERN`, `TDOC_SUBDIRS`, `EXCLUDED_DIRS` — для TDoc.

---

### 2.10 БЛОК I: Workspace-пакеты

#### `packages/convert-lo` — LibreOffice CLI wrapper

**Что делает**: Типизированная обёртка над `soffice --headless`. Предоставляет существенно больше, чем `subprocess.run`:

| Возможность | Детали |
|---|---|
| Бинарный поиск | `LIBREOFFICE_PATH` env → стандартные пути ОС → `shutil.which` |
| Валидация форматов | `LibreOfficeFormat` enum (21 формат), матрица неподдерживаемых конвертаций |
| PDF→DOCX блокировка | Явный `UNSUPPORTED_CONVERSIONS` frozenset |
| Windows-специфика | `STARTUPINFO` + `CREATE_NO_WINDOW` — без мигания окон |
| Path resolving | `.resolve()` на всех путях перед вызовом |
| Таймаут | 300 сек на файл |
| Типизированный результат | `ConversionResult(input_file, output_file, output_format)` |
| Классы ошибок | `SofficeNotFoundError`, `UnsupportedConversionError`, `ConversionError` |

**Вердикт**: ✅ **НУЖНО — адаптируем под свои нужды**

Это НЕ просто `subprocess.run(['soffice', ...])`. Здесь реальная инженерная работа: бинарный поиск, обработка ошибок, Windows-специфика. Но нам нужна только PDF-конвертация, не все 21 формат.

**Что адаптируем**: `Converter` класс, урезанный до `.doc/.docx → PDF`. Оставляем: бинарный поиск, таймаут, Windows-флаги, типизированные ошибки.

#### `packages/pool_executors` — Executor factory

**Что делает**: Фабрика `create_executor("serial"|"mp"|"thread"|"subinterpreter")`. `SerialPoolExecutor` выполняет задачи в главном потоке немедленно (для отладки).

**Вердикт**: ⚠️ **ЧАСТИЧНО — только `SerialPoolExecutor`**

`SerialPoolExecutor` полезен для отладки: заменяет `ProcessPoolExecutor` без изменения кода. Но:
- Многопроцессность нам не нужна (Docling сам использует GPU-параллелизм)
- `InterpreterPoolExecutor` — Python 3.14+
- Сам `SerialPoolExecutor` — 50 строк, можно написать свой

---

### 2.11 БЛОК J: Форматы вывода

#### `ison-py`, `isonantic`, `toon-format`

**Что делает**: Специфичные форматы сериализации для CLI-вывода (`spec-crawler query`).

**Вердикт**: ❌ **НЕ НУЖНО**

Нам не нужен CLI-query. Результаты пишутся в файлы (MD + JSON + TXT).

---

### 2.12 БЛОК K: Неиспользуемые зависимости

#### `pdf-remote-converter`

**Что делает**: Онлайн-сервис конвертации Office→PDF. Fallback, когда локальный LibreOffice не установлен.

**Вердикт**: ❌ **НЕ НУЖНО**

LibreOffice установлен локально (v26.2.4.2).

#### `doc2txt`

**Что делает**: Конвертация .doc (бинарный формат) в текст.

**Вердикт**: ❌ **НЕ НУЖНО**

Все спецификации 3GPP — .docx (современный формат). Для старых .doc используем LibreOffice.

---

### 2.13 СВОДНАЯ ТАБЛИЦА

| Компонент | Размер | Нужен? | Действие |
|---|---|---|---|
| `specs/downloads.py` | 295 строк | ✅ | Переписать: RemoteZipFile логика + HTTP-загрузка |
| `specs/sources/whatthespec.py` | 70 строк | ✅ | Переписать: httpx клиент (30 строк) |
| `specs/sources/threegpp.py` | 55 строк | ⚠️ | Fallback-источник (опционально) |
| `database/specs.py` | 555 строк | ✅ | Сильно упростить: 2 таблицы, сырой SQL |
| `database/base.py` | 315 строк | ❌ | Свой лёгкий слой |
| `database/oxyde_models.py` | 228 строк | ❌ | Замена на dataclass + sqlite3.Row |
| `extraction/convert.py` | 608 строк | ✅ | Ядро — переписать с разделением на функции |
| `extraction/docling/converter.py` | 96 строк | ✅ | Адаптировать: кэш + CSV-экспорт |
| `extraction/docling/pipeline.py` | 52 строки | ✅ | Перенести с тюнингом под RTX 3060 |
| `extraction/docling/filter.py` | 35 строк | ✅ | Перенести как есть |
| `extraction/fetch_spec.py` | 125 строк | ⚠️ | Логика уходит в downloader |
| `extraction/profiles.py` | 15 строк | ✅ | Перенести enums |
| `extraction/errors.py` | 10 строк | ✅ | Перенести |
| `extraction/metrics.py` | 30 строк | ✅ | `timed_operation()` |
| `workspaces/` | весь | ❌ | Паттерн tracking'а через INDEX.md |
| `config/settings.py` | 310 строк | ❌ | `speckit.toml` + tomllib |
| `config/cache_manager.py` | 132 строки | ❌ | Module-level config |
| `config/sources.py` | 260 строк | ❌ | Не нужно |
| `http_client/session.py` | 346 строк | ❌ | `httpx` сессия (30 строк) |
| `cli/` (Typer) | | ❌ | `argparse` + `rich` прогресс |
| `constants/urls.py` | 47 строк | ✅ | Перенести константы |
| `constants/patterns.py` | 28 строк | ⚠️ | Частично (TDOC_PATTERN) |
| `models/` (Pydantic) | | ⚠️ | Частично: enums + extraction-модели |
| `convert-lo` | пакет | ✅ | Адаптировать: урезать до .docx→PDF |
| `pool_executors` | пакет | ⚠️ | Только SerialPoolExecutor (50 строк) |
| `ison-py/isonantic/toon` | пакеты | ❌ | Неиспользуемые форматы |
| `pdf-remote-converter` | пакет | ❌ | Локальный LibreOffice |
| `doc2txt` | пакет | ❌ | Не используется |
| `tdocs/` | модуль | ❌ | Meeting documents |
| `meetings/` | модуль | ❌ | Meeting metadata |

**Сохраняем**: 14 компонентов (полностью или с адаптацией)
**Выбрасываем**: 15 компонентов (нерелевантны ObsidianDB)

---

## 3. Архитектура `speckit`

### 3.1 Структура пакета

```
D:\ObsidianDB\
├── speckit.toml                     ← Конфиг (пути, Docling-настройки)
├── pyproject.toml                   ← Зависимости
├── .venv/                           ← Локальное окружение с CUDA
│
├── _pipeline/                       ← Пакет speckit (новое имя)
│   ├── __init__.py
│   │
│   ├── config.py                    ← Чтение speckit.toml → dataclass
│   ├── constants.py                 ← URL-шаблоны + BROWSER_HEADERS
│   │
│   ├── download/                    ← БЛОК Α: Скачивание
│   │   ├── __init__.py
│   │   ├── metadata.py              ← WhatTheSpec + 3GPP dynareport → БД
│   │   ├── ftp.py                   ← 3GPP FTP download (RemoteZipFile логика)
│   │   └── db.py                    ← SQLite: specs + releases (2 таблицы)
│   │
│   ├── extract/                     ← БЛОК C: Извлечение
│   │   ├── __init__.py
│   │   ├── profiles.py              ← ExtractionProfile, FiguresMode, etc.
│   │   ├── docx_extract.py          ← Tier 1: .docx → TXT + MD таблицы (перенос)
│   │   ├── docling_extract.py       ← Tier 2: PDF → Docling MD+JSON
│   │   ├── docling_pipeline.py      ← PipelineOptions builder
│   │   ├── docling_filter.py        ← bad_alloc suppressor
│   │   ├── pypdf2_extract.py        ← Tier 3: PDF → плоский TXT (legacy)
│   │   ├── converter.py             ← convert-lo адаптация (.docx→PDF)
│   │   └── errors.py                ← ConversionError + timed_operation
│   │
│   ├── index.py                     ← Обновление specs-extracted/INDEX.md
│   ├── status.py                    ← Статус: что скачано/извлечено
│   │
│   └── __main__.py                  ← CLI: python -m speckit ...
│
├── _tech/scripts/                   ← ДИАГНОСТИКА (остаётся)
│   ├── bench_cpu_vs_gpu.py          ← GPU-бенчмарк
│   ├── auto_patch_docling.py        ← F1 fix для docling
│   └── ...
│
└── .3gpp-crawler/                   ← КЭШ (переиспользуем)
    ├── 3gpp_crawler.db              ← готовая БД метаданных
    └── http-cache.sqlite3           ← HTTP-кэш
```

### 3.2 Конфиг: `speckit.toml`

```toml
[paths]
vault = "D:\\ObsidianDB"
specifications = "Specifications"
incoming = "Specifications/!INCOMING"
double = "Specifications/!double"
extracted = "specs-extracted"
category_map = "Specifications/.category-map.md"

[db]
path = ".speckit/speckit.db"          # своя БД (легче 3gpp_crawler.db)

[download]
default_source = "whatthespec"        # whatthespec | threegpp
doc_only = true                       # RemoteZipFile — только .docx из ZIP

[extraction]
device = "cuda"                       # cuda | cpu | auto
profile = "default"                   # pdf-only | markdown-only | default | advanced

[extraction.docling]
images_scale = 1.5
layout_batch_size = 2
table_batch_size = 2
do_ocr = false
generate_picture_images = true

[extraction.libreoffice]
timeout = 300                          # секунд на файл
```

### 3.3 Серия → тема mapping

Берём из `Specifications/.category-map.md` (уже существует). Формат: таблица Markdown, серия → директория.

Логика `_map_series_to_topic(series: str) -> str` читает этот файл и возвращает путь для размещения спецификации.

### 3.4 CLI

```bash
# Метаданные
uv run python -m speckit metadata fetch 31.102          # заполнить БД
uv run python -m speckit metadata show 31.102           # показать версии

# Скачивание
uv run python -m speckit download 31.102                # latest в !INCOMING
uv run python -m speckit download 31.102 --rel 18.0     # конкретный релиз
uv run python -m speckit download 31.102 102.221 35.206 # несколько

# Извлечение
uv run python -m speckit extract docx "Specifications/ETSI_3GPP/USIM/31102-j40.docx"
uv run python -m speckit extract docling "Specifications/eSIM/sgp02.pdf"
uv run python -m speckit extract all --tier 1           # все .docx в Specifications/

# Статус
uv run python -m speckit status                         # что скачано/извлечено
uv run python -m speckit status --missing               # PDF без MD+JSON
```

### 3.5 Зависимости (pyproject.toml)

```toml
[project]
name = "speckit"
version = "0.1.0"
description = "3GPP specification ingestion toolkit for ObsidianDB"
requires-python = ">=3.13,<3.14"

dependencies = [
    # Tier 2: Docling + ML (GPU)
    "docling>=2.93.0",

    # HTTP
    "httpx>=0.28.0",

    # PDF (Tier 2 markdown-only + Tier 3 PyPDF2)
    "pymupdf>=1.27.2",
    "pymupdf4llm>=1.27.2",

    # CLI
    "rich>=14.2.0",
]
```

**Зависимостей: 5** (против 37 в 3gpp-crawler).

torch НЕ в списке — он придёт как транзитивная зависимость docling'а (docling → torch). При установке через `uv sync` с правильным index-url, torch подхватит CUDA.

---

## 4. Этапы реализации

### Этап 1: Окружение и структура (~30 мин) — ✅ ВЫПОЛНЕНО

- [x] Создать `pyproject.toml` с 5 зависимостями
- [x] `uv sync --index-url https://download.pytorch.org/whl/cu126` → `.venv` с CUDA
- [x] Проверить: `uv run python -c "import torch; assert torch.cuda.is_available()"`
- [x] Создать структуру `_pipeline/`
- [ ] Создать `speckit.toml` ← НЕ СДЕЛАНО (настройки захардкожены)
- [x] Обновить `.gitignore`: `.venv/`, `.speckit/`

### Этап 2: Downloader (~2 ч) — ✅ ВЫПОЛНЕНО (упрощённо)

- [x] `_pipeline/config.py` — чтение конфига (упрощённый)
- [x] `_pipeline/_metadata_db.py` — SQLite (2 таблицы)
- [x] `_pipeline/_resolve_spec.py` — WhatTheSpec API + URL resolution
- [x] `_pipeline/_download_spec.py` — FTP download (RemoteZipFile логика)
- [x] `_pipeline/cli.py` — CLI `resolve`, `download`, `extract`
- [x] `_pipeline/__main__.py` — точка входа

### Этап 3: Extractor (~1.5 ч) — ✅ ВЫПОЛНЕНО (базово)

- [x] `_pipeline/extract_docx.py` — Tier 1: .docx → TXT + MD
- [x] `_pipeline/extract_docling.py` — Tier 2: Docling MD+JSON
- [x] `_pipeline/extract_pypdf2.py` — Tier 3: PyPDF2 fallback
- [ ] `speckit.toml` — profiles, device, docling options (НЕ СДЕЛАНО)

### Этап 4: Утилиты (~30 мин) — ⬜ НЕ НАЧАТО

- [ ] `_pipeline/index.py` — обновление `specs-extracted/INDEX.md`
- [ ] `_pipeline/status.py` — `status` и `status --missing`

### Этап 5: Замена в агентах (~1 ч) — ⚠️ ЧАСТИЧНО

- [x] `_pipeline/` интегрирован с SpecExtractor через `extract_docx.py`
- [ ] `SpecDownloader`: всё ещё использует `spec-crawler checkout` (не заменён)
- [ ] `CLAUDE.md`: всё ещё упоминает spec-crawler
- [ ] `_tech/README.md`: обновлён частично

### Этап 6: Верификация GPU (~30 мин) — ✅ ВЫПОЛНЕНО

- [x] `python -m _pipeline extract docling` работает на GPU
- [x] CUDA видна через `.venv` (uv sync)
- [x] Время сравнимо с бенчмарком B3

### Этап 7: Деcommission 3gpp-crawler (~15 мин) — ⬜ НЕ НАЧАТО

- [ ] `uv tool uninstall 3gpp-crawler` (оставить до полной верификации)
- [ ] Удалить `3gpp-crawler.toml`
- [ ] `.3gpp-crawler/` оставить как резервную копию метаданных

---

## 5. Оценка

| Этап | Часы | Статус |
|---|---|---|---|
| 1. Окружение и структура | 0.5 | ✅ (без speckit.toml) |
| 2. Downloader | 2.0 | ✅ (упрощённый) |
| 3. Extractor | 1.5 | ✅ (базовый) |
| 4. Утилиты | 0.5 | ⬜ Не начато |
| 5. Замена в агентах | 1.0 | ⚠️ Частично |
| 6. Верификация GPU | 0.5 | ✅ |
| 7. Деcommission | 0.25 | ⬜ Не начато |
| **Реализовано** | **~4.5 ч** | **~70%** |
| **Осталось** | **~1.75 ч** | Этапы 4, 5 (доделать), 7 |

---

## 6. Риски

| Риск | Вероятность | Митигация |
|---|---|---|
| WhatTheSpec API изменится | Низкая | Протокол простой, есть fallback на 3GPP dynareport |
| 3GPP FTP изменит URL-структуру | Низкая | Стабильна 20+ лет |
| torch с CUDA не подхватится в venv | Средняя | Проверить в Этапе 1; `uv pip install torch --index-url https://download.pytorch.org/whl/cu126` |
| Docling bad_alloc на некоторых PDF | Средняя | `auto_patch_docling.py` (F1 fix) + `docling_filter.py` |
| RemoteZipFile логика сложна для переписывания | Средняя | Fallback: полное скачивание ZIP (медленнее, но надёжно) |
| 3gpp-crawler БД понадобится для старых данных | Низкая | Оставляем `.3gpp-crawler/` read-only на время перехода |

---

*План v3 (аудит состояния) — 2026-06-14. Архитектурный анализ 29 компонентов 3gpp-crawler проведён. Реализация ~70%: `_pipeline/` работает, .venv с CUDA, CLI доступен. Осталось: speckit.toml, утилиты (status/index), замена в агентах, декомиссия 3gpp-crawler.*
