#!/usr/bin/env python3
"""Сохранить веб-страницу заметкой в хранилище Obsidian.

Текст забирается через defuddle (markdown + метаданные), картинки скачиваются
в папку вложений и перелинковываются абсолютными ссылками хранилища, формат
подгоняется под правила obsidian-linter (.claude/rules/markdown.md).

Пример:
    save_url.py https://habr.com/ru/articles/1082610/ --tags ml,карьера
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parents[4]
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
SITE_NAMES = {"habr.com": "Хабр"}
EXT_BY_MIME = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "image/avif": "avif",
}
IMG_MD = re.compile(r"!\[([^\]]*)\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
IMG_HTML = re.compile(r"<img\b[^>]*?\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)
BAD_CHARS = re.compile(r"[\\/*?\"<>|#^\[\]]")


def die(msg: str, code: int = 1) -> None:
    print(f"ошибка: {msg}", file=sys.stderr)
    sys.exit(code)


def run_defuddle(url: str) -> dict:
    cmd = ["defuddle", "parse", url, "--json", "--md", "-u", USER_AGENT]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        die("defuddle не найден — npm install -g defuddle")
    except subprocess.CalledProcessError as e:
        die(f"defuddle завершился с ошибкой:\n{e.stderr.strip()}")
    return json.loads(out)


def safe_name(title: str) -> str:
    name = re.sub(r"\s*:\s*", " — ", title)
    name = BAD_CHARS.sub("", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:120].rstrip(" .")


def site_name(data: dict) -> str:
    for tag in data.get("metaTags") or []:
        if tag.get("property") == "og:site_name" and tag.get("content"):
            return tag["content"].strip()
    domain = (data.get("domain") or "").lower()
    return SITE_NAMES.get(domain) or data.get("site") or domain


def published_date(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        m = re.search(r"\d{4}-\d{2}-\d{2}", raw)
        return m.group(0) if m else None


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        ctype = resp.headers.get_content_type()
        return resp.read(), ctype


def guess_ext(url: str, ctype: str) -> str:
    if ctype in EXT_BY_MIME:
        return EXT_BY_MIME[ctype]
    m = re.search(r"\.(png|jpe?g|gif|webp|svg|avif)(?:[?#]|$)", url, re.I)
    return m.group(1).lower().replace("jpeg", "jpg") if m else "bin"


def split_code(md: str) -> list[tuple[bool, str]]:
    """Разбить текст на чередующиеся куски: (внутри_кода, текст)."""
    parts: list[tuple[bool, str]] = []
    buf: list[str] = []
    in_code = False
    for line in md.splitlines(keepends=True):
        if re.match(r"^\s*(```|~~~)", line):
            buf.append(line)
            if in_code:
                parts.append((True, "".join(buf)))
                buf = []
            else:
                if len(buf) > 1:
                    parts.append((False, "".join(buf[:-1])))
                buf = [line]
            in_code = not in_code
            continue
        buf.append(line)
    if buf:
        parts.append((in_code, "".join(buf)))
    return parts


def map_prose(md: str, fn) -> str:
    return "".join(chunk if is_code else fn(chunk) for is_code, chunk in split_code(md))


def process_images(md: str, name: str, files_dir: Path, link_prefix: str) -> tuple[str, list[str], list[str]]:
    md = IMG_HTML.sub(lambda m: f"![]({m.group(1)})", md)
    urls: list[str] = []
    for m in IMG_MD.finditer(md):
        if m.group(2).startswith(("http://", "https://")) and m.group(2) not in urls:
            urls.append(m.group(2))
    saved: list[str] = []
    failed: list[str] = []
    local: dict[str, str] = {}
    for i, url in enumerate(urls, 1):
        try:
            data, ctype = fetch(url)
        except Exception as e:  # noqa: BLE001 — любая сетевая ошибка: оставляем внешнюю ссылку
            failed.append(f"{url} ({e})")
            continue
        fname = f"{name} — {i:02d}.{guess_ext(url, ctype)}"
        (files_dir / fname).write_bytes(data)
        local[url] = f"<{link_prefix}/{fname}>"
        saved.append(fname)

    def repl(m: re.Match) -> str:
        target = local.get(m.group(2))
        return f"![{m.group(1)}]({target})" if target else m.group(0)

    return IMG_MD.sub(repl, md), saved, failed


def normalize(md: str) -> str:
    def prose(chunk: str) -> str:
        chunk = chunk.replace("«", '"').replace("»", '"')
        chunk = chunk.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        chunk = chunk.replace("\u00a0", " ")
        chunk = re.sub(r"^\t+", lambda m: "    " * len(m.group(0)), chunk, flags=re.M)
        chunk = re.sub(r"[ \t]+$", "", chunk, flags=re.M)
        return chunk

    def fences(chunk: str) -> str:
        """Табы отступа вложенного код-блока → пробелы; табы внутри самого кода не трогаем."""
        lines = chunk.splitlines(keepends=True)
        depth = len(lines[0]) - len(lines[0].lstrip("\t"))
        if depth == 0:
            return chunk
        return "".join(re.sub(rf"^\t{{1,{depth}}}", lambda m: "    " * len(m.group(0)), line) for line in lines)

    md = "".join(fences(c) if is_code else prose(c) for is_code, c in split_code(md))
    levels = [len(m.group(1)) for is_code, chunk in split_code(md) if not is_code
              for m in re.finditer(r"^(#{1,6}) ", chunk, re.M)]
    if levels and (shift := min(levels) - 1) > 0:
        md = map_prose(md, lambda c: re.sub(r"^(#{1,6}) ", lambda m: "#" * (len(m.group(1)) - shift) + " ", c, flags=re.M))
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def build_note(data: dict, url: str, body: str, tags: list[str]) -> str:
    title = data["title"].strip()
    author = (data.get("author") or "").strip()
    date = published_date(data.get("published"))
    fm = ["---", "tags:"] + [f"  - {t}" for t in tags] + [f"source: {url}"]
    if author:
        fm.append(f"author: {author}")
    if date:
        fm.append(f"published: {date}")
    fm.append("---")
    cite = [site_name(data)]
    if author:
        cite.append(author)
    if date:
        cite.append(datetime.fromisoformat(date).strftime("%d.%m.%Y"))
    callout = f"> [!info] Источник\n> [{title}]({url}) — {', '.join(cite)}."
    return "\n".join(fm) + "\n\n" + callout + "\n\n" + body


def print_vocab(vault: Path) -> None:
    """Частоты тегов из frontmatter заметок (кроме служебных папок)."""
    skip = {"archive", "templates", "_files", "tmp"}
    counts: dict[str, int] = {}
    for path in vault.rglob("*.md"):
        rel = path.relative_to(vault)
        if rel.parts[0].startswith(".") or rel.parts[0] in skip:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---") or text.count("---") < 2:
            continue
        in_tags = False
        for line in text.split("---", 2)[1].splitlines():
            if re.match(r"^tags:\s*$", line):
                in_tags = True
            elif in_tags and (m := re.match(r"^\s+-\s+(\S+)", line)):
                counts[m.group(1)] = counts.get(m.group(1), 0) + 1
            elif in_tags and not line.startswith(" "):
                in_tags = False
    for tag, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{n:4d}  {tag}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?")
    ap.add_argument("--tags", default="", help="теги через запятую")
    ap.add_argument("--name", help="имя заметки без .md (по умолчанию — из заголовка страницы)")
    ap.add_argument("--out-dir", default="inbox", help="папка заметки относительно хранилища")
    ap.add_argument("--files-dir", default="_files", help="папка вложений относительно хранилища")
    ap.add_argument("--vault", type=Path, default=VAULT, help="корень хранилища")
    ap.add_argument("--force", action="store_true", help="перезаписать существующую заметку")
    ap.add_argument("--vocab", action="store_true", help="показать словарь тегов хранилища (частоты) и выйти")
    args = ap.parse_args()

    vault = args.vault.resolve()
    if args.vocab:
        print_vocab(vault)
        return
    if not args.url:
        ap.error("нужен URL")
    out_dir = (vault / args.out_dir).resolve()
    files_dir = (vault / args.files_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    files_dir.mkdir(parents=True, exist_ok=True)
    link_prefix = "/" + files_dir.relative_to(vault).as_posix() if files_dir.is_relative_to(vault) else files_dir.as_posix()

    data = run_defuddle(args.url)
    if not data.get("title") or not data.get("content"):
        die("defuddle не извлёк заголовок или текст — страница не разобрана")
    name = args.name or safe_name(data["title"])
    note_path = out_dir / f"{name}.md"
    if note_path.exists() and not args.force:
        die(f"заметка уже есть: {note_path} (перезапись — --force)", 2)

    body, saved, failed = process_images(data["content"], name, files_dir, link_prefix)
    body = normalize(body)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    note_path.write_text(build_note(data, args.url, body, tags), encoding="utf-8")

    print(f"заметка: {note_path.relative_to(vault) if note_path.is_relative_to(vault) else note_path}")
    print(f"картинок сохранено: {len(saved)}" + (f" в {link_prefix}/" if saved else ""))
    for f in failed:
        print(f"не скачалось (осталась внешняя ссылка): {f}")
    print(f"слов: {data.get('wordCount', '?')}, автор: {data.get('author') or '—'}, дата: {published_date(data.get('published')) or '—'}")
    heads = [m.group(1) for is_code, c in split_code(body) if not is_code for m in re.finditer(r"^(#{1,6}) ", c, re.M)]
    print(f"заголовков: {len(heads)}" + (f" (уровни {min(heads, key=len)}…{max(heads, key=len)})" if heads else ""))
    ext = sum(1 for is_code, c in split_code(body) if not is_code for m in IMG_MD.finditer(c) if m.group(2).startswith("http"))
    if ext:
        print(f"внешних картинок осталось в тексте: {ext}")


if __name__ == "__main__":
    main()
