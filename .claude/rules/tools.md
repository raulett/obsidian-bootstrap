# Инструменты работы с хранилищем

Как ты (AI) выбираешь канал доступа к базе. **Базовый принцип:** файловые инструменты — основа, работают всегда. MCP-сервер `obsidian` и `obsidian-cli` — опциональные усиления: дают то, чего нет у файлов, но доступны, **только пока Obsidian открыт**. Недоступны — спокойно работай файлами (фолбэк), не блокируйся и не считай это ошибкой.

## Каналы

### 1. Файлы — основной канал (всегда доступен)

`Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` (`mv`, `rg`, `fd`, `jq`, `yq`). Работают с диском независимо от того, запущен ли Obsidian.

- Чтение, создание, правка, перемещение (`mv`), удаление заметок.
- Текстовый/regex-поиск (`Grep`), поиск файлов по имени (`Glob`/`fd`).
- **Любая запись в базу идёт через файлы** — это дефолт.

### 2. MCP-сервер `obsidian` — опциональное усиление (Obsidian открыт)

Сконфигурирован в `.mcp.json`, включён в `.claude/settings.json`; работает поверх плагина Local REST API. Закрыт Obsidian — недоступен, фолбэк на файлы. Подключай для того, чего файлы не умеют:

- **Поиск** `obsidian_search_notes`: режим `omnisearch` (релевантность BM25) и `jsonlogic` (Dataview-запросы по frontmatter/тегам) — точнее «слепого» grep.
- **Навигация по длинной заметке** `obsidian_get_note`: структурная карта документа, чтение по секции.
- **Показать владельцу** `obsidian_open_in_ui` — открыть заметку в интерфейсе Obsidian.
- **Команды Obsidian** `obsidian_execute_command` (+ `obsidian_list_commands`).
- **Теги** `obsidian_list_tags`, `obsidian_manage_tags`.
- **Frontmatter** `obsidian_manage_frontmatter` (atomic get/set/delete). НЕ трогай `created`/`updated` — их ведёт плагин (см. `CLAUDE.md`).
- Сервер умеет и CRUD (`write`/`patch`/`append`/`replace`/`delete`), но по умолчанию запись веди файлами.

### 3. `obsidian-cli` — опциональное усиление (Obsidian открыт)

Скилл поверх бинаря `obsidian` (часть Obsidian.app, говорит с живым приложением напрямую). Закрыт Obsidian — не работает. Подключай за тем, чего нет ни у файлов, ни у MCP:

- **`backlinks`** — обратные ссылки по резолвленному графу Obsidian (grep даёт лишь текст, не граф).
- **`tasks`** — сбор задач по области/статусу.
- **Шаблоны** при создании (`template=`), **`--copy`** — вывод в буфер обмена.
- **dev-слой** (`eval`, `plugin:reload`, `dev:screenshot`/`dom`/`css`/`console`/`errors`) — для разработки плагинов/тем.
- CRUD и поиск дублируют файлы/MCP — для них бери файлы/MCP.

### Скиллы-знания (всегда доступны)

- **obsidian-markdown** — синтаксис Obsidian (коллауты, эмбеды, properties, math, Mermaid). Ссылки и эмбеды — **по конвенции хранилища** (markdown с абсолютным путём), не wikilinks.
- **obsidian-bases** — формат `.base` (виды, фильтры, формулы, сводки).
- **json-canvas** — формат `.canvas` (ноды, рёбра, группы).
- **defuddle** — чистый markdown из веб-страницы для ресёрча; готовую заметку клади в `inbox/`.

## Матрица «задача → чем»

| Задача | Основной (всегда) | Усиление (Obsidian открыт) |
|--------|-------------------|----------------------------|
| Чтение / запись / правка | `Read` / `Write` / `Edit` | `obsidian_get_note` / `_patch_note` / `_write_note`; шаблоны (cli) |
| Перемещение / удаление | `Bash` `mv` / `rm` | `obsidian_delete_note` |
| Текстовый поиск | `Grep` | `obsidian_search_notes` (text) |
| Релевантный / Dataview-поиск | — | `obsidian_search_notes` omnisearch / jsonlogic |
| Бэклинки (граф связей) | `Grep` (только текст) | `obsidian-cli backlinks` |
| Задачи | `Grep` по `- [ ]` | `obsidian-cli tasks` |
| Теги / frontmatter | `Grep` / `Edit` | `obsidian_list_tags` / `obsidian_manage_frontmatter` |
| Команда Obsidian / показать в UI | — | `obsidian_execute_command` / `obsidian_open_in_ui` |
| `.base` / `.canvas` | `Write`/`Edit` + скилл | — |
| Веб-ресёрч | `defuddle` | — |

> Внешние корпоративные системы (Nextcloud, Outline) — отдельный канал со своими правилами (по умолчанию только чтение): `.claude/rules/integrations.md`.

## Фолбэк (MCP/cli недоступны)

Obsidian закрыт или сервер не отвечает — нормальная ситуация, не ошибка. Переключайся на файлы: `Grep` вместо omnisearch, текстовый поиск вместо графа бэклинков, `Edit` вместо `manage_frontmatter`. Базовый рабочий процесс целиком обеспечивается файловыми инструментами — MCP и cli лишь ускоряют и уточняют отдельные операции.
