# Skill: spec-download
# Trigger: /spec-download

Скачивание спецификаций 3GPP/ETSI через speckit (`_pipeline/`) напрямую в `!INCOMING/` и запуск полного пайплайна обработки.

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
python -m _pipeline metadata fetch 31.102 102.221 ...
```

### Шаг 2: Скачать в !INCOMING

```bash
python -m _pipeline download 31.102 102.221 ... [--release 18.0]
```

### Шаг 3: Librarian — flatten и сортировка

Найди файлы в `!INCOMING/Specs/archive/` → перемести в правильную тематическую директорию.

**Маппинг серий → тем**: см. `Specifications/.category-map.md` — **единый source of truth**. Не дублируй таблицу здесь.

После перемещения — **удали** всю структуру `!INCOMING/Specs/`.

### Шаг 4: Параллельный Batch Authoring + пайплайн (если не --no-ingest)

**Для нескольких спецификаций — диспатч ВСЕ Author v2 вызовы ПАРАЛЛЕЛЬНО в одном сообщении.** Это ключевая оптимизация: 3 спецификации обрабатываются за время одной.

```
ОДНИМ СООБЩЕНИЕМ:
  Agent: Author v2 — пакетная обработка <путь-к-Spec1>
  Agent: Author v2 — пакетная обработка <путь-к-Spec2>
  Agent: Author v2 — пакетная обработка <путь-к-Spec3>
  (все три выполняются одновременно!)
```

**Для одной спецификации** — просто один вызов Author v2 Batch.

После завершения ВСЕХ Author'ов:
1. **Linker** — ОДИН проход кросс-ссылок между всеми новыми страницами
2. **extract_docx.py --tables** — для каждого .docx (Tier 1, параллельно)
3. **Обновить индексы** — `wiki/index.md` + раздельные (один проход)

⏱️ **Время**: 3 спецификации = max(время одной) + Linker, вместо суммы трёх.

### Шаг 5: SpecExtractor — Tier 1 (.docx) или Tier 2/3 (PDF)

**Для .docx файлов** — основной путь, Tier 1:

```bash
python -m _pipeline extract docx "<путь-к-.docx>" --tables
→ specs-extracted/<категория>/*.txt (plain, grep)
→ specs-extracted/<категория>/*.md (таблицы, структурировано)
```

**Только если .docx не доступен** — PDF извлечение:
```
Agent: SpecExtractor — извлеки <путь-к-PDF>
→ specs-extracted/<категория>/*.txt (+ MD+JSON для 3GPP через Docling)
```

⚠️ **extract_docx.py — всегда первый**. Без таблиц Reviewer не может проверить структуры EF.

### Шаг 6: /lint — авто-вызов

Проверить здоровье: битые ссылки, сироты, frontmatter. Если ошибки → исправить.

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
- GSMA/ISO/GP спецификации (_pipeline их не найдёт)

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
