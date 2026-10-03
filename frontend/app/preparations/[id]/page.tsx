import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"
import { getLocale, getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { EditableTitle } from "@/components/editable-title"
import { PageHeader } from "@/components/page-header"
import { DoneBadge } from "@/components/preparations/done-badge"
import { MakeItYours } from "@/components/preparations/make-it-yours"
import {
  PreparationActions,
  PreparationShare,
} from "@/components/preparations/preparation-actions"
import { PreparationStats } from "@/components/preparations/preparation-stats"
import { RatingStars } from "@/components/preparations/rating-stars"
import { SubtopicList } from "@/components/questions/subtopic-list"
import { TopicQuestions } from "@/components/questions/topic-questions"
import { StartRound } from "@/components/rounds/start-round"
import { BuyCertificate } from "@/components/rounds/buy-certificate"
import { CertificateButton } from "@/components/rounds/certificate-button"
import { TopicProgress } from "@/components/rounds/topic-progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { Catalog } from "@/types/billing"
import type { PreparationDetail } from "@/types/preparation"
import type { TopicProgress as Progressed } from "@/types/round"

type PageProps = { params: Promise<{ id: string }> }

async function getPreparation(id: string) {
  return serverFetch<PreparationDetail>(`/library/preparations/${id}`)
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { id } = await params
  const preparation = await getPreparation(id)
  const t = await getTranslations("preparations")

  if (!preparation) {
    return { title: t("metaTitle") }
  }

  return pageMetadata(
    preparation.title,
    t("metaDescription", {
      title: preparation.title,
      count: preparation.topic_count,
    }),
    `/preparations/${id}`
  )
}

export default async function PreparationPage({ params }: PageProps) {
  const { id } = await params
  const t = await getTranslations("preparations")
  const levels = await getTranslations("levels")
  const visibility = await getTranslations("visibility")
  const locale = await getLocale()
  const [preparation, progressRows, catalog] = await Promise.all([
    getPreparation(id),
    serverFetch<Progressed[]>(`/rounds/preparations/${id}/progress`),
    serverFetch<Catalog>("/billing/catalog"),
  ])

  if (!preparation) {
    notFound()
  }

  const progressByTopic = new Map(
    (progressRows ?? []).map((item) => [item.topic_id, item])
  )

  const canPractice = preparation.access !== "public"
  const isOwner = preparation.access === "owner"
  const done = preparation.done
  // Someone else's public kit: invite the learner to a kit of their own.
  const othersPublic = preparation.visibility === "public" && !isOwner

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={<BackLink href="/preparations">{t("title")}</BackLink>}
        before={
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant="secondary"
                className="h-7 px-3 text-sm font-light"
              >
                {levels(preparation.level)}
              </Badge>
              <Badge
                variant="outline"
                className="h-7 px-3 text-sm font-light"
              >
                {visibility(preparation.visibility)}
              </Badge>
              {done && <DoneBadge />}
              <PreparationStats preparation={preparation} />
            </div>
            {preparation.access === "joined" && (
              <RatingStars
                preparationId={preparation.id}
                myRating={preparation.my_rating}
                scale={preparation.rating_scale}
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
                <h1 className="font-heading text-3xl font-medium tracking-tight text-balance normal-case">
                  {preparation.title}
                </h1>
              )}
            </div>
            <PreparationShare preparation={preparation} />
          </div>
        }
      >
        <p className="text-sm text-muted-foreground">
          {t("topics", { count: preparation.topics.length })} ·{" "}
          {t("created", { date: formatDate(preparation.created_at, locale) })}
        </p>
        <PreparationActions preparation={preparation} />
      </PageHeader>

      {othersPublic && <MakeItYours />}

      <ul className="divide-y rounded-2xl border">
        {preparation.topics.map((topic) => {
          const progress = progressByTopic.get(topic.id)

          return (
            <li key={topic.id} className="space-y-4 p-4 sm:p-6">
              <div className="flex items-start justify-between gap-8">
                <span className="min-w-0 space-y-2">
                  <span className="block text-2xl font-medium">
                    {topic.title}
                  </span>
                  <SubtopicList subtopics={topic.subtopics} />
                </span>
                {canPractice && (
                  <StartRound
                    topicId={topic.id}
                    inProgress={progress?.in_progress}
                  />
                )}
              </div>
              {/* Questions, progress, actions; on phones the progress bar takes its own line. */}
              <div className="flex flex-wrap items-center justify-between gap-3 sm:grid sm:grid-cols-[auto_1fr_auto] sm:gap-6">
                <span className="flex items-center">
                  <TopicQuestions
                    title={topic.title}
                    count={topic.question_count}
                    path={`/library/preparations/topics/${topic.id}/questions`}
                    regeneratePath={isOwner ? "/library/questions" : undefined}
                    reportsPath={isOwner ? "/library/questions" : undefined}
                  />
                </span>
                {canPractice && (
                  <div className="order-last w-full sm:order-none">
                    <TopicProgress
                      progress={progress}
                      total={topic.question_count}
                    />
                  </div>
                )}
                {canPractice && (
                  <span className="flex items-center justify-end gap-2">
                    {progress?.certificate_for_sale && catalog ? (
                      <BuyCertificate
                        topicId={topic.id}
                        price={catalog.certificate_credits}
                      />
                    ) : (
                      <CertificateButton
                        certificateId={progress?.certificate_id ?? null}
                      />
                    )}
                    <Button
                      variant="outline"
                      nativeButton={false}
                      render={
                        <Link
                          href={`/preparations/${preparation.id}/topics/${topic.id}/history`}
                        />
                      }
                    >
                      {t("history")}
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
