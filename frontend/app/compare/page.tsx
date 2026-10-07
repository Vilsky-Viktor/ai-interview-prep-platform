import { getLocale, getTranslations } from "next-intl/server"

import { ContentList } from "@/components/content/content-list"
import { contentPages } from "@/lib/content"
import { pageMetadata } from "@/lib/site"

export async function generateMetadata() {
  const t = await getTranslations("compare")

  return pageMetadata(t("title"), t("intro"), "/compare", true)
}

/** The compare hub: every page in content/compare, by title. */
export default async function HubPage() {
  const t = await getTranslations("compare")
  // In the interface's language where translated.
  const pages = await contentPages("compare", await getLocale())

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="space-y-2">
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-base text-muted-foreground">{t("intro")}</p>
      </div>
      <ContentList pages={pages} base="/compare" />
    </main>
  )
}
