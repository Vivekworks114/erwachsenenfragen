import type { CollectionEntry } from 'astro:content';

const GERMAN_MONTHS = [
  'Januar',
  'Februar',
  'März',
  'April',
  'Mai',
  'Juni',
  'Juli',
  'August',
  'September',
  'Oktober',
  'November',
  'Dezember',
] as const;

/** Listing excerpts aligned with the live WordPress blog archive. */
const LISTING_EXCERPTS: Record<string, string> = {
  'geheimnisse-fuer-ein-umweltfreundlicheres-unternehmen':
    'Eine grüne Strategie zu übernehmen bedeutet, Nachhaltigkeit in die grundlegenden Werte des Unternehmens zu integrieren. Der ökologische Wandel ist nicht nur eine Gelegenheit, die Umweltbelastung',
  'het-bedrijfsregister-een-essentieel-instrument-voor-transparantie-en-toegankelijkheid':
    'Het bedrijfsregister: Een essentieel instrument voor transparantie en toegankelijkheid Een bedrijfsregister is een officiële database waarin gegevens van bedrijven en organisaties worden vastgelegd. Dit register',
  'de-verschillende-formaten-die-externe-dvd-branders-kunnen-branden':
    'De behoefte aan fysieke media blijft bestaan, vooral voor het bewaren en delen van gegevens. Externe dvd-branders spelen een cruciale rol in dit proces door',
  'echtzeit-notfallmeldungen-in-deventer':
    'Echtzeit-Notfallmeldungen in Deventer: Ein Einblick in das 112-Meldesystem Die Stadt Deventer ist wie jede andere Stadt auf ein zuverlässiges Notfallmeldesystem angewiesen, um die Sicherheit ihrer',
  'de-werking-van-snelladers-en-hun-technologieen':
    'Het vermogen om elektronische apparaten snel op te laden is een waardevolle eigenschap. Snelladers hebben de manier waarop we onze apparaten opladen revolutionair veranderd, waardoor',
  'linkedin-kontakte-guenstig-kaufen':
    'LinkedIn spielt eine entscheidende Rolle beim Aufbau beruflicher Netzwerke und bei der Gewinnung wertvoller Kontakte. Immer mehr Menschen erwägen den Kauf günstiger LinkedIn-Kontakte als Strategie,',
  'youtube-likes-online-kaufen':
    'YouTube-Likes online kaufend Im digitalen Zeitalter ist eine starke Online-Präsenz entscheidend für den Erfolg, insbesondere auf Plattformen wie YouTube. Hier dreht sich alles um Sichtbarkeit und',
};

const LISTING_IMAGES: Record<
  string,
  { src: string; width: number; height: number }
> = {
  'geheimnisse-fuer-ein-umweltfreundlicheres-unternehmen': {
    src: '/images/blog/pexels-pixabay-265087-4-300x200.jpg',
    width: 300,
    height: 200,
  },
  'de-verschillende-formaten-die-externe-dvd-branders-kunnen-branden': {
    src: '/images/blog/image-300x225.png',
    width: 300,
    height: 225,
  },
  'echtzeit-notfallmeldungen-in-deventer': {
    src: '/images/blog/pexels-pixabay-263402-300x199.jpg',
    width: 300,
    height: 199,
  },
  'de-werking-van-snelladers-en-hun-technologieen': {
    src: '/images/blog/image-300x211.png',
    width: 300,
    height: 211,
  },
  'linkedin-kontakte-guenstig-kaufen': {
    src: '/images/blog/image-300x225.png',
    width: 300,
    height: 225,
  },
  'youtube-likes-online-kaufen': {
    src: '/images/blog/youtube4-300x169.jpg',
    width: 300,
    height: 169,
  },
};

export interface ListingImage {
  src: string;
  width: number;
  height: number;
  alt: string;
}

export function formatBlogDate(date: Date): string {
  return `${GERMAN_MONTHS[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
}

function stripHtml(html: string): string {
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function isBrokenDescription(description: string): boolean {
  return description.includes('elementor') || description.includes('/*!');
}

function excerptFromContentHtml(contentHtml?: string): string | undefined {
  if (!contentHtml) return undefined;

  const paragraph = contentHtml.match(/<p[^>]*>([\s\S]*?)<\/p>/i);
  if (!paragraph) return undefined;

  const text = stripHtml(paragraph[1]);
  return text.length > 0 ? text : undefined;
}

function truncateExcerpt(text: string, maxLength = 200): string {
  const cleaned = text.replace(/…/g, '').replace(/\.\.\.$/g, '').trim();
  if (cleaned.length <= maxLength) return cleaned;

  const slice = cleaned.slice(0, maxLength);
  const lastSpace = slice.lastIndexOf(' ');
  return lastSpace > 0 ? slice.slice(0, lastSpace) : slice;
}

export function getListingExcerpt(entry: CollectionEntry<'blog'>): string {
  if (LISTING_EXCERPTS[entry.id]) {
    return LISTING_EXCERPTS[entry.id];
  }

  const { description, contentHtml } = entry.data;

  if (description && !isBrokenDescription(description)) {
    return truncateExcerpt(description);
  }

  const fromContent = excerptFromContentHtml(contentHtml);
  if (fromContent) {
    return truncateExcerpt(fromContent);
  }

  return entry.data.title;
}

export function getListingImage(entry: CollectionEntry<'blog'>): ListingImage | null {
  const mapped = LISTING_IMAGES[entry.id];
  if (!mapped) return null;

  return {
    ...mapped,
    alt: entry.data.imageAlt || entry.data.title,
  };
}
