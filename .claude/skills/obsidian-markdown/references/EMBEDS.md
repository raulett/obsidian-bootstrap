# Embeds Reference

> Obsidian also supports `![[wikilink]]` embeds, but THIS vault uses Markdown embeds with absolute paths from the vault root, in angle brackets with a leading `/` — e.g. `![](</Folder/Note Name.md>)` (`useMarkdownLinks: true`, `newLinkFormat: absolute`, `better-markdown-links` defaults) — do NOT use `![[...]]` here; the link plugins normalize embeds to this form. Attachments live in `_files/`.

## Embed Notes

```markdown
![](</Folder/Note Name.md>)
![](</Folder/Note Name.md#Heading>)
![](</Folder/Note Name.md#^block-id>)
```

## Embed Images

```markdown
![](</_files/image.png>)
![|640x480](</_files/image.png>)    Width x Height (in alt text)
![|300](</_files/image.png>)        Width only (maintains aspect ratio)
```

## External Images

```markdown
![Alt text](https://example.com/image.png)
![Alt text|300](https://example.com/image.png)
```

## Embed Audio

```markdown
![](</_files/audio.mp3>)
![](</_files/audio.ogg>)
```

## Embed PDF

```markdown
![](</_files/document.pdf>)
![](</_files/document.pdf#page=3>)
![](</_files/document.pdf#height=400>)
```

## Embed Bases

```markdown
![](</Folder/BaseFile.base>)
![](</Folder/BaseFile.base#View Name>)
```

## Embed Lists

```markdown
![](</Folder/Note.md#^list-id>)
```

Where the list has a block ID:

```markdown
- Item 1
- Item 2
- Item 3

^list-id
```

## Embed Search Results

````markdown
```query
tag:#project status:done
```
````
