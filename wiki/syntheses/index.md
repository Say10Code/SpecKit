---
tags: [hub, syntheses]
type: hub
created: 2026-06-10
updated: 2026-06-12
---

# Syntheses: Комплексные отчёты и кросс-анализ (30)

## Практические руководства
- [[javacard_stk_end_to_end]] — **Java Card: от исходников до STK-меню за 30 минут**
- [[cell_broadcast_pws_applet]] — **Java Card апплет для Cell Broadcast / PWS / CMAS**
- [[sim_vs_uicc_toolkit]] — **sim.toolkit vs uicc.toolkit: Миграция 2G→5G**
- [[uicc_testing_pipeline]] — **Тестирование UICC: от pySim до TS 31.124 Conformance**
- [[sim_testing_specs]] — **Тестирование SIM-карт согласно спецификациям**
- [[sim_toolkit_commands_catalog]] — **SIM Toolkit: полный каталог proactive команд**
- [[sim_ims_volte_vonr]] — **SIM и IMS: VoLTE/VoNR через ISIM**

## Эволюция технологий
- [[auth_evolution]] — **Эволюция аутентификации: от COMP128 к 5G AKA**
- [[gsm_vs_usim_filesystem]] — **GSM SIM vs 3G USIM: Сравнение файловых систем**
- [[esim_evolution]] — **eSIM: От UICC к встроенному профилю**
- [[ota_evolution]] — **OTA: От SMS-PP к eSIM RSP**
- [[uicc_api_evolution]] — **Эволюция UICC API: sim.toolkit → uicc.toolkit → 5G**

## Безопасность
- [[security_landscape]] — **Security Landscape: угрозы, атаки и защита**

## 📁 Каталог файлов SIM (16 статей)

### Обзорные и мета-синтезы
- [[sim_filesystem_overview]] — **SIM-карта как файловая система: обзорное руководство**
- [[sim_pin_access_control]] — **Права доступа и PIN-иерархия: PIN1, PIN2, ADM**

### Идентификация и оператор
- [[sim_files_identifiers]] — **Идентификаторы: ICCID, IMSI, MSISDN**
- [[sim_files_operator_name]] — **Имя оператора: SPN, PNN, OPL**
- [[sim_files_admin]] — **Административные данные: EF_AD**

### Контакты и сообщения
- [[sim_files_phonebook]] — **Телефонная книга: ADN, FDN, SDN, BDN**
- [[sim_files_sms]] — **SMS на SIM: хранение, формат, 7-bit packing**

### Сеть и роуминг
- [[sim_files_plmn]] — **PLMN и роуминг: как SIM выбирает сеть**
- [[sim_files_service_table]] — **Сервисная таблица: EF_UST / EF_SST**

### Безопасность и доступ
- [[sim_files_security]] — **Безопасность через файлы: EF_ARR, EF_Keys, EF_ACC**
- [[sim_files_location]] — **Локация и tracking: LOCI, PSLOCI, EPSLOCI, 5GS*LOCI**

### 5G и современные
- [[sim_files_5g]] — **5G в SIM: DF_5GS и новые EF**
- [[sim_files_graphics]] — **Графика и иконки: EF_SPNI, EF_PNNI, EF_IMG**

### Сервисы
- [[sim_files_call_metering]] — **Звонки и счётчики: ACM, ICT, OCT**
- [[sim_files_emergency]] — **Экстренные номера: EF_ECC**
- [[sim_files_language]] — **Языки и локализация: EF_PL, EF_LI**

См. [[Roadmap|Roadmap]].
