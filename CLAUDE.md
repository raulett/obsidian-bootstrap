# CLAUDE.md

Инструкции для AI-агента (Claude Code), работающего с этим хранилищем. Claude подхватывает этот файл автоматически из корня хранилища.

## Что это

Это личный **second brain** в Obsidian — база заметок одного владельца, а не кодовая база: нет сборки, тестов и «приложения». Хранилищем управляют **параллельно двое**: владелец через интерфейс Obsidian и ты (AI) через файловую систему. Любое твоё изменение должно остаться корректным после того, как Obsidian его подхватит и переформатирует.

- Контент заметок — на **русском языке**.
- Ты помогаешь владельцу вести его базу: захватывать, структурировать, связывать и находить знания. Действуй как аккуратный второй редактор: крупные перестройки, массовые переименования и удаление — только по явной просьбе.

## Конвенции хранилища (легко нарушить по привычке)

1. **Ссылки — стандартный Markdown с абсолютным путём от корня хранилища, НЕ wikilinks.** Пиши `[Текст](Папка/Заметка.md)` и `![](_files/файл.png)`, а не `[[Заметка]]`. Настройки: `useMarkdownLinks: true`, `newLinkFormat: "absolute"`. Плагины `better-markdown-links` и `consistent-attachments-and-links` нормализуют ссылки и чинят их при перемещении/переименовании.
2. **Новые заметки → `inbox/`** — посадочная папка для всего входящего и для результатов ресёрча.
3. **Вложения → `_files/`** (картинки, PDF и т.п.). Папка скрыта из навигатора.
4. **Шаблоны → `templates/`.**

## Карта папок

- `inbox/` — входящие: быстрый захват и неразобранные черновики; сюда же падают результаты ресёрча.
- `knowledge/` — постоянная база знаний: атомарные «вечнозелёные» заметки.
- `meetings/` — заметки встреч.
- `projects/` — проектные заметки и материалы.
- `archive/` — то, что потеряло актуальность (не удаляй — архивируй).
- `_files/` — вложения (скрыта, исключена из проверок ссылок).
- `templates/` — шаблоны заметок.

## Как вести second brain (рабочий метод)

1. **Захват:** всё новое и недодуманное — в `inbox/`. Не раскладывай преждевременно.
2. **Разбор inbox:** периодически разбирай `inbox/` — атомизируй, добавляй ссылки на связанные заметки, переноси «вечнозелёное» в `knowledge/`, встречи в `meetings/`, проектное в `projects/`.
3. **Связывай:** строй граф знаний markdown-ссылками между заметками — это ценнее тегов и папок.
4. **Архивируй, не удаляй:** устаревшее перемещай в `archive/`.
5. **Ресёрч:** когда нужно изучить тему — собери источники и сохрани готовую заметку в `inbox/`.

## Frontmatter и даты — не трогай руками

Плагин `frontmatter-date-manager` сам ведёт поля **`created`**, **`updated`**, **`updated_count`** (формат `yyyy-MM-dd'T'HH:mm:ss`), пока Obsidian открыт.

- **Не задавай и не правь `updated` / `updated_count`** — плагин перезапишет.
- `created` плагин ставит при создании заметки в Obsidian. Если создаёшь файл через ФС при **закрытом** Obsidian и нужна дата сразу — можешь задать `created` сам в том же формате.
- **Файлы-исключения (плагин их не трогает):** `README.md`, `CLAUDE.md`, и всё в `.claude/`, `templates/`, `tmp/`.

## Редактирование: ожидай вмешательства Obsidian

Запущенный Obsidian мгновенно подхватывает изменения на диске, а плагины могут сами дописать/переписать файл (даты во frontmatter, нормализация ссылок). **Не удивляйся расхождению с тем, что записал, и не перезаписывай вслепую** — сначала перечитай актуальное содержимое.

## Git и синхронизация

- Синхронизация — через плагин `obsidian-git`: `pull` при старте (`autoPullOnBoot`) **плюс** авто-commit-and-sync и авто-`pull` каждые 15 минут (`autoSaveInterval`/`autoPullInterval`; режим `autoBackupAfterFileChange` — коммит через 15 минут после последней правки). Пока Obsidian открыт, плагин сам коммитит и пушит все изменения в рабочем дереве — в том числе твои.
- **Сам через git (Bash) не коммить и не пушь без явной просьбы** — за регулярную синхронизацию отвечает плагин.
- Перед началом работы помни, что Obsidian мог сделать pull — проверяй актуальное состояние репозитория.

## Плагины, влияющие на редактирование

- `obsidian-linter` — установлен, но все правила сейчас отключены: автоформатирования при сохранении нет.
- Core-плагины `bases` (`.base` — табличные/карточные представления) и `canvas` (`.canvas`) включены.
- Активно: `omnisearch` (полнотекстовый поиск), `notebook-navigator`, `table-editor-obsidian`, `obsidian-heading-shifter`.

## Репозитории внешних плагинов

Понадобились детали поведения плагина или его настройки — **открой исходный код в репозитории, не угадывай и не реверси по сборке**. Маппинг `id → репозиторий` (id совпадает с папкой в `.obsidian/plugins/` и с ключами в `data.json`/настройках):

- `better-markdown-links` — Better Markdown Links — https://github.com/mnaoumov/obsidian-better-markdown-links
- `consistent-attachments-and-links` — Consistent Attachments and Links — https://github.com/dy-sh/obsidian-consistent-attachments-and-links
- `data-files-editor` — Data Files Editor — https://github.com/ZukTol/obsidian-data-files-editor
- `frontmatter-date-manager` — Frontmatter Date Manager — https://github.com/SmetDenis/obsidian-frontmatter-date-manager
- `notebook-navigator` — Notebook Navigator — https://github.com/johansan/notebook-navigator
- `obsidian-git` — Git — https://github.com/Vinzent03/obsidian-git
- `obsidian-heading-shifter` — Heading Shifter — https://github.com/k4a-l/obsidian-heading-shifter
- `obsidian-linter` — Linter — https://github.com/platers/obsidian-linter
- `omnisearch` — Omnisearch — https://github.com/scambier/obsidian-omnisearch
- `open-tab-settings` — Open Tab Settings — https://github.com/jesse-r-s-hines/obsidian-open-tab-settings
- `table-editor-obsidian` — Advanced Tables — https://github.com/tgrosinger/advanced-tables-obsidian

## Скиллы (входят в шаблон, `.claude/skills/`)

- **Разметка заметок:** `obsidian-markdown` — Obsidian-синтаксис (коллауты, эмбеды, свойства/frontmatter).
- **`.base` и `.canvas`:** `obsidian-bases` (табличные/карточные представления) и `json-canvas` (канвасы, mind maps, схемы).
- **Хранилище из CLI:** `obsidian-cli` — чтение/создание/поиск заметок, задачи, свойства.
- **Чтение веб-страниц:** `defuddle` — чистый markdown из страницы для ресёрча; готовую заметку сохраняй в `inbox/`.

## Личные правки

Личные инструкции, не входящие в общий шаблон, держи в `CLAUDE.local.md` в корне: он в `.gitignore`, а Claude грузит его автоматически рядом с `CLAUDE.md`.
