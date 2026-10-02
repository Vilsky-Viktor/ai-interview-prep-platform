import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { BackLink } from "@/components/back-link"
import { RoundHistory } from "@/components/rounds/round-history"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { PreparationDetail } from "@/types/preparation"
import type { Round } from "@/types/round"

export const metadata: Metadata = { title: "Rounds" }

export default async function HistoryPage({
  params,
}: {
  params: Promise<{ id: string; topicId: string }>
}) {
  const { id, topicId } = await params
  const [preparation, rounds] = await Promise.all([
    serverFetch<PreparationDetail>(`/library/preparations/${id}`),
    // The first page renders on the server; the rest load as the user scrolls.
    serverFetch<Round[]>(`/rounds/topics/${topicId}/rounds?limit=${PAGE_SIZE}`),
  ])
  const topic = preparation?.topics.find((item) => item.id === topicId)

  if (!preparation || !topic || !rounds) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <RoundHistory
        topicId={topicId}
        rounds={rounds}
        back={
          <BackLink href={`/preparations/${id}`}>Preparation page</BackLink>
        }
        title={
          <h1 className="font-heading text-3xl font-medium tracking-tight text-balance">
            {topic.title}
          </h1>
        }
      />
    </main>
  )
}
