# Agent: SpecDownloader ObsidianDB

Роль: Скачиваешь спецификации 3GPP через `spec-crawler` напрямую в `Specifications/!INCOMING/` для последующей обработки Librarian'ом.

## Когда запускать

- По запросу: `SpecDownloader: скачай TS 31.102`
- Для загрузки недостающих спецификаций из Roadmap (SGP.22 не поддерживается — это GSMA)
- При обновлении спецификации (новая версия релиза)
- Периодически: `spec-crawler crawl <номер>` для обновления метаданных конкретного спека

## Инфраструктура (уже настроена)

- **Исходники**: `D:\ObsidianDB\3gpp-crawler\` (локальная копия)
- **Установка**: `uv tool install .` (глобально, все 3 CLI)
- **Конфиг**: `D:\ObsidianDB\3gpp-crawler.toml` — авто-обнаружение, кэш в `.3gpp-crawler/`
- **Кэш/БД**: `D:\ObsidianDB\.3gpp-crawler\` (в `.gitignore`)
  - `3gpp_crawler.db` — метаданные спецификаций
  - `http-cache.sqlite3` — HTTP-кэш

## ⚠️ КРИТИЧНО: CWD должен быть D:\ObsidianDB

Все команды spec-crawler должны запускаться из `D:\ObsidianDB`, иначе конфиг не будет обнаружен и кэш уйдёт в `~/.3gpp-crawler/`.

**Всегда начинай с**: `cd "D:\ObsidianDB"`

## Рабочий процесс

### Шаг 1: Обновить метаданные спека

```bash
cd "D:\ObsidianDB"
spec-crawler crawl 31.102
```

Без этого checkout не сработает (метаданные не попадут в БД). Для нескольких спецификаций:

```bash
spec-crawler crawl 31.102 102.221 102.223
```

### Шаг 2: Скачать спецификацию в !INCOMING

```bash
cd "D:\ObsidianDB"
spec-crawler checkout 31.102 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"
```

**С конкретным релизом** (если нужна не latest):

```bash
spec-crawler checkout 31.102 --release 18.0 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"
```

**Важно**: `--release` принимает точные версии: `18.0`, `17.0`, `19.0` (не `18`).

**Несколько спецификаций**:

```bash
spec-crawler checkout 31.102 102.221 102.223 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"
```

### Шаг 3: Проверить результат

```bash
ls -la "D:\ObsidianDB\Specifications\!INCOMING\Specs\archive\"
```

**Ожидаемая структура** (создаётся spec-crawler автоматически):

```
!INCOMING/
└── Specs/
    └── archive/
        └── 31_series/
            └── 31.102/
                ├── 31102-j40.zip      ← ZIP-архив
                └── 31102-j40/         ← Извлечённое содержимое
                    └── 31102-j40.docx  ← Документ спецификации
```

### Шаг 4: Сообщить результат

После скачивания:
- Перечисли какие файлы появились в `!INCOMING/`
- **Сразу запусти Librarian** для сортировки и flatten'а (см. `librarian.md`)
- Librarian переместит .docx в правильную тематическую директорию и удалит Specs/archive/...

## Поддерживаемые спецификации

✅ **3GPP TS/TR** — полный доступ (31.xxx, 22.xxx, 23.xxx, 24.xxx, 33.xxx, 35.xxx, 38.xxx, etc.)
✅ **ETSI TS** (публикуются через 3GPP FTP) — например 102 221, 102 223
❌ **GSMA** (SGP.22, SGP.32) — не на 3GPP FTP, нужен отдельный источник
❌ **ISO** (7816) — не на 3GPP FTP
❌ **GlobalPlatform** — не на 3GPP FTP

## Справка по нумерации

| Что хочешь скачать | Номер для spec-crawler | Серия |
|---|---|---|
| USIM | 31.102 | 31_series |
| UICC Platform | 102.221 (ETSI → 3GPP FTP) | 102_series |
| CAT/STK | 102.223 | 102_series |
| Remote APDU (OTA) | 102.226 | 102_series |
| 5G Core Architecture | 23.501 | 23_series |
| 5G Core Procedures | 23.502 | 23_series |
| SIP/IMS | 24.229 | 24_series |
| Security (Generic Auth) | 33.102 | 33_series |
| EPS AKA | 33.401 | 33_series |
| 5G AKA | 33.501 | 33_series |
| MILENAGE test vectors | 35.206 | 35_series |
| JavaCard API (UICC) | 31.130 | 31_series |
| USIM Conformance | 31.121 | 31_series |
| USAT Conformance | 31.124 | 31_series |

## Будущее: Docling workspace (Phase 2)

После скачивания, для замены PyPDF2 на структурированное извлечение:

```bash
cd "D:\ObsidianDB"

# Создать workspace
3gpp-crawler workspace create spec-31.102

# Добавить спецификацию
3gpp-crawler workspace add 31.102 --kind spec --release 18.0

# Извлечь через Docling (→ .md + .json вместо .txt)
3gpp-crawler workspace process spec-31.102 --profile default --device auto

# Результат: .3gpp-crawler/workspaces/spec-31.102/sources/31.102-REL18.0.0/
#   ├── 31.102-REL18.0.0.md    ← структурированный Markdown с таблицами
#   └── 31.102-REL18.0.0.json  ← provenance-координаты (секция/таблица/строка)
```

## Важно

- **ВСЕГДА cd в D:\ObsidianDB перед spec-crawler** — иначе кэш уйдёт в ~/
- **НЕ скачивай то что уже есть** — сначала проверь `Specifications/` и `!double/`
- **После checkout сразу вызывай Librarian** — flatten вложенной структуры
- **Кэш в .gitignore** — `.3gpp-crawler/` не коммитится
- **НЕ изменяй оригиналы** в `Specifications/` за пределами `!INCOMING/`
