import type { Metadata } from "next"
import { notFound } from "next/navigation"
import { getLocale, getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { PageHeader } from "@/components/page-header"
import { CompareList } from "@/components/rounds/compare-list"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import type { ReviewItem, Round } from "@/types/round"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("rounds")

  return { title: t("compareTitle") }
}

async function loadRound(id: string | undefined) {
  if (!id) {
    return null
  }

  const [round, review] = await Promise.all([
    serverFetch<Round>(`/rounds/rounds/${id}`),
    serverFetch<ReviewItem[]>(`/rounds/rounds/${id}/review`),
  ])

  return round && review ? { round, review } : null
}

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<{ a?: string; b?: string }>
}) {
  const { a, b } = await searchParams
  const t = await getTranslations("rounds")
  const locale = await getLocale()
  const [first, second] = await Promise.all([loadRound(a), loadRound(b)])

  if (!first || !second || first.round.topic_id !== second.round.topic_id) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={
          <BackLink
            href={`/preparations/${first.round.preparation_id}/topics/${first.round.topic_id}/history`}
          >
            {t("rounds")}
          </BackLink>
        }
        title={
          <h1 className="font-heading text-3xl font-medium tracking-tight">
            {t("compareTitle")}
          </h1>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2">
        {[first.round, second.round].map((round) => (
          <div key={round.id} className="rounded-2xl border p-4">
            <p className="font-heading text-3xl font-medium tabular-nums">
              {round.final_score ?? 0}%
            </p>
            <p className="text-sm text-muted-foreground">
              {formatDate(round.started_at, locale)}
            </p>
          </div>
        ))}
      </div>

      <CompareList first={first.review} second={second.review} />
    </main>
  )
}
