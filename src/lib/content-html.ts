import { readFileSync } from 'node:fs';
import path from 'node:path';

type ContentEntry = {
  data: {
    contentHtml?: string;
    contentHtmlFile?: string;
  };
};

export function getContentHtml(entry: ContentEntry): string {
  if (entry.data.contentHtml) {
    return entry.data.contentHtml;
  }

  if (entry.data.contentHtmlFile) {
    const filePath = path.join(
      process.cwd(),
      'src/content/page-html',
      entry.data.contentHtmlFile,
    );
    return readFileSync(filePath, 'utf-8');
  }

  return '';
}

export function hasContentTitle(entry: ContentEntry): boolean {
  const html = getContentHtml(entry);
  return /<h1\b/i.test(html);
}
