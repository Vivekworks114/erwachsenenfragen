import type { CollectionEntry } from 'astro:content';

export const blogCategoryArchives = {
  artikel: {
    label: 'Artikel',
    title: 'Artikel Archives - erwachsenenfragen.de',
    description: 'Artikel category archive',
  },
  business: {
    label: 'Business',
    title: 'Business Archives - erwachsenenfragen.de',
    description: 'Business category archive',
  },
  uncategorized: {
    label: 'Uncategorized',
    title: 'Uncategorized Archives - erwachsenenfragen.de',
    description: 'Uncategorized category archive',
  },
} as const;

export type BlogCategorySlug = keyof typeof blogCategoryArchives;

export function isBlogCategorySlug(value: string): value is BlogCategorySlug {
  return value in blogCategoryArchives;
}

export function getPostsForCategory(
  posts: CollectionEntry<'blog'>[],
  categorySlug: BlogCategorySlug,
): CollectionEntry<'blog'>[] {
  const label = blogCategoryArchives[categorySlug].label;
  return posts
    .filter((post) => post.data.categories?.includes(label))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}
