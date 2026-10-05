import type { MetadataRoute } from "next"

import { PUBLIC_PATHS } from "@/constants/seo"
import { siteUrl } from "@/lib/site"

// The API's largest page, and how many pages of practice tests the sitemap reads at most.
const PAGE = 100
const MAX_PAGES = 50

/** Every free practice test's page, read from the public template list a page at a time. */
async function practicePaths(): Promise<string[]> {
  const paths: string[] = []

  for (let page = 0; page < MAX_PAGES; page++) {
    const response = await fetch(
      `${process.env.API_URL}/api/library/templates?offset=${page * PAGE}&limit=${PAGE}`,
      { cache: "no-store" }
    )

    if (!response.ok) {
      break
    }

    const rows: { id: string }[] = await response.json()
    paths.push(...rows.map((row) => `/practice/${row.id}`))

    if (rows.length < PAGE) {
      break
    }
  }

  return paths
}

/** The public pages, and one page per free practice test. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const paths = [...PUBLIC_PATHS, ...(await practicePaths())]

  return paths.map((path) => ({ url: `${siteUrl()}${path}` }))
}
