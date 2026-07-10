# erwachsenenfragen.de – Astro

Modern Astro.js site for [erwachsenenfragen.de](https://erwachsenenfragen.de/), preserving the original brand identity, URLs, and WordPress content hierarchy.

## Quick Start

```bash
cd site
npm install
npm run dev
```

Open [http://localhost:4321](http://localhost:4321)

## Build

```bash
npm run build
npm run preview
```

## Content Migration

WordPress content is migrated from `erwachsenenfragende.WordPress.2026-07-10.xml` into Astro content collections:

| Collection | Path | Count |
|------------|------|-------|
| Blog posts | `src/content/blog/*.mdx` | 7 |
| Pages | `src/content/pages/*.mdx` | 17 |
| Authors | `src/content/authors/` | 3 |
| Categories | `src/content/categories/` | 3 |
| Media | `public/images/media/` | 110 |

Re-run migration:

```bash
python3 scripts/migrate-wordpress.py
```

## Project Structure

```
site/
├── astropayload.config.json
├── wrangler.jsonc
├── public/images/          # Brand assets + migrated WordPress media
├── scripts/
│   └── migrate-wordpress.py
├── src/
│   ├── components/
│   ├── content/
│   │   ├── blog/           # One .mdx per post slug
│   │   ├── pages/
│   │   ├── authors/
│   │   └── categories/
│   ├── content.config.ts
│   ├── data/
│   ├── layouts/
│   ├── pages/
│   └── styles/
```

## URL Structure

WordPress permalinks are preserved:

- Blog listing: `/blog/`
- Blog posts: `/{post-slug}/` (root-level, not `/blog/{slug}/`)
- Pages: `/{page-slug}/`
- Static routes: `/kontakt/`, `/uber-uns/`, `/fragen-stellen/`, etc.

## Configuration

- **Content collections**: `src/content.config.ts` (glob loaders, no remote CMS)
- **Payload CMS**: `astropayload.config.json`
- **Cloudflare Workers**: `wrangler.jsonc`

## Design System

| Token | Value |
|-------|-------|
| Primary | `#CB0000` |
| Background | `#0B0D15` |
| Surface | `#0C0F17` |
| Border | `#464B58` |
| Heading font | Century Gothic |
| Accent font | Montserrat |
