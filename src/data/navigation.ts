import { catalog } from '../lib/catalog';

export interface NavItem {
  label: string;
  href: string;
  children?: NavItem[];
}

function buildCategoryChildren(categorySlug: string): NavItem[] {
  const category = catalog.categories.find((c) => c.slug === categorySlug);
  if (!category) return [];
  return category.products.map((p) => ({
    label: p.name,
    href: p.href.endsWith('/') ? p.href : `${p.href}/`,
  }));
}

export const mainNavigation: NavItem[] = [
  { label: 'Fragen ansehen', href: '/fragen-anzeigen/' },
  { label: 'Fragen stellen', href: '/fragen-stellen/' },
  { label: 'Über uns', href: '/uber-uns/' },
  { label: 'Kontakt', href: '/kontakt/' },
  { label: 'Anmeldung', href: '/anmeldung/' },
];

/** Matches live header nav: https://erwachsenenfragen.de/ */
const bettwaescheCategory = catalog.categories.find((c) => c.slug === 'bettwaesche-und-moebel');
const makeupCategory = catalog.categories.find((c) => c.slug === 'gesichtspflege-und-make-up');

function productLink(slug: string, label?: string): NavItem {
  const product = catalog.products.find((p) => p.slug === slug);
  if (!product) {
    return { label: label ?? slug, href: `/${slug}/` };
  }
  return {
    label: label ?? product.name,
    href: product.href,
  };
}

export const headerNavigation: NavItem[] = [
  { label: 'Fragen ansehen', href: '/fragen-anzeigen/' },
  { label: 'Fragen stellen', href: '/fragen-stellen/' },
  {
    label: 'Bettwäsche und möbel',
    href: bettwaescheCategory?.href ?? '/bettwaesche-und-moebel/',
    children: [
      productLink('beste-pouf', 'Pouf'),
      productLink('beste-sitzsack', 'Sitzsack'),
      productLink('beste-betttisch', 'Betttisch'),
      productLink('beste-beistelltisch', 'Beistelltisch'),
      productLink('beste-haengesessel', 'Hängesessel'),
      productLink('beste-matratzenkeil', 'Matratzenkeil'),
      productLink('beste-kleiderschrank', 'Kleiderschrank'),
      productLink('beste-matratzenbezug', 'Matratzenbezug'),
      productLink('beste-matratzenschoner', 'Matratzenschoner'),
      productLink('beste-satin-kopfkissenbezug', 'Satin-Kopfkissenbezug'),
    ],
  },
  {
    label: 'Gesichtspflege und Make-up',
    href: makeupCategory?.href ?? '/gesichtspflege-und-make-up/',
    children: [
      productLink('beste-epilierer', 'Epilierer'),
      productLink('beste-entwickler', 'Entwickler'),
      productLink('beste-lippenstift', 'Lippenstift'),
      productLink('beste-abdeckstift', 'Abdeckstift'),
      productLink('beste-rasierapparat', 'Rasierapparat'),
      productLink('beste-lippenbalsam', 'Lippenbalsam'),
      productLink('beste-gesichtsreiniger', 'Gesichtsreiniger'),
      productLink('beste-gesichtsepilierer', 'Gesichtsepilierer'),
      productLink('beste-foundation-pinsel', 'Foundation-Pinsel'),
      productLink('beste-make-up-schwamm', 'Make-up-Schwamm'),
    ],
  },
  { label: 'Über uns', href: '/uber-uns/' },
  { label: 'Kontakt', href: '/kontakt/' },
  { label: 'Anmeldung', href: '/anmeldung/' },
];

export const categoryNavigation: NavItem[] = catalog.categories.map((category) => ({
  label: category.name,
  href: category.href.endsWith('/') ? category.href : `${category.href}/`,
  children: category.products.map((product) => ({
    label: product.name,
    href: product.href.endsWith('/') ? product.href : `${product.href}/`,
  })),
}));

export const footerInfoLinks = [
  { label: 'Fragen ansehen', href: '/fragen-anzeigen/' },
  { label: 'Über uns', href: '/uber-uns/' },
  { label: 'Kontakt', href: '/kontakt/' },
  { label: 'Blog', href: '/blog/' },
];

/** Matches live footer: https://erwachsenenfragen.de/ */
export const footerElectronicsLinks = [
  { label: '4k Beamer', href: '/beste-4k-beamer/' },
  { label: 'Smart Tv 32 Zoll', href: '/beste-smart-tv-32-zoll/' },
  { label: 'Smart Tv 40 Zoll', href: '/beste-smart-tv-40-zoll/' },
  { label: 'Smart Tv 50 Zoll', href: '/beste-smart-tv-50-zoll/' },
  { label: 'Smart Tv 55 Zoll', href: '/beste-smart-tv-55-zoll/' },
  { label: 'Smart Tv 65 Zoll', href: '/beste-smart-tv-65-zoll/' },
];

export const footerBodyCareLinks = [
  { label: 'Badeschaum', href: '/beste-badeschaum/' },
  { label: 'Duschschaum', href: '/beste-duschschaum/' },
  { label: 'Selbstbräuner', href: '/beste-selbstbraeuner/' },
  { label: 'Entgiftungstee', href: '/beste-entgiftungstee/' },
  { label: 'Damenrasierer', href: '/beste-damenrasierer/' },
  { label: 'Whirlpool Aufblasbar', href: '/beste-whirlpool-aufblasbar/' },
];

export const footerAirLinks = [
  { label: 'Ventilator,', href: '/beste-ventilator/' },
  { label: 'wierook,', href: '/beste-weihrauch/' },
  { label: 'luchtreiniger,', href: '/beste-luftreiniger/' },
  { label: 'luchtbevochtiger', href: '/beste-luftbefeuchter/' },
  { label: 'luchtontvochtiger,', href: '/beste-luftentfeuchter/' },
  { label: 'aromadiffuser', href: '/beste-aroma-diffusor/' },
];
