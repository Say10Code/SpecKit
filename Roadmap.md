# 🗺️ Roadmap: Развитие базы знаний по телеком-спецификациям

> **Последнее обновление**: 2026-06-13 00:45
> **Актуальная версия CLAUDE.md**: D:\ObsidianDB\CLAUDE.md
> **Детальный план**: [outputs/STATUS_AND_PLAN.md](outputs/STATUS_AND_PLAN.md)
> **Техническая документация**: [_tech/README.md](_tech/README.md)
> **Беклог**: [_tech/BACKLOG.md](_tech/BACKLOG.md)

---

## 📊 Текущее состояние

### Wiki: 129 .md файлов (+7 index), ~1950 KB, 100% reviewed

| Раздел | Страниц | Статус |
|---|---|---|
| concepts/ | **25** | ✅ 100% reviewed |
| entities/ | **8** | ✅ 100% reviewed |
| summaries/ | **49** | ✅ 100% reviewed |
| syntheses/ | **31** | ✅ 100% reviewed |
| reference/ | **6** | ✅ 100% reviewed |
| research/ | **10** | ✅ 100% reviewed |

### Инфраструктура

| Компонент | Состояние |
|---|---|
| Sub-Agents | **8** (Author, Reviewer v3, Linker, Librarian, Researcher, Formatter, SpecExtractor v2, SpecDownloader) |
| Skills | **6** (lint-wiki, ingest, review, format-html, roadmap-status, spec-download) |
| Torch CUDA | ✅ RTX 3060 (11 GB VRAM), GPU speedup 2.4-4.2× CPU |
| Templates | **6** (.obsidian/templates/) |
| Notes | **4** (Шпаргалка APDU, Как установить апплет, Глоссарий, EF_SPN_PNN) |
| Specifications/ | **65 файлов** в 11 тематических директориях |
| specs-extracted/ | **58 TXT + 16 новых MD/JSON** (11×3GPP + 5×ETSI) |
| !INCOMING | 0 (чисто) |
| !double | 24 дубликата |
| 3gpp-crawler | ✅ `3gpp-crawler.toml`, `.3gpp-crawler/`, `uv tool install` |
| .gitignore | ✅ Исключает `.3gpp-crawler/`, сессии, Python |
| specs-extracted план | ✅ `_tech/specs-extracted-migration-plan.md` |
| Битых ссылок | 0 |
| Сирот | 0 |

---

## 🎯 Фаза 1: Фундамент (Foundation) ✅ 100% — 2026-06-10

- [x] Инициализация структуры wiki/ (5 разделов)
- [x] TS 102 221 (UICC Platform) — summary + 6 concepts
- [x] TS 31.101 (UICC I/F for 3GPP) — summary + integrated
- [x] TS 31.102 (USIM) — summary + USIM EF Table
- [x] TS 102 223 (CAT/STK) — summary + CAT_STK concept
- [x] TS 102 226 (Remote APDU) — summary
- [x] GSM 11.11 (Legacy SIM) — summary
- [x] Все учебные материалы (6 книг + pySim + APDU примеры)
- [x] Все Clippings (RuimTools ×2, HelloSTK)
- [x] Материалы .doc (AID-пособие, TCA, GPC, StepStones, etc.)
- [x] Базовая обвязка: CLAUDE.md, Roadmap, wikilinks

## 🔬 Фаза 2: Углубление (Deepen) ✅ 100% — 2026-06-11

- [x] ISO 7816 !recheck — документировано (PDFs защищены)
- [x] SGP.02 v4.1 + eSIM Whitepaper → concepts/eSIM, entities/GSMA
- [x] Sjors Gielen — SIM Toolkit in Practice → summary
- [x] TS 101 220 — ETSI Numbering System → summary
- [x] Syntheses: Auth Evolution, GSM vs USIM, eSIM Evolution, OTA Evolution, SIM vs UICC Toolkit
- [x] Sub-Agents v1 (Author/Reviewer/Linker/Librarian)
- [x] Mermaid-диаграммы + Obsidian callouts на ключевых страницах
- [x] Obsidian-темплейты (6)
- [x] Реорганизация `Specifications/` (10 тематических директорий)
- [x] `!INCOMING` → `!double` пайплайн
- [x] wikilinks: префикс `wiki/`, lint 0/0

## 🚀 Фаза 3: Расширение (Expand) ✅ 100% — 2026-06-12

- [x] **5G Core** — concept + 5G FID исправлены (4Fxx) по TS 31.102
- [x] **IMS / VoLTE / VoNR** — concept + synthesis Sim+IMS
- [x] **GCF / PTCRB** — concept
- [x] **GlobalPlatform TEE** — concept
- [x] **pySim / osmopysim** — summary + Testing Pipeline synthesis
- [x] **Cell Broadcast / PWS / CMAS** — synthesis (sim+uicc toolkit)
- [x] **14 статей о файлах SIM** (А1-А14) — каталог всех EF по группам
- [x] **SIM Toolkit Commands Catalog** — 33+ proactive команд
- [x] **PIN Rights System** — APDU-команды, state machine
- [x] **Contactless / NFC** (SWP, HCI, CLF, EMV) — research
- [x] **SCWS / BIP** (SIM как веб-сервер) — research
- [x] **GPS / LCS** (Location Services) — research
- [x] **USIM EF Catalog** (120+ EF) — research
- [x] **PLMN Selection Algorithm** — research
- [x] **MILENAGE vs TUAK** — research
- [x] **Auth Evolution Deep Dive** — research (COMP128/MILENAGE/TUAK/кванты)
- [x] **SIM Testing Deep Dive** — research
- [x] **Operator Icons on SIM** — research
- [x] Notes/: Шпаргалка APDU, Как установить апплет, Глоссарий
- [x] `Добро пожаловать.md` переписан

## 🔄 Фаза 4: Поддержание (Maintain) ✅ 2026-06-12

- [x] `/lint` — 0 битых ссылок, 0 сирот
- [x] Рецензирование: 100% reviewed (122/122 контентных страниц)
- [x] Reviewer v2: сверка по эталонным спецификациям (specs-extracted/)
- [x] Глоссарий в wiki/reference/Glossary.md
- [x] Шпаргалки в notes/
- [x] CLAUDE.md: модульная архитектура (8 agents, 5 skills)
- [x] SpecDownloader: автоматическое скачивание 3GPP-спецификаций через spec-crawler
- [x] 3gpp-crawler: интеграция (spec-crawler CLI + SpecDownloader agent)
- [x] 3gpp-crawler: `3gpp-crawler.toml`, `.gitignore`, кэш в `.3gpp-crawler/`
- [x] Librarian v2: адаптирован к вложенной структуре spec-crawler checkout
- [x] План миграции specs-extracted (PyPDF2 → Docling): `_tech/specs-extracted-migration-plan.md`
- [x] Docling пилот: 5 спецификаций успешно, CPU + CUDA (RTX 3060), гибридный вердикт
- [x] LibreOffice 26.2.4.2 установлен (docx→PDF конвертация)
- [x] 3gpp-crawler fix: `PipelineOptions` → `PdfPipelineOptions` (совместимость с docling 2.102.0)
- [x] Skill `/spec-download`: 7 шагов от скачивания до Roadmap
- [x] Анализ архитектуры `Specifications/`: `_tech/specs-directory-architecture.md`
- [x] Docling миграция: 11×3GPP + 5×ETSI = 16 MD+JSON в `specs-extracted/`
- [x] `std::bad_alloc` анализ: OOM в PIL/pypdfium2 при `images_scale=1.5`, не GPU
- [x] Torch проверка: `AssertionError: Torch not compiled with CUDA enabled` — RTX 3060 простаивает
- [x] Reviewer v3: гибридный Pass 1 (TXT Grep / JSON lookup / MD read)
- [x] SpecExtractor v2: PyPDF2 + Docling dual approach
- [x] B2: PyTorch CUDA (RTX 3060 активирован)
- [x] B3: CPU vs GPU бенчмарк — 2.4-4.2× speedup, MD output идентичен
- [x] F1+F2+F3: bad_alloc решён (247→1), данные не потеряны, структура сохранена
- [x] Архитектура v2: `_tech/ARCHITECTURE-v2.md` (полный анализ)
- [x] Беклог актуализирован: `_tech/BACKLOG.md` (20 завершённых задач)
- [x] US Patent US20130045737A1 — анализ + summary
- [x] Все планы актуализированы с временем обновления

---

## 📋 Мастер-список

### Concepts (25)
UICC, UICC_File_System, EF_Types, FCP, APDU, ATR, Transmission_Protocols, UICC_Security, USIM, CAT_STK, eSIM, JavaCard, JavaCard_Applet_Development, GlobalPlatform_Card, STK_Applet, OTA_Remote_Management, AID, EF_DIR, SCP, Command_Scripting, 5G_Core, IMS_VoLTE, Certification_GCF_PTCRB, TEE

### Entities (8)
ETSI, 3GPP, GlobalPlatform, GSMA, ISO7816, TCA, Osmocom

### Syntheses (31)
**Guides (8)**: javacard_stk_end_to_end, cell_broadcast_pws_applet, sim_vs_uicc_toolkit, uicc_testing_pipeline, sim_testing_specs, sim_toolkit_commands_catalog, sim_pin_rights_commands, sim_ims_volte_vonr

**SIM Files (16)**: sim_filesystem_overview, sim_pin_access_control, sim_files_identifiers, sim_files_operator_name, sim_files_phonebook, sim_files_sms, sim_files_plmn, sim_files_call_metering, sim_files_emergency, sim_files_5g, sim_files_security, sim_files_location, sim_files_service_table, sim_files_graphics, sim_files_language, sim_files_admin

**Evolution (5)**: auth_evolution, gsm_vs_usim_filesystem, esim_evolution, ota_evolution, uicc_api_evolution

**Security (1)**: security_landscape

### Research (10)
milenage_vs_tuak, operator_icons_on_sim, auth_evolution_deep_dive, sim_testing_deep_dive, usim_ef_catalog, plmn_selection_algorithm, sim_nfc_contactless, sim_scws_webserver, sim_gps_lcs

### Reference (6)
USIM_EF_Table, JavaCard_APIs, Status_Words, CLA_INS_SFI, Glossary

---

## ⏳ Что осталось (только внешние зависимости)

| Задача | Статус | Блокер |
|---|---|---|
| SGP.22 Consumer eSIM — summary | ⬜ | Нужен PDF |
| SGP.32 IoT eSIM — summary | ⬜ | Нужен PDF |
| ISO 7816 незащищённые PDF — анализ | 🔄 | Нужны копии |
| ISO/IEC 7816-5 — RID registry | ⬜ | Нужен PDF |
| GP Card Spec 2.3.1 полный текст | ⬜ | Нужен PDF |
| TS 35.206 — MILENAGE test vectors | ⬜ | Нужен PDF |
| Git-инициализация | ✅ | `a35abfc` — 266 файлов, 110K+ вставок |

---

## 🏷️ Легенда

| Статус | Значение |
|---|---|
| ⬜ | Не начато |
| 🔄 | В процессе / требует внешних файлов |
| ✅ | Завершено |
| ⏸️ | Отложено |

---

*Дорожная карта обновлена 2026-06-13 03:30. Детальный план: [outputs/STATUS_AND_PLAN.md](outputs/STATUS_AND_PLAN.md). Техническая документация: [_tech/README.md](_tech/README.md). Беклог: [_tech/BACKLOG.md](_tech/BACKLOG.md).*
