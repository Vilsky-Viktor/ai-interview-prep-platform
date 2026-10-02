"use client"

import { UsersIcon } from "lucide-react"
import Link from "next/link"

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
  const { items, loadMore } = usePagedList(
    `/companies/interviews?company_id=${companyId}`,
    initial
  )

  if (items.length === 0) {
    return (
      <p className="py-16 text-center text-muted-foreground">
        No interviews yet. Create your first one.
      </p>
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
        <Link
          href={`/company/${companyId}/interviews/${interview.id}`}
          className="flex items-center justify-between gap-4 p-6 transition-colors hover:bg-muted/50"
        >
          <span className="space-y-1">
            <span className="block text-lg font-medium">
              {interview.title ?? "Generating…"}
            </span>
            <span className="block text-sm text-muted-foreground">
              <time dateTime={interview.created_at} suppressHydrationWarning>
                {formatDate(interview.created_at)}
              </time>
            </span>
          </span>
          <span className="flex shrink-0 items-center gap-4">
            <span
              className="flex items-center gap-1.5 text-sm text-muted-foreground tabular-nums"
              aria-label={`${interview.candidate_count} candidates`}
            >
              <UsersIcon aria-hidden className="size-5" />
              {interview.candidate_count}
            </span>
          </span>
        </Link>
      )}
    />
  )
}
