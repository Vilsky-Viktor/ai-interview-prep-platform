import type { Metadata } from "next"
import { headers } from "next/headers"
import { getTranslations } from "next-intl/server"

import { DEFAULT_LOCALE } from "@/constants/i18n"
import { LOCALE_HEADER, SITE_NAME } from "@/constants/seo"
import { languageAlternates, localizedPath } from "@/lib/locale-path"

/** The site's public address, for absolute links in metadata, robots.txt and the sitemap. */
export function siteUrl() {
  return process.env.SITE_URL ?? "http://localhost:8090"
}

/** The link-preview picture (app/opengraph-image.tsx) at the site's own address: Next.js would
 * otherwise name the dev server's internal one, and a page's openGraph would drop it. */
export function previewImage() {
  return [{ url: `${siteUrl()}/opengraph-image`, width: 1200, height: 630 }]
}

/** The language of the address the page was asked for (/de/pricing gives de), or null for a
 * plain address. */
export async function urlLocale() {
  return (await headers()).get(LOCALE_HEADER)
}

/** A page's title in the interface language, for its generateMetadata. */
export async function translatedTitle(
  namespace: string,
  key: string
): Promise<Metadata> {
  const t = await getTranslations(namespace)

  return { title: t(key) }
}

/** A public page's own description and canonical address, also used in its link previews. A
 * localized page (lib/locale-path.ts isLocalizedPath) names the address of the language it's
 * served in as canonical, and every language's address for hreflang; `localized` as a list
 * names only those languages (an article's translations), and a language outside it has the
 * English address as canonical. */
export async function pageMetadata(
  title: string,
  description: string,
  path: string,
  localized: boolean | readonly string[] = false
): Promise<Metadata> {
  const locale = (await urlLocale()) ?? DEFAULT_LOCALE
  const languages = localized === true ? undefined : localized || undefined
  const own = localized === true || (languages ?? []).includes(locale)
  const canonical = own ? localizedPath(locale, path) : path

  return {
    title,
    description,
    alternates: {
      canonical,
      languages: localized ? languageAlternates(path, languages) : undefined,
    },
    // A page's openGraph replaces the layout's, so the shared fields are repeated here.
    openGraph: {
      siteName: SITE_NAME,
      type: "website",
      url: canonical,
      images: previewImage(),
    },
  }
}
