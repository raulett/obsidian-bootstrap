# Properties (Frontmatter) Reference

Properties use YAML frontmatter at the start of a note:

```yaml
---
title: My Note Title
date: 2024-01-15
tags:
  - project
  - important
aliases:
  - My Note
  - Alternative Name
cssclasses:
  - custom-class
status: in-progress
rating: 4.5
completed: false
due: 2024-02-01T14:30:00
---
```

## Property Types

| Type | Example |
|------|---------|
| Text | `title: My Title` |
| Number | `rating: 4.5` |
| Checkbox | `completed: true` |
| Date | `date: 2024-01-15` |
| Date & Time | `due: 2024-01-15T14:30:00` |
| List | multiline YAML list (see below) |
| Links | `related: "[Other Note](</Folder/Other Note.md>)"` |

In THIS vault, list properties like `tags` and `aliases` are written as a multiline YAML list (one `-` item per line), not as an inline array `[a, b]` — a vault convention for clean diffs (the YAML-array linter rule is currently off, so keep this style yourself). Link properties use Markdown links with an absolute path from the vault root, in angle brackets with a leading `/` (e.g. `[Other Note](</Folder/Other Note.md>)`), not `[[wikilinks]]` (`useMarkdownLinks: true`, `newLinkFormat: absolute`).

## Default Properties

- `tags` - Note tags (searchable, shown in graph view)
- `aliases` - Alternative names for the note (used in link suggestions)
- `cssclasses` - CSS classes applied to the note in reading/editing view

## Tags

```markdown
#tag
#nested/tag
#tag-with-dashes
#tag_with_underscores
```

Tags can contain: letters (any language), numbers (not first character), underscores `_`, hyphens `-`, forward slashes `/` (for nesting).

In frontmatter:

```yaml
---
tags:
  - tag1
  - nested/tag2
---
```
