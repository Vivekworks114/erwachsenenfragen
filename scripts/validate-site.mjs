#!/usr/bin/env node
/**
 * Validate migrated site routes against live erwachsenenfragen.de
 * Usage: node scripts/validate-site.mjs [--base http://localhost:4321]
 */

import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const LIVE_BASE = 'https://erwachsenenfragen.de';
const LOCAL_BASE = process.argv.includes('--base')
  ? process.argv[process.argv.indexOf('--base') + 1]
  : 'http://localhost:4321';

function collectLocalRoutes() {
  const routes = new Set(['/', '/blog/']);

  const blogDir = path.join(ROOT, 'src/content/blog');
  for (const file of readdirSync(blogDir)) {
    if (file.endsWith('.mdx') || file.endsWith('.md')) {
      routes.add(`/${file.replace(/\.mdx?$/, '')}/`);
    }
  }

  const pagesDir = path.join(ROOT, 'src/content/pages');
  const staticSlugs = new Set([
    'fragen-anzeigen',
    'fragen-stellen',
    'kontakt',
    'uber-uns',
    'anmeldung',
    'impressum',
    'sitemap',
    'blog',
  ]);

  for (const file of readdirSync(pagesDir)) {
    if (!file.endsWith('.mdx') && !file.endsWith('.md')) continue;
    const slug = file.replace(/\.mdx?$/, '');
    if (!staticSlugs.has(slug)) {
      routes.add(`/${slug}/`);
    } else {
      routes.add(`/${slug}/`);
    }
  }

  return [...routes].sort();
}

function textContent(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

async function fetchText(url) {
  const response = await fetch(url, {
    headers: { 'User-Agent': 'AstroMigrationValidator/1.0' },
    redirect: 'follow',
  });
  const html = await response.text();
  return { status: response.status, html, text: textContent(html) };
}

async function validateRoute(route) {
  const normalizedRoute = route === '/' ? '/' : route.endsWith('/') ? route : `${route}/`;
  const localUrl = `${LOCAL_BASE}${normalizedRoute}`;
  const liveUrl = `${LIVE_BASE}${normalizedRoute}`;

  const result = {
    route,
    localStatus: 0,
    liveStatus: 0,
    localTitle: '',
    liveTitle: '',
    localTextLength: 0,
    liveTextLength: 0,
    contentRatio: 0,
    brokenImages: 0,
    issues: [],
  };

  try {
    const local = await fetchText(localUrl);
    result.localStatus = local.status;
    result.localTextLength = local.text.length;
    const titleMatch = local.html.match(/<title>([^<]*)<\/title>/i);
    result.localTitle = titleMatch?.[1]?.trim() || '';

    const images = [...local.html.matchAll(/<img[^>]+src="([^"]+)"/gi)].map((m) => m[1]);
    const checkImages = process.argv.includes('--check-images');
    if (checkImages) {
      for (const src of images.slice(0, 10)) {
        if (src.startsWith('data:')) continue;
        const imageUrl = src.startsWith('http') ? src : `${LOCAL_BASE}${src}`;
        try {
          const imgRes = await fetch(imageUrl, { method: 'HEAD' });
          if (!imgRes.ok) result.brokenImages += 1;
        } catch {
          result.brokenImages += 1;
        }
      }
    }
  } catch (error) {
    result.issues.push(`Local fetch failed: ${error.message}`);
  }

  try {
    const live = await fetchText(liveUrl);
    result.liveStatus = live.status;
    result.liveTextLength = live.text.length;
    const titleMatch = live.html.match(/<title>([^<]*)<\/title>/i);
    result.liveTitle = titleMatch?.[1]?.trim() || '';
    if (result.liveTextLength > 0) {
      result.contentRatio = Number((result.localTextLength / result.liveTextLength).toFixed(2));
    }
  } catch (error) {
    result.issues.push(`Live fetch failed: ${error.message}`);
  }

  if (result.localStatus !== 200) result.issues.push(`Local status ${result.localStatus}`);
  if (result.liveStatus !== 200) result.issues.push(`Live status ${result.liveStatus}`);
  if (result.localTextLength < 80) result.issues.push('Local content too short');
  if (result.brokenImages > 0) result.issues.push(`${result.brokenImages} broken images`);
  if (result.contentRatio > 0 && result.contentRatio < 0.35) {
    result.issues.push(`Content ratio low (${result.contentRatio})`);
  }

  result.ok = result.issues.length === 0;
  return result;
}

async function main() {
  const routes = collectLocalRoutes();
  console.log(`Validating ${routes.length} routes against ${LIVE_BASE}`);
  console.log(`Local base: ${LOCAL_BASE}`);

  const results = [];
  for (const route of routes) {
    const result = await validateRoute(route);
    results.push(result);
    const status = result.ok ? 'OK' : 'FAIL';
    console.log(
      `${status} ${route} local=${result.localTextLength} live=${result.liveTextLength} ratio=${result.contentRatio}`,
    );
    if (!result.ok) {
      for (const issue of result.issues) console.log(`  - ${issue}`);
    }
  }

  const summary = {
    total: results.length,
    passed: results.filter((r) => r.ok).length,
    failed: results.filter((r) => !r.ok).length,
    results,
  };

  const out = path.join(ROOT, 'validation-summary.json');
  writeFileSync(out, JSON.stringify(summary, null, 2));
  console.log(`\nValidation summary: ${summary.passed}/${summary.total} passed`);
  console.log(`Written to ${out}`);

  if (summary.failed > 0) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
