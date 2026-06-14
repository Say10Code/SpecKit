---
tags: [hub, research]
type: hub
created: 2026-06-12
updated: 2026-06-12
---

# Research: Глубокие исследования и детальные разборы

В отличие от [[wiki/summaries/index|Summaries]] (краткие конспекты 1-3 страницы), **Research** — это детальные отчёты: 5-20+ страниц глубокого анализа темы, объединяющие множество источников.

## Отличия от других разделов

| | Summaries | Syntheses | **Research** |
|---|---|---|---|
| **Глубина** | Конспект | Кросс-анализ | **Исчерпывающий разбор** |
| **Объём** | 1-3 KB | 5-15 KB | **15-50+ KB** |
| **Источников** | 1-2 | 3-7 | **5-20+** |
| **Кода** | Немного | Много | **Очень много** |
| **Таблиц/диаграмм** | Минимум | Умеренно | **Много** |
| **Создаётся** | Librarian | Synthesizer | **Researcher** |

## Когда создавать Research

- Тема требует объединения 5+ источников
- Нужен полный код (не фрагменты, а рабочий проект)
- Нужен сравнительный анализ 3+ стандартов/технологий
- Нужна пошаговая инструкция с отладкой
- Нужен математический/криптографический разбор

## Текущие Research

- [[wiki/research/milenage_vs_tuak\|MILENAGE vs TUAK]] — криптографический разбор, псевдокод, сравнительный анализ, рекомендации
- [[wiki/research/operator_icons_on_sim\|Иконки оператора на SIM-карте]] — EF_SPNI, EF_PNNI, DF_GRAPHICS, EF_ICON, TERMINAL PROFILE биты, тест-план, практический код
- [[wiki/research/auth_evolution_deep_dive\|Auth Evolution Deep Dive]] — COMP128 математический разбор, MILENAGE/TUAK полный криптоанализ, квантовая угроза, хронология инцидентов, сравнение производительности, полная EF-карта, диаграммы всех поколений

- [[wiki/research/sim_testing_deep_dive\|SIM Testing Deep Dive]] — полное практическое руководство по тестированию SIM/USIM: 8 разделов, 30+ KB, 100+ тест-кейсов, полный Python-скрипт автоматизации

- [[wiki/research/usim_ef_catalog\|EF-каталог USIM]] — исчерпывающий справочник по каждому элементарному файлу ADF.USIM: 120+ EF, 10 групп, структура byte-by-byte, hex-примеры, access conditions, Python-скрипты, 80+ KB

- [[wiki/research/plmn_selection_algorithm\|PLMN Selection Algorithm]] — полный алгоритм выбора сети от SIM к соте: 14 EF с hex-дампами, пошаговая трассировка 6 шагов, Steer of Roaming, flowchart, практический пример роуминга, 95+ KB

- [[wiki/research/sim_scws_webserver\|SIM как веб-сервер — SCWS + BIP]] — UICC как HTTP-сервер: SCWS, BIP, DF_CD, TAR B2 01 01, LAUNCH BROWSER, OTA-обновление веб-страниц, Trusted UI, IoT, банкинг, архитектурный разбор

- [[wiki/research/sim_nfc_contactless\|SIM и NFC — SWP, HCI, CLF, Contactless]] — SWP (C6), HCI поверх SWP, EMV/MIFARE на SIM, PPSE/CRS, STK contactless events, SE vs HCE безопасность, полный платёжный flow

- [[wiki/research/sim_gps_lcs\|SIM и GPS/LCS — Location Services на UICC]] — архитектура LCS (GMLC, MO-LR/MT-LR), EF_LOCI-семейство, PROVIDE LOCAL INFORMATION (STK), GAD Shapes (TS 23.032), JavaCard-код слежения, сценарии: роуминг, fleet management, гео-ограниченные услуги

- [[wiki/research/operator_icon_display_pipeline\|Отображение иконки оператора — путь от SIM до экрана]] — полный display pipeline: TERMINAL PROFILE биты, Icon Qualifier, пассивный (SPN) vs активный (STK), OTA-обновление, vendor-specific (Android vs iOS), EF_IMG → PNG → рендер

## Запланированы
- "Сравнительный анализ SCP02/03/80/81: криптография и применение" — детальный crypto-анализ
- "Reverse engineering SIM Toolkit: полный разбор протокола" — провода, байты, инструменты

См. [[../Roadmap|Roadmap]].
