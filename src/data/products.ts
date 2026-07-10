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
    icon: '/images/media/2022/05/icon-park-outline_swimsuit1.svg',
  },
  {
    title: 'Sexspielzeug',
    href: '/bettwaesche-und-moebel/',
    image: '/images/categories/frame-245.png',
    icon: '/images/media/2022/05/icon-park-outline_eggplant.svg',
  },
  {
    title: 'Cosplay',
    href: '/bettwaesche-und-moebel/',
    image: '/images/categories/frame-243.png',
    icon: '/images/media/2022/05/mask-svgrepo-com-1.svg',
  },
  {
    title: 'LGBTQ+',
    href: '/blog/',
    image: '/images/categories/frame-244.png',
    icon: '/images/media/2022/05/icon-park-outline_oval-love.svg',
  },
  {
    title: 'Partnersuche',
    href: '/fragen-anzeigen/',
    image: '/images/categories/frame-247.png',
    icon: '/images/media/2022/05/icon-park-outline_heart-ballon.svg',
  },
  {
    title: 'Mehr...',
    href: '/sitemap/',
    image: '/images/categories/frame-248.png',
    icon: '/images/media/2022/05/icon-park-outline_application-menu.svg',
  },
];

export { catalog };
