import { notFound } from "next/navigation"
import { getLocale } from "next-intl/server"

import { ContentArticle } from "@/components/content/content-article"
import { contentLanguages, contentPage } from "@/lib/content"
import { pageMetadata } from "@/lib/site"

const PATH = "/pre-employment-testing"

export async function generateMetadata() {
  const page = await contentPage(
    "pages",
    "pre-employment-testing",
    await getLocale()
  )

  return page
    ? pageMetadata(
        page.seoTitle,
        page.description,
        PATH,
        await contentLanguages("pages", "pre-employment-testing")
      )
    : {}
}

/** A category page for companies searching the category (content/pages/pre-employment-testing.md). */
export default async function CategoryPage() {
  // In the interface's language where translated.
  const page = await contentPage(
    "pages",
    "pre-employment-testing",
    await getLocale()
  )

  if (!page) {
    notFound()
  }

  return <ContentArticle page={page} path={PATH} />
}
