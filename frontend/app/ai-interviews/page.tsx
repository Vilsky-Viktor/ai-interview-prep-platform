import { notFound } from "next/navigation"
import { getLocale } from "next-intl/server"

import { ContentArticle } from "@/components/content/content-article"
import { contentLanguages, contentPage } from "@/lib/content"
import { pageMetadata } from "@/lib/site"

const PATH = "/ai-interviews"

export async function generateMetadata() {
  const page = await contentPage("pages", "ai-interviews", await getLocale())

  return page
    ? pageMetadata(
        page.seoTitle,
        page.description,
        PATH,
        await contentLanguages("pages", "ai-interviews")
      )
    : {}
}

/** A category page for companies searching the category (content/pages/ai-interviews.md). */
export default async function CategoryPage() {
  // In the interface's language where translated.
  const page = await contentPage("pages", "ai-interviews", await getLocale())

  if (!page) {
    notFound()
  }

  return <ContentArticle page={page} path={PATH} />
}
