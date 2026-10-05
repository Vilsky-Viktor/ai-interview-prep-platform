import Link from "next/link"
import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { CandidatesReport } from "@/components/company/candidates-report"
import { CandidateList } from "@/components/company/candidate-list"
import { CandidateSearch } from "@/components/company/candidate-search"
import { DeleteInterview } from "@/components/company/delete-interview"
import { InterviewNav } from "@/components/company/interview-nav"
import { TryInterview } from "@/components/company/try-interview"
import { EditableTitle } from "@/components/editable-title"
import { InterviewSettings } from "@/components/company/interview-settings"
import { InterviewStatus } from "@/components/company/interview-status"
import { InviteCandidate } from "@/components/company/invite-candidate"
import { ShareLink } from "@/components/company/share-link"
import { SuggestedTalents } from "@/components/company/suggested-talents"
import { PageHeader } from "@/components/page-header"
import { SubtopicList } from "@/components/questions/subtopic-list"
import { TopicQuestionLimit } from "@/components/questions/topic-question-limit"
import { TopicQuestions } from "@/components/questions/topic-questions"
import { Button } from "@/components/ui/button"
import { CANDIDATE_SORTS } from "@/constants/interviews"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type {
  Candidate,
  CandidateFilters,
  InterviewDetail,
} from "@/types/company"

export const generateMetadata = () => translatedTitle("interviews", "interview")

export default async function InterviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ companyId: string; id: string }>
  searchParams: Promise<{
    tab?: string
    sort?: string
    q?: string
    status?: string
  }>
}) {
  const { companyId, id } = await params
  const { tab, sort: asked, q, status: askedStatus } = await searchParams
  const sort =
    CANDIDATE_SORTS.find((option) => option === asked) ?? CANDIDATE_SORTS[0]
  const t = await getTranslations("interviews")
  const filters = await serverFetch<CandidateFilters>(
    "/companies/interviews/candidates/filters"
  )
  // Only what the API offers; anything else in the address is ignored.
  const status =
    filters?.filters.find((option) => option === askedStatus) ?? null
  const search = q?.trim() ?? ""
  const query = new URLSearchParams({ sort })

  if (search) {
    query.set("q", search)
  }

  if (status) {
    query.set("status", status)
  }

  const candidatesPath = `/companies/interviews/${id}/candidates?${query}`
  const [interview, candidates] = await Promise.all([
    serverFetch<InterviewDetail>(`/companies/interviews/${id}`),
    // The first page renders on the server; the rest load as the user scrolls.
    serverFetch<Candidate[]>(`${candidatesPath}&limit=${PAGE_SIZE}`),
  ])

  if (!interview) {
    notFound()
  }

  const interviewsHref = `/company/${companyId}/interviews`
  const interviewHref = `${interviewsHref}/${id}`
  const ready = Boolean(interview.set_id)
  const current =
    ready && (tab === "candidates" || tab === "talents") ? tab : "topics"

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="space-y-6">
        <PageHeader
          back={<BackLink href={interviewsHref}>{t("title")}</BackLink>}
          tags={ready && <InterviewStatus status={interview.status} />}
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
              {/* The test's own actions sit on its tab; inviting, on the candidates tab. The
                  buttons overhang the title's line, so the row is as tall as the title on every
                  tab: switching tabs doesn't move the page. */}
              <div className="-my-1.5 flex shrink-0 items-center gap-4">
                {current === "topics" ? (
                  <>
                    {ready && (
                      <TryInterview
                        companyId={companyId}
                        interviewId={interview.id}
                        title={interview.title ?? t("fallbackTitle")}
                      />
                    )}
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
                      passMark={interview.pass_mark}
                      hired={interview.hired}
                    />
                  </>
                ) : (
                  current === "candidates" && (
                    <>
                      <CandidatesReport interviewId={interview.id} />
                      <InviteCandidate
                        interviewId={interview.id}
                        candidatesHref={`${interviewHref}?tab=candidates`}
                      />
                    </>
                  )
                )}
              </div>
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

      {current === "talents" ? (
        <SuggestedTalents interviewId={interview.id} />
      ) : current === "candidates" ? (
        <div className="space-y-6">
          <ShareLink
            interviewId={interview.id}
            linkToken={interview.link_token}
          />
          <CandidateSearch
            action={interviewHref}
            sort={sort}
            q={search}
            status={status}
            filters={filters?.filters ?? []}
          />
          <CandidateList
            path={candidatesPath}
            interviewHref={interviewHref}
            narrowed={Boolean(search || status)}
            initial={candidates ?? []}
          />
        </div>
      ) : (
        interview.topics.length > 0 && (
          <ul className="divide-y rounded-2xl border">
            {interview.topics.map((topic) => (
              <li
                key={topic.id}
                className="flex items-center justify-between gap-6 p-4 sm:p-6"
              >
                <span className="max-w-3xl min-w-0 space-y-3">
                  <span className="block text-lg font-medium">
                    {topic.title}
                  </span>
                  <SubtopicList subtopics={topic.subtopics} />
                </span>
                <span className="flex shrink-0 flex-col items-center gap-3">
                  <TopicQuestions
                    title={topic.title}
                    path={`/companies/interviews/${id}/topics/${topic.id}/questions`}
                    regeneratePath={`/companies/interviews/${id}/questions`}
                    wrongPath={`/companies/interviews/${id}/questions`}
                    reportsPath={`/companies/interviews/${id}/questions`}
                  />
                  <TopicQuestionLimit
                    count={topic.question_count}
                    limit={topic.question_limit}
                    limitPath={`/companies/interviews/${id}/topics/${topic.id}/limit`}
                  />
                </span>
              </li>
            ))}
          </ul>
        )
      )}
    </main>
  )
}
