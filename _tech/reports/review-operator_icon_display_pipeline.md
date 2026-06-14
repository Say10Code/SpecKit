# Review: operator_icon_display_pipeline.md

> **Дата**: 2026-06-14 · **Reviewer v3** · **Форматы**: TXT (TS 31.102 R16 flat) + MD (TS 31.102 R19.4 Docling)

## Форматы в specs-extracted/

| Спецификация | TXT | MD | JSON |
|---|---|---|---|
| TS 31.102 Rel 16 | ✅ `31_102-REL16_31102-gf0.txt` | ❌ | ❌ |
| TS 31.102 Rel 17 | ✅ `31_102-REL17_31102-hg0.txt` | ❌ | ❌ |
| TS 31.102 Rel 19.4 | — | ✅ `31102-j40.md` | ✅ `31102-j40.json` |

---

## Pass 1: Техническая точность

| # | Утверждение | Метод | Спецификация (раздел) | Вердикт |
|---|---|---|---|---|
| 1 | EF_SPN FID = `6F46` | TXT Grep | TS 31.102 R16 §4.2.12 (строка 1522) | ✅ CORRECT |
| 2 | EF_SPNI FID = `6FDE` | TXT Grep | TS 31.102 R16 §4.2.88 (строка 4193) | ✅ CORRECT |
| 3 | Service n°19 required for SPN | TXT Grep | TS 31.102 R16 (строка 1300) | ✅ CORRECT |
| 4 | Service n°78 required for SPN Icon | TXT Grep | TS 31.102 R16 (строка 1359) | ✅ CORRECT |
| 5 | Icon Qualifier '01' = self-explanatory | TXT Grep + MD | TS 31.102 R16 §4.2.88 (строка 4222) | ✅ CORRECT |
| 6 | Icon Qualifier '02' = not self-explanatory | TXT Grep + MD | TS 31.102 R16 §4.2.88 (строка 4223) | ✅ CORRECT |
| 7 | Icon Tag '80' = URI link | MD | TS 31.102 R19.4 §4.2.88 (строка 5907, Note 1) | ✅ CORRECT |
| 8 | Icon Tag '81' = EF_IMG record number | MD | TS 31.102 R19.4 §4.2.88 (строка 5915) | ✅ CORRECT |
| 9 | ME reading procedure §5.3.37 for SPN Icon | TXT | TS 31.102 R16 (строка 10339-10341) | ✅ CORRECT |
| 10 | EF_PNNI содержит ровно одно изображение | — | Не верифицировано (источник — sim_files_graphics.md) | ⚠️ NEEDS_SPEC |

**10 проверено: 9 CORRECT, 0 INCORRECT, 1 NEEDS_SPEC**

**Комментарий к #10**: Утверждение из раздела 2.6 «EF_PNNI содержит ровно одно изображение» — sourced from synthesis page, не из первичной спецификации. Требует прямой проверки по TS 31.102 §4.2.89 (EF_PNNI).

---

## Pass 2: Структура и читабельность

- ✅ Frontmatter: 7 тегов, type=research, status=draft, created/updated, 9 источников
- ✅ Mermaid: 2 диаграммы (sequence + flowchart), синтаксис валидный, ASCII-стрелки
- ❌ Callouts: отсутствуют. Рекомендация: `> [!seealso]` для перекрёстных ссылок в разделе 5 (Render Pipeline)
- ✅ Заголовки: иерархия `## → ### → ####` соблюдена
- ✅ Provenance: `^[extracted]` и `^[inferred]` присутствуют
- ⚠️ Раздел 2.1 «При персонализации» — дерево файлов в кодовом блоке. Лучше Mermaid или таблица

---

## Pass 3: Связность

- **Inbound**: 4 (index.md, USIM.md, sim_files_graphics.md, sim_files_operator_name.md)
- **Outbound**: 14 wikilinks — все валидны ✅
- **Orphan**: Нет — страница сразу получила 4 входящих ссылки
- **Рекомендации**: добавить ссылку из `OTA_Remote_Management.md` (там есть раздел про OTA-обновление EF)

---

## Итого

| Категория | Найдено |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 2 (⚠️) |
| NEEDS_SPEC | 1 |
| **Общая оценка** | **✅ PASS** |

---

## Обратная связь (R4: Reviewer → Author)

**Исправления (Pass 2 — Low):**

1. **LOW**: Добавить callout `> [!seealso]` в раздел 5 (Render Pipeline) со ссылкой на `sim_files_graphics.md`:
   ```markdown
   > [!seealso] Структуры файлов
   > Детальное описание EF_IMG/EF_IIDF/EF_ICON — в [[wiki/syntheses/sim_files_graphics|Графика и иконки]].
   ```

2. **LOW**: Раздел 2.1 — заменить кодовый блок с деревом файлов на Mermaid-диаграмму для лучшей читабельности.

**Требует спецификации (Pass 1):**

3. **NEEDS_SPEC**: Утверждение #10 (EF_PNNI — ровно одно изображение). Проверить по TS 31.102 §4.2.89. После верификации — пометить `^[extracted]` или `^[inferred]`.

---

*Review completed 2026-06-14. 9/10 CORRECT, 0 INCORRECT, 1 NEEDS_SPEC.*
