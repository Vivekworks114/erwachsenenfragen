import {
  catalog,
  getFeaturedReviews,
  getPopularProducts,
  toProductCard,
  type ProductCardData,
} from '../lib/catalog';

export type Product = ProductCardData;

export const reviews: Product[] = getFeaturedReviews().map(toProductCard);
export const popularProducts: Product[] = getPopularProducts().map(toProductCard);

export interface Category {
  title: string;
  href: string;
  image: string;
  icon: string;
}

export const categories: Category[] = [
  {
    title: 'Enthaarungscreme',
    href: '/gesichtspflege-und-make-up/',
    image: '/images/categories/frame-246.png',
    icon: 'hair-removal',
  },
  {
    title: 'Sexspielzeug',
    href: '/bettwaesche-und-moebel/',
    image: '/images/categories/frame-245.png',
    icon: 'toys',
  },
  {
    title: 'Cosplay',
    href: '/bettwaesche-und-moebel/',
    image: '/images/categories/frame-243.png',
    icon: 'cosplay',
  },
  {
    title: 'LGBTQ+',
    href: '/blog/',
    image: '/images/categories/frame-244.png',
    icon: 'lgbtq',
  },
  {
    title: 'Partnersuche',
    href: '/fragen-anzeigen/',
    image: '/images/categories/frame-247.png',
    icon: 'dating',
  },
  {
    title: 'Mehr...',
    href: '/sitemap/',
    image: '/images/categories/frame-248.png',
    icon: 'more',
  },
];

export { catalog };
