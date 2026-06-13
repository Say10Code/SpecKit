---
tags: [smart-card, Linux, HOWTO, PCSC, summary]
source: "[[Specifications/Manuals/Smart-Card-HOWTO.pdf]]"
type: tutorial
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# Smart Card HOWTO (Tolga KILIÇLI, 2001)

> **Автор**: Tolga KILIÇLI (tolga@deepnight.org)
> **Дата**: 2001, версия 1.0.4
> **Страниц**: 16

## Обзор

Краткий HOWTO по смарт-картам в Linux-окружении. Объясняет типы карт, операционные системы, программные интерфейсы (CT-API, PC/SC, OpenCard), GlobalPlatform и применение с PKI. Исторический артефакт, но полезен как введение в PC/SC. ^[inferred]

## Ключевое содержание

### Классификация смарт-карт
- **Contact** (ISO 7816) vs **Contactless** (ISO 14443)
- **Memory cards** (простое хранение) vs **Microprocessor cards** (CPU + OS)

### Программные интерфейсы для Linux
- **CT-API**: низкоуровневый, проприетарный
- **PC/SC**: стандартный API для Windows/Linux (pcsc-lite)
- **OpenCard**: Java-ориентированный framework

### Инструменты для Linux (на 2001 год)
- scas — Smart Card Application Server
- ssh-smart — SSH с аутентификацией через смарт-карту
- smartsign — цифровая подпись

### PKI и смарт-карты
Смарт-карта как защищённое хранилище приватных ключей для PKI.

## Современное состояние

Сегодня PC/SC — стандарт де-факто для взаимодействия со смарт-картами. GlobalPlatformPro и pySim работают поверх PC/SC.

## Связи

- pySim: [[wiki/summaries/osmopysim_usermanual]]
- GP-управление: [[wiki/concepts/GlobalPlatform_Card]]
