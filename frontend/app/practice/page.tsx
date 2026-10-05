import { getTranslations } from "next-intl/server"

import {
  TemplateBrowser,
  type TemplateSearchParams,
} from "@/components/templates/template-browser"
import { pageMetadata } from "@/lib/site"

export async function generateMetadata() {
  const t = await getTranslations("practice")

  return pageMetadata(t("title"), t("intro"), "/practice")
}

/** The free practice library: every template, searched and filtered like the companies' list.
 * Public, for search engines; advertised as practice, never as a real interview. */
export default async function PracticePage({
  searchParams,
}: {
  searchParams: Promise<TemplateSearchParams>
}) {
  const t = await getTranslations("practice")
  const browser = await TemplateBrowser({
    base: "/practice",
    listPath: "/library/templates",
    params: await searchParams,
    openBase: "/practice",
  })

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="space-y-2">
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-base text-muted-foreground">{t("intro")}</p>
      </div>
      {browser}
    </main>
  )
}
