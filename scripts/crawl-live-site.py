#!/usr/bin/env python3
"""Crawl live WordPress pages and migrate rendered HTML into Astro content."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
import time
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
XML_PATH = ROOT.parent / "erwachsenenfragende.WordPress.2026-07-10.xml"
PAGES_DIR = ROOT / "src" / "content" / "pages"
HTML_DIR = ROOT / "src" / "content" / "page-html"
PUBLIC_MEDIA = ROOT / "public" / "images" / "media"
WP_BASE = "https://erwachsenenfragen.de"

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
}


def fetch(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "60", "-A", "Mozilla/5.0 (compatible; AstroMigration/1.0)", url],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch {url}: {result.stderr}")
    return result.stdout


def extract_main_html(html: str) -> str:
    header_marker = "elementor-location-header"
    footer_marker = "elementor-location-footer"
    start = html.find(header_marker)
    end = html.find(footer_marker)
    if start < 0 or end <= start:
        raise ValueError("Could not locate header/footer markers")

    chunk = html[start:end]
    header_close = chunk.rfind("</header>")
    body = chunk[header_close + len("</header>") :] if header_close >= 0 else chunk

    body = re.sub(r"<footer\b[^>]*>.*", "", body, flags=re.I | re.S)
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.I | re.S)
    body = re.sub(r"<style\b[^>]*>.*?</style>", "", body, flags=re.I | re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"\sdata-elementor-[^=]+=\"[^\"]*\"", "", body)
    body = re.sub(r"\sdata-id=\"[^\"]*\"", "", body)
    body = re.sub(r"\sdata-widget_type=\"[^\"]*\"", "", body)
    body = re.sub(r"\sdata-element_type=\"[^\"]*\"", "", body)
    body = re.sub(r"\sdata-settings=\"[^\"]*\"", "", body)
    body = re.sub(r"<svg\b[^>]*>.*?</svg>", "", body, flags=re.I | re.S)
    body = re.sub(r"\[dwqa-list-questions\]", "", body)
    body = re.sub(r"\[dwqa-submit-question-form\]", "", body)
    body = re.sub(r"\[dwqa-user-profile[^\]]*\]", "", body)
    body = re.sub(r"\[zb_mpx_category_links[^\]]*\]", "", body)
    # Keep [zb_mp_*] template tokens on product template pages.
    body = re.sub(r"<div class=\"elementor-element[^\"]*elementor-widget-divider[^\"]*\"[^>]*>.*?</div>\s*</div>", "", body, flags=re.S)
    body = re.sub(r"\sclass=\"elementor[^\"]*\"", "", body)
    body = re.sub(r"\sclass=\"\"", "", body)
    body = re.sub(r"<div>\s*</div>", "", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = re.sub(r'\s*<footer class="elementor elementor-245[\s\S]*$', "", body, flags=re.I)
    body = re.sub(r'\s*<footer class="elementor-location-footer[\s\S]*$', "", body, flags=re.I)
    return body.strip()


def extract_title(html: str) -> str:
    match = re.search(r"<title>([^<]+)</title>", html, re.I)
    if not match:
        return "Untitled"
    title = unescape(match.group(1)).strip()
    title = re.sub(r"\s*-\s*erwachsenenfragen\.de\s*$", "", title, flags=re.I)
    title = re.sub(r"\s*-\s*AdultVragen\.de\s*$", "", title, flags=re.I)
    return title


def extract_description(html: str) -> str:
    match = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"',
        html,
        re.I,
    )
    return unescape(match.group(1)).strip() if match else ""


def extract_text_preview(html: str, limit: int = 200) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def local_media_path(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.netloc or "erwachsenenfragen.de" in parsed.netloc:
        path = parsed.path.lstrip("/")
        if path.startswith("wp-content/uploads/"):
            rel = path.replace("wp-content/uploads/", "")
            local = PUBLIC_MEDIA / rel
            local.parent.mkdir(parents=True, exist_ok=True)
            if not local.exists():
                try:
                    subprocess.run(
                        ["curl", "-sL", "--max-time", "60", "-o", str(local), url],
                        check=True,
                    )
                except subprocess.CalledProcessError:
                    return url
            return f"/images/media/{rel}"
    return url


def rewrite_images(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        attr = match.group(1)
        url = match.group(2)
        if '[' in url or not url.strip():
            return match.group(0)
        if url.startswith("/"):
            url = urljoin(WP_BASE, url)
        local = local_media_path(url)
        return f'{attr}="{local}"'

    html = re.sub(r'(src|href|srcset)="([^"]+)"', repl, html)
    html = re.sub(r'(src|href|srcset)=\'([^\']+)\'', repl, html)
    html = re.sub(r"https?://erwachsenenfragen\.de", "", html)
    return html


def rewrite_internal_links(html: str) -> str:
    html = re.sub(
        r'href="https?://erwachsenenfragen\.de([^"]*)"',
        r'href="\1"',
        html,
    )
    html = re.sub(r'href="([^"]+?)/"', r'href="\1"', html)
    return html


def yaml_block(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if not value:
        return '""'
    if "\n" in value or len(value) > 120:
        lines = value.split("\n")
        indented = "\n".join("  " + line for line in lines)
        return "|\n" + indented
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_mdx(
    slug: str,
    title: str,
    description: str,
    content_html: str,
    page_type: str = "page",
) -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    html_path = HTML_DIR / f"{slug}.html"
    html_path.write_text(content_html, encoding="utf-8")

    path = PAGES_DIR / f"{slug}.mdx"
    frontmatter = f"""---
title: {yaml_block(title)}
description: {yaml_block(description)}
slug: {yaml_block(slug)}
pageType: {yaml_block(page_type)}
contentHtmlFile: {yaml_block(f"{slug}.html")}
---

{{/* Crawled from live site */}}
"""
    path.write_text(frontmatter, encoding="utf-8")


def collect_urls() -> list[str]:
    urls: set[str] = set()

    nav_text = (ROOT / "src" / "data" / "navigation.ts").read_text(encoding="utf-8")
    prod_text = (ROOT / "src" / "data" / "products.ts").read_text(encoding="utf-8")
    for match in re.findall(r"href:\s*['\"]([^'\"]+)['\"]", nav_text + prod_text):
        if match.startswith("/") and match != "/blog":
            urls.add(match.rstrip("/"))

    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    for item in root.findall(".//item"):
        status = item.find("wp:status", NS)
        post_type = item.find("wp:post_type", NS)
        slug_el = item.find("wp:post_name", NS)
        if status is None or post_type is None or slug_el is None:
            continue
        if status.text != "publish":
            continue
        if post_type.text == "page" and slug_el.text not in {"home", "zb_mp_product", "blog"}:
            urls.add(f"/{slug_el.text}")

    urls.add("/")
    return sorted(urls)


def crawl_url(path: str) -> dict:
    url = urljoin(WP_BASE, path + "/")
    print(f"Crawling {url}")
    html = fetch(url)
    title = extract_title(html)
    description = extract_description(html) or extract_text_preview(extract_main_html(html))
    content = extract_main_html(html)
    content = rewrite_images(content)
    content = rewrite_internal_links(content)

    slug = path.strip("/") or "home"
    page_type = "review" if slug.startswith("beste-") else "page"
    if slug != "home":
        write_mdx(slug, title, description, content, page_type)

    return {
        "path": path,
        "slug": slug,
        "title": title,
        "description": description,
        "contentLength": len(content),
        "pageType": page_type,
        "status": "ok",
    }


def main() -> int:
    urls = collect_urls()
    results: list[dict] = []
    errors: list[dict] = []

    for path in urls:
        if path == "/":
            continue
        try:
            results.append(crawl_url(path))
            time.sleep(0.3)
        except Exception as exc:  # noqa: BLE001
            errors.append({"path": path, "error": str(exc)})
            print(f"ERROR {path}: {exc}", file=sys.stderr)

    summary = {
        "crawled": len(results),
        "errors": len(errors),
        "reviews": sum(1 for r in results if r["pageType"] == "review"),
        "pages": sum(1 for r in results if r["pageType"] == "page"),
        "results": results,
        "errorDetails": errors,
    }
    out = ROOT / "crawl-summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"crawled": summary["crawled"], "errors": summary["errors"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
