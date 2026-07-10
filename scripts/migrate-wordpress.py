#!/usr/bin/env python3
"""Migrate WordPress XML export to Astro content collections."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
XML_PATH = ROOT.parent / "erwachsenenfragende.WordPress.2026-07-10.xml"
PUBLIC_MEDIA = ROOT / "public" / "images" / "media"
BLOG_DIR = ROOT / "src" / "content" / "blog"
PAGES_DIR = ROOT / "src" / "content" / "pages"
AUTHORS_DIR = ROOT / "src" / "content" / "authors"
CATEGORIES_DIR = ROOT / "src" / "content" / "categories"
TAGS_DIR = ROOT / "src" / "content" / "tags"
WP_BASE = "https://erwachsenenfragen.de"

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}


def cdata_text(el) -> str:
    if el is None or el.text is None:
        return ""
    return el.text


def yaml_quote(value: str) -> str:
    if not value:
        return '""'
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    if any(c in value for c in ':#[]{}&,*?|>-<>=!%@`'):
        return f'"{escaped}"'
    return f'"{escaped}"'


def strip_wp_blocks(html: str) -> str:
    html = re.sub(r"<!--\s*/?wp:[^>]+-->", "", html)
    html = re.sub(r"<!--\s*wp:[^>]+-->", "", html)
    return html.strip()


    inner = "\n".join(fixed_lines).strip()
    return f'<div class="wp-content">\n{inner}\n</div>\n'


def html_to_mdx_body(html: str) -> str:
    html = unescape(html or "")
    html = strip_wp_blocks(html)
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.I | re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.I | re.S)
    html = re.sub(r"\[dwqa-submit-question-form\]", "", html)
    lines = html.splitlines()
    fixed_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            fixed_lines.append("")
            continue
        if stripped.startswith("<") or stripped.startswith("{"):
            fixed_lines.append(stripped)
        else:
            fixed_lines.append(f"<p>{stripped}</p>")
    inner = "\n".join(fixed_lines).strip()
    return inner


def excerpt_from_content(html: str, max_len: int = 200) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def local_media_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    if "/wp-content/uploads/" not in path:
        return url
    rel = path.split("/wp-content/uploads/", 1)[1]
    return f"/images/media/{rel}"


def download_file(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        subprocess.run(
            ["curl", "-sfL", url, "-o", str(dest)],
            check=True,
            capture_output=True,
            timeout=120,
        )
        return dest.exists() and dest.stat().st_size > 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def replace_media_urls(content: str, url_map: dict[str, str]) -> str:
    for remote, local in sorted(url_map.items(), key=lambda x: -len(x[0])):
        content = content.replace(remote, local)
        content = content.replace(remote.replace("https://", "http://"), local)
    return content


def yaml_block_scalar(value: str) -> str:
    if not value:
        return '""'
    # Use literal block scalar for multiline HTML
    escaped = value.replace("\n", "\n  ")
    return f"|\n  {escaped}"


def write_frontmatter(fields: dict) -> str:
    lines = ["---"]
    content_html = fields.pop("contentHtml", None)
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {yaml_quote(str(item))}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {yaml_quote(str(value))}")
    if content_html:
        lines.append(f"contentHtml: {yaml_block_scalar(content_html)}")
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    if not XML_PATH.exists():
        print(f"XML not found: {XML_PATH}", file=sys.stderr)
        return 1

    tree = ET.parse(XML_PATH)
    channel = tree.getroot().find("channel")

    # Attachment map
    attachments: dict[str, str] = {}
    for item in channel.findall("item"):
        if cdata_text(item.find("wp:post_type", NS)) != "attachment":
            continue
        pid = cdata_text(item.find("wp:post_id", NS))
        url = cdata_text(item.find("wp:attachment_url", NS))
        if pid and url:
            attachments[pid] = url

    url_map: dict[str, str] = {}
    downloaded = 0
    for url in set(attachments.values()):
        local_web = local_media_path(url)
        rel = local_web.replace("/images/media/", "")
        dest = PUBLIC_MEDIA / rel
        if download_file(url, dest):
            url_map[url] = local_web
            downloaded += 1
        else:
            print(f"WARN: failed download {url}", file=sys.stderr)

    print(f"Downloaded {downloaded} media files")

    # Categories & tags
    categories = []
    for c in channel.findall("wp:category", NS):
        categories.append(
            {
                "slug": cdata_text(c.find("wp:category_nicename", NS)),
                "name": cdata_text(c.find("wp:cat_name", NS)),
            }
        )

    tags = []
    for t in channel.findall("wp:tag", NS):
        tags.append(
            {
                "slug": cdata_text(t.find("wp:tag_slug", NS)),
                "name": cdata_text(t.find("wp:tag_name", NS)),
            }
        )

    authors: dict[str, dict] = {}

  # Clean output dirs
    for d in [BLOG_DIR, PAGES_DIR, AUTHORS_DIR, CATEGORIES_DIR, TAGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*"):
            if f.is_file():
                f.unlink()

    blog_count = 0
    page_count = 0

    for item in channel.findall("item"):
        post_type = cdata_text(item.find("wp:post_type", NS))
        status = cdata_text(item.find("wp:status", NS))
        if status != "publish":
            continue

        slug = cdata_text(item.find("wp:post_name", NS))
        title = cdata_text(item.find("title"))
        creator = cdata_text(item.find("dc:creator", NS))
        pub_date = cdata_text(item.find("wp:post_date", NS))
        mod_date = cdata_text(item.find("wp:post_modified", NS))
        raw_content = cdata_text(item.find("content:encoded", NS))
        raw_excerpt = cdata_text(item.find("excerpt:encoded", NS))

        item_categories = [
            c.text for c in item.findall("category") if c.get("domain") == "category" and c.text
        ]
        item_tags = [
            c.text for c in item.findall("category") if c.get("domain") == "post_tag" and c.text
        ]

        if creator:
            if creator not in authors:
                authors[creator] = {"slug": creator, "name": creator, "postCount": 0}
            authors[creator]["postCount"] += 1 if post_type == "post" else 0

        thumbnail_id = None
        for meta in item.findall("wp:postmeta", NS):
            if cdata_text(meta.find("wp:meta_key", NS)) == "_thumbnail_id":
                thumbnail_id = cdata_text(meta.find("wp:meta_value", NS))
                break

        featured_image = ""
        if thumbnail_id and thumbnail_id in attachments:
            thumb_url = attachments[thumbnail_id]
            local_web = local_media_path(thumb_url)
            rel = local_web.replace("/images/media/", "")
            dest = PUBLIC_MEDIA / rel
            if download_file(thumb_url, dest):
                url_map[thumb_url] = local_web
                featured_image = local_web

        body = replace_media_urls(html_to_mdx_body(raw_content), url_map)
        description = raw_excerpt.strip() or excerpt_from_content(raw_content)

        if post_type == "post":
            fields = {
                "title": title,
                "description": description,
                "pubDate": pub_date,
                "updatedDate": mod_date if mod_date != pub_date else None,
                "author": creator,
                "categories": item_categories,
                "tags": item_tags,
                "image": featured_image or None,
                "imageAlt": title,
                "contentHtml": body or f"<p>{description}</p>",
            }
            out = BLOG_DIR / f"{slug}.mdx"
            out.write_text(
                write_frontmatter(fields) + "\n\n{/* Migrated WordPress content */}\n",
                encoding="utf-8",
            )
            blog_count += 1

        elif post_type == "page" and slug not in ("home",):
            fields = {
                "title": title,
                "description": description,
                "pubDate": pub_date,
                "updatedDate": mod_date if mod_date != pub_date else None,
                "slug": slug,
                "contentHtml": body or f"<p>{title}</p>",
            }
            out = PAGES_DIR / f"{slug}.mdx"
            out.write_text(
                write_frontmatter(fields) + "\n\n{/* Migrated WordPress content */}\n",
                encoding="utf-8",
            )
            page_count += 1

    # Write metadata
    for cat in categories:
        (CATEGORIES_DIR / f"{cat['slug']}.json").write_text(
            json.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    for tag in tags:
        (TAGS_DIR / f"{tag['slug']}.json").write_text(
            json.dumps(tag, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    for author in authors.values():
        (AUTHORS_DIR / f"{author['slug']}.json").write_text(
            json.dumps(author, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Navigation from nav_menu_item
    nav_items = []
    for item in channel.findall("item"):
        if cdata_text(item.find("wp:post_type", NS)) != "nav_menu_item":
            continue
        if cdata_text(item.find("wp:status", NS)) != "publish":
            continue
        title = cdata_text(item.find("title"))
        url = ""
        parent = "0"
        for meta in item.findall("wp:postmeta", NS):
            key = cdata_text(meta.find("wp:meta_key", NS))
            val = cdata_text(meta.find("wp:meta_value", NS))
            if key == "_menu_item_url":
                url = val
            elif key == "_menu_item_menu_item_parent":
                parent = val or "0"
        if title and title != " ":
            nav_items.append({"title": title, "url": url, "parent": parent})

    (ROOT / "src" / "data" / "nav-menu.json").write_text(
        json.dumps(nav_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "blogs": blog_count,
        "pages": page_count,
        "categories": len(categories),
        "tags": len(tags),
        "authors": len(authors),
        "mediaDownloaded": downloaded,
        "navItems": len(nav_items),
    }
    (ROOT / "migration-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
