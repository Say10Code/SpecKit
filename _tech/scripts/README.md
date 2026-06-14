# Служебные скрипты — инструкция

> Как бэкапить Data-слой проекта и синхронизировать его между разными ObsidianDB-проектами.

## Состав `_tech/scripts/`

| Скрипт | Назначение |
|---|---|
| **backup_data.py** | Бэкап Data-слоя (wiki, Specifications, specs-extracted, notes, Clippings) → ZIP |
| **sync_data.py** | Синхронизация Data между проектами из бэкапа |
| **quality_metrics.py** | 8 категорий метрик + история — вызывается `/roadmap` |
| **audit_connectivity.py** | Граф-анализ wikilinks — вызывается `/lint --deep` |
| **check_frontmatter.py** | Валидация YAML frontmatter |
| **auto_patch_docling.py** | F1 fix для docling — pre-flight в SpecExtractor |
| **docling_migrate.py** | Пакетная миграция PDF → Docling MD+JSON |
| **bench_cpu_vs_gpu.py** | Проверка CUDA после обновлений |
| **build_html.py** | Пакетный экспорт wiki/ → HTML |

Ниже — инструкция к `backup_data.py` и `sync_data.py`.

---

## Что такое Data-слой

Data-слой — это всё, что НЕ является движком (Core). Это контент, который создаётся и обрабатывается агентами:

| Директория | Что внутри | Кто наполняет |
|---|---|---|
| `wiki/` | База знаний (130 страниц) | Author v2, Researcher |
| `Specifications/` | Исходные PDF/DOCX спецификаций (74 + 20) | SpecDownloader, пользователь |
| `specs-extracted/` | Эталонные тексты для Reviewer (237 файлов) | SpecExtractor |
| `notes/` | Заметки пользователя | Пользователь |
| `Clippings/` | Web-clippings из Obsidian | Obsidian |

Data-слой **НЕ версионируется в git** (файлы большие, бинарные, восстанавливаемые). Для его сохранения и переноса — эти скрипты.

---

## 1. backup_data.py — создание бэкапа

Собирает Data-директории в ZIP-архив с манифестом.

### Базовое использование

```bash
# Из корня проекта
cd D:\ObsidianDB

# Полный бэкап всех Data-директорий
python _tech/scripts/backup_data.py
```

**Результат**: `_backups/obsidiandb-data-2026-06-14-154103.zip`

Внутри ZIP:
```
MANIFEST.json               ← метаданные: дата, размеры, количество файлов
wiki/index.md
wiki/concepts/...
wiki/summaries/...
Specifications/.category-map.md
Specifications/ETSI_3GPP/...
specs-extracted/INDEX.md
specs-extracted/ETSI_3GPP/...
notes/...
Clippings/...
```

### Частичный бэкап

```bash
# Без Specifications/ (экономия ~181 MB — самые тяжёлые файлы)
python _tech/scripts/backup_data.py --no-specs

# Без specs-extracted/ (экономия ~444 MB — восстанавливается SpecExtractor'ом)
python _tech/scripts/backup_data.py --no-extracted

# Только wiki + notes (лёгкий бэкап знаний и заметок)
python _tech/scripts/backup_data.py --no-specs --no-extracted --no-clippings

# Только Specifications/ (перенос исходников между проектами)
python _tech/scripts/backup_data.py --no-wiki --no-extracted --no-notes --no-clippings
```

### Настройка вывода

```bash
# Сохранить в конкретную папку (а не _backups/)
python _tech/scripts/backup_data.py --output-dir D:/MyBackups/2026-06

# Без сжатия — быстрее, но больше размер
python _tech/scripts/backup_data.py --compress-level 0

# Максимальное сжатие — медленнее, но меньше размер
python _tech/scripts/backup_data.py --compress-level 9

# JSON-вывод для автоматизации (cron/CI)
python _tech/scripts/backup_data.py --json
```

**JSON-вывод** возвращает:
```json
{
  "archive": "D:\\ObsidianDB\\_backups\\obsidiandb-data-2026-06-14.zip",
  "size_bytes": 55500000,
  "size_human": "52.9 MB",
  "backup_date": "2026-06-14T15:41:03+00:00",
  "directories": {
    "wiki": {"files": 130, "bytes": 1687000, "size_human": "1.6 MB"},
    ...
  },
  "total_files": 376,
  "total_bytes": 467500000,
  "total_human": "445.8 MB"
}
```

### Типичные сценарии

| Сценарий | Команда |
|---|---|
| **Ежедневный бэкап** | `python _tech/scripts/backup_data.py --no-extracted` |
| **Перед большими изменениями** | `python _tech/scripts/backup_data.py` (полный) |
| **Перенос на другой компьютер** | `python _tech/scripts/backup_data.py --output-dir D:/USB/backups` |
| **В CI/CD** | `python _tech/scripts/backup_data.py --json` |
| **Только знания (лёгкий)** | `python _tech/scripts/backup_data.py --no-specs --no-extracted --no-clippings` |

---

## 2. sync_data.py — синхронизация между проектами

Читает бэкап (ZIP от `backup_data.py`) и переносит Data в другой проект ObsidianDB.

### Главное правило

**Сначала dry-run, потом apply.** Dry-run показывает что изменится, apply применяет.

### Базовое использование

```bash
# 1. ПОСМОТРЕТЬ что изменится (без реальных изменений)
python _tech/scripts/sync_data.py D:/USB/backups/obsidiandb-data-2026-06-14.zip

# Вывод:
#   NEW — будут добавлены: 15 files (3.2 MB)
#     wiki/concepts/NR_RRC.md
#     Specifications/ETSI_3GPP/Security/ts_33501.pdf
#     ...
#   SKIP — пропущены: 130 files (1.6 MB)
#   ...
#   Dry run — 15 changes would be applied.

# 2. ПРИМЕНИТЬ (если dry-run устроил)
python _tech/scripts/sync_data.py D:/USB/backups/obsidiandb-data-2026-06-14.zip --apply
```

### Стратегии при конфликтах

Конфликт = файл из бэкапа уже существует в целевом проекте, но с другим размером.

```bash
# SKIP — не трогать существующие (по умолчанию, безопасно)
python _tech/scripts/sync_data.py backup.zip --apply
python _tech/scripts/sync_data.py backup.zip --apply --strategy skip

# OVERWRITE — заменить существующие версиями из бэкапа
# Используй когда: хочешь обновить старые спецификации до новых версий
python _tech/scripts/sync_data.py backup.zip --apply --strategy overwrite

# BACKUP — старый файл → .bak, новый из бэкапа
# Используй когда: хочешь обновиться но сохранить старую версию на всякий случай
python _tech/scripts/sync_data.py backup.zip --apply --strategy backup
```

### Частичная синхронизация

```bash
# Только wiki + notes (перенести знания и заметки, без спецификаций)
python _tech/scripts/sync_data.py backup.zip --apply --only wiki,notes

# Только Specifications/ (добавить спецификации в новый проект)
python _tech/scripts/sync_data.py backup.zip --apply --only Specifications

# Обновить specs-extracted/ (эталонные тексты из другого проекта)
python _tech/scripts/sync_data.py backup.zip --apply --only specs-extracted
```

### Синхронизация между проектами

```bash
# Перенести Data из Проекта А в Проект Б
python _tech/scripts/sync_data.py ^
    D:/backups/obsidiandb-data-2026-06-14.zip ^
    --apply ^
    --output-dir D:/ObsidianDB-New

# ⚠️ Важно: после cross-project синхронизации wikilinks могут указывать
# на старый vault. Запусти Linker для перелинковки:
#   /lint --deep
```

### Cross-project предупреждения

При синхронизации **между разными проектами** скрипт выводит:

```
[sync] ⚠️  CROSS-PROJECT sync: backup.zip → D:/OtherProject
[sync]    wikilinks внутри wiki/ содержат пути относительно исходного vault.
[sync]    После синхронизации запусти Linker для перелинковки.
```

**После cross-project sync обязательно**:
1. Запусти `/lint --deep` — проверит битые ссылки
2. Запусти `Linker` — перелинкует wikilinks под новый vault
3. Проверь `Specifications/.category-map.md` — пути к спецификациям могут отличаться

---

## Типичный workflow: перенос проекта на новый компьютер

```bash
# === НА СТАРОМ КОМПЬЮТЕРЕ ===
cd D:\ObsidianDB
python _tech/scripts/backup_data.py --output-dir D:/USB/transfer

# → D:/USB/transfer/obsidiandb-data-2026-06-14.zip

# === НА НОВОМ КОМПЬЮТЕРЕ ===
# 1. Клонируем Core (движок)
git clone <repo-url> D:\ObsidianDB-New
cd D:\ObsidianDB-New

# 2. Устанавливаем окружение
uv sync

# 3. Смотрим что попадёт из бэкапа
python _tech/scripts/sync_data.py D:/USB/transfer/obsidiandb-data-2026-06-14.zip

# 4. Применяем
python _tech/scripts/sync_data.py D:/USB/transfer/obsidiandb-data-2026-06-14.zip --apply

# 5. Перелинковываем wikilinks под новый vault
#    (запусти Linker agent через Claude Code)

# 6. Проверяем здоровье
#    /lint --deep
```

## Типичный workflow: поделиться спецификациями с коллегой

```bash
# === ВАШ ПРОЕКТ ===
# Бэкапим только спецификации
python _tech/scripts/backup_data.py --no-wiki --no-extracted --no-notes --no-clippings

# → _backups/obsidiandb-data-2026-06-14.zip (только Specifications/)

# === ПРОЕКТ КОЛЛЕГИ ===
# Он смотрит что добавляется
python _tech/scripts/sync_data.py obsidiandb-data.zip

# Применяет только новые спецификации (существующие не трогает)
python _tech/scripts/sync_data.py obsidiandb-data.zip --apply --strategy skip
```

## Типичный workflow: еженедельный бэкап через планировщик Windows

```powershell
# Создать задачу в Task Scheduler:
# Trigger: Weekly, Sunday 03:00
# Action: Start a program
#   Program: python
#   Arguments: D:\ObsidianDB\_tech\scripts\backup_data.py --no-extracted --json
#   Start in: D:\ObsidianDB
```

Или одной строкой в PowerShell:
```powershell
python D:\ObsidianDB\_tech\scripts\backup_data.py --no-extracted --output-dir D:\Backups\ObsidianDB
```

---

## Что НЕ делают скрипты

- **НЕ бэкапят Core** (`.claude/`, `_pipeline/`, `_tech/`) — Core версионируется в git
- **НЕ бэкапят кэш** (`.speckit/`, `.venv/`) — восстанавливается через `uv sync` и `python -m _pipeline metadata fetch`
- **НЕ бэкапят сгенерированные артефакты** (`graphify-out/`, `outputs/`) — перегенерируются
- **НЕ решают конфликты wikilinks** — после cross-project sync нужен Linker
- **НЕ сжимают если не указано** — уровень сжатия по умолчанию 6 (хороший баланс скорость/размер)

---

*Инструкция актуальна на 2026-06-14. Скрипты: `backup_data.py` v1.0, `sync_data.py` v1.0.*
