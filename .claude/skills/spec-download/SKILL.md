# Skill: spec-download
# Trigger: /spec-download

Скачивание спецификаций 3GPP/ETSI через `spec-crawler` напрямую в `!INCOMING/` и запуск полного пайплайна обработки.

## Синтаксис

```
/spec-download <номера> [--release <версия>] [--no-ingest]
```

**Примеры**:
- `/spec-download 31.102` — скачать последнюю версию USIM
- `/spec-download 31.102 102.221 102.223` — несколько спецификаций
- `/spec-download 35.206 --release 18.0` — MILENAGE vectors, конкретный релиз
- `/spec-download 23.501 --no-ingest` — только скачать, без wiki-обработки

## Аргументы

| Аргумент | Описание |
|---|---|
| `<номера>` | Номера через пробел: dotted (31.102) или undotted (31102) |
| `--release` | Версия релиза: `latest` (по умолчанию), `18.0`, `17.0`, `19.0` |
| `--no-ingest` | Только скачать + Librarian сортировка, без `/ingest` |

## Workflow

### Шаг 1: Обновить метаданные

```bash
cd "D:\ObsidianDB"
spec-crawler crawl 31.102 102.221 ...
```

### Шаг 2: Скачать в !INCOMING

```bash
cd "D:\ObsidianDB"
spec-crawler checkout 31.102 102.221 ... --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING" [--release 18.0]
```

### Шаг 3: Librarian — flatten и сортировка

Найди файлы в `!INCOMING/Specs/archive/` → перемести в правильную тематическую директорию.

**Таблица серий → тем:**

| Серия | Тематическая директория |
|---|---|
| 31.xxx (UICC/USIM) | `ETSI_3GPP/USIM/` |
| 102.221 (UICC Platform) | `ETSI_3GPP/UICC/` |
| 102.223 (CAT/STK) | `ETSI_3GPP/CAT_STK/` |
| 102.225, 102.226 (OTA) | `ETSI_3GPP/OTA/` |
| 102.241, 131.130, 143.019 | `ETSI_3GPP/UICC_API/` |
| 101.xxx (Numbering) | `ETSI_3GPP/Numbering/` |
| 123.xxx, 133.xxx (Security) | `ETSI_3GPP/Security/` |
| 151.xxx, GSM 11.11 | `ETSI_3GPP/GSM_Legacy/` |
| 131.121, 131.124, 151.017 | `ETSI_3GPP/Test_Conformance/` |
| 35.xxx (Algorithms) | `ETSI_3GPP/Security/` |
| 23.xxx (5G Core) | `ETSI_3GPP/` |
| 24.xxx (SIP/IMS) | `ETSI_3GPP/` |
| Остальные 3GPP/ETSI | `ETSI_3GPP/` |

После перемещения — **удали** всю структуру `!INCOMING/Specs/`.

### Шаг 4: /ingest (если не --no-ingest)

Для каждого нового файла:
1. Author создаёт summary в `wiki/summaries/`
2. Author извлекает концепты → `wiki/concepts/`
3. Author фиксирует сущности → `wiki/entities/`
4. Linker расставляет связи
5. Обновить `wiki/index.md` и раздельные индексы

### Шаг 5: SpecExtractor

Извлечь текст PDF → TXT в `specs-extracted/` для Reviewer'а.

### Шаг 6: /lint

Проверить здоровье: битые ссылки, сироты, frontmatter.

### Шаг 7: Обновить Roadmap

Добавить новый summary в мастер-список.

## Поддерживаемые спецификации

✅ **3GPP TS/TR** — 31.xxx, 22.xxx, 23.xxx, 24.xxx, 33.xxx, 35.xxx, 38.xxx
✅ **ETSI TS** через 3GPP FTP — 102.221, 102.223, 102.225, 102.226, 101.220, 101.476
❌ **GSMA** (SGP.22, SGP.32) — не поддерживается
❌ **ISO** (7816) — не поддерживается
❌ **GlobalPlatform** — не поддерживается

## Что НЕ скачивать

- Уже существующие в `Specifications/` (проверь перед checkout)
- Уже лежащие в `!double/` (дубликаты)
- GSMA/ISO/GP спецификации (spec-crawler их не найдёт)

## Отчёт после выполнения

Выведи сводку:
```
/spec-download 31.102 35.206
  ✅ TS 31.102 Release 19.4.0 → ETSI_3GPP/USIM/31102-j40.docx
  ✅ TS 35.206 Release 18.0  → ETSI_3GPP/Security/35206-h00.docx
  📄 wiki/summaries/ts_31102.md — создан
  📄 wiki/summaries/ts_35206.md — создан
  🔍 /lint: 0 битых ссылок, 0 сирот
```
