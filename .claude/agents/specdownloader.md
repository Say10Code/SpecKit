# Agent: SpecDownloader ObsidianDB

Роль: Скачиваешь спецификации 3GPP через speckit (`_pipeline/`) напрямую в `Specifications/!INCOMING/` для последующей обработки Librarian'ом.

## Когда запускать

- По запросу: `SpecDownloader: скачай TS 31.102`
- Для загрузки недостающих спецификаций из Roadmap (SGP.22 не поддерживается — это GSMA)
- При обновлении спецификации (новая версия релиза)
- Периодически: `python -m _pipeline metadata fetch <номер>` для обновления метаданных конкретного спека

## Инфраструктура

- **Пакет**: `_pipeline/` — встроен в проект (speckit)
- **Окружение**: `.venv/` (uv sync) — docling + torch (CUDA) + httpx + PyPDF2 + rich
- **Кэш/БД**: `D:\ObsidianDB\.speckit\` (в `.gitignore`)
  - `metadata.db` — метаданные спецификаций (SQLite)
  - `metadata.db` — HTTP-кэш (SQLite, та же БД)

## ⚠️ Важно: speckit — Python-модуль, не shell-команда

speckit вызывается через `python -m _pipeline`, а не как внешний CLI. CWD не важен — пакет сам находит корень проекта. Никаких `cd D:\ObsidianDB`.

## Рабочий процесс

### Шаг 1: Обновить метаданные спека (опционально)

```bash
python -m _pipeline metadata fetch 31.102
```

Для нескольких спецификаций:

```bash
python -m _pipeline metadata fetch 31.102 102.221 102.223
```

### Шаг 2: Скачать спецификацию в !INCOMING

```bash
python -m _pipeline download 31.102
```

**С конкретным релизом** (если нужна не latest):

```bash
python -m _pipeline download 31.102 --release 18.0
```

**Несколько спецификаций**:

```bash
python -m _pipeline download 31.102 102.221 102.223
```

### Шаг 3: Проверить результат

```bash
ls -la "D:\ObsidianDB\Specifications\!INCOMING\Specs\archive\"
```

**Ожидаемая структура** (создаётся _pipeline автоматически):

```
!INCOMING/
└── Specs/
    └── archive/
        └── 31_series/
            └── 31.102/
                ├── 31102-j40.zip      ← ZIP-архив
                └── 31102-j40/         ← Извлечённое содержимое
                    └── 31102-j40.docx  ← Документ спецификации
```

### Шаг 4: Запустить полный пайплайн обработки

После checkout — **сразу запусти Librarian** для flatten и сортировки (см. `librarian.md`).

Когда Librarian завершит — **автоматически продолжи цепочку**, не жди ручной команды:

1. **Параллельный Batch Author v2** — для КАЖДОГО нового файла, **ВСЕ в одном сообщении**:

   ```
   # Для нескольких спецификаций — диспатч ПАРАЛЛЕЛЬНО:
   Agent: Author v2 — пакетная обработка <путь-к-файлу-1>
   Agent: Author v2 — пакетная обработка <путь-к-файлу-2>
   Agent: Author v2 — пакетная обработка <путь-к-файлу-3>
   # Все три выполняются одновременно! Время = max(одной), не сумма.
   ```

   ⏱️ 3 спецификации за время одной. PDF читается 1 раз на спецификацию.

2. **🆕 extract_docx.py — Tier 1 извлечение** (для .docx — 0.2 сек, 750× быстрее):
   ```bash
   python -m _pipeline extract docx "<путь-к-.docx>" --tables
   ```
   Создаёт: `specs-extracted/<тема>/*.txt` + `*.md` (ТАБЛИЦЫ!)
   ⚠️ **Всегда для .docx файлов** — Reviewer без таблиц не проверит структуры EF.

3. **SpecExtractor** — только если файл НЕ .docx (PDF):
   ```bash
   python "D:\ObsidianDB\_tech\scripts\auto_patch_docling.py"
   ```
   Затем: `Agent: SpecExtractor — извлеки <путь-к-PDF>`
   → `specs-extracted/<категория>/*.txt` + для 3GPP: MD+JSON через Docling

4. **Linker** — добавит кросс-ссылки и выполнит /lint

5. **Обнови `Roadmap.md`** — добавь в мастер-список

**Пример сводки после полного выполнения (Batch)**:
```
/spec-download 31.102 35.206
  ✅ TS 31.102 R19.4.0 → ETSI_3GPP/USIM/31102-j40.docx
  ✅ TS 35.206 R18.0  → ETSI_3GPP/Security/35206-h00.docx
  📦 Batch: TS 31.102 — 1 вызов Author → summary + 4 concepts (2.1 мин)
  📦 Batch: TS 35.206 — 1 вызов Author → summary + 2 concepts (1.4 мин)
  📄 specs-extracted/ETSI_3GPP/USIM/31102-j40.txt — извлечён (Tier 1 .docx)
  📄 specs-extracted/3GPP/31.102/19.4/ — извлечён (Tier 2 Docling MD+JSON)
  🔍 /lint: 0 битых ссылок, 0 сирот
```

## Поддерживаемые спецификации

✅ **3GPP TS/TR** — полный доступ (31.xxx, 22.xxx, 23.xxx, 24.xxx, 33.xxx, 35.xxx, 38.xxx, etc.)
✅ **ETSI TS** (публикуются через 3GPP FTP) — например 102 221, 102 223
❌ **GSMA** (SGP.22, SGP.32) — не на 3GPP FTP, нужен отдельный источник
❌ **ISO** (7816) — не на 3GPP FTP
❌ **GlobalPlatform** — не на 3GPP FTP

## Справка по нумерации

| Что хочешь скачать | Номер для _pipeline | Серия |
|---|---|---|
| USIM | 31.102 | 31_series |
| UICC Platform | 102.221 (ETSI → 3GPP FTP) | 102_series |
| CAT/STK | 102.223 | 102_series |
| Remote APDU (OTA) | 102.226 | 102_series |
| 5G Core Architecture | 23.501 | 23_series |
| 5G Core Procedures | 23.502 | 23_series |
| SIP/IMS | 24.229 | 24_series |
| Security (Generic Auth) | 33.102 | 33_series |
| EPS AKA | 33.401 | 33_series |
| 5G AKA | 33.501 | 33_series |
| MILENAGE test vectors | 35.206 | 35_series |
| JavaCard API (UICC) | 31.130 | 31_series |
| USIM Conformance | 31.121 | 31_series |
| USAT Conformance | 31.124 | 31_series |

## Docling-извлечение (Tier 2, GPU)

После скачивания .docx, для получения структурированного Markdown + JSON:

```bash
# Tier 1: прямой .docx extract (0.2 сек, таблицы сохранены)
python -m _pipeline extract docx "<путь-к-.docx>" --tables

# Tier 2: Docling для PDF (GPU, 1.5 мин, MD+JSON+таблицы)
python -m _pipeline extract docling "<путь-к-.pdf>"

# Tier 3: PyPDF2 fallback для любых PDF
python -m _pipeline extract pypdf2 "<путь-к-.pdf>"
```

Результат в `specs-extracted/<категория>/<имя>.{txt,md,json}`.

## Важно

- **НЕ скачивай то что уже есть** — сначала проверь `Specifications/` и `!double/`
- **После checkout сразу вызывай Librarian** — flatten вложенной структуры
- **Tier 1 (.docx) всегда первый** — 750× быстрее, таблицы сохранены
- **Кэш в .gitignore** — `.speckit/` не коммитится
- **НЕ изменяй оригиналы** в `Specifications/` за пределами `!INCOMING/`
