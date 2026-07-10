import catalogData from '../data/catalog.json';

export interface CatalogTopItem {
  rank: number;
  name: string;
  description: string;
  image: string;
  link: string;
}

export interface CatalogProduct {
  slug: string;
  name: string;
  ev: string;
  mv: string;
  category: string;
  categorySlug: string;
  intro: string;
  conclusion: string;
  modifiedDate: string;
  modifiedDisplay: string;
  href: string;
  image: string;
  topItems: CatalogTopItem[];
  breadcrumb: { name: string; url: string };
  seoTitle: string;
  seoDescription: string;
}

export interface CatalogCategoryProduct {
  name: string;
  slug: string;
  href: string;
  image: string;
}

export interface CatalogCategory {
  slug: string;
  name: string;
  href: string;
  productCount: number;
  products: CatalogCategoryProduct[];
}

export interface Catalog {
  version: number;
  syncedAt: string;
  source: string;
  productCount: number;
  categoryCount: number;
  products: CatalogProduct[];
  categories: CatalogCategory[];
}

export const catalog = catalogData as Catalog;

export function getProductBySlug(slug: string): CatalogProduct | undefined {
  return catalog.products.find((p) => p.slug === slug);
}

export function getCategoryBySlug(slug: string): CatalogCategory | undefined {
  return catalog.categories.find((c) => c.slug === slug);
}

export function getProductsByCategory(categorySlug: string): CatalogProduct[] {
  return catalog.products.filter((p) => p.categorySlug === categorySlug);
}

export function getRelatedProducts(product: CatalogProduct, limit = 5): CatalogProduct[] {
  return catalog.products
    .filter((p) => p.categorySlug === product.categorySlug && p.slug !== product.slug)
    .slice(0, limit);
}

export function getFeaturedReviews(limit = 14): CatalogProduct[] {
  const featuredSlugs = new Set([
    'beste-gesichtsepilierer',
    'beste-gesichtsreiniger',
    'beste-lippenbalsam',
    'beste-lippenstift',
    'beste-lockenstab',
    'beste-make-up-schwamm',
    'beste-rasierapparat',
    'beste-rasierpinsel',
    'beste-rasierspiegel',
    'beste-selbstbraeuner',
    'beste-volumenpuder',
    'beste-4k-beamer',
    'beste-fotodrucker-fuer-10-x-15-cm',
    'beste-satin-kopfkissenbezug',
  ]);
  return catalog.products.filter((p) => featuredSlugs.has(p.slug)).slice(0, limit);
}

export function getPopularProducts(limit = 14): CatalogProduct[] {
  const popularSlugs = new Set([
    'beste-aroma-diffusor',
    'beste-entgiftungstee',
    'beste-luftbefeuchter',
    'beste-luftentfeuchter',
    'beste-luftreiniger',
    'beste-weihrauch',
    'beste-abdeckstift',
    'beste-badeschaum',
    'beste-bartbalsam',
    'beste-damenrasierer',
    'beste-duschschaum',
    'beste-entwickler',
    'beste-epilierer',
    'beste-foundation-pinsel',
  ]);
  return catalog.products.filter((p) => popularSlugs.has(p.slug)).slice(0, limit);
}

export function toProductCard(product: CatalogProduct) {
  return {
    title: product.name,
    href: product.href,
    image: product.image,
    category: product.category,
    categorySlug: product.categorySlug,
  };
}

export type ProductCardData = ReturnType<typeof toProductCard>;
