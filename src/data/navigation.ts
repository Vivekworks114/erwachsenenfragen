import { catalog } from '../lib/catalog';

export interface NavItem {
  label: string;
  href: string;
  children?: NavItem[];
}

const CATEGORY_NAV: Record<string, string> = {
  'bettwaesche-und-moebel': 'Bettwäsche und möbel',
  'gesichtspflege-und-make-up': 'Gesichtspflege und Make-up',
  'elektronische-geraete': 'Elektronische Geräte',
  'luftaufbereitung': 'Luftaufbereitung',
  'koerperpflege': 'Körperpflege',
  'heimzubehoer-und-sicherheit': 'Heimzubehör und Sicherheit',
  'haarpflege': 'Haarpflege',
};

function buildCategoryChildren(categorySlug: string): NavItem[] {
  const category = catalog.categories.find((c) => c.slug === categorySlug);
  if (!category) return [];
  return category.products.map((p) => ({
    label: p.name,
    href: p.href.replace(/\/$/, ''),
  }));
}

export const mainNavigation: NavItem[] = [
  { label: 'Fragen ansehen', href: '/fragen-anzeigen' },
  { label: 'Fragen stellen', href: '/fragen-stellen' },
  {
    label: CATEGORY_NAV['bettwaesche-und-moebel'],
    href: '/bettwaesche-und-moebel',
    children: buildCategoryChildren('bettwaesche-und-moebel'),
  },
  {
    label: CATEGORY_NAV['gesichtspflege-und-make-up'],
    href: '/gesichtspflege-und-make-up',
    children: buildCategoryChildren('gesichtspflege-und-make-up'),
  },
  {
    label: CATEGORY_NAV['elektronische-geraete'],
    href: '/elektronische-geraete',
    children: buildCategoryChildren('elektronische-geraete'),
  },
  {
    label: CATEGORY_NAV['koerperpflege'],
    href: '/koerperpflege',
    children: buildCategoryChildren('koerperpflege'),
  },
  {
    label: CATEGORY_NAV['luftaufbereitung'],
    href: '/luftaufbereitung',
    children: buildCategoryChildren('luftaufbereitung'),
  },
  { label: 'Über uns', href: '/uber-uns' },
  { label: 'Kontakt', href: '/kontakt' },
  { label: 'Anmeldung', href: '/anmeldung' },
];

export const footerInfoLinks = [
  { label: 'Fragen ansehen', href: '/fragen-anzeigen' },
  { label: 'Über uns', href: '/uber-uns' },
  { label: 'Kontakt', href: '/kontakt' },
  { label: 'Blog', href: '/blog' },
];

export const footerElectronicsLinks = buildCategoryChildren('elektronische-geraete').map((item) => ({
  label: item.label,
  href: item.href,
}));

export const footerBodyCareLinks = buildCategoryChildren('koerperpflege').map((item) => ({
  label: item.label,
  href: item.href,
}));

export const footerAirLinks = buildCategoryChildren('luftaufbereitung').map((item) => ({
  label: item.label,
  href: item.href,
}));
