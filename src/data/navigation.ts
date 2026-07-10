export interface NavItem {
  label: string;
  href: string;
  children?: NavItem[];
}

export const mainNavigation: NavItem[] = [
  { label: 'Fragen ansehen', href: '/fragen-anzeigen' },
  { label: 'Fragen stellen', href: '/fragen-stellen' },
  {
    label: 'Bettwäsche und möbel',
    href: '/bettwaesche-und-moebel',
    children: [
      { label: 'Pouf', href: '/beste-pouf' },
      { label: 'Sitzsack', href: '/beste-sitzsack' },
      { label: 'Betttisch', href: '/beste-betttisch' },
      { label: 'Beistelltisch', href: '/beste-beistelltisch' },
      { label: 'Hängesessel', href: '/beste-haengesessel' },
      { label: 'Matratzenkeil', href: '/beste-matratzenkeil' },
      { label: 'Kleiderschrank', href: '/beste-kleiderschrank' },
      { label: 'Matratzenbezug', href: '/beste-matratzenbezug' },
      { label: 'Matratzenschoner', href: '/beste-matratzenschoner' },
      { label: 'Satin-Kopfkissenbezug', href: '/beste-satin-kopfkissenbezug' },
    ],
  },
  {
    label: 'Gesichtspflege und Make-up',
    href: '/gesichtspflege-und-make-up',
    children: [
      { label: 'Epilierer', href: '/beste-epilierer' },
      { label: 'Entwickler', href: '/beste-entwickler' },
      { label: 'Lippenstift', href: '/beste-lippenstift' },
      { label: 'Abdeckstift', href: '/beste-abdeckstift' },
      { label: 'Rasierapparat', href: '/beste-rasierapparat' },
      { label: 'Lippenbalsam', href: '/beste-lippenbalsam' },
      { label: 'Gesichtsreiniger', href: '/beste-gesichtsreiniger' },
      { label: 'Gesichtsepilierer', href: '/beste-gesichtsepilierer' },
      { label: 'Foundation-Pinsel', href: '/beste-foundation-pinsel' },
      { label: 'Make-up-Schwamm', href: '/beste-make-up-schwamm' },
    ],
  },
  { label: 'Über uns', href: '/uber-uns' },
  { label: 'Kontakt', href: '/kontakt' },
  { label: 'Anmeldung', href: '/anmeldung' },
];

export const footerInfoLinks = [
  { label: 'Vragen weergeven', href: '/fragen-anzeigen' },
  { label: 'Over ons', href: '/uber-uns' },
  { label: 'contact', href: '/kontakt' },
  { label: 'Blog', href: '/blog' },
];

export const footerElectronicsLinks = [
  { label: '4k Beamer', href: '/beste-4k-beamer' },
  { label: 'Smart Tv 32 Zoll', href: '/beste-smart-tv-32-zoll' },
  { label: 'Smart Tv 40 Zoll', href: '/beste-smart-tv-40-zoll' },
  { label: 'Smart Tv 50 Zoll', href: '/beste-smart-tv-50-zoll' },
  { label: 'Smart Tv 55 Zoll', href: '/beste-smart-tv-55-zoll' },
  { label: 'Smart Tv 65 Zoll', href: '/beste-smart-tv-65-zoll' },
];

export const footerBodyCareLinks = [
  { label: 'Badeschaum', href: '/beste-badeschaum' },
  { label: 'Duschschaum', href: '/beste-duschschaum' },
  { label: 'Selbstbräuner', href: '/beste-selbstbraeuner' },
  { label: 'Entgiftungstee', href: '/beste-entgiftungstee' },
  { label: 'Damenrasierer', href: '/beste-damenrasierer' },
  { label: 'Whirlpool Aufblasbar', href: '/beste-whirlpool-aufblasbar' },
];

export const footerAirLinks = [
  { label: 'Ventilator', href: '/beste-ventilator' },
  { label: 'Weihrauch', href: '/beste-weihrauch' },
  { label: 'Luftreiniger', href: '/beste-luftreiniger' },
  { label: 'Luftbefeuchter', href: '/beste-luftbefeuchter' },
  { label: 'Luftentfeuchter', href: '/beste-luftentfeuchter' },
  { label: 'Aroma-Diffusor', href: '/beste-aroma-diffusor' },
];
