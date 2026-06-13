---
tags: [entity, project, open-source, STK]
created: 2026-06-10
updated: 2026-06-11
status: reviewed
aliases: [Open Source Mobile Communications]
---

# Osmocom — Open Source Mobile Communications

## Общие сведения

**Osmocom** — открытая экосистема для мобильной связи. Проекты: OsmoBSC, OsmoMSC, OsmoBTS (GSM сеть), а также инструменты для SIM-карт.

## Релевантные проекты

| Проект | Назначение |
|---|---|
| **pySim** | Чтение/запись/программирование UICC/SIM-карт |
| **HelloSTK** | Примеры JavaCard STK-апплетов с открытым кодом |
| **SIMtrace** | Сниффинг обмена SIM↔ME |
| **osmo-sim-auth** | Аутентификация SIM |

## HelloSTK

HelloSTK (https://gitea.osmocom.org/sim-card/hello-stk) — коллекция примеров апплетов:
- Использует STK API (sim.toolkit)
- Работает на sysmoUSIM-SJS1, sysmoISIM-SJA2, sysmoISIM-SJA5
- Примеры: меню, DISPLAY TEXT, SMS, Location Info
- Сборка через ant-javacard
- Установка через GlobalPlatformPro с install parameters

## Связи

- HelloSTK clipping: `[[Clippings/HelloSTK - Cellular Network Infrastructure - Open Source Mobile Communications]]`
- STK-апплеты: [[wiki/concepts/STK_Applet]]
- Инструменты: pySim, shadysim
