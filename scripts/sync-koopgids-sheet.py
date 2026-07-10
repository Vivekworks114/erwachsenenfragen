#!/usr/bin/env python3
"""Sync product catalog from Koopgids Excel sheet into Astro project."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
XLSX = Path('/home/devcorebit/Downloads/Koopgids magic Erwachsenenfragen.de.xlsx')
CATALOG_JSON = ROOT / 'src' / 'data' / 'catalog.json'
PAGES_DIR = ROOT / 'src' / 'content' / 'pages'
HTML_DIR = ROOT / 'src' / 'content' / 'page-html'
IMAGE_DIR = ROOT / 'public' / 'images' / 'products'

CATEGORY_SLUGS = {
    'bettwäsche und möbel': 'bettwaesche-und-moebel',
    'gesichtspflege und make-up': 'gesichtspflege-und-make-up',
    'elektronische geräte': 'elektronische-geraete',
    'luftaufbereitung': 'luftaufbereitung',
    'körperpflege': 'koerperpflege',
    'heimzubehör und sicherheit': 'heimzubehoer-und-sicherheit',
    'haarpflege': 'haarpflege',
}

CATEGORY_LABELS = {
    'bettwaesche-und-moebel': 'Bettwäsche und Möbel',
    'gesichtspflege-und-make-up': 'Gesichtspflege und Make-up',
    'elektronische-geraete': 'Elektronische Geräte',
    'luftaufbereitung': 'Luftaufbereitung',
    'koerperpflege': 'Körperpflege',
    'heimzubehoer-und-sicherheit': 'Heimzubehör und Sicherheit',
    'haarpflege': 'Haarpflege',
}


def slugify(name: str) -> str:
    s = name.strip().lower()
    for src, dst in {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'à': 'a', 'é': 'e'}.items():
        s = s.replace(src, dst)
    s = unicodedata.normalize('NFKD', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return f'beste-{s}'


def read_xlsx(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as z:
        sst = ET.fromstring(z.read('xl/sharedStrings.xml'))
        strings = [
            ''.join(t.text or '' for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'))
            for si in sst.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')
        ]
        root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))

        def col_to_num(col: str) -> int:
            n = 0
            for c in col:
                n = n * 26 + ord(c) - 64
            return n

        def cell_value(c: ET.Element) -> str:
            t = c.attrib.get('t')
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            if v is None or v.text is None:
                return ''
            return strings[int(v.text)] if t == 's' else v.text

        rows: list[dict[str, str]] = []
        for row in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            cells: dict[str, str] = {}
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = c.attrib.get('r', '')
                m = re.match(r'([A-Z]+)', ref)
                if m:
                    cells[m.group(1)] = cell_value(c)
            rows.append(cells)

    header = rows[0]
    cols = sorted(header.keys(), key=col_to_num)
    products: list[dict[str, str]] = []
    for r in rows[1:]:
        d = {header[c]: r.get(c, '') for c in cols}
        if d.get('product', '').strip():
            products.append(d)
    return products


def replace_shortcodes(text: str, ev: str, mv: str) -> str:
    text = text or ''
    text = text.replace('[zb_mp_ev]', ev).replace('[zb_mp_mv]', mv)
    return re.sub(r'\[zb_mp_[^\]]+\]', mv, text)


def download_image(url: str, slug: str, index: int, skip_existing: bool = True) -> str:
    if not url or not url.startswith('http'):
        return ''
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    product_dir = IMAGE_DIR / slug
    product_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(urlparse(url).path).suffix or '.jpg'
    if ext not in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
        ext = '.jpg'
    filename = f'{index:02d}{ext}'
    local = product_dir / filename
    public_path = f'/images/products/{slug}/{filename}'

    if skip_existing and local.exists() and local.stat().st_size > 0:
        return public_path

    try:
        subprocess.run(
            ['curl', '-sL', '--max-time', '20', '-o', str(local), url],
            check=True,
            capture_output=True,
        )
        if local.stat().st_size > 0:
            return public_path
    except (subprocess.CalledProcessError, OSError):
        pass
    return url


def build_top_items(row: dict[str, str], slug: str) -> list[dict]:
    items = []
    for i in range(1, 11):
        suffix = str(i) if i < 10 else '_10'
        name_key = f'product{suffix}' if i < 10 else 'product_10'
        desc_key = f'omschrijving{suffix}' if i < 10 else 'omschrijving_10'
        img_key = f'afbeelding{suffix}' if i < 10 else 'afbeelding_10'
        link_key = f'Link{i}' if i < 10 else 'Link_10'

        name = row.get(name_key, '').strip()
        if not name:
            continue
        img_url = row.get(img_key, '').strip()
        local_img = download_image(img_url, slug, i) if i <= 1 else img_url
        items.append(
            {
                'rank': i,
                'name': name,
                'description': row.get(desc_key, '').strip(),
                'image': local_img or img_url,
                'link': row.get(link_key, '').strip(),
            }
        )
    return items


def build_product(row: dict[str, str]) -> dict:
    name = row['product'].strip()
    slug = slugify(name)
    ev = row.get('ev', name).strip() or name
    mv = row.get('mv', name).strip() or name
    category = row.get('Category', '').strip()
    category_slug = CATEGORY_SLUGS.get(category.lower(), '')

    top_items = build_top_items(row, slug)
    modified = row.get('modified_datetime', '').strip()
    if modified:
        try:
            if re.match(r'^\d+(\.\d+)?$', modified):
                from datetime import timedelta
                serial = float(modified)
                base = datetime(1899, 12, 30)
                modified_display = (base + timedelta(days=serial)).strftime('%d %b %Y')
            else:
                dt = datetime.fromisoformat(modified.replace(' ', 'T'))
                modified_display = dt.strftime('%d %b %Y')
        except ValueError:
            modified_display = modified
    else:
        modified_display = ''

    return {
        'slug': slug,
        'name': name,
        'ev': ev,
        'mv': mv,
        'category': category,
        'categorySlug': category_slug,
        'intro': replace_shortcodes(row.get('inleiding', ''), ev, mv),
        'conclusion': replace_shortcodes(row.get('conclusie', ''), ev, mv),
        'modifiedDate': modified,
        'modifiedDisplay': modified_display,
        'href': f'/{slug}/',
        'image': top_items[0]['image'] if top_items else '',
        'topItems': top_items,
        'breadcrumb': {
            'name': row.get('breadcrumb_1_name', '').strip(),
            'url': row.get('breadcrumb_1_url', '').strip(),
        },
        'seoTitle': f'BEST {ev} im 2024 verglichen: Sehen Sie sich unsere TOP 10 an',
        'seoDescription': (
            f'Welches sind die 10 BESTEN {mv} von 2024? '
            f'AdultVragen.de teilt die TOP 10 der am besten getesteten {mv}.'
        ),
    }


def build_categories(products: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {slug: [] for slug in CATEGORY_SLUGS.values()}
    for p in products:
        if p['categorySlug']:
            grouped[p['categorySlug']].append(
                {'name': p['name'], 'slug': p['slug'], 'href': p['href'], 'image': p.get('image', '')}
            )

    categories = []
    for cat_key, cat_slug in CATEGORY_SLUGS.items():
        items = sorted(grouped.get(cat_slug, []), key=lambda x: x['name'].lower())
        categories.append(
            {
                'slug': cat_slug,
                'name': CATEGORY_LABELS[cat_slug],
                'href': f'/{cat_slug}/',
                'productCount': len(items),
                'products': items,
            }
        )
    return categories


def yaml_quote(value: str) -> str:
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def write_page_files(product: dict) -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    mdx = f"""---
title: {yaml_quote(product['seoTitle'])}
description: {yaml_quote(product['seoDescription'])}
slug: {yaml_quote(product['slug'])}
pageType: "review"
catalogSlug: {yaml_quote(product['slug'])}
---

{{/* Generated from Koopgids sheet */}}
"""
    (PAGES_DIR / f"{product['slug']}.mdx").write_text(mdx, encoding='utf-8')


def write_category_pages(categories: list[dict]) -> None:
    for cat in categories:
        intro = (
            f"In der Kategorie {cat['name'].lower()} finden Sie ausführliche Bewertungen "
            f"und Vergleiche der besten Produkte. Schauen Sie sich alle {cat['productCount']} "
            f"Kaufberatungen in dieser Kategorie an."
        )
        groups: dict[str, list] = {}
        for p in cat['products']:
            letter = p['name'][0].upper() if p['name'] else '#'
            groups.setdefault(letter, []).append(p)

        links_html = '<div class="zbmp-category-links category-links">'
        for letter in sorted(groups):
            links_html += f'<div class="category-links__group"><h5>{letter}</h5><ul>'
            for p in groups[letter]:
                links_html += f'<li><a href="{p["href"]}">{p["name"]}</a></li>'
            links_html += '</ul></div>'
        links_html += '</div>'

        html = f"""<main class="category-page">
  <header class="category-page__header">
    <h1 class="entry-title">{cat['name']}</h1>
    <p class="category-page__intro">{intro}</p>
  </header>
  <section class="category-page__grid">
    {links_html}
  </section>
</main>"""

        HTML_DIR.mkdir(parents=True, exist_ok=True)
        (HTML_DIR / f"{cat['slug']}.html").write_text(html, encoding='utf-8')

        mdx = f"""---
title: {yaml_quote(cat['name'])}
description: {yaml_quote(intro)}
slug: {yaml_quote(cat['slug'])}
pageType: "category"
catalogSlug: {yaml_quote(cat['slug'])}
---

{{/* Generated from Koopgids sheet */}}
"""
        (PAGES_DIR / f"{cat['slug']}.mdx").write_text(mdx, encoding='utf-8')


def main() -> None:
    if not XLSX.exists():
        raise SystemExit(f'Excel file not found: {XLSX}')

    rows = read_xlsx(XLSX)
    products = [build_product(r) for r in rows]
    categories = build_categories(products)

    catalog = {
        'version': 1,
        'syncedAt': datetime.utcnow().isoformat() + 'Z',
        'source': str(XLSX.name),
        'productCount': len(products),
        'categoryCount': len(categories),
        'products': products,
        'categories': categories,
    }

    CATALOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_JSON.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')

    for product in products:
        write_page_files(product)
    write_category_pages(categories)

    summary = {
        'products': len(products),
        'categories': len(categories),
        'slugs': [p['slug'] for p in products],
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
