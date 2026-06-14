# Review: operator_icons_on_sim.md

> **Reviewer v3** | Pass 1 (hybrid TXT/MD/JSON) | 2026-06-14
> **Спецификации**: TS 31.102 v17.10.0, TS 102 221 v18.2.0, TS 102 223 v18.2.0
> **Метод**: TXT Grep (FID/CLA) + JSON lookup (таблицы) + MD read (контекст)

---

## Вердикт: ❌ FAIL — 3 CRITICAL, 5 HIGH, 4 MEDIUM

---

## 🔴 CRITICAL — неверные FID и структура

### C1: EF_SPNI FID = 0x6FD7 → неверно. Правильно: 0x6FDE

| Поле | Wiki утверждает | Спецификация говорит |
|---|---|---|
| FID | `0x6FD7` | **`0x6FDE`** (TS 31.102 v17.10.0, §4.2.88) |
| Структура | Transparent | Transparent ✅ (структура верна) |

**Источник**: `specs-extracted/ETSI_3GPP/USIM/ts_131102v171000p.pdf.txt`:

```
4.2.88 EF SPNI (Service Provider Name Icon)
Identifier: '6FDE' Structure: transparent Optional
```

FID `0x6FD7` принадлежал EF_SPNI в **старых версиях** spec-а (до Release 13). В текущем Release 17 это **MBMS Service Keys List**. Использование старого FID сломает чтение/запись на современных UICC.

### C2: EF_PNNI FID = 0x6FD8 → неверно. Правильно: 0x6FDF

| Поле | Wiki утверждает | Спецификация говорит |
|---|---|---|
| FID | `0x6FD8` | **`0x6FDF`** (TS 31.102 v17.10.0, §4.2.89) |
| Структура | **Transparent** | **Linear fixed** |

**Источник**: там же:

```
4.2.89 EF PNNI (PLMN Network Name Icon)
Identifier: '6FDF' Structure: linear fixed Optional
```

Две ошибки в одной: и FID устарел, и структура неверна. `0x6FD8` сейчас = MBMS User Key.

### C3: «EF_PNNI содержит ОДНУ иконку на ВСЕ PNN-записи» — неверно

Wiki (строка 177): «EF_PNNI содержит **одну** иконку, которая используется для **всех** записей EF_PNN»

Спецификация (§4.2.89): **«Each record may contain one or several PLMN network name Icon TLV object(s).»**

EF_PNNI — Linear fixed EF, каждая запись которого содержит свою иконку (TLV). Разные PNN-записи могут иметь РАЗНЫЕ иконки. Это противоположно тому, что утверждает wiki.

---

## 🟡 HIGH — структурные ошибки

### H1: DF_GRAPHICS — неверное расположение

Wiki (стр. 189-195): DF_GRAPHICS = `0x5F50` внутри DF_CD (`0x5F01`) или MF (`0x3F00`)

TS 31.102 v17.10.0, §4.6.0: **DF_GRAPHICS '5F50' находится под DF_TELECOM**, не под DF_CD.

```
Спецификация:
MF (3F00)
└── DF_TELECOM (7F10)
    └── DF_GRAPHICS (5F50)
        ├── EF_IMG (4F20)
        ├── EF_IIDF (4F21)  ← не 5F21!
        └── EF_ICE_graphics
```

**Замечание**: FID `0x5F50` разделяется с **DF_HNB** в другом контексте — ambiguity не отмечено в wiki.

### H2: EF_IIDF FID = 0x5F21 → возможно неверен

Wiki утверждает FID = `0x5F21`. В TS 31.102 §4.6.1.2 параметры EF_IIDF не используют `5F21` явно. Согласно структуре DF_GRAPHICS, **EF_IMG = 4F20, EF_IIDF = 4F21** (внутри DF_TELECOM). FID `5F21` не подтверждён. Требуется перепроверка.

### H3: EF_LAUNCH_PAD (0x4F21) — не найден в извлечённых спецификациях

Wiki утверждает FID = `0x4F21` в DF_CD. В TS 102 223 v18.2.0 TXT термин "LAUNCH_PAD" не обнаружен. FID `4F21` может коллидировать с EF_IIDF внутри DF_GRAPHICS. Требуется проверка в других версиях CAT-спецификации.

### H4: Номера сервисов для SPNI/PNNI не указаны

Wiki в сравнительной таблице (§6) указывает «USIM Service 12 (SPN)» для EF_SPNI. Это **неверно**:
- **Service 12** = EF_SPN (текст)
- **Service 78** = EF_SPNI (иконка) ← не указан в wiki
- **Service 79** = EF_PNNI ← не указан в wiki

**Источник**: TS 31.102 v17.10.0 — Service table: «Service n°78 Service Provider Name Icon», «Service n°79 PLMN Network Name Icon».

### H5: Номера разделов устарели

Wiki: EF_SPNI «Clause 4.2.82», EF_PNNI «Clause 4.2.83». В TS 31.102 v17.10.0:
- EF_SPNI = **§4.2.88**
- EF_PNNI = **§4.2.89**

6 новых EF добавлено между v10 и v17 — нумерация сдвинулась.

---

## 🟢 MEDIUM — требуется уточнение

### M1: Таблица Image Coding — не верифицирована

Wiki (§2.4): коды `0x01=PNG, 0x02=JPEG, 0x03=BMP, 0x11=PNG colour, 0x21=PNG transparency`. Значения не найдены в извлечённых текстах TS 102 221 v18. Требуется проверка в Annex H.

### M2: Terminal Profile byte map — частичная верификация

Wiki (§4.1): Byte 7 Bit 7 = Icon support, Byte 9 Bit 1 = SPN Icon, Byte 9 Bit 2 = PNN Icon, Byte 25 Bit 1 = Image support. Структура TERMINAL PROFILE определена в TS 102 223 §5.2, но побайтовая карта не извлечена из TXT — не могу подтвердить/опровергнуть. Требуется Docling-извлечение TS 102 223 с таблицами.

### M3: PNG requirements — не верифицированы

Wiki (§3.2): максимальный размер 64x64, 8-bit indexed предпочтителен. Эти значения — отраслевая практика, не нормативные требования спецификации. Стоит явно указать это различие.

### M4: Таблица совместимости телефонов — без ссылок

Wiki (§8.5): таблица «Samsung Galaxy: Да» и т.д. — основана на «тестах сообщества Osmocom и pySim». Нет ссылок на конкретные отчёты/issue. Стоит добавить источники.

---

## ✅ CORRECT — подтверждённые утверждения

- EF_SPN FID = `0x6F46` ✅
- EF_PNN FID = `0x6FC5` ✅
- EF_OPL FID = `0x6FC6` ✅
- TERMINAL PROFILE command INS = `0x70` ✅
- EF_UST FID = `0x6F38` ✅
- DF_CD FID = `0x5F01` ✅
- EF_IMG exists under DF_GRAPHICS (TS 31.102 §4.6.1.1) ✅
- EF_IIDF exists under DF_GRAPHICS (TS 31.102 §4.6.1.2) ✅
- PNG обязателен для UICC ✅
- iPhone не поддерживает EF_SPNI/PNNI ✅ (общеизвестный факт)
- Структура EF_SPNI = Transparent ✅ (только FID неверен)
- EF_SPN Display Condition байт 0 ✅

---

## 📋 Сводка

| Уровень | Количество | Ключевое |
|---|---|---|
| 🔴 CRITICAL | 3 | FID'ы SPNI/PNNI устарели, структура PNNI неверна |
| 🟡 HIGH | 5 | DF_GRAPHICS не там, EF_IIDF/LAUNCH_PAD FID под вопросом, номера сервисов |
| 🟢 MEDIUM | 4 | Image coding, Terminal Profile, PNG reqs, таблица телефонов |
| ✅ CORRECT | 11 | Большинство базовых FID'ов, протокольных констант |

**Причина ошибок**: страница написана по старым версиям спецификаций (Release 6-10). TS 31.102 прошёл через значительную реструктуризацию между Release 10 и 17 — FID'ы `6FD7`/`6FD8` были перемещены на `6FDE`/`6FDF`, структура PNNI изменена с transparent на linear fixed, DF_GRAPHICS перемещён под DF_TELECOM.

**Рекомендация**: переписать разделы 2.1, 2.2, 2.3, 2.4 с использованием TS 31.102 v17.10.0 как эталона. Обновить все FID'ы, структуры, номера сервисов и расположение DF_GRAPHICS.
