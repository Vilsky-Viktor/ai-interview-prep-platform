import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"

import { GenerationView } from "@/components/generation/generation-view"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("generation")

  return { title: t("title") }
}

export default async function GeneratePage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ next?: string }>
}) {
  const { id } = await params
  const t = await getTranslations("generation")
  const preparations = await getTranslations("preparations")
  const raw = (await searchParams).next
  const next = raw?.startsWith("/company/") ? raw : undefined
  const companyMatch = next?.match(/^\/company\/([^/]+)\/interviews\/([^/?]+)/)

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col space-y-8 px-6 py-12">
      <GenerationView
        // Interview generations go through companies, so every admin can follow them.
        path={
          companyMatch
            ? `/companies/interviews/${companyMatch[2]}/generation`
            : `/generate/generations/${id}`
        }
        next={next}
        backHref={
          companyMatch
            ? `/company/${companyMatch[1]}/interviews`
            : "/preparations"
        }
        backLabel={companyMatch ? t("interviews") : preparations("title")}
      />
    </main>
  )
}
