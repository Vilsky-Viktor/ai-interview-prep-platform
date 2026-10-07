import { notFound } from "next/navigation"
import { getLocale, getTranslations } from "next-intl/server"

import { ContentArticle } from "@/components/content/content-article"
import { contentLanguages, contentPage } from "@/lib/content"
import { pageMetadata } from "@/lib/site"

type Params = { params: Promise<{ slug: string }> }

export async function generateMetadata({ params }: Params) {
  const { slug } = await params
  const page = await contentPage("compare", slug, await getLocale())

  return page
    ? pageMetadata(
        page.seoTitle,
        page.description,
        `/compare/${slug}`,
        await contentLanguages("compare", slug)
      )
    : {}
}

/** One page of content/compare, under its hub. */
export default async function HubArticlePage({ params }: Params) {
  const { slug } = await params
  const t = await getTranslations("compare")
  // In the interface's language where translated.
  const page = await contentPage("compare", slug, await getLocale())

  if (!page) {
    notFound()
  }

  return (
    <ContentArticle
      page={page}
      path={`/compare/${slug}`}
      section={{ name: t("title"), path: "/compare" }}
    />
  )
}
