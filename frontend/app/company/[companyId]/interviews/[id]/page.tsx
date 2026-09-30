import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"

import { BackLink } from "@/components/back-link"
import { InterviewNav } from "@/components/company/interview-nav"
import { EditableTitle } from "@/components/editable-title"
import { InterviewSettings } from "@/components/company/interview-settings"
import { InviteCandidate } from "@/components/company/invite-candidate"
import { PageHeader } from "@/components/page-header"
import { TopicQuestionLimit } from "@/components/questions/topic-question-limit"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MODE_LABELS } from "@/constants/rounds"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import type { Candidate, InterviewDetail } from "@/types/company"

export const metadata: Metadata = { title: "Interview" }

export default async function InterviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ companyId: string; id: string }>
  searchParams: Promise<{ tab?: string }>
}) {
  const { companyId, id } = await params
  const { tab } = await searchParams
  const [interview, candidates] = await Promise.all([
    serverFetch<InterviewDetail>(`/companies/interviews/${id}`),
    serverFetch<Candidate[]>(`/companies/interviews/${id}/candidates`),
  ])

  if (!interview) {
    notFound()
  }

  const interviewsHref = `/company/${companyId}/interviews`
  const interviewHref = `${interviewsHref}/${id}`
  const ready = Boolean(interview.set_id)
  const current = ready && tab === "candidates" ? "candidates" : "topics"

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="space-y-4">
        <PageHeader
          back={<BackLink href={interviewsHref}>Interviews</BackLink>}
          before={
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant="secondary"
                className="h-7 px-3 text-sm font-light"
              >
                {MODE_LABELS[interview.mode]}
              </Badge>
              <Badge
                variant="outline"
                className="h-7 px-3 text-sm font-light"
              >
                {interview.share_results ? "Show results" : "Hide results"}
              </Badge>
            </div>
          }
          title={
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                {interview.title ? (
                  <EditableTitle
                    title={interview.title}
                    path={`/companies/interviews/${interview.id}/title`}
                  />
                ) : (
                  <h1 className="font-heading text-3xl font-medium tracking-tight text-balance">
                    Generating…
                  </h1>
                )}
              </div>
              <InterviewSettings
                interviewId={interview.id}
                mode={interview.mode}
                shareResults={interview.share_results}
              />
            </div>
          }
        >
          {!ready && (
            <Button
              variant="outline"
              className="h-12 px-6 text-base"
              render={
                <Link
                  href={`/generate/${interview.generation_id}?next=${interviewHref}`}
                />
              }
              nativeButton={false}
            >
              Continue generation
            </Button>
          )}
        </PageHeader>
        {ready && <InterviewNav href={interviewHref} current={current} />}
      </div>

      {current === "candidates" ? (
        <div className="space-y-6">
          <InviteCandidate interviewId={interview.id} />
          {(candidates ?? []).length === 0 ? (
            <p className="py-16 text-center text-muted-foreground">
              No candidates invited yet.
            </p>
          ) : (
            <ul className="divide-y rounded-2xl border">
              {(candidates ?? []).map((candidate) => (
                <li key={candidate.id}>
                  <Link
                    href={`${interviewHref}/candidates/${candidate.id}`}
                    className="flex flex-col gap-4 p-4 transition-colors hover:bg-muted/50 sm:flex-row sm:items-center sm:justify-between sm:p-6"
                  >
                    <span className="min-w-0 space-y-1">
                      <span className="block text-lg font-medium break-all">
                        {candidate.email}
                      </span>
                      <span className="block text-sm text-muted-foreground">
                        {formatDate(candidate.created_at)}
                      </span>
                    </span>
                    <span className="flex shrink-0 items-center gap-6 sm:gap-10">
                      <span className="w-20 text-center sm:w-24">
                        <span className="block text-2xl font-light tabular-nums">
                          {candidate.progress}%
                        </span>
                        <span className="block text-sm text-muted-foreground">
                          Progress
                        </span>
                      </span>
                      <span className="w-20 text-center sm:w-24">
                        <span
                          className={cn(
                            "block text-2xl font-light tabular-nums",
                            candidate.grade == null && "text-muted-foreground"
                          )}
                        >
                          {candidate.grade == null ? "—" : `${candidate.grade}%`}
                        </span>
                        <span className="block text-sm text-muted-foreground">
                          Grade
                        </span>
                      </span>
                      <span className="flex justify-end sm:w-32">
                        <Badge
                          variant="outline"
                          className="h-7 px-3 text-sm font-light capitalize"
                        >
                          {candidate.status.replace("_", " ")}
                        </Badge>
                      </span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : (
        interview.topics.length > 0 && (
          <ul className="divide-y rounded-2xl border">
              {interview.topics.map((topic) => (
                <li
                  key={topic.id}
                  className="flex flex-wrap items-center justify-between gap-4 p-4 sm:p-6"
                >
                  <span className="min-w-0 space-y-2">
                    <span className="block text-lg font-medium">{topic.title}</span>
                    {topic.subtopics.length > 0 && (
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
                    )}
                  </span>
                  <TopicQuestionLimit
                    title={topic.title}
                    count={topic.question_count}
                    path={`/companies/interviews/${id}/topics/${topic.id}/questions`}
                    regeneratePath={`/companies/interviews/${id}/questions`}
                    reportsPath={`/companies/interviews/${id}/questions`}
                    limit={topic.question_limit}
                    limitPath={`/companies/interviews/${id}/topics/${topic.id}/limit`}
                    caption="per session"
                  />
                </li>
              ))}
          </ul>
        )
      )}
    </main>
  )
}
