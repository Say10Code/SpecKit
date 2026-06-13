# План переименования: Specifications → Specifications

> **Дата**: 2026-06-13
> **Причина**: pymupdf/docling C++ слой не принимает кириллические пути → `std::bad_alloc` и «not valid» ошибки
> **Цель**: 100% ASCII-пути для всех файлов с которыми работают внешние тулзы (Docling, PyMuPDF, spec-crawler)

---

## 1. Что ломается из-за кириллицы

| Инструмент | Ошибка | Причина |
|---|---|---|
| **pymupdf** (Docling backend) | `Input document is not valid` | C++ слой fpdf не парсит кириллические пути |
| **Bash** (git-bash) | `Бла...` (mojibake) | Несоответствие кодировок между bash и NTFS |
| **PowerShell** | `std::bad_alloc` на определённых страницах | PIL/pypdfium2 не может выделить буфер для рендера |

**Временный workaround**: копирование PDF во временную ASCII-директорию → Docling → удаление копии. Работает, но медленно (×2 время из-за копирования).

## 2. Объём изменений

| Локация | Файлов | Упоминаний `Specifications` | Тип ссылок |
|---|---|---|---|
| `CLAUDE.md` | 1 | 18 | Абсолютные пути, markdown |
| `.claude/CLAUDE.md` | 1 | 1 | Текст |
| `.claude/agents/*.md` | 5 | ~20 | Пути к PDF, wikilinks |
| `.claude/skills/*.md` | 1 | 10 | Пути |
| `Roadmap.md` | 1 | 3 | Текст |
| `wiki/**/*.md` | **129** | **~400** | Wikilinks `[[Specifications/...]]` |
| `notes/*.md` | 4 | ~5 | Wikilinks |
| `outputs/*.md` | 2 | ~5 | Wikilinks |
| `specs-extracted/INDEX.md` | 1 | ~60 | Пути |
| `3gpp-crawler.toml` | 1 | 1 | TOML |
| `_tech/**/*.md` | 9 | 34 | Пути, markdown |
| `_tech/scripts/*.py` | 2 | 2 | Python str |
| **Всего** | **~160** | **~560** | — |

## 3. План миграции

### Фаза 1: Переименование директории (Windows)

```powershell
# Ничего не ломает — Windows понимает оба имени.
# Obsidian авто-обновит wikilinks ЕСЛИ включено "Automatically update internal links"
Rename-Item "D:\ObsidianDB\Specifications" "Specifications"
```

### Фаза 2: Поиск+замена во всех .md файлах

```powershell
$files = Get-ChildItem "D:\ObsidianDB" -Recurse -Include "*.md" | 
    Where-Object { $_.FullName -notmatch '\\(\.obsidian|\.claudian|\.claude\\skills|\.claude\\agents)\\?' }

foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    if ($content -match 'Specifications') {
        $new = $content -replace 'Specifications', 'Specifications'
        Set-Content $f.FullName -Value $new -Encoding UTF8 -NoNewline
    }
}
```

### Фаза 3: Обновить пути в .py и .toml

- `3gpp-crawler.toml`: `checkout-dir` путь
- `_tech/scripts/*.py`: жёстко закодированные пути

### Фаза 4: Обновить CLAUDE.md

Вручную проверить все 18 упоминаний — особенно пути к директориям.

### Фаза 5: Верификация

```bash
# Проверить что НИ ОДНОГО упоминания "Specifications" не осталось
grep -r "Specifications" D:/ObsidianDB --include="*.md" --include="*.py" --include="*.toml"
# Должен вернуть пустой результат
```

## 4. Риски

| Риск | Вероятность | Митигация |
|---|---|---|
| Obsidian не авто-обновит wikilinks | Высокая | Проверить настройку "Automatically update internal links"; если выключена — ручная замена |
| `[[Specifications/...]]` в wiki/ сломаются | Средняя | Фаза 2 делает поиск+замену во ВСЕХ .md файлах, включая wiki/ |
| `specs-extracted/` структура нарушится | Низкая | Там уже латиница |
| `!INCOMING` и `!double` внутри `Specifications/` | Низкая | Переименование родительской папки не трогает содержимое |
| Жёстко закодированные пути в скриптах | Средняя | Фаза 3 |

## 5. Альтернатива: не переименовывать

Если риски переименования слишком высоки (129 wiki-страниц), можно:

1. **Оставить `Specifications/` для всего кроме Docling**
2. **Создать `Specs/` (ASCII) как рабочую копию для Docling**:
   - `Specifications/` → read-only, wikilinks, Obsidian (кириллица остаётся)
   - `Specs/` → ASCII-копия, используется ТОЛЬКО Docling/PyMuPDF/spec-crawler
   - Авто-синхронизация через hardlink/junction

## 6. Рекомендация

**Фазы 1-5 выполнимы за ~5 минут** (1 команда rename + 1 скрипт поиска/замены). Obsidian при следующем запуске переиндексирует wikilinks. Риск низкий — Windows NTFS и Obsidian оба поддерживают переименование с авто-обновлением ссылок.

**Альтернатива (Specs/ копия)** проще и безопаснее, но создаёт дублирование данных (53 MB × 2).

*Решение за пользователем.*
