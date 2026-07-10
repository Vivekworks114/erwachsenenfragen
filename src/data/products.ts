export interface Product {
  title: string;
  href: string;
}

export const reviews: Product[] = [
  { title: 'Gesichtsepilierer', href: '/beste-gesichtsepilierer' },
  { title: 'Gesichtsreiniger', href: '/beste-gesichtsreiniger' },
  { title: 'Lippenbalsam', href: '/beste-lippenbalsam' },
  { title: 'Lippenstift', href: '/beste-lippenstift' },
  { title: 'Lockenstab', href: '/beste-lockenstab' },
  { title: 'Make up Schwamm', href: '/beste-make-up-schwamm' },
  { title: 'Rasierapparat', href: '/beste-rasierapparat' },
  { title: 'Rasierpinsel', href: '/beste-rasierpinsel' },
  { title: 'Rasierspiegel', href: '/beste-rasierspiegel' },
  { title: 'Selbstbraeuner', href: '/beste-selbstbraeuner' },
  { title: 'Volumenpuder', href: '/beste-volumenpuder' },
  { title: '4k Beamer', href: '/beste-4k-beamer' },
  { title: 'Fotodrucker für 10 X 15 Cm', href: '/beste-fotodrucker-fuer-10-x-15-cm' },
  { title: 'Satin-Kopfkissenbezug', href: '/beste-satin-kopfkissenbezug' },
];

export const popularProducts: Product[] = [
  { title: 'Aroma-Diffusor', href: '/beste-aroma-diffusor' },
  { title: 'Entgiftungstee', href: '/beste-entgiftungstee' },
  { title: 'Luftbefeuchter', href: '/beste-luftbefeuchter' },
  { title: 'Luftentfeuchter', href: '/beste-luftentfeuchter' },
  { title: 'Luftreiniger', href: '/beste-luftreiniger' },
  { title: 'Weihrauch', href: '/beste-weihrauch' },
  { title: 'Abdeckstift', href: '/beste-abdeckstift' },
  { title: 'Badeschaum', href: '/beste-badeschaum' },
  { title: 'Bartbalsam', href: '/beste-bartbalsam' },
  { title: 'Damenrasierer', href: '/beste-damenrasierer' },
  { title: 'Duschschaum', href: '/beste-duschschaum' },
  { title: 'Entwickler', href: '/beste-entwickler' },
  { title: 'Epilierer', href: '/beste-epilierer' },
  { title: 'Foundation-Pinsel', href: '/beste-foundation-pinsel' },
];

export interface Category {
  title: string;
  href: string;
  image: string;
  icon: string;
}

export const categories: Category[] = [
  {
    title: 'Enthaarungscreme',
    href: '#',
    image: '/images/categories/frame-246.png',
    icon: 'hair-removal',
  },
  {
    title: 'Sexspielzeug',
    href: '#',
    image: '/images/categories/frame-245.png',
    icon: 'toys',
  },
  {
    title: 'Cosplay',
    href: '#',
    image: '/images/categories/frame-243.png',
    icon: 'cosplay',
  },
  {
    title: 'LGBTQ+',
    href: '#',
    image: '/images/categories/frame-244.png',
    icon: 'lgbtq',
  },
  {
    title: 'Partnersuche',
    href: '#',
    image: '/images/categories/frame-247.png',
    icon: 'dating',
  },
  {
    title: 'Mehr...',
    href: '#',
    image: '/images/categories/frame-248.png',
    icon: 'more',
  },
];
