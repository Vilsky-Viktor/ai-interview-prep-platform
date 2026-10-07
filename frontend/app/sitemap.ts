import type { MetadataRoute } from "next"

import { CATEGORY_PAGES } from "@/constants/content"
import { DEFAULT_LOCALE, LOCALES } from "@/constants/i18n"
import { LOCALIZED_PATHS, PUBLIC_PATHS } from "@/constants/seo"
import { contentLanguages, contentPages } from "@/lib/content"
import {
  languageAlternates,
  localizedPath,
  templateLocales,
} from "@/lib/locale-path"
import { siteUrl } from "@/lib/site"

// The API's largest page, and how many pages of templates the sitemap reads at most.
const PAGE = 100
const MAX_PAGES = 50

type Template = {
  id: string
  slug: string | null
  language: string
  created_at: string
}

/** Every template, read from the public list a page at a time. */
async function templates(): Promise<Template[]> {
  const rows: Template[] = []

  for (let page = 0; page < MAX_PAGES; page++) {
    const response = await fetch(
      `${process.env.API_URL}/api/library/templates?offset=${page * PAGE}&limit=${PAGE}`,
      { cache: "no-store" }
    )

    if (!response.ok) {
      break
    }

    const batch: Template[] = await response.json()
    rows.push(...batch)

    if (batch.length < PAGE) {
      break
    }
  }

  return rows
}

// Articles in each content folder, by the address they live at.
const ARTICLES = [
  { folder: "pages", base: "" },
  { folder: "compare", base: "/compare" },
  { folder: "guides", base: "/guides" },
] as const

/** Every article in each language it's written in, each naming its translations, with the
 * date it was last updated. */
async function articles(site: string) {
  const absolute = (links: Record<string, string>) =>
    Object.fromEntries(
      Object.entries(links).map(([locale, path]) => [locale, `${site}${path}`])
    )
  const lists = await Promise.all(
    ARTICLES.map(async ({ folder, base }) => {
      const pages = await contentPages(folder)

      return Promise.all(
        pages.map(async (page) => {
          const path = `${base}/${page.slug}`
          const languages = await contentLanguages(folder, page.slug)

          return languages.map((locale) => ({
            url: `${site}${localizedPath(locale, path)}`,
            lastModified: page.updated || undefined,
            alternates: {
              languages: absolute(languageAlternates(path, languages)),
            },
          }))
        })
      )
    })
  )

  return lists.flat(2)
}

/** The public pages (those in every language with each language's address), the articles in
 * their languages with their dates, and each template's role test page and free practice
 * page. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const site = siteUrl()
  const absolute = (links: Record<string, string>) =>
    Object.fromEntries(
      Object.entries(links).map(([locale, path]) => [locale, `${site}${path}`])
    )
  // The category pages are articles: listed with their translations below.
  const everyLanguage = LOCALIZED_PATHS.filter(
    (path) => !CATEGORY_PAGES.includes(path.slice(1))
  )
  const [rows, written] = await Promise.all([templates(), articles(site)])

  return [
    // A page in every language is listed once per language, each naming all of them.
    ...everyLanguage.flatMap((path) =>
      LOCALES.map((locale) => ({
        url: `${site}${localizedPath(locale, path)}`,
        alternates: { languages: absolute(languageAlternates(path)) },
      }))
    ),
    ...PUBLIC_PATHS.filter((path) => !LOCALIZED_PATHS.includes(path)).map(
      (path) => ({ url: `${site}${path}` })
    ),
    ...written,
    // A template's pages in English and in its language, each naming the other.
    ...rows.flatMap((row) => {
      const languages = templateLocales(row.language)

      return ["/tests", "/practice"].flatMap((base) => {
        const path = `${base}/${row.slug ?? row.id}`
        const alternates = languages
          ? { languages: absolute(languageAlternates(path, languages)) }
          : undefined

        return (languages || [DEFAULT_LOCALE]).map((locale) => ({
          url: `${site}${localizedPath(locale, path)}`,
          lastModified: row.created_at,
          alternates,
        }))
      })
    }),
  ]
}
