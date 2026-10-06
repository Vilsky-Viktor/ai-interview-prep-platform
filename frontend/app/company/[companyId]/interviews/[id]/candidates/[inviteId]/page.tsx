import { InfoIcon } from "lucide-react"
import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"
import { cn } from "cn"

import { BackLink } from "@/components/back-link"
import { CandidateActions } from "@/components/company/candidate-actions"
import { CandidateReport } from "@/components/company/candidate-report"
import { ExtraTime } from "@/components/company/extra-time"
import { IntegrityLine } from "@/components/company/integrity-line"
import { CandidateReportActions } from "@/components/company/candidate-report-actions"
import { ScorecardReview } from "@/components/company/scorecard-review"
import { PageHeader } from "@/components/page-header"
import { Badge } from "@/components/ui/badge"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Scorecard } from "@/types/company"

export const generateMetadata = () => translatedTitle("candidates", "scorecard")

export default async function ScorecardPage({
  params,
}: {
  params: Promise<{ companyId: string; id: string; inviteId: string }>
}) {
  const { companyId, id, inviteId } = await params
  const reportT = await getTranslations("report")
  const t = await getTranslations("candidates")
  const statuses = await getTranslations("candidateStatus")
  const card = await serverFetch<Scorecard>(
    `/companies/interviews/${id}/candidates/${inviteId}`
  )

  if (!card) {
    notFound()
  }

  const deleted = card.status === "deleted"

  const reportable = !deleted && card.sessions.length > 0
  const report = {
    company: card.company,
    logoUrl: card.logo_url,
    verifiedDomain: card.verified_domain,
    title: card.title,
    email: card.email,
    grade: card.grade,
    passed: card.passed,
    passMark: card.pass_mark,
    // Without the questions: the report never shows them.
    sections: card.sessions.map((session) => ({
      id: session.id,
      topic_title: session.topic_title,
      final_score: session.final_score,
      passed: session.passed,
      tab_leaves: session.tab_leaves,
      copies: session.copies,
      fast_answers: session.fast_answers,
    })),
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      {reportable && <CandidateReport report={report} />}
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
          tags={
            <Badge
              variant={
                card.status === "undelivered" ? "destructive" : "outline"
              }
              className="h-7 px-3 text-sm font-light"
            >
              {statuses(card.status)}
            </Badge>
          }
          title={
            <h1 className="font-heading text-3xl font-medium tracking-tight">
              {deleted ? t("deleted") : card.email}
            </h1>
          }
        />
        {!deleted && (
          <div className="flex items-center gap-3">
            <ExtraTime
              interviewId={id}
              inviteId={inviteId}
              current={card.extra_time}
              options={card.extra_time_options}
            />
            {card.can_edit && (
              <CandidateActions
                interviewId={id}
                inviteId={inviteId}
                email={card.email}
                status={card.status}
                backHref={`/company/${companyId}/interviews/${id}?tab=candidates`}
              />
            )}
            {reportable && (
              <CandidateReportActions
                interviewId={id}
                inviteId={inviteId}
                report={report}
              />
            )}
          </div>
        )}
      </div>

      {/* The score supports a decision people make; in the gray info card, like the practice
          test page's. */}
      {card.sessions.length > 0 && (
        <div className="flex items-center gap-3 rounded-2xl border bg-muted px-5 py-4 text-base text-muted-foreground">
          <InfoIcon aria-hidden className="size-6 shrink-0 text-primary" />
          <p>{reportT("humanReview")}</p>
        </div>
      )}

      {card.sessions.length === 0 && (
        <p className="py-16 text-center text-muted-foreground">
          {deleted ? t("deletedText") : t("notStarted")}
        </p>
      )}

      {card.sessions.map((session) => {
        const score = session.final_score
        const tone =
          session.passed === true
            ? "text-green-600 dark:text-green-400"
            : session.passed === false
              ? "text-red-600 dark:text-red-400"
              : "text-muted-foreground"

        return (
          <section key={session.id} className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0 space-y-1">
                <h2 className="font-heading text-2xl font-medium normal-case">
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
