---
tags: [reference, glossary]
type: reference
created: 2026-06-11
updated: 2026-06-12
status: reviewed
---

# Глоссарий терминов UICC/SIM/JavaCard

## A

| Термин | Расшифровка | Кратко |
|---|---|---|
| **ADF** | Application Dedicated File | Точка входа в приложение (USIM, ISIM) — выбирается по AID |
| **AID** | Application Identifier | 5–16 байт, уникальный ID приложения (RID + PIX) |
| **APDU** | Application Protocol Data Unit | Единица обмена: C-APDU (команда) → R-APDU (ответ) |
| **ARR** | Access Rule Reference | Ссылка на запись в EF_ARR с security attributes |
| **ATR** | Answer To Reset | Ответ UICC на сброс (до 33 байт): параметры, протокол |

## B

| **BER-TLV** | Basic Encoding Rules — TLV | Формат данных: Tag + Length + Value |
| **BIP** | Bearer Independent Protocol | TCP/IP через UICC (OPEN CHANNEL в CAT) |

## C

| **CAT** | Card Application Toolkit | Механизм проактивных команд UICC (TS 102 223) |
| **CLA** | Class Byte | Первый байт C-APDU: `00`=3GPP, `A0`=GSM, `80`=ETSI |
| **COMP128** | — | Алгоритм GSM-аутентификации (A3/A8) |
| **C-APDU** | Command APDU | Команда от терминала к UICC |
| **CSIM** | CDMA Subscriber Identity Module | Аналог USIM для CDMA-сетей |

## D

| **DF** | Dedicated File | Директория в файловой системе UICC |
| **DF_GSM** | DF GSM Application | `7F20` — корень GSM-файлов |

## E

| **EF** | Elementary File | Конечный файл с данными |
| **EF_DIR** | EF Directory | `2F00` — каталог AID приложений |
| **EF_ICCID** | EF ICC Identification | `2FE2` — серийный номер карты |
| **EF_IMSI** | EF IMSI | `6F07` — идентификатор абонента |
| **eSIM** | Embedded SIM | Технология удалённой загрузки профилей (GSMA) |
| **ETSI** | European Telecomm. Standards Inst. | Выпускает TS для SIM/UICC |
| **eUICC** | Embedded UICC | Чип для eSIM (может быть встроенным или съёмным) |

## F

| **FCP** | File Control Parameters | Метаданные файла в ответе на SELECT |
| **FID** | File Identifier | 2-байтовый идентификатор файла (напр. `3F00`=MF) |

## G

| **GBA** | Generic Bootstrapping Architecture | Аутентификация приложений через UICC |
| **GP** | GlobalPlatform | Стандарт управления смарт-картами |
| **GSMA** | GSM Association | Владелец eSIM спецификаций (SGP.02, SGP.22) |

## I

| **ICC** | Integrated Circuit Card | Формальное ISO-название смарт-карты |
| **IMSI** | International Mobile Subscriber ID | Главный идентификатор абонента |
| **INS** | Instruction Byte | Второй байт C-APDU: `A4`=SELECT, `B0`=READ, `20`=VERIFY |
| **ISD** | Issuer Security Domain | Главный домен безопасности на карте |
| **ISIM** | IMS Subscriber Identity Module | Приложение для IMS (VoLTE/VoNR) |

## J

| **JCRE** | Java Card Runtime Environment | Среда выполнения JavaCard апплетов |
| **JCVM** | Java Card Virtual Machine | Виртуальная машина Java Card |

## K

| **KIC/KID/KIK** | Key Encryption/MAC/DEK | Ключи GP для защищённого канала |
| **Ki** | Subscriber Key | Секретный ключ абонента (GSM/UMTS) |
| **KVN** | Key Version Number | Версия набора ключей |

## L

| **LPA** | Local Profile Assistant | Компонент eSIM в устройстве (Consumer) |
| **LSI** | Logical Secure element Interface | Логический интерфейс secure element |

## M

| **ME** | Mobile Equipment | Телефон (без SIM) |
| **MF** | Master File | `3F00` — корень файловой системы |
| **MILENAGE** | — | Алгоритм UMTS/LTE/5G аутентификации |
| **MNO** | Mobile Network Operator | Оператор связи |

## N

| **NAA** | Network Access Application | Общее имя для (U)SIM/ISIM приложений |

## O

| **OTA** | Over-the-Air | Удалённое управление SIM через SMS/BIP |

## P

| **PIN** | Personal Identification Number | Код доступа к карте |
| **PIX** | Proprietary Identifier Extension | Часть AID (0–11 байт, определяется RID-holder) |
| **PPS** | Protocol and Parameter Selection | Согласование скорости после ATR |
| **Proactive Command** | — | Команда от UICC к терминалу (CAT) |
| **PUK** | PIN Unblocking Key | Код разблокировки PIN |

## R

| **RAM** | Remote Application Management | OTA-управление апплетами |
| **R-APDU** | Response APDU | Ответ UICC на команду |
| **RFM** | Remote File Management | OTA-управление файлами |
| **RID** | Registered Application Provider ID | Первые 5 байт AID |
| **RSP** | Remote SIM Provisioning | Технология eSIM |

## S

| **SCP** | Secure Channel Protocol | Защищённый канал (SCP02/03/80/81) |
| **SFI** | Short File Identifier | 5-битный ID для быстрого доступа к EF |
| **SIM** | Subscriber Identity Module | Приложение/карта для GSM (2G) |
| **SM-DP+** | Subscription Manager Data Prep.+ | Сервер подготовки профилей eSIM |
| **SPN** | Service Provider Name | Имя оператора (EF_SPN, `6F46`) |
| **SSD** | Supplementary Security Domain | Дополнительный домен безопасности |
| **STK** | SIM Toolkit | Механизм проактивных команд (2G) |
| **SUCI** | Subscription Concealed Identifier | Зашифрованный IMSI (5G privacy) |
| **SW1/SW2** | Status Word 1/2 | Код ответа в R-APDU |

## T

| **TAR** | Toolkit Application Reference | 3-байтовый ID для OTA-маршрутизации |
| **TLV** | Tag-Length-Value | Структура данных: тег + длина + значение |
| **T=0/T=1** | Transmission Protocol 0/1 | Байт-ориентированный / блочный протокол |

## U

| **UICC** | Universal Integrated Circuit Card | Универсальная смарт-карта (платформа) |
| **USAT** | USIM Application Toolkit | STK для 3G/4G/5G (3GPP) |
| **USIM** | Universal Subscriber Identity Module | Приложение для 3G/4G/5G |

## См. также

- [[wiki/index|База знаний]]
- [[wiki/reference/Status_Words|Status Words]]
- [[wiki/reference/CLA_INS_SFI|CLA/INS/SFI]]
