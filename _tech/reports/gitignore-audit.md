# .gitignore — аудит и исправление

> **Дата**: 2026-06-13 14:20
> **Цель**: Проверить что `.gitignore` покрывает всё лишнее и не исключает нужное перед `git init`

---

## 1. Инвентаризация проекта

### Структура на диске

| Путь | Размер | Тип | В git? | Почему |
|---|---|---|---|---|
| `.3gpp-crawler/` | ~50 MB | Кэш spec-crawler | ❌ Игнор | ✅ Уже в .gitignore |
| `.claude/` | ~50 KB | Агенты + skills | ✅ Коммит | Ядро AI-логики |
| `.claudian/` | ~8 KB | Сессии Claude | ❌ Игнор | ⚠️ Только `sessions/`, не хватает `claudian-settings.json` |
| `.obsidian/` | ~100 KB | Obsidian config | ⚠️ Частично | `workspace.json` игнорится, остальное надо коммитить |
| `.obsidian/plugins/` | ~5 MB | Плагины (бинарные) | ❌ Игнор | ❌ НЕ в .gitignore! |
| `.git/` | — | Git сам | Авто | — |
| `_tech/` | ~200 KB | Тех. документация | ✅ Коммит | Архитектурный анализ |
| `3gpp-crawler/` | ~500 MB | Исходники + .venv | ❌ Игнор | 🔴 Имеет свой `.git/` → submodule conflict! |
| `Clippings/` | ~42 KB | Веб-клиппинги | ✅ Коммит | Исходный материал (read-only) |
| `notes/` | ~20 KB | Заметки | ✅ Коммит | Пользовательские заметки |
| `outputs/` | ~160 KB | Отчёты + HTML | ⚠️ Частично | HTML — сгенерированный, MD — проектные документы |
| `raw/` | 0 KB (пусто) | Temp input | ❌ Игнор | ❌ НЕ в .gitignore |
| `Specifications/` | 88 MB | Исходные PDF | ✅ Коммит | Источник истины |
| `specs-extracted/` | 205 MB | Извлечённый текст | ❌ Игнор | 🔴 НЕ в .gitignore! 205 MB! |
| `wiki/` | 1.9 MB | База знаний | ✅ Коммит | Ядро проекта |

### Файлы в корне

| Файл | Размер | В git? | Почему |
|---|---|---|---|
| `CLAUDE.md` | 13 KB | ✅ Коммит | Главный AI-контекст |
| `Roadmap.md` | 10 KB | ✅ Коммит | Дорожная карта |
| `.gitignore` | 0.3 KB | ✅ Коммит | Сам себя |
| `3gpp-crawler.toml` | 0.5 KB | ✅ Коммит | Конфиг spec-crawler |
| `Добро пожаловать.md` | 2 KB | ✅ Коммит | Welcome-страница |
| `_build_html.py` | 19 KB | ⚠️ Спорно | Одноразовый скрипт → `_tech/scripts/` |
| `_convert_research.py` | 8 KB | ⚠️ Спорно | Одноразовый скрипт → `_tech/scripts/` |
| `2026-04-30.md` | 35 B | ❌ Игнор | Личная заметка «День открытия Obsidian!» |

---

## 2. Найденные проблемы (8)

| # | Проблема | Серьёзность | Что произойдёт без исправления |
|---|---|---|---|
| **G1** | `3gpp-crawler/` не в .gitignore | 🔴 CRITICAL | Git увидит вложенный `.git/` → submodule conflict. Ошибка при `git add`. |
| **G2** | `specs-extracted/` не в .gitignore | 🔴 CRITICAL | 205 MB сгенерированных данных попадёт в репо. Каждый `git clone` = +205 MB. |
| **G3** | `.claudian/` не полностью игнорится | 🟡 HIGH | `claudian-settings.json` (7 KB) попадёт в репо. Сессионные данные. |
| **G4** | `.obsidian/plugins/` не игнорится | 🟡 HIGH | ~5 MB скомпилированных плагинов. Переустанавливаются Obsidian автоматически. |
| **G5** | `raw/` не в .gitignore | 🟢 MEDIUM | Пустая сейчас, но задумана как temp-директория. |
| **G6** | `outputs/*.html` не игнорится | 🟢 MEDIUM | 144 KB сгенерированных HTML. |
| **G7** | `_build_html.py`, `_convert_research.py` в корне | 🟢 MEDIUM | Одноразовые скрипты с хардкод-путями. Захламляют корень. |
| **G8** | `2026-04-30.md` в корне | 🔵 LOW | Личная заметка, не часть проекта. |

---

## 3. Исправленный `.gitignore`

```gitignore
# ── 3gpp-crawler: кэш + исходники ────────────────────
# Кэш spec-crawler (БД + HTTP-кэш + workspace artifacts — ~50 MB)
.3gpp-crawler/
# Исходники 3gpp-crawler (имеют свой .git/ — избегаем submodule conflict)
3gpp-crawler/

# ── Сгенерированные данные ────────────────────────────
# Извлечённые тексты спецификаций (205 MB — перегенерируются SpecExtractor'ом)
specs-extracted/
# Сгенерированные HTML-отчёты
outputs/*.html

# ── Obsidian: волатильные файлы ───────────────────────
.obsidian/workspace.json
.obsidian/plugins/
.trash/

# ── Claude Code: сессии ───────────────────────────────
.claudian/

# ── Temp и мусор ──────────────────────────────────────
raw/
__pycache__/
*.pyc
.venv/
```

---

## 4. Рекомендации (не .gitignore, но связанные)

| # | Рекомендация | Почему |
|---|---|---|
| **R1** | Перенести `_build_html.py` → `_tech/scripts/build_html.py` | Захламляет корень. Уже есть `_tech/scripts/`. |
| **R2** | Перенести `_convert_research.py` → `_tech/scripts/convert_research.py` | Аналогично. |
| **R3** | Перенести `2026-04-30.md` → `notes/` или удалить | Личная заметка. |
| **R4** | Удалить `outputs/IMPROVEMENT_PLAN.md` | Дубликат `_tech/plans/IMPROVEMENT_PLAN.md`. |
| **R5** | `Specifications/` (88 MB) оставить в git | Это исходные PDF — источник истины. Без них клон бесполезен. |
| **R6** | `specs-extracted/` добавить в `.gitignore` | 205 MB. Генерируется SpecExtractor'ом. В README описать как восстановить. |

## 5. Что БУДЕТ в git (после исправлений)

| Категория | Размер | Файлов |
|---|---|---|
| Агенты + skills + шаблоны | ~80 KB | 20 |
| wiki/ (база знаний) | 1.9 MB | 129+7 |
| Specifications/ (исходные PDF) | 88 MB | 65 |
| _tech/ (тех. документация) | ~200 KB | 25 |
| Clippings/ + notes/ + outputs/*.md | ~100 KB | 12 |
| Корневые файлы | ~30 KB | 6 |
| **Итого (без specs-extracted и 3gpp-crawler)** | **~90 MB** | **~237** |

---

*Аудит завершён 2026-06-13 14:20. `.gitignore` готов к исправлению.*
