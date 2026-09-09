#!/usr/bin/env python3
"""检查仓库内 HTML 的本地链接是否指向存在且非空的文件。"""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def broken_links():
    broken = []
    for html in ROOT.rglob("*.html"):
        parser = LinkParser()
        parser.feed(html.read_text(encoding="utf-8"))
        for href in parser.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (html.parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(ROOT):
                broken.append((html, href, "超出仓库"))
            elif not target.is_file():
                broken.append((html, href, "目标不存在"))
            elif target.stat().st_size == 0:
                broken.append((html, href, "目标为空"))
    return broken


def main():
    broken = broken_links()
    if broken:
        for source, href, reason in broken:
            print(f"{source.relative_to(ROOT)} -> {href} ({reason})")
        raise SystemExit(f"发现 {len(broken)} 个失效 HTML 链接")
    print("HTML 本地链接检查通过")


if __name__ == "__main__":
    main()
