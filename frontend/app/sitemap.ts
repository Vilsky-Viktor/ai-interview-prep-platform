import type { MetadataRoute } from "next"

import {
  PUBLIC_PATHS,
  SITEMAP_PAGE,
  SITEMAP_PREPARATIONS,
} from "@/constants/seo"
import { serverFetch } from "@/lib/server-api"
import { siteUrl } from "@/lib/site"
import type { PreparationSummary } from "@/types/preparation"

/** The public pages, and the public library's preparations, best rated first. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages: MetadataRoute.Sitemap = PUBLIC_PATHS.map((path) => ({
    url: `${siteUrl()}${path}`,
  }))

  for (let offset = 0; offset < SITEMAP_PREPARATIONS; offset += SITEMAP_PAGE) {
    const batch = await serverFetch<PreparationSummary[]>(
      `/library/library?q=&offset=${offset}&limit=${SITEMAP_PAGE}`
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
