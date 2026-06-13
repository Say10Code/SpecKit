---
tags: [thesis, SIM, JavaCard, overview, summary]
source: "[[Specifications/Tutorials/SIM_cards_thesis_text.txt]]"
type: thesis
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# SIM Cards for Cellular Networks (B.Sc. Thesis)

> **Автор**: Peter Edsbäcker, Mid Sweden University
> **Дата**: 2010-06-12 — 2011-06-12
> **Объём**: 31 699 слов (с приложениями)

## Обзор

Дипломная работа, служащая введением в разработку приложений для SIM-карт. Охватывает: архитектуру смарт-карт, Java Card, SIM Toolkit, стандарты GSM/3G/LTE, практическую разработку с Gemalto Developer Suite. ^[extracted]

Несмотря на возраст (2010-2011), многие концептуальные разделы остаются актуальными: архитектура UICC, Java Card 2.x, STK, AID, GlobalPlatform.

## Ключевые темы

### 1. Смарт-карты (§2)
- Аппаратная платформа: CPU (8/16/32-bit), RAM (2-8 KB), EEPROM (32-128 KB), ROM
- Программная платформа: Native OS → Java Card → GlobalPlatform → Applets
- Типичные применения: финансы (EMV), ID-карты, SIM

### 2. SIM и сотовые сети (§3)
- Эволюция: GSM → CDMAone/CDMA2000 → UMTS → LTE
- Типы SIM-карт: ID-1, Plug-in, Mini-UICC (3FF)
- Генерации SIM: SIM→USIM→CSIM→ISIM
- GSM-аутентификация: RAND → COMP128 → SRES + Kc

### 3. Разработка (§4)
- Получение SIM-карт для разработки (Gemalto, G+D)
- Среды: Gemalto Developer Suite (коммерческая), Eclipse + ant-javacad
- Java Card 2.x ограничения: нет String, Thread, double, GC
- Java Card 3.x Connected Edition: сервлеты, TCP/IP
- Память: Transient (RAM) vs Persistent (EEPROM)
- Пакеты: `javacard.framework`, `javacard.security`, `sim.toolkit`, `sim.access`

### 4. Загрузка (§5)
- Компиляция: `.java` → `.class` (javac 1.1) → `.cap` (converter)
- Аутентификация: Secure Channel (KIC, KID, KIK)
- Установка: INSTALL [for install], DELETE

### 5. SIM Toolkit (§6)
- Проактивные команды: DISPLAY TEXT, GET INPUT, SET UP MENU, SEND SMS...
- Регистрация меню: `ToolkitRegistry.initMenuEntry()`
- ProactiveHandler: формирование команд
- ProactiveResponseHandler: получение ответа
- События: MT call, location update, idle screen

## Актуальность

Многие разделы перекрываются более новыми источниками (TCA Stepping Stones 2024, ETSI Release 18), но работа ценна как исторический контекст и введение для начинающих.

## Связи

- JavaCard: [[wiki/concepts/JavaCard]]
- STK: [[wiki/concepts/STK_Applet]]
- Более новый учебник: [[wiki/summaries/java_card_stepping_stones]]
