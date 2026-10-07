import { notFound } from "next/navigation"
import { getLocale, getTranslations } from "next-intl/server"

import { ContentArticle } from "@/components/content/content-article"
import { contentLanguages, contentPage } from "@/lib/content"
import { pageMetadata } from "@/lib/site"

type Params = { params: Promise<{ slug: string }> }

export async function generateMetadata({ params }: Params) {
  const { slug } = await params
  const page = await contentPage("guides", slug, await getLocale())

  return page
    ? pageMetadata(
        page.seoTitle,
        page.description,
        `/guides/${slug}`,
        await contentLanguages("guides", slug)
      )
    : {}
}

/** One page of content/guides, under its hub. */
export default async function HubArticlePage({ params }: Params) {
  const { slug } = await params
  const t = await getTranslations("guides")
  // In the interface's language where translated.
  const page = await contentPage("guides", slug, await getLocale())

  if (!page) {
    notFound()
  }

  return (
    <ContentArticle
      page={page}
      path={`/guides/${slug}`}
      section={{ name: t("title"), path: "/guides" }}
    />
  )
}
