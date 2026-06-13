---
tags: [SIM, APDU, examples, практика, summary, Russian]
source: "[[Specifications/Tutorials/Работа_с_SIM_APDU_примеры.txt]]"
type: practical-examples
status: reviewed
created: 2026-06-10
updated: 2026-06-12
---

# Работа с SIM APDU — Практические примеры

> **Источник**: `Specifications/Tutorials/Работа_с_SIM_APDU_примеры.txt`
> **Язык**: Русский

## Обзор

Практический лог-файл работы с SIM-картой через raw APDU-команды. Демонстрирует реальный процесс чтения ICCID, IMSI и SPN с SIM-карты. Ценен как наглядное пособие — показывает, как выглядят реальные APDU-команды и ответы. ^[extracted]

## Пример 1: Чтение ICCID

```
ATR: 3B 9F 94 80 1F C7 80 31 E0 73 FE 21 1B 57 3C 86 60 C2 00 00 A0 5A

→ SELECT MF (3F00)
  00 A4 00 00 02 3F 00
← 90 00

→ SELECT EF_ICCID (2FE2)
  00 A4 00 00 02 2F E2
← 90 00

→ READ BINARY (Le=00 — запрос размера)
  00 B0 00 00 00
← 6C 0A           ← Размер файла = 0x0A = 10 байт

→ READ BINARY (Le=0A)
  00 B0 00 00 0A
← 98 07 91 29 02 04 07 42 74 F1 90 00
   ↑ ICCID в REVERSE CODE (b1↔b2): 89 70 19 92 20 40 70 24 47 1F
```

> 🔑 **Reverse Code**: байты b1 и b2 меняются местами. `98 07` → `89 70`. Так закодирован ICCID в SIM.

## Пример 2: Чтение IMSI

```
→ SELECT MF (3F00)
  00 A4 00 00 02 3F 00

→ SELECT DF_GSM (7F20)
  00 A4 00 00 02 7F 20

→ SELECT EF_IMSI (6F07)
  00 A4 00 00 02 6F 07

→ READ BINARY (Le=00)
  00 B0 00 00 00
← 6C 09           ← 9 байт

→ READ BINARY (Le=09)
  00 B0 00 00 09
← 08 29 05 99 37 05 41 33 57 90 00
   ↑ b1=08 (длина IMSI), b2-b9 = IMSI в reverse code:
   08 92 50 99 73 50 14 33 75
   IMSI = 250 99 750533317 (MCC=250, MNC=99, MSIN=...)
```

## Пример 3: Чтение SPN

```
→ SELECT MF (3F00)
→ SELECT DF_GSM (7F20)
→ SELECT EF_SPN (6F46)

→ READ BINARY (Le=00)
  00 B0 00 00 00
← 6C 11           ← 17 байт

→ READ BINARY (Le=11)
  00 B0 00 00 11
← 00 62 65 65 6C 69 6E 65 FF FF FF FF FF FF FF FF FF 90 00
   ↑ b1 = Display Condition (00 = display not required)
   ↑ b2-b17 = SPN в SMS 7-bit default alphabet:
     62=b, 65=e, 65=e, 6C=l, 69=i, 6E=n, 65=e
     → "beeline"
```

## Пример 4: Verify ADM

```
→ VERIFY ADM (ключ №0A)
  00 20 00 0A 08 XX XX XX XX XX XX XX XX
← 90 00          ← ADM verified
```

## Ключевые уроки

1. **T=0 Case 2 pattern**: первый READ BINARY с Le=00 → `6C XX` (размер) → повтор с правильным Le
2. **Reverse Code**: ICCID и IMSI хранятся с переставленными полубайтами (nibble-reversed)
3. **SPN**: b1 = display condition; остальное — текст в SMS 7-bit alphabet
4. **Путь**: MF (3F00) → DF_GSM (7F20) → EF_xxx для GSM-файлов
5. **ADM ключи**: VERIFY CHV с P2=0A для административных ключей

## Связи

- APDU команды: [[wiki/concepts/APDU]]
- Файловая система: [[wiki/concepts/UICC_File_System]]
- GSM 11.11: [[wiki/summaries/gsm_1111]]
- SPN/PNN: [[notes/EF_SPN_PNN]]
