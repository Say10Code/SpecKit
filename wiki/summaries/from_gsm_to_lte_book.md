---
tags: [book, GSM, UMTS, LTE, evolution, network, architecture, summary]
type: summary
created: 2026-06-12
updated: 2026-06-12
status: reviewed
source: "[[Specifications/Books/From_GSM_to_LTE-Advanced_2e.pdf]]"
---

# «From GSM to LTE-Advanced» — Martin Sauter (2nd Edition)

> **Автор**: Martin Sauter
> **Издание**: 2-е, расширенное и переработанное
> **Охват**: 2G (GSM/GPRS) → 3G (UMTS/HSPA) → 4G (LTE/LTE-Advanced)
> **Файл**: `From_GSM_to_LTE-Advanced_2e.pdf`

## Обзор

Фундаментальная книга, описывающая эволюцию мобильных сетей от GSM (2G) до LTE-Advanced (4G). Рассматривает архитектуру, протоколы, радиоинтерфейс и сигнализацию — с практическим уклоном. Не включает 5G. Полезна для понимания того, **почему** протоколы и файлы UICC/USIM устроены так, а не иначе. ^[inferred]

> Это не книга о SIM-картах. Это книга о сетях. Но для проекта полезна как контекст: понимание того, что происходит «за пределами UICC».

## Структура содержания

### Главы релевантные для проекта

| Глава | Тема | Релевантность |
|---|---|---|
| **1. GSM (Global System for Mobile)** | Архитектура 2G, BTS/BSC/MSC, подсистемы, идентификация (IMSI/TMSI) | Высокая — объясняет, зачем нужны EF_IMSI, EF_LOCI, EF_Kc |
| **2. GSM Radio Interface** | TDMA, каналы (BCCH/SDCCH/SACCH), кодирование речи, handover | Средняя — контекст для EF_SST, EF_ACM (метрики радио) |
| **3. GPRS & EDGE** | Пакетный домен 2.5G, SGSN/GGSN, PDP-контекст, кодирование MCS | Средняя — контекст для EF_PSLOCI, GPRS-сервисов в EF_UST |
| **4. UMTS (Universal Mobile Terrestrial)** | Архитектура 3G: UTRAN, RNC/NodeB, мягкий handover, коды OVSF | Высокая — объясняет, зачем ADF.USIM и EF_UST |
| **5. HSPA** | High-Speed Packet Access: HSDPA/HSUPA, адаптивная модуляция, HARQ | Низкая — радио-уровень, мало влияет на UICC |
| **6. LTE** | Архитектура 4G «flat»: eNodeB, MME/S-GW/P-GW, SON (Self-Organizing Network) | **Высокая** — объясняет LTE-архитектуру, зачем EF_EPSLOCI, EF_EPSNSC, LTE-сервисы |
| **7. LTE-Advanced** | Carrier Aggregation, CoMP, eICIC, Relay Nodes | Низкая — продвинутое радио |
| **8. Cellular IoT** | NB-IoT, LTE-M, энергосбережение (PSM, eDRX) | Средняя — контекст для IoT-профилей |
| **Приложения** | Словарь терминов, цифровой модуляции, структура кадров | Справочный материал |

### Не-релевантные главы (для проекта)
- Главы по VoIP, IMS/VoLTE, Wi-Fi offload, Voice over LTE — затрагивают IMS, но не UICC
- Главы по регулированию спектра, операторским стратегиям

## Как использовать книгу в проекте

1. **Контекст для EF**: когда вы читаете про EF_LOCI или EF_EPSLOCI — книга объясняет, зачем они нужны и как используются сетью
2. **Понимание аутентификации**: главы про GSM объясняют COMP128 и RAND/SRES/Kc; главы про UMTS/LTE объясняют MILENAGE и EPS AKA
3. **Эволюция как история**: книга показывает, как сеть эволюционировала от иерархической (BSC/MSC) к плоской (eNodeB/MME), и как это отразилось на UICC
4. **Терминология**: отличный справочник телеком-аббревиатур и понятий

## Связи

- Концепция UICC: [[wiki/concepts/UICC]]
- USIM: [[wiki/summaries/ts_131102|TS 31.102]]
- Эволюция аутентификации: [[wiki/syntheses/auth_evolution|Evolution of Authentication]]
- USIM Service Table: [[wiki/reference/USIM_EF_Table]]
- Синтез по файловой системе: [[wiki/syntheses/gsm_vs_usim_filesystem|GSM vs USIM Filesystem]]
- 5G (не охвачено книгой): [[wiki/concepts/5G_Core]]
- IMS/VoLTE (частично охвачено): [[wiki/concepts/IMS_VoLTE]]
