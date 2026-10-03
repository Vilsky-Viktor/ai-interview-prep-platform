import { MinusIcon } from "lucide-react"
import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"
import { cn } from "cn"

import { BackLink } from "@/components/back-link"
import { CandidateActions } from "@/components/company/candidate-actions"
import { ScorecardReview } from "@/components/company/scorecard-review"
import { PageHeader } from "@/components/page-header"
import { Badge } from "@/components/ui/badge"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { ReviewItem } from "@/types/round"

export const generateMetadata = () => translatedTitle("candidates", "scorecard")

type Scorecard = {
  id: string
  email: string
  status: string
  sessions: {
    id: string
    topic_title: string
    status: string
    final_score: number | null
    tab_leaves: number
    copies: number
    fast_answers: number
    review: ReviewItem[]
  }[]
}

/** What the candidate's browser and timing showed; counts above zero stand out. */
async function IntegrityLine({
  session,
}: {
  session: { tab_leaves: number; copies: number; fast_answers: number }
}) {
  const t = await getTranslations("candidates")
  const signals = [
    t("pageLeaves", { count: session.tab_leaves }),
    t("copies", { count: session.copies }),
    t("fastAnswers", { count: session.fast_answers }),
  ]
  const counts = [session.tab_leaves, session.copies, session.fast_answers]

  return (
    <p className="flex flex-wrap items-center gap-x-1.5 text-sm text-muted-foreground tabular-nums">
      {signals.map((signal, index) => (
        <span key={signal} className="flex items-center gap-x-1.5">
          {index > 0 && (
            <MinusIcon aria-hidden className="size-3.5 text-foreground" />
          )}
          <span
            className={cn(
              counts[index] > 0 && "text-amber-600 dark:text-amber-400"
            )}
          >
            {signal}
          </span>
        </span>
      ))}
    </p>
  )
}

export default async function ScorecardPage({
  params,
}: {
  params: Promise<{ companyId: string; id: string; inviteId: string }>
}) {
  const { companyId, id, inviteId } = await params
  const t = await getTranslations("candidates")
  const statuses = await getTranslations("candidateStatus")
  const card = await serverFetch<Scorecard>(
    `/companies/interviews/${id}/candidates/${inviteId}`
  )

  if (!card) {
    notFound()
  }

  const deleted = card.status === "deleted"

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      {/* The actions sit beside the email and status, centered on both. */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <PageHeader
          back={
            <BackLink
              href={`/company/${companyId}/interviews/${id}?tab=candidates`}
            >
              {t("interview")}
            </BackLink>
          }
          title={
            <h1 className="font-heading text-3xl font-medium tracking-tight">
              {deleted ? t("deleted") : card.email}
            </h1>
          }
        >
          <Badge
            variant={card.status === "undelivered" ? "destructive" : "outline"}
            className="h-7 px-3 text-sm font-light capitalize"
          >
            {statuses(card.status)}
          </Badge>
        </PageHeader>
        {!deleted && (
          <CandidateActions
            interviewId={id}
            inviteId={inviteId}
            email={card.email}
            status={card.status}
            backHref={`/company/${companyId}/interviews/${id}?tab=candidates`}
          />
        )}
      </div>

      {card.sessions.length === 0 && (
        <p className="py-16 text-center text-muted-foreground">
          {deleted ? t("deletedText") : t("notStarted")}
        </p>
      )}

      {card.sessions.map((session) => {
        const score = session.final_score
        const tone =
          score == null
            ? "text-muted-foreground"
            : "text-blue-600 dark:text-blue-400"

        return (
          <section key={session.id} className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0 space-y-1">
                <h2 className="font-heading text-2xl font-medium">
                  {session.topic_title}
                </h2>
                <IntegrityLine session={session} />
              </div>
              <p className={cn("text-5xl font-light tabular-nums", tone)}>
                {score == null ? "—" : `${score}%`}
              </p>
            </div>
            <ScorecardReview items={session.review} />
          </section>
        )
      })}
    </main>
  )
}
