"use client"

import { UsersIcon } from "lucide-react"
import Link from "next/link"
import { useLocale, useTranslations } from "next-intl"

import { DeleteInterview } from "@/components/company/delete-interview"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate } from "@/lib/format"
import type { Interview } from "@/types/company"

/** A company's interviews, newest first, a page at a time; `initial` is the server's first page. */
export function InterviewList({
  companyId,
  initial,
}: {
  companyId: string
  initial: Interview[]
}) {
  const t = useTranslations("interviews")
  const locale = useLocale()
  const { items, loadMore } = usePagedList(
    `/companies/interviews?company_id=${companyId}`,
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
      getKey={(interview) => interview.id}
      estimateSize={89}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(interview) => (
        // One hover surface: the link stretches over the whole row, Delete sits on top of it.
        <div className="relative flex items-center gap-2 p-6 pr-3 transition-colors hover:bg-muted/50">
          <Link
            href={`/company/${companyId}/interviews/${interview.id}`}
            className="flex min-w-0 flex-1 items-center justify-between gap-4 after:absolute after:inset-0"
          >
            <span className="min-w-0 space-y-1">
              <span className="block text-lg font-medium">
                {interview.title ?? t("generating")}
              </span>
              <span className="block text-sm text-muted-foreground">
                <time dateTime={interview.created_at} suppressHydrationWarning>
                  {formatDate(interview.created_at, locale)}
                </time>
              </span>
            </span>
            <span
              className="flex shrink-0 items-center gap-1.5 text-sm text-muted-foreground tabular-nums"
              aria-label={t("candidateCount", {
                count: interview.candidate_count,
              })}
            >
              <UsersIcon aria-hidden className="size-5" />
              {interview.candidate_count}
            </span>
          </Link>
          {/* Still generating: cancelling it, on its page, is the way to remove it. */}
          {interview.set_id && (
            <div className="relative z-10">
              <DeleteInterview
                interviewId={interview.id}
                title={interview.title ?? t("fallbackTitle")}
              />
            </div>
          )}
        </div>
      )}
    />
  )
}
