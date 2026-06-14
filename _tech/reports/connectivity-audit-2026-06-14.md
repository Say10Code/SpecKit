# Connectivity Audit — ObsidianDB wiki/

> **Дата**: 2026-06-14 13:35
> **Метод**: Полный граф-анализ wikilinks
> **Страниц**: 130 (123 контентных + 7 индексов)
> **Связей**: 903

## Dashboard

| Метрика | Значение | Статус |
|---|---|---|
| Битых ссылок | 0 | ✅ |
| Сирот (0 inbound) | 1 | ❌ |
| Слабых (<3 in) | 32 | ⚠️ |
| Слабых (<3 out) | 11 | ⚠️ |
| Изолированных кластеров | 1 | ⚠️ |
| Мостовых страниц | 86 | ℹ️ |
| Cross-ref пробелов | 0 | ✅ |
| Средняя связность | 7.3 in / 6.2 out | — |

> **Вердикт**: ⚠️ NEEDS ATTENTION — 3 проблем требуют исправления.

## ❌ Сиротские страницы (1)

Страницы с 0 входящих wikilinks:

- `summaries/telcoai_3gpp_search` (type=summary) — ни одна страница не ссылается

## ⚠️ Слабые страницы — <3 входящих (32)

| Страница | In | Out | Тип |
|---|---|---|---|
| `summaries/telcoai_3gpp_search` | 0 | 2 | summary |
| `concepts/Command_Scripting` | 1 | 4 | concept |
| `reference/Glossary` | 1 | 3 | reference |
| `summaries/cartes_sim_fichiers` | 1 | 4 | slides |
| `summaries/from_gsm_to_lte_book` | 1 | 7 | summary |
| `summaries/functional_characteristics` | 1 | 3 | summary |
| `summaries/os_rusim` | 1 | 2 | summary |
| `summaries/rsat_at_commands` | 1 | 2 | summary |
| `summaries/sim_profile_markup_language` | 1 | 3 | summary |
| `summaries/ts_31213` | 1 | 3 | summary |
| `summaries/us_patent_20130045737` | 1 | 6 | summary |
| `syntheses/sim_ims_volte_vonr` | 1 | 11 | synthesis |
| `syntheses/sim_pin_rights_commands` | 1 | 11 | synthesis |
| `syntheses/sim_toolkit_commands_catalog` | 1 | 11 | synthesis |
| `syntheses/uicc_api_evolution` | 1 | 6 | synthesis |
| `concepts/AID` | 2 | 4 | concept |
| `concepts/EF_DIR` | 2 | 5 | concept |
| `concepts/TEE` | 2 | 4 | concept |
| `summaries/hello_stk` | 2 | 4 | project |
| `summaries/sim_presentation_ru` | 2 | 4 | presentation |

## ⚠️ Слабые страницы — <3 исходящих (11)

| Страница | In | Out | Тип |
|---|---|---|---|
| `entities/Osmocom` | 4 | 1 | ? |
| `summaries/intro_to_sim_cards` | 3 | 2 | tutorial |
| `summaries/os_rusim` | 1 | 2 | summary |
| `summaries/rsat_at_commands` | 1 | 2 | summary |
| `summaries/sim_personalization` | 3 | 2 | technical-document |
| `summaries/smart_card_howto` | 2 | 2 | tutorial |
| `summaries/telcoai_3gpp_search` | 0 | 2 | summary |
| `summaries/tr_311919` | 2 | 2 | summary |
| `summaries/ts_102225` | 5 | 2 | summary |
| `summaries/ts_133220` | 3 | 2 | summary |

## ⚠️ Изолированные кластеры (1)

Группы страниц, связанных только между собой (нет внешних ссылок):

### Кластер 1: 123 страниц (synthesis(25), summary(21), specification(10))
- `concepts/5G_Core`
- `concepts/AID`
- `concepts/APDU`
- `concepts/ATR`
- `concepts/CAT_STK`
- `concepts/Certification_GCF_PTCRB`
- `concepts/Command_Scripting`
- `concepts/EF_DIR`
- `concepts/EF_Types`
- `concepts/FCP`
- `concepts/GlobalPlatform_Card`
- `concepts/IMS_VoLTE`
- `concepts/JavaCard`
- `concepts/JavaCard_Applet_Development`
- `concepts/OTA_Remote_Management`
- `concepts/SCP`
- `concepts/STK_Applet`
- `concepts/TEE`
- `concepts/Transmission_Protocols`
- `concepts/UICC`
- `concepts/UICC_File_System`
- `concepts/UICC_Security`
- `concepts/USIM`
- `concepts/eSIM`
- `entities/3GPP`
- `entities/ETSI`
- `entities/GSMA`
- `entities/GlobalPlatform`
- `entities/ISO7816`
- `entities/Osmocom`
- `entities/TCA`
- `reference/CLA_INS_SFI`
- `reference/Glossary`
- `reference/JavaCard_APIs`
- `reference/Status_Words`
- `reference/USIM_EF_Table`
- `research/auth_evolution_deep_dive`
- `research/milenage_vs_tuak`
- `research/operator_icons_on_sim`
- `research/plmn_selection_algorithm`
- `research/sim_gps_lcs`
- `research/sim_nfc_contactless`
- `research/sim_scws_webserver`
- `research/sim_testing_deep_dive`
- `research/usim_ef_catalog`
- `summaries/cartes_sim_fichiers`
- `summaries/esim_whitepaper`
- `summaries/from_gsm_to_lte_book`
- `summaries/functional_characteristics`
- `summaries/gpc_card_spec_2_3_1`
- `summaries/gsm_1111`
- `summaries/hello_stk`
- `summaries/intro_to_sim_cards`
- `summaries/iso7816_analysis`
- `summaries/java_card_stepping_stones`
- `summaries/os_rusim`
- `summaries/osmopysim_usermanual`
- `summaries/outsmarting_smart_cards`
- `summaries/rsat_at_commands`
- `summaries/ruimtools_javacard_guidelines`
- `summaries/ruimtools_javacard_samples`
- `summaries/sgp02`
- `summaries/sim_apdu_examples`
- `summaries/sim_cards_thesis`
- `summaries/sim_personalization`
- `summaries/sim_presentation_ru`
- `summaries/sim_profile_markup_language`
- `summaries/simalliance_lte_uicc_profile`
- `summaries/sjors_gielen_stk`
- `summaries/smart_card_howto`
- `summaries/smart_card_tutorial`
- `summaries/telcoai_3gpp_search`
- `summaries/tr_311919`
- `summaries/ts_101476`
- `summaries/ts_101_220`
- `summaries/ts_102221`
- `summaries/ts_102223`
- `summaries/ts_102225`
- `summaries/ts_102241`
- `summaries/ts_102_226`
- `summaries/ts_123048`
- `summaries/ts_131101`
- `summaries/ts_131102`
- `summaries/ts_131130`
- `summaries/ts_133220`
- `summaries/ts_143019`
- `summaries/ts_151014`
- `summaries/ts_31121`
- `summaries/ts_31124`
- `summaries/ts_31213`
- `summaries/ts_51011`
- `summaries/ts_51017`
- `summaries/us_patent_20130045737`
- `syntheses/auth_evolution`
- `syntheses/cell_broadcast_pws_applet`
- `syntheses/esim_evolution`
- `syntheses/gsm_vs_usim_filesystem`
- `syntheses/javacard_stk_end_to_end`
- `syntheses/ota_evolution`
- `syntheses/security_landscape`
- `syntheses/sim_files_5g`
- `syntheses/sim_files_admin`
- `syntheses/sim_files_call_metering`
- `syntheses/sim_files_emergency`
- `syntheses/sim_files_graphics`
- `syntheses/sim_files_identifiers`
- `syntheses/sim_files_language`
- `syntheses/sim_files_location`
- `syntheses/sim_files_operator_name`
- `syntheses/sim_files_phonebook`
- `syntheses/sim_files_plmn`
- `syntheses/sim_files_security`
- `syntheses/sim_files_service_table`
- `syntheses/sim_files_sms`
- `syntheses/sim_filesystem_overview`
- `syntheses/sim_ims_volte_vonr`
- `syntheses/sim_pin_access_control`
- `syntheses/sim_pin_rights_commands`
- `syntheses/sim_testing_specs`
- `syntheses/sim_toolkit_commands_catalog`
- `syntheses/sim_vs_uicc_toolkit`
- `syntheses/uicc_api_evolution`
- `syntheses/uicc_testing_pipeline`
  → **Рекомендация**: добавить хотя бы 1 внешнюю ссылку из кластера на `wiki/concepts/...` или `wiki/summaries/...`

## 🔗 Мостовые страницы (86)

Страницы, соединяющие разные разделы wiki/:

| Страница | Связывает разделы | In | Out |
|---|---|---|---|
| `concepts/UICC_File_System` | concepts, entities, reference, research, summaries | 50 | 7 |
| `concepts/APDU` | concepts, entities, reference, research, summaries | 21 | 8 |
| `concepts/CAT_STK` | concepts, reference, research, summaries, syntheses | 27 | 11 |
| `concepts/eSIM` | concepts, entities, research, summaries, syntheses | 15 | 6 |
| `concepts/GlobalPlatform_Card` | concepts, entities, reference, research, summaries | 22 | 7 |
| `concepts/STK_Applet` | concepts, entities, reference, research, summaries | 27 | 12 |
| `summaries/gpc_card_spec_2_3_1` | concepts, entities, reference, research, summaries | 10 | 4 |
| `concepts/JavaCard` | concepts, reference, research, summaries, syntheses | 17 | 11 |
| `concepts/OTA_Remote_Management` | concepts, research, summaries, syntheses | 18 | 12 |
| `concepts/UICC` | concepts, entities, research, summaries, syntheses | 32 | 13 |
| `research/operator_icons_on_sim` | concepts, reference, research, summaries, syntheses | 10 | 10 |
| `research/plmn_selection_algorithm` | concepts, reference, research, summaries, syntheses | 5 | 15 |
| `summaries/ts_102221` | concepts, entities, reference, research, summaries | 35 | 4 |
| `syntheses/auth_evolution` | concepts, reference, research, summaries, syntheses | 15 | 8 |
| `syntheses/sim_files_location` | concepts, reference, research, summaries, syntheses | 5 | 9 |

## 📊 Матрица связности по типам

| Тип | Страниц | Avg In | Avg Out | Cross-type links |
|---|---|---|---|---|
| **concept** | 9 | 6.1 | 4.7 | 13 |
| **summary** | 21 | 2.7 | 4.0 | 31 |
| **synthesis** | 25 | 3.2 | 8.1 | 92 |
| **reference** | 5 | 7.8 | 4.6 | 8 |
| **research** | 9 | 5.3 | 13.7 | 66 |

## 📈 Распределение связности

### Inbound links

| Степень | Страниц |
|---|---|
| 1 in | 14 ██████████████ |
| 2 in | 17 █████████████████ |
| 3 in | 17 █████████████████ |
| 4 in | 16 ████████████████ |
| 5 in | 15 ███████████████ |
| 6 in | 6 ██████ |
| 7 in | 8 ████████ |
| 8 in | 3 ███ |
| 15 in | 3 ███ |
| 27 in | 2 ██ |

### Outbound links

| Степень | Страниц |
|---|---|
| 2 out | 10 ██████████ |
| 3 out | 16 ████████████████ |
| 4 out | 22 ██████████████████████ |
| 5 out | 14 ██████████████ |
| 6 out | 14 ██████████████ |
| 7 out | 12 ████████████ |
| 8 out | 9 █████████ |
| 9 out | 7 ███████ |
| 11 out | 6 ██████ |
| 12 out | 3 ███ |

## 🔧 Приоритеты исправлений

2. **Срочно**: добавить входящие ссылки на 1 сиротских страниц
3. **Важно**: усилить 32 страниц с <3 входящими ссылками
4. **Планово**: создать мосты для 1 изолированных кластеров
