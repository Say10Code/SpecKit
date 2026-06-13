---
tags: [JavaCard, TCA, tutorial, summary]
source: "[[Specifications/JavaCard/Java-Card-Stepping-Stones_FINAL.pdf]]"
type: tutorial
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# Java Card Applet Developer Stepping Stones (TCA, 2024)

> **Издатель**: Trusted Connectivity Alliance (TCA, бывш. SimAlliance)
> **Версия**: 1.0, апрель 2024
> **Формат**: PDF + текстовая версия

## Обзор

Практическое руководство по разработке Java Card апплетов для UICC/SIM-карт. Фокусируется на **best practices**, а не на теории. Создано TCA на основе опыта производителей SIM-карт и тестовых лабораторий. ^[extracted]

### Целевая аудитория
Разработчики Java Card апплетов для SIM/UICC, уже знакомые с основами Java Card, желающие улучшить качество и интероперабельность своих приложений.

## Ключевые разделы

### 1. Экосистема Java Card Applet (§5)
- Java Card 3.0.5 и 3.1.0 Classic Edition
- Связь с GSMA и 3GPP стандартами
- SGP.22 (RSP), SGP.05 (eUICC Protection Profile)

### 2. Best Practices (§6) — Основное

#### NVM (EEPROM) Update
- Запись в NVM атомарна только внутри транзакции
- Не использовать `beginTransaction` без необходимости
- Память выделяется кластерами по 32 байта — эффективное использование критично

#### Поля и локальные переменные
- Локальные переменные быстрее instance fields (на стеке vs в EEPROM)
- Static поля для констант (не создают копий)
- Reuse локальных переменных для экономии стека

#### Удаление апплетов и конструкторы
- Все `new` должны быть в конструкторе (вызывается один раз)
- Не создавай объекты в `process()` — риск Out of Memory и замедление

#### Stack Management
- Стек ограничен (~2-4 KB)
- Глубокая вложенность: запрещена
- Рекурсия: смертельна на смарт-карте

#### Handlers (Re-entrance)
- Два апплета могут получать события параллельно (multi-selection)
- Обработчики должны быть reentrant
- Не блокировать надолго — другие апплеты ждут

#### Execution Time
- EEPROM запись: 1-10 ms на байт
- RAM запись: микросекунды
- Используй APDU buffer и transient массивы
- Native API (Util.arrayCopy, etc.) — на порядок быстрее

#### RAM Management
- Transient массивы (`JCSystem.makeTransientByteArray()`) — RAM вместо EEPROM
- CLEAR_ON_RESET vs CLEAR_ON_DESELECT
- APDU buffer — всегда доступен, используй его

### 3. Безопасность (§7)
- Изолируй crypto-операции в отдельные классы (для CC evaluation)
- Используй native crypto API (не самодельное)
- Fixed-size PIN предотвращает timing attacks
- Проверяй RSA подписи перед отправкой (anti-DFA)

### 4. Инструменты тестирования (§8)
- **TCA Loader** — установка апплетов (альтернатива gp.jar)
- **TCA eSIM Interoperability Service** — облачный сервис проверки
- **GlobalPlatform Test Fest** — ежегодные мероприятия интероп-тестирования
- **GSMA LITE Event** — тестирование eSIM

### 5. Интероперабельность (§9-10)
- Проверочные листы (checklists) для верификации апплета
- Совместимость с разными производителями SIM (G+D, Idemia, Thales, ...)
- Version matrix: Java Card × GlobalPlatform × UICC

## Ключевые выводы

1. **Минимизируй EEPROM операции** — используй RAM/APDU buffer
2. **Конструктор для аллокаций** — не в process()
3. **Native API где возможно** — не изобретай велосипед
4. **Интероперабельность через TCA инструменты** — тестируй на разных картах
5. **Безопасность с CC в виду** — изолируй чувствительные операции

## Связи

- JavaCard платформа: [[wiki/concepts/JavaCard]]
- Разработка апплетов: [[wiki/concepts/JavaCard_Applet_Development]]
- Best practices: [[wiki/summaries/ruimtools_javacard_guidelines]]
- GP-управление: [[wiki/concepts/GlobalPlatform_Card]]
- Организация: [[wiki/entities/TCA]]
