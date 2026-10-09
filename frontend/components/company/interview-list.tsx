"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { DeleteInterview } from "@/components/company/delete-interview"
import { InterviewSummary } from "@/components/company/interview-summary"
import { TryInterview } from "@/components/company/try-interview"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { byId } from "@/lib/paged-list"
import type { Interview } from "@/types/company"
import { LIST_BOX } from "@/constants/lists"

/** A company's interviews, newest first, a page at a time; `initial` is the server's first page. */
export function InterviewList({
  companyId,
  initial,
  canEdit,
}: {
  companyId: string
  initial: Interview[]
  // Viewers preview a test but don't delete it.
  canEdit: boolean
}) {
  const t = useTranslations("interviews")
  const { items, loadMore } = usePagedList(
    `/companies/interviews?company_id=${companyId}`,
    byId,
    initial
  )

  if (items.length === 0) {
    return (
      <p className="py-16 text-center text-muted-foreground">{t("empty")}</p>
    )
  }

  return (
    <VirtualList
      items={items}
      getKey={byId}
      estimateSize={89}
      onEndReached={loadMore}
      className={LIST_BOX}
      renderItem={(interview) => (
        // One hover surface: the link stretches over the whole row, Delete sits on top of it.
        // Phones show the title and date, without the status, counts and preview button.
        <div className="relative flex items-center gap-2 p-6 pe-3 transition-colors hover:bg-muted/50 active:bg-muted/50">
          <Link
            href={`/companies/${companyId}/interviews/${interview.id}`}
            className="flex min-w-0 flex-1 items-center justify-between gap-4 after:absolute after:inset-0 max-sm:[&_[data-slot=interview-stats]]:hidden"
          >
            <InterviewSummary
              title={
                interview.title ??
                (interview.generation_failed
                  ? t("generationFailed")
                  : t("generating"))
              }
              createdAt={interview.created_at}
              // Still generating: no status yet.
              status={interview.set_id ? interview.status : null}
              candidateCount={interview.candidate_count}
            />
          </Link>
          {/* Still generating: cancelling it, on its page, is the way to remove it. */}
          {interview.set_id && (
            <div className="relative z-10 flex">
              <TryInterview
                companyId={companyId}
                interviewId={interview.id}
                title={interview.title ?? t("fallbackTitle")}
                className="max-sm:hidden"
              />
              {canEdit && (
                <DeleteInterview
                  interviewId={interview.id}
                  title={interview.title ?? t("fallbackTitle")}
                />
              )}
            </div>
          )}
        </div>
      )}
    />
  )
}
