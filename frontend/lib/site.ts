import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"

import { SITE_NAME } from "@/constants/seo"

/** The site's public address, for absolute links in metadata, robots.txt and the sitemap. */
export function siteUrl() {
  return process.env.SITE_URL ?? "http://localhost:8090"
}

/** A page's title in the interface language, for its generateMetadata. */
export async function translatedTitle(
  namespace: string,
  key: string
): Promise<Metadata> {
  const t = await getTranslations(namespace)

  return { title: t(key) }
}

/** A public page's own description and canonical address, also used in its link previews. */
export function pageMetadata(
  title: string,
  description: string,
  path: string
): Metadata {
  return {
    title,
    description,
    alternates: { canonical: path },
    // A page's openGraph replaces the layout's, so the shared fields are repeated here.
    openGraph: { siteName: SITE_NAME, type: "website", url: path },
  }
}
