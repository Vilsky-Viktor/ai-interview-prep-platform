import { MinusIcon } from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"

import { BackLink } from "@/components/back-link"
import { EditableTitle } from "@/components/editable-title"
import { PageHeader } from "@/components/page-header"
import { DoneBadge } from "@/components/preparations/done-badge"
import {
  PreparationActions,
  PreparationShare,
} from "@/components/preparations/preparation-actions"
import { PreparationStats } from "@/components/preparations/preparation-stats"
import { RatingStars } from "@/components/preparations/rating-stars"
import { TopicQuestionLimit } from "@/components/questions/topic-question-limit"
import { StartRound } from "@/components/rounds/start-round"
import { CertificateButton } from "@/components/rounds/certificate-button"
import { TopicPasses } from "@/components/rounds/topic-passes"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate, plural } from "@/lib/format"
import { isPreparationDone, topicCertificate, topicMastered } from "@/lib/rounds"
import { serverFetch } from "@/lib/server-api"
import type { PreparationDetail } from "@/types/preparation"
import type { TopicPass } from "@/types/round"

type PageProps = { params: Promise<{ id: string }> }

async function getPreparation(id: string) {
  return serverFetch<PreparationDetail>(`/library/preparations/${id}`)
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const preparation = await getPreparation((await params).id)

  return { title: preparation?.title ?? "Preparation" }
}

export default async function PreparationPage({ params }: PageProps) {
  const { id } = await params
  const [preparation, passes] = await Promise.all([
    getPreparation(id),
    serverFetch<TopicPass[]>(`/rounds/preparations/${id}/passes`),
  ])

  if (!preparation) {
    notFound()
  }

  const passing = new Map<string, TopicPass[]>()

  for (const item of passes ?? []) {
    const current = passing.get(item.topic_id) ?? []

    current.push(item)
    passing.set(item.topic_id, current)
  }

  const canPractice = preparation.access !== "public"
  const isOwner = preparation.access === "owner"
  const done = isPreparationDone(
    preparation.topics.length,
    preparation.topics.filter((topic) =>
      topicMastered(passing.get(topic.id) ?? [])
    ).length
  )

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={<BackLink href="/preparations">My preparations</BackLink>}
        before={
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant="secondary"
                className="h-7 px-3 text-sm font-light capitalize"
              >
                {preparation.level}
              </Badge>
              <Badge
                variant="outline"
                className="h-7 px-3 text-sm font-light capitalize"
              >
                {preparation.visibility}
              </Badge>
              {done && <DoneBadge />}
              <PreparationStats preparation={preparation} />
            </div>
            {preparation.access === "joined" && (
              <RatingStars
                preparationId={preparation.id}
                myRating={preparation.my_rating}
              />
            )}
          </div>
        }
        title={
          <div className="flex items-center justify-between gap-4">
            <div className="min-w-0 flex-1">
              {preparation.access === "owner" ? (
                <EditableTitle
                  title={preparation.title}
                  path={`/library/preparations/${preparation.id}/title`}
                />
              ) : (
                <h1 className="font-heading text-3xl font-medium tracking-tight text-balance">
                  {preparation.title}
                </h1>
              )}
            </div>
            <PreparationShare preparation={preparation} />
          </div>
        }
      >
        <p className="text-sm text-muted-foreground">
          {plural(preparation.topics.length, "topic")} · Created{" "}
          {formatDate(preparation.created_at)}
        </p>
        <PreparationActions preparation={preparation} />
      </PageHeader>

      <ul className="divide-y rounded-2xl border">
        {preparation.topics.map((topic) => {
          const topicPasses = passing.get(topic.id) ?? []
          const certificateId = topicCertificate(topicPasses)

          return (
            <li key={topic.id} className="space-y-4 p-4 sm:p-6">
              <div className="flex items-start justify-between gap-4">
                <span className="min-w-0 space-y-2">
                  <span className="block text-2xl font-medium">{topic.title}</span>
                  <span className="block text-sm text-muted-foreground">
                    {topic.subtopics.map((subtopic, index) => (
                      <span key={subtopic}>
                        {index > 0 && (
                          <MinusIcon
                            aria-hidden
                            className="mx-1.5 inline size-3.5 align-[-2px] text-foreground/55"
                          />
                        )}
                        {subtopic}
                      </span>
                    ))}
                  </span>
                </span>
                {canPractice && <StartRound topicId={topic.id} />}
              </div>
              <div className="flex flex-wrap items-center justify-between gap-3 sm:grid sm:grid-cols-[1fr_auto_1fr]">
                <span className="flex items-center">
                  <TopicQuestionLimit
                    title={topic.title}
                    count={topic.question_count}
                    path={`/library/preparations/topics/${topic.id}/questions`}
                    regeneratePath={isOwner ? "/generate/questions" : undefined}
                    reportsPath={isOwner ? "/library/questions" : undefined}
                    limit={topic.question_limit}
                    limitPath={
                      isOwner
                        ? `/library/preparations/topics/${topic.id}/limit`
                        : undefined
                    }
                    caption="per round"
                  />
                </span>
                <span className="flex justify-center">
                  <TopicPasses passes={topicPasses} total={topic.question_count} />
                </span>
                {canPractice && (
                  <span className="flex items-center justify-end gap-2">
                    <CertificateButton certificateId={certificateId} />
                    <Button
                      variant="outline"
                      nativeButton={false}
                      render={
                        <Link
                          href={`/preparations/${preparation.id}/topics/${topic.id}/history`}
                        />
                      }
                    >
                      History
                    </Button>
                  </span>
                )}
              </div>
            </li>
          )
        })}
      </ul>
    </main>
  )
}
