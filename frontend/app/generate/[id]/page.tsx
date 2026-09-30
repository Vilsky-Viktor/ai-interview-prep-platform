import type { Metadata } from "next"

import { GenerationView } from "@/components/generation/generation-view"

export const metadata: Metadata = { title: "New preparation" }

export default async function GeneratePage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ next?: string }>
}) {
  const { id } = await params
  const raw = (await searchParams).next
  const next = raw?.startsWith("/company/") ? raw : undefined
  const companyMatch = next?.match(/^\/company\/([^/]+)\/interviews\/([^/?]+)/)

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
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
        backLabel={companyMatch ? "Interviews" : "My preparations"}
      />
    </main>
  )
}
