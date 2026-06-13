---
tags: [smart-card, security, thesis, side-channel, summary]
source: "[[Specifications/Books/Outsmarting_Smart_Cards.pdf]]"
type: thesis
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# Outsmarting Smart Cards (PhD Thesis, 2013)

> **Автор**: Gerhard de Koning Gans, Radboud University Nijmegen
> **Научные руководители**: Prof. B.P.F. Jacobs, Dr. F.D. Garcia
> **Дата**: 11 апреля 2013
> **Страниц**: 200
> **ISBN**: 978-94-6191-675-4

## Обзор

Докторская диссертация о **безопасности смарт-карт**. Методология: дизайн, реализация и атаки. Охватывает платёжные (EMV), транспортные (MIFARE, OV-chipkaart) и SIM-карты. Глубокий анализ side-channel атак, reverse engineering и формальной верификации. ^[inferred]

## Ключевые темы

### 1. Платёжные системы (EMV)
- Анализ безопасности EMV (Europay-MasterCard-Visa)
- Математические модели DDA/CDA (Dynamic/Combined Data Authentication)
- Уязвимости в реализации EMV-терминалов

### 2. Транспортные карты (MIFARE, OV-chipkaart)
- Взлом MIFARE Classic (CRYPTO1 — 48-bit stream cipher)
- Анализ голландской транспортной карты OV-chipkaart
- Практические последствия взлома (2008 — media storm)

### 3. e-Passports
- Моделирование безопасности RFID-паспортов
- BAC (Basic Access Control), EAC (Extended Access Control)

### 4. Методология reverse engineering
- Side-channel анализ: power analysis (SPA/DPA), timing attacks
- Программный reverse engineering прошивок смарт-карт
- Fuzzing, black-box тестирование

### 5. SIM-карты
- Анализ алгоритмов аутентификации GSM (COMP128-1/2/3)
- Теоретические основы атак на SIM
- В контексте более широкого анализа безопасности

## Актуальность для проекта

- **Безопасность UICC**: понимание уязвимостей → более безопасные STK-апплеты
- **Side-channel awareness**: разработчики JavaCard должны знать о timing/DPA атаках
- См. TCA Stepping Stones §7 — security recommendations базируются на подобных исследованиях

## Связи

- Безопасность UICC: [[wiki/concepts/UICC_Security]]
- TCA security best practices: [[wiki/summaries/java_card_stepping_stones]]
- RuimTools security guidelines: [[wiki/summaries/ruimtools_javacard_guidelines]]
- Аутентификация GSM: [[wiki/syntheses/auth_evolution]]
