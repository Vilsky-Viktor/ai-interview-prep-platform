import type { MetadataRoute } from "next"

import {
  PUBLIC_PATHS,
  SITEMAP_PAGE,
  SITEMAP_PREPARATIONS,
} from "@/constants/seo"
import { serverFetch } from "@/lib/server-api"
import { siteUrl } from "@/lib/site"
import type { LibraryFilters, PreparationSummary } from "@/types/preparation"

/** The public pages, and the public library's preparations, best rated first. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages: MetadataRoute.Sitemap = PUBLIC_PATHS.map((path) => ({
    url: `${siteUrl()}${path}`,
  }))

  // Every language: without them the library lists only the reader's own and English.
  const filters = await serverFetch<LibraryFilters>("/library/library/filters")
  const languages = (filters?.languages ?? [])
    .map((language) => `&language=${language}`)
    .join("")

  for (let offset = 0; offset < SITEMAP_PREPARATIONS; offset += SITEMAP_PAGE) {
    const batch = await serverFetch<PreparationSummary[]>(
      `/library/library?q=${languages}&offset=${offset}&limit=${SITEMAP_PAGE}`
    )

    for (const preparation of batch ?? []) {
      pages.push({
        url: `${siteUrl()}/preparations/${preparation.id}`,
        lastModified: preparation.created_at,
      })
    }

    if (!batch || batch.length < SITEMAP_PAGE) {
      break
    }
  }

  return pages
}
