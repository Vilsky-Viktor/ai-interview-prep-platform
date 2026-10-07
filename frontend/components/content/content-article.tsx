import { cn } from "cn"
import { getLocale, getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { Markdown } from "@/components/content/markdown"
import { StartCard } from "@/components/content/start-card"
import { JsonLd } from "@/components/json-ld"
import { RTL_LOCALES, type Locale } from "@/constants/i18n"
import type { ContentPage } from "@/lib/content"
import { localizeHref } from "@/lib/locale-path"
import { siteUrl, urlLocale } from "@/lib/site"
import { articleData, breadcrumbData } from "@/lib/structured-data"

/** One content page (a category page, a comparison or a guide): its heading, date and text,
 * then the way to a first test, in the language it's written in (English where it has no
 * translation yet, with a note). `section` is the hub it belongs to, for the back link and the
 * breadcrumb. */
export async function ContentArticle({
  page,
  path,
  section,
}: {
  page: ContentPage
  path: string
  section?: { name: string; path: string }
}) {
  const t = await getTranslations("content")
  const locale = await getLocale()
  const address = await urlLocale()
  const direction = RTL_LOCALES.includes(page.language as Locale)
    ? "rtl"
    : "ltr"
  // The breadcrumb names the addresses in the page's own language.
  const steps = [
    { name: "prepza", path: "/" },
    ...(section ? [section] : []),
    { name: page.title, path },
  ].map((step) => ({ ...step, path: localizeHref(address, step.path) }))

  return (
    <main className="mx-auto max-w-5xl space-y-10 px-6 py-12">
      <JsonLd
        data={[
          articleData(siteUrl(), {
            ...page,
            path: localizeHref(address, path),
          }),
          breadcrumbData(siteUrl(), steps),
        ]}
      />
      <header className="space-y-4">
        {section && <BackLink href={section.path}>{section.name}</BackLink>}
        <h1
          className={cn(
            "font-heading text-4xl font-medium tracking-tight text-balance normal-case",
            page.title.endsWith("?") && "no-dot"
          )}
        >
          {page.title}
        </h1>
        <p className="text-lg text-muted-foreground">{page.description}</p>
        <p className="text-sm text-muted-foreground">
          {page.language !== locale && (
            <span className="block pb-2">{t("englishOnly")}</span>
          )}
          {t("updated")} <time dateTime={page.updated}>{page.updated}</time>
        </p>
      </header>
      <article lang={page.language} dir={direction} className="space-y-5">
        <Markdown text={page.body} />
      </article>
      <StartCard />
    </main>
  )
}
