import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { BackLink } from "@/components/back-link"
import { PageHeader } from "@/components/page-header"
import { CompareCell } from "@/components/rounds/compare-cell"
import { MODE_LABELS } from "@/constants/rounds"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import type { ReviewItem, Round } from "@/types/round"

export const metadata: Metadata = { title: "Compare rounds" }

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
  const [first, second] = await Promise.all([loadRound(a), loadRound(b)])

  if (!first || !second || first.round.topic_id !== second.round.topic_id) {
    notFound()
  }

  const secondByQuestion = new Map(
    second.review.map((item) => [item.question_id, item])
  )

  return (
    <main className="mx-auto max-w-4xl space-y-8 px-6 py-12">
      <PageHeader
        back={
          <BackLink
            href={`/preparations/${first.round.preparation_id}/topics/${first.round.topic_id}/history`}
          >
            Rounds
          </BackLink>
        }
        title={
          <h1 className="font-heading text-3xl font-medium tracking-tight">
            Compare rounds
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
              {MODE_LABELS[round.mode]} · {formatDate(round.started_at)}
            </p>
          </div>
        ))}
      </div>

      <ul className="divide-y rounded-2xl border">
        {first.review.map((item) => {
          const other = secondByQuestion.get(item.question_id)
          const reference = item.reference_answer ?? other?.reference_answer

          return (
            <li key={item.question_id} className="space-y-4 p-5">
              <p className="font-medium">{item.text}</p>
              <div className="grid gap-4 sm:grid-cols-2">
                <CompareCell item={item} />
                <CompareCell item={other} />
              </div>
              {reference && (
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">Reference: </span>
                  {reference}
                </p>
              )}
            </li>
          )
        })}
      </ul>
    </main>
  )
}
