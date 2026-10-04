import Link from "next/link"
import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { CandidateList } from "@/components/company/candidate-list"
import { CandidateSortMenu } from "@/components/company/candidate-sort"
import { DeleteInterview } from "@/components/company/delete-interview"
import { InterviewNav } from "@/components/company/interview-nav"
import { EditableTitle } from "@/components/editable-title"
import { InterviewSettings } from "@/components/company/interview-settings"
import { InviteCandidate } from "@/components/company/invite-candidate"
import { PageHeader } from "@/components/page-header"
import { SubtopicList } from "@/components/questions/subtopic-list"
import { TopicQuestionLimit } from "@/components/questions/topic-question-limit"
import { Button } from "@/components/ui/button"
import { CANDIDATE_SORTS } from "@/constants/interviews"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Candidate, InterviewDetail } from "@/types/company"

export const generateMetadata = () => translatedTitle("interviews", "interview")

export default async function InterviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ companyId: string; id: string }>
  searchParams: Promise<{ tab?: string; sort?: string }>
}) {
  const { companyId, id } = await params
  const { tab, sort: asked } = await searchParams
  const sort =
    CANDIDATE_SORTS.find((option) => option === asked) ?? CANDIDATE_SORTS[0]
  const t = await getTranslations("interviews")
  const [interview, candidates] = await Promise.all([
    serverFetch<InterviewDetail>(`/companies/interviews/${id}`),
    // The first page renders on the server; the rest load as the user scrolls.
    serverFetch<Candidate[]>(
      `/companies/interviews/${id}/candidates?sort=${sort}&limit=${PAGE_SIZE}`
    ),
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
          back={<BackLink href={interviewsHref}>{t("title")}</BackLink>}
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
                    {t("generating")}
                  </h1>
                )}
              </div>
              {ready && (
                <DeleteInterview
                  interviewId={interview.id}
                  title={interview.title ?? t("fallbackTitle")}
                  leaveTo={interviewsHref}
                />
              )}
              <InterviewSettings
                interviewId={interview.id}
                questionSeconds={interview.question_seconds}
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
              {t("continueGeneration")}
            </Button>
          )}
        </PageHeader>
        {ready && <InterviewNav href={interviewHref} current={current} />}
      </div>

      {current === "candidates" ? (
        <div className="space-y-6">
          {/* The invite takes the row; the sort sits at its end, and wraps under it on phones. */}
          <div className="flex flex-wrap items-center justify-end gap-3">
            <div className="min-w-64 flex-1">
              <InviteCandidate interviewId={interview.id} />
            </div>
            <CandidateSortMenu current={sort} />
          </div>
          <CandidateList
            interviewId={id}
            interviewHref={interviewHref}
            sort={sort}
            initial={candidates ?? []}
          />
        </div>
      ) : (
        interview.topics.length > 0 && (
          <ul className="divide-y rounded-2xl border">
            {interview.topics.map((topic) => (
              <li
                key={topic.id}
                className="flex items-center justify-between gap-8 p-4 sm:p-6"
              >
                <span className="min-w-0 space-y-2">
                  <span className="block text-lg font-medium">
                    {topic.title}
                  </span>
                  <SubtopicList subtopics={topic.subtopics} />
                </span>
                <TopicQuestionLimit
                  title={topic.title}
                  count={topic.question_count}
                  path={`/companies/interviews/${id}/topics/${topic.id}/questions`}
                  regeneratePath={`/companies/interviews/${id}/questions`}
                  reportsPath={`/companies/interviews/${id}/questions`}
                  limit={topic.question_limit}
                  limitPath={`/companies/interviews/${id}/topics/${topic.id}/limit`}
                  caption={t("perSession")}
                />
              </li>
            ))}
          </ul>
        )
      )}
    </main>
  )
}
