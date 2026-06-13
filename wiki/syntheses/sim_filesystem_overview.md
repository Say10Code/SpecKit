---
tags:
  - synthesis
  - SIM
  - UICC
  - file-system
  - overview
  - meta-synthesis
  - MF
  - ADF
  - EF
type: synthesis
created: 2026-06-12
updated: 2026-06-12
status: reviewed
sources:
  - "[[wiki/concepts/UICC_File_System]]"
  - "[[wiki/concepts/EF_Types]]"
  - "[[wiki/reference/USIM_EF_Table]]"
  - "[[wiki/syntheses/gsm_vs_usim_filesystem]]"
  - "[[wiki/summaries/ts_102221]]"
  - "[[wiki/summaries/ts_131102]]"
  - "[[wiki/summaries/gsm_1111]]"
---

# SIM-карта как файловая система: обзорное руководство

> **Meta-Synthesis** -- путеводитель по файловой системе UICC/SIM, объединяющий все 14 статей каталога `sim_files_*.md` в единую навигационную картину. Здесь нет деталей реализации -- только архитектура, навигация и связи.

---

## 1. Архитектура: MF -> DF/ADF -> EF

Файловая система UICC -- строго иерархическая, корнем является единственный Master File (MF, `0x3F00`). От него отходят Dedicated Files (DF) и Application Dedicated Files (ADF). Внутри них -- Elementary Files (EF), содержащие собственно данные.

```
MF (3F00)                           ← корень, выбран после ATR
├── EF_ICCID (2FE2)                ← идентификатор карты
├── EF_DIR (2F00)                  ← каталог AID приложений
├── EF_PL (2F05)                   ← предпочтительные языки
├── EF_ARR (2F06)                  ← реестр правил доступа
├── EF_UMPC (306D)                 ← конфигурация multi-PIN
├── DF_CD                           ← Config Data (STK-иконки)
│
├── ADF.USIM                        ← основное приложение (AID: A0..87.10.02)
├── ADF.ISIM                        ← IMS-приложение (AID: A0..87.10.04)
├── ADF.GSM                         ← legacy (AID: A0..09.00.01)
│
└── [другие ADF]                    ← через EF_DIR
```

**Ключевой принцип**: FID большинства EF сохранены одинаковыми между GSM, 3G, 4G и 5G. Телефон читает `EF_IMSI` по `0x6F07` и не знает, с SIM это или с USIM.

Подробнее об архитектуре: [[wiki/concepts/UICC_File_System|UICC File System]].

---

## 2. Полное дерево MF -> ADF.USIM

```mermaid
graph TD
    MF["MF (3F00) ⭐"]

    subgraph "Уровень MF"
        ICCID["EF_ICCID (2FE2): ID карты"]
        DIR["EF_DIR (2F00): каталог приложений"]
        PL["EF_PL (2F05): языки"]
        ARR["EF_ARR (2F06): правила доступа"]
        UMPC["EF_UMPC (306D): multi-PIN конфиг"]
    end

    MF --> ICCID
    MF --> DIR
    MF --> PL
    MF --> ARR
    MF --> UMPC

    subgraph "ADF.USIM"
        USIM["⭐ ADF.USIM"]
        
        subgraph "Идентификация"
            IMSI["EF_IMSI (6F07)"]
            MSISDN["EF_MSISDN (6F40)"]
        end

        subgraph "Имя оператора"
            SPN["EF_SPN (6F46)"]
            PNN["EF_PNN (6FC5)"]
            OPL["EF_OPL (6FC6)"]
            SPNI["EF_SPNI (6FD7)"]
            PNNI["EF_PNNI (6FD8)"]
        end

        subgraph "Контакты"
            ADN["EF_ADN (6F3A)"]
            FDN["EF_FDN (6F3B)"]
            SDN["EF_SDN (6F49)"]
            BDN["EF_BDN (6FDB)"]
        end

        subgraph "SMS"
            SMSP["EF_SMSP (6F42)"]
            SMSS["EF_SMSS (6F43)"]
            SMSR["EF_SMSR (6F47)"]
            SMS["EF_SMS (6F3C)"]
        end

        subgraph "PLMN и сеть"
            PLMNwAcT["EF_PLMNwAcT (6F60)"]
            OPLMNwACT["EF_OPLMNwACT (6F61)"]
            HPLMNwAcT["EF_HPLMNwAcT (6F62)"]
            FPLMN["EF_FPLMN (6F7B)"]
            EHPLMN["EF_EHPLMN (6FD9)"]
            UST["EF_UST (6F38)"]
            EST["EF_EST (6F56)"]
        end

        subgraph "Безопасность"
            EFKeys["EF_Keys (6F08)"]
            EFKeysPS["EF_KeysPS (6F09)"]
            EFACC["EF_ACC (6F78)"]
            AD["EF_AD (6FAD)"]
        end

        subgraph "Локация"
            LOCI["EF_LOCI (6F7E)"]
            PSLOCI["EF_PSLOCI (6F73)"]
            EPSLOCI["EF_EPSLOCI (6FE3)"]
            LOCI5GS["EF_5GS3GPPLOCI (6FF0)"]
            LOCI5GSN["EF_5GSN3GPPLOCI (6FF1)"]
        end

        subgraph "DF_5GS"
            AUTHKEYS["EF_5GAUTHKEYS (6FF3)"]
            SUCI["EF_SUCI_Calc_Info (6FF6)"]
            URSP["EF_URSP (6FFA)"]
            UAC["EF_UAC_AIC (6FF5)"]
            KAUSF["EF_KAUSF_Derivation (6FFC)"]
        end

        subgraph "Графика"
            IMG["EF_IMG (4F20)"]
            IIDF["EF_IIDF (4F21)"]
        end

        subgraph "Языки"
            LI["EF_LI (6F05)"]
        end

        subgraph "Админ и счётчики"
            ADM["EF_AD (6FAD)"]
            ACM["EF_ACM (6F39)"]
            ACMmax["EF_ACMmax (6F37)"]
            PUCT["EF_PUCT (6F41)"]
            ECC["EF_ECC (6FB7)"]
        end
    end

    MF --> USIM

    USIM --> IMSI
    USIM --> MSISDN
    USIM --> SPN
    USIM --> PNN
    USIM --> OPL
    USIM --> SPNI
    USIM --> PNNI
    USIM --> ADN
    USIM --> FDN
    USIM --> SDN
    USIM --> BDN
    USIM --> SMS
    USIM --> SMSS
    USIM --> SMSP
    USIM --> SMSR
    USIM --> PLMNwAcT
    USIM --> OPLMNwACT
    USIM --> HPLMNwAcT
    USIM --> FPLMN
    USIM --> EHPLMN
    USIM --> UST
    USIM --> EST
    USIM --> EFKeys
    USIM --> EFKeysPS
    USIM --> EFACC
    USIM --> AD
    USIM --> LOCI
    USIM --> PSLOCI
    USIM --> EPSLOCI
    USIM --> LOCI5GS
    USIM --> LOCI5GSN
    USIM --> AUTHKEYS
    USIM --> SUCI
    USIM --> URSP
    USIM --> UAC
    USIM --> KAUSF
    USIM --> IMG
    USIM --> IIDF
    USIM --> LI
    USIM --> ACM
    USIM --> ACMmax
    USIM --> PUCT
    USIM --> ECC

    style MF fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    style USIM fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style ICCID fill:#fff3e0
    style ARR fill:#fce4ec
    style IMSI fill:#e3f2fd
```

---

## 3. Категории файлов по назначению

14 статей каталога охватывают все ключевые категории EF. Ниже -- карта: категория, суть, ссылка.

### Идентификация
Файлы, определяющие кто есть кто: ICCID идентифицирует пластик, IMSI -- абонента, MSISDN -- телефонный номер. Без них сеть не узнает абонента. Все три используют BCD reverse-nibble кодирование.
- **[[sim_files_identifiers|Идентификаторы: ICCID, IMSI, MSISDN]]**

### Идентификация оператора
SIM сообщает телефону какое имя показывать на экране. SPN -- простая строка (напр. «MTS RUS»), PNN+OPL -- более гибкая система с привязкой имени к MCC/MNC конкретной PLMN. Иконки (SPNI, PNNI) опциональны.
- **[[sim_files_operator_name|Имя оператора: SPN, PNN, OPL]]**

### Контакты (телефонная книга)
SIM хранит контакты в DF_PHONEBOOK: от обычных номеров (ADN) до фиксированных (FDN -- только разрешённые номера), запрещённых (BDN) и сервисных (SDN). Современные расширения включают email (EF_EMAIL), URI и второй номер (EF_ANR).
- **[[sim_files_phonebook|Телефонная книга: ADN, FDN, SDN, BDN]]**

### SMS
Сообщения хранятся в Linear Fixed EF_SMS, параметры SMSC -- в EF_SMSP, статусы -- в EF_SMSS, статус-отчёты -- в EF_SMSR. Формат: 7-bit GSM packing, до 176 байт на сообщение.
- **[[sim_files_sms|SMS на SIM: хранение сообщений]]**

### PLMN и роуминг
Шесть EF управляют выбором сети: пользовательские предпочтения (EF_PLMNwAcT), политика оператора (EF_OPLMNwACT), домашняя сеть (EF_HPLMNwAcT), эквиваленты (EF_EHPLMN) и чёрный список (EF_FPLMN). EF_ACC определяет приоритет при перегрузке.
- **[[sim_files_plmn|PLMN и роуминг: как SIM выбирает сеть]]**

### Безопасность
Три EF реализуют файловую безопасность: EF_ARR -- центральный реестр правил доступа (вместо дублирования в каждом EF), EF_Keys/EF_KeysPS -- сессионные ключи CK+IK от AKA, EF_ACC -- класс приоритета доступа к сети.
- **[[sim_files_security|Безопасность через файлы: EF_ARR, EF_Keys, EF_ACC]]**

### Локация и tracking
Семейство LOCI-файлов хранит временные идентификаторы и зоны регистрации. 3G: EF_LOCI (TMSI+LAI), 4G: EF_EPSLOCI (GUTI+TAI), 5G: EF_5GS3GPPLOCI и EF_5GSN3GPPLOCI. Раздельные файлы позволяют межпоколенные переходы.
- **[[sim_files_location|Локация и tracking: LOCI, PSLOCI, EPSLOCI, 5GS*LOCI]]**

### 5G
DF_5GS приносит 10+ новых EF: ключи 5G AKA (EF_5GAUTHKEYS), SUCI-приватность (EF_SUCI_Calc_Info), сетевая маршрутизация (EF_URSP), контроль доступа (EF_UAC_AIC), SOR для роуминга (EF_SOR-CMCI).
- **[[sim_files_5g|5G в SIM: DF_5GS и новые элементарные файлы]]**

### Графика и иконки
Три подсистемы: иконки оператора (EF_SPNI, EF_PNNI -- PNG/JPEG 32x32), STK-иконки (EF_ICON в DF_CD), и универсальный контейнер DF_GRAPHICS (EF_IMG + EF_IIDF).
- **[[sim_files_graphics|Графика и иконки: EF_SPNI, EF_PNNI, EF_IMG]]**

### Языки и локализация
Два EF задают языковые предпочтения: глобальный EF_PL на уровне MF (для всех приложений) и локальный EF_LI внутри ADF.USIM. Коды -- ISO 639, до 16 языков в порядке приоритета.
- **[[sim_files_language|Языки и локализация: EF_PL и EF_LI]]**

### Административные данные
EF_AD -- один из важнейших служебных файлов: длина MNC (2 или 3 цифры), режим работы UICC (normal/type approval), битовая маска опций, длина PIN. Без него терминал не может корректно распарсить IMSI.
- **[[sim_files_admin|Административные данные: EF_AD]]**

### Сервисная таблица
EF_UST (и legacy EF_SST) -- битовая карта доступных сервисов. 100+ бит сообщают терминалу что поддерживает карта: от телефонной книги (service 1) до 5GS (service 99), ProSe (86), V2X и Mission Critical. Терминал читает один файл вместо проверки каждого сервиса.
- **[[sim_files_service_table|Сервисная таблица: EF_UST и EF_SST]]**

### Тарификация звонков
Advice of Charge (AoC): EF_ACM (Cyclic -- накопительный счётчик), EF_ACMmax (лимит), EF_PUCT (валюта и цена единицы), EF_ICI/EF_OCI (информация о входящих/исходящих). Команда INCREASE обновляет ACM.
- **[[sim_files_call_metering|Звонки и счётчики: ACM, ICT, OCT]]**

### Экстренные номера
EF_ECC -- список номеров экстренных служб. Уникален тем, что читается **до верификации PIN** -- один из немногих EF доступных при заблокированной карте. Дополняется, но не заменяется, eCall.
- **[[sim_files_emergency|Экстренные номера: EF_ECC]]**

### Категории вне каталога
Статья [[sim_files_security|EF_ARR, EF_Keys, EF_ACC]] покрывает security-файлы, а PIN-иерархия (PIN1/PIN2/ADM/PUK/Universal PIN) детально описана в отдельном синтезе [[sim_pin_access_control|Права доступа и PIN-иерархия]].

---

## 4. Как ориентироваться в 150+ EF

```
ВКЛЮЧЕНИЕ ТЕЛЕФОНА — навигационная цепочка:

1. ATR      → UICC сообщает протокол, скорость, исторические байты
2. MF       → активен автоматически после ATR
3. EF_DIR   → какие ADF доступны (AID-каталог)
4. EF_ICCID → идентификатор карты (BCD reverse nibble)
5. ADF.USIM → SELECT по AID: A0 00 00 00 87 10 02 FF FF FF
6. EF_UST   → какие сервисы доступны (битовая карта 100+)
7. EF_AD    → административные параметры (длина MNC, режим)
8. EF_IMSI  → идентификатор абонента
9. Далее    → EF по потребности: SPN, LOCI, PLMN, Keys...
```

> [!tip] Практический принцип навигации
> **Сначала UST, потом EF**. Прочитав EF_UST, терминал знает какие сервисы поддерживает карта, и не тратит время на чтение EF, которые не существуют (нет риска получить `6A82: file not found`).

### Быстрый поиск EF по категории

| Нужно найти | Категория | Статья |
|---|---|---|
| IMSI, ICCID, номер телефона | Идентификация | [[sim_files_identifiers]] |
| Имя оператора на экране | Оператор | [[sim_files_operator_name]] |
| Контакты, запрещённые номера | Контакты | [[sim_files_phonebook]] |
| SMS, центр сообщений | SMS | [[sim_files_sms]] |
| Выбор сети, роуминг | PLMN | [[sim_files_plmn]] |
| Права доступа, ключи шифрования | Безопасность | [[sim_files_security]] |
| Где телефон сейчас (TMSI, LAI) | Локация | [[sim_files_location]] |
| 5G ключи, SUCI, слайсы | 5G | [[sim_files_5g]] |
| Иконки, картинки | Графика | [[sim_files_graphics]] |
| Язык меню, RU/EN | Языки | [[sim_files_language]] |
| Параметры PIN, длина MNC | Админ | [[sim_files_admin]] |
| Какие сервисы есть, UST | Сервисы | [[sim_files_service_table]] |
| Счётчик денег, валюта | Тарификация | [[sim_files_call_metering]] |
| 112, 911 и другие | Экстренные | [[sim_files_emergency]] |

---

## 5. Инструменты для работы с файловой системой

| Инструмент | Назначение | Ключевые возможности |
|---|---|---|
| **pySim** (osmocom) | Чтение/запись EF, кардинг | `pySim-read --usim`, `pySim-shell` интерактивный режим, парсинг ICCID/IMSI/SPN |
| **GlobalPlatformPro** (gp.jar) | Управление картой Java Card | `gp --list`, `gp --install`, `gp --delete`, работа с SCP02/SCP03 |
| **shadysim** | Эмуляция SIM | Полная программная UICC, создание виртуальных карт, отладка без физической карты |
| **sysmoUSIM-tool** | Программирование sysmoUSIM | Запись IMSI, Ki, OPC, SPN на программируемые SIM-карты |
| **APDU Playground** (веб) | Интерактивная отправка APDU | Веб-интерфейс к PC/SC reader, просмотр FCP, отладка |
| **PC/SC reader + Python** | Программный доступ | `smartcard` library, ручная отправка APDU команд |

### Минимальный набор APDU для чтения EF

```
; Выбрать ADF.USIM
00 A4 04 00 09 A0 00 00 00 87 10 02 FF FF FF

; Выбрать EF (по FID)
00 A4 00 00 02 <FID_HI> <FID_LO>

; Читать Transparent EF
00 B0 <OFFSET_HI> <OFFSET_LO> <LENGTH>

; Читать Linear Fixed запись
00 B2 <REC_NO> 04 <LENGTH>
```

---

## 6. Эволюция: от GSM 11.11 к Release 18

| Эпоха | Спецификация | EF | Характерные черты |
|---|---|---|---|
| **1995** GSM | GSM 11.11 | ~20 | DF_GSM + DF_TELECOM, только 2G, Kc (64 bit), простые сервисы |
| **2001** 3G | TS 31.102 Rel-4 | ~60 | ADF.USIM, ADF-архитектура, CK+IK (128 bit), PIN-терминология |
| **2009** 4G | Rel-8 | ~100 | EPSLOCI, EPS-keys, EF_ARR, BER-TLV EF, DF_5GS зародыш |
| **2018** 5G | Rel-15 | ~130 | DF_5GS, SUCI, URSP, UAC, K_AUSF derivation |
| **2024** Rel-18 | TS 31.102 V18.x | **150+** | V2X, SNPN, 5G ProSe, Mission Critical, IoT-оптимизации |

> [!info] Почему FID не меняются
> FID ключевых EF (6F07=IMSI, 6F46=SPN, 6F3A=ADN, 6F3C=SMS) **сохранены одинаковыми** на протяжении 30 лет -- от GSM 11.11 до 3GPP Rel-18. Это сознательное дизайнерское решение для обратной совместимости: телефон 1998 года может прочитать IMSI из USIM 2024 года теми же командами.

### Что добавилось в каждом поколении

- **2G -> 3G**: ADF-архитектура, multiple applications, UCS2-кодирование, EF_ARR (ARR-ссылки), BER-TLV EF, логические каналы
- **3G -> 4G**: EPS-локация, PS-domain keys, H(e)NB, расширенные контакты (email, URI, ANR), иконки операторов
- **4G -> 5G**: DF_5GS с 10+ EF, SUCI-приватность, URSP для network slicing, UAC, C-V2X, 5G ProSe

Подробное сравнение GSM vs USIM: [[gsm_vs_usim_filesystem|GSM SIM vs 3G USIM: Сравнение файловых систем]].

---

## 7. Связи

### Внутренние (wiki/)

- [[wiki/concepts/UICC_File_System|UICC File System]] — архитектура и методы выбора файлов
- [[wiki/concepts/EF_Types|Elementary File Types]] — Transparent, Linear Fixed, Cyclic, BER-TLV
- [[wiki/reference/USIM_EF_Table|USIM EF Reference Table]] — быстрый справочник по FID
- [[wiki/concepts/UICC_Security|UICC Security]] — архитектура безопасности UICC
- [[wiki/concepts/USIM|USIM Application]] — контекст ADF.USIM
- [[wiki/concepts/FCP|File Control Parameters]] — как UICC сообщает метаданные файла
- [[wiki/concepts/APDU|APDU Commands]] — SELECT, READ BINARY, READ RECORD

### Статьи каталога (14)

- [[sim_files_identifiers|Идентификаторы: ICCID, IMSI, MSISDN]]
- [[sim_files_operator_name|Имя оператора: SPN, PNN, OPL]]
- [[sim_files_admin|Административные данные: EF_AD]]
- [[sim_files_phonebook|Телефонная книга: ADN, FDN, SDN, BDN]]
- [[sim_files_sms|SMS на SIM]]
- [[sim_files_plmn|PLMN и роуминг]]
- [[sim_files_service_table|Сервисная таблица: EF_UST]]
- [[sim_files_security|Безопасность: EF_ARR, EF_Keys, EF_ACC]]
- [[sim_files_location|Локация: LOCI, EPSLOCI, 5GS*LOCI]]
- [[sim_files_5g|5G в SIM: DF_5GS]]
- [[sim_files_graphics|Графика и иконки]]
- [[sim_files_language|Языки и локализация]]
- [[sim_files_call_metering|Звонки и счётчики]]
- [[sim_files_emergency|Экстренные номера: EF_ECC]]

### Родственные синтезы

- [[gsm_vs_usim_filesystem|GSM vs USIM: эволюция файловой системы]]
- [[sim_pin_access_control|Права доступа и PIN-иерархия]]
- [[auth_evolution|Эволюция аутентификации]]
- [[esim_evolution|eSIM: от UICC к eUICC]]

### Specifications

- [[wiki/summaries/ts_102221|TS 102 221]] — UICC: физические и логические характеристики
- [[wiki/summaries/ts_131102|TS 31.102]] — USIM: характеристики приложения
- [[wiki/summaries/gsm_1111|GSM 11.11]] — SIM: legacy-спецификация
