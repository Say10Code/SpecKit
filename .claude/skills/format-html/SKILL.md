# Skill: format-html
# Trigger: /format-html

Конвертация wiki-страницы в красивый тёмный HTML с Mermaid, callouts и таблицами.

## Структура HTML

```
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>...</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>/* тёмная тема */</style>
</head>
<body>
  <header>...</header>
  <div class="container">...контент...</div>
  <script>mermaid.initialize({theme:'dark',...})</script>
</body>
</html>
```

## Стилизация

- Тёмная тема: `background: #0d1117`, текст `#e0e0e0`
- Заголовки: h2 `#7ee787`, h3 `#a5d6ff`, h4 `#d2a8ff`
- Таблицы: `<thead>` тёмный `#1a2332`, чётные ряды `#161b22`, hover `#1c2433`
- Адаптивная: `@media (max-width: 768px)`
- Шрифт: Segoe UI, system-ui
- Моноширинный: Cascadia Code, Fira Code, Consolas

## Конвертация контента

| Markdown | HTML |
|---|---|
| `##` / `###` / `####` | `<h2>` / `<h3>` / `<h4>` |
| Markdown table | `<table>` → `<thead>` + `<tbody>`, `tr:nth-child(even)` |
| ` ```code``` ` | `<pre><code>` |
| `` `inline` `` | `<code>` |
| `**bold**` | `<strong>` |
| `*italic*` | `<em>` |
| `> [!note]` | `<div class="callout callout-note">` |
| `[[wiki/...]]` | Plain text или ссылка |

## Callout mapping

| Obsidian | CSS class |
|---|---|
| `[!note]` | `callout-note` (синий border) |
| `[!warning]` | `callout-warning` (жёлтый border) |
| `[!danger]` | `callout-danger` (красный border) |
| `[!tip]` | `callout-tip` (зелёный border) |
| `[!abstract]` | `callout-abstract` (фиолетовый border) |
| `[!info]` | `callout-info` (синий border) |
| `[!example]` | `callout-example` |

---

## 🔴 Mermaid-диаграммы — КРИТИЧЕСКИЕ ПРАВИЛА

Это ЕДИНСТВЕННЫЙ источник истины для Mermaid-правил. Все агенты ссылаются сюда.

### Извлечение и обёртка
- Извлеки блок `\`\`\`mermaid ... \`\`\`` из Markdown
- Оберни в `<div class="mermaid">`
- **НЕ преобразуй символы внутри** — HTML entity encoding ЛОМАЕТ Mermaid

### Синтаксические ограничения (ОБЯЗАТЕЛЬНО)

```
✅ РАЗРЕШЕНО:                     ❌ ЗАПРЕЩЕНО:
   ->> Target: message               &gt;&gt; Target (HTML entity!)
   -->> Target: message              &amp;gt;&amp;gt;
   Note over A,B: text               ═══ (box-drawing chars)
   participant X as Name             ─── ┌┐└┘ (box-drawing chars)
   sequenceDiagram                   ✅ (emoji)
   graph TD                          ❌ (emoji)
   style X fill:#color               → (Unicode arrow)
```

### Правила

1. **Стрелки**: ТОЛЬКО literal ASCII символы
   - `->>` — solid arrow (синхронный вызов)
   - `-->>` — dashed arrow (ответ)
   - `-->` — dashed open arrow
   - `->>|TEXT|` — arrow with label
   - `->>TARGET: MESSAGE` — arrow with message text
   - КАТЕГОРИЧЕСКИ НЕ: `&gt;`, `&amp;gt;`, `→`, any HTML entity!

2. **Текст**: ТОЛЬКО ASCII (латиница + цифры + базовые символы)
   - НЕ использовать: кириллицу в box-drawing, emoji, Unicode arrows
   - Вместо emoji: `OK`, `FAIL`, `KEY`, `IDEA`, `WARN`, `INFO`
   - Кириллица ДОПУСТИМА в обычных сообщениях (текст внутри кавычек)

3. **Разделители**: НЕ использовать `||` (двойной pipe)
   - `||` конфликтует с синтаксисом Mermaid, особенно в стрелках
   - Заменить на `/` или пробел

4. **Note блоки**: НЕ использовать `<br/>` внутри Note
   - `<br/>` не рендерится в Mermaid v10
   - Вместо этого: разделить на несколько отдельных `Note` блоков:

```
❌ ПЛОХО:
Note over X: Line 1<br/>Line 2<br/>Line 3

✅ ХОРОШО:
Note over X: Line 1
Note over X: Line 2  
Note over X: Line 3
```

5. **Специальные символы** в сообщениях (внутри кавычек):
   - `()` скобки: OK
   - `:` двоеточие: OK
   - `=` равно: OK
   - `/` слэш: OK
   - `#` решётка: OK
   - Осторожно с: `<`, `>`, `{`, `}`, `&`, `|`

### Известные ошибки и исправления

| Ошибка в HTML | Причина | Исправление |
|---|---|---|
| `Syntax error in text` | `&gt;` вместо `>` в стрелках | Использовать literal `>` |
| `Parse error on line N` | Box-drawing chars `═══` или `───` | Заменить на `===` или `---` |
| Diagram not rendering | Emoji в тексте (✅❌🔑) | Заменить на текст (OK/FAIL/KEY) |
| Arrows show as text | HTML entities в `<div class="mermaid">` | Весь Mermaid через Python raw-строку |
| `\|` breaking arrows | Двойной pipe в сообщениях | Заменить на `/` |

### Технический приём

Если Write tool экранирует символы `>` → `&gt;`, используй **Python-скрипт**:

```python
path = r'D:\ObsidianDB\outputs\file.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

mermaid_block = r'''<div class="mermaid">
sequenceDiagram
    X->>Y: message
</div>'''

start = content.find('<div class="mermaid">')
end = content.find('</div>', start) + len('</div>')
content = content[:start] + mermaid_block + content[end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
assert '->>' in open(path).read(), 'Arrows missing!'
```

### Проверка после конвертации

```bash
# Должно быть >= 5 для любой sequence diagram
grep -c '->>' outputs/имя.html

# Не должно быть HTML entities в Mermaid блоке
sed -n '/<div class="mermaid">/,/<\/div>/p' outputs/имя.html | grep -c '&gt;'  # Должно быть 0
```
