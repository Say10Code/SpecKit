---
tags: [HeloSTK, Osmocom, STK, clipping, summary]
source: "[[Clippings/HelloSTK - Cellular Network Infrastructure - Open Source Mobile Communications]]"
type: project
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# HelloSTK — Osmocom JavaCard STK Examples

> **Источник**: https://osmocom.org/projects/cellular-infrastructure/wiki/HelloSTK
> **Извлечено**: 2026-05-31, обновлено 03/2026

## Обзор

HelloSTK — коллекция примеров JavaCard-апплетов, использующих SIM Toolkit (STK) API. Проект от сообщества Osmocom. Нацелен на sysmoUSIM-SJS1 и sysmoISIM-SJA2/SJA5 карты. ^[extracted]

## Ключевые компоненты

### 1. Сборка
- Git: `https://gitea.osmocom.org/sim-card/hello-stk`
- Сборка через ant-javacard
- Требуется JDK (Java 1.1 bytecode) и GlobalPlatformPro

### 2. Установка
Standard install parameters (BER-TLV):
```
PARAMS=c900ef1cc8020100c7020100ca12010001001505000000000000000000000000
```
- NVM Quota: 256 bytes
- RAM Quota: 256 bytes  
- Access Domain: 0x00
- Priority: 1
- Max menu text length: 21
- Max menu entries: 5

### 3. Управление апплетами

```bash
# Установка
gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK \
       --key-ver $KVN --install $CAP --params $PARAMS

# Список
gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --list

# Удаление
gp.jar --key-enc $KIC --key-mac $KID --key-dek $KIK --uninstall $CAP
```

### 4. Что нужно для работы
- sysmoUSIM-SJS1 (или новее) карта
- KIC, KID, KIK — приватные ключи карты
- KVN — Key Version Number
- PCSC или serial card reader (или SMS на SIM)
- GlobalPlatformPro (gp.jar) v20.08.12+

## HelloSTK и AID из реальной карты

Пример GET STATUS с установленным HelloSTK:
```
ISD: A000000003000000 (SECURED)
APP: A0000000871002FFFFFFFF8907090000 (USIM)
APP: A0000000871004FFFFFFFF8907090000 (ISIM)
PKG: D07002CA44 (LOADED)
     Applet: D07002CA44900101
PKG: A0000000620001 (javacard.framework)
```

## Связи

- STK-апплеты: [[wiki/concepts/STK_Applet]]
- GP-установка: [[wiki/concepts/JavaCard_Applet_Development]]
- Osmocom: [[wiki/entities/Osmocom]]
- Примеры кода: [[wiki/summaries/ruimtools_javacard_samples]]
