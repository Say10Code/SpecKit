---
tags: [RuimTools, JavaCard, guidelines, clipping, summary]
source: "[[Clippings/RuimTools JavaCard best programming guidelines.md]]"
type: article
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# RuimTools: JavaCard Best Programming Guidelines

> **Источник**: http://www.ruimtools.com/doc.php?doc=jc_best
> **Извлечено**: 2026-05-31

## Обзор

Практическое руководство по оптимизации Java Card апплетов. Сфокусировано на трёх аспектах: **design**, **memory**, **speed**. Отличается конкретными примерами кода «до/после оптимизации». ^[extracted]

## Ключевые рекомендации

### Design (Проектирование)
- Java Card — НЕ Java. OO-дизайн вреден для смарт-карт
- Минимум классов (1-10), минимум иерархии (≤3 уровня)
- Избегать design patterns — они увеличивают CAP
- Избегать get()/set() — поднимать видимость полей
- Память выделять в конструкторе (install time) — не в process()

### Memory (Память)
- Кластеры: ОС выделяет память блоками по 32 байта
- 6 маленьких массивов → 9 кластеров (288 байт); 1 большой массив → 5 кластеров (160 байт)
- static поля примитивов занимают 1 байт EEPROM (не 2)
- Объектный заголовок: 6 байт (объекты), 8 байт (primitive arrays), 12 байт (object arrays)
- Transient массивы — для временных данных (RAM)

### Speed (Скорость)
- EEPROM запись в ~1000× медленнее RAM
- static/private/final методы быстрее из-за отсутствия dynamic binding
- Native API (Util.arrayCopy, etc.) на порядок быстрее
- Использовать возвращаемые значения API (offset = Util.setShort(...))
- Проверять CLA+INS в одном switch (Util.getShort())
- Не использовать исключения для flow control

## Конкретные примеры оптимизации

- **SMS packing**: использовать APDU buffer вместо new byte[]
- **Loop optimization**: выносить array.length из цикла
- **Local variables**: кешировать instance fields в локальные переменные
- **Switch/case**: одна локальная переменная перед switch (не в каждом case)
- **Transactions**: использовать только когда реально нужна атомарность

## Связи

- Платформа: [[wiki/concepts/JavaCard]]
- Разработка: [[wiki/concepts/JavaCard_Applet_Development]]
- TCA-учебник: [[wiki/summaries/java_card_stepping_stones]]
- Примеры: [[wiki/summaries/ruimtools_javacard_samples]]
