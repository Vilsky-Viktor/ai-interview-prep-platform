"use client"

import { cn } from "cn"
import Link from "next/link"
import { useLocale, useTranslations } from "next-intl"

import { CandidateSignals } from "@/components/company/candidate-signals"
import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { byId } from "@/lib/paged-list"
import { formatDate } from "@/lib/format"
import { gradeTone } from "@/lib/grade-tone"
import type { Candidate } from "@/types/company"

/** An interview's candidates, a page at a time, from `path` (the API list with its sort and
filters); `initial` is the server's first page. `narrowed` when a search or filter is on. */
export function CandidateList({
  path,
  interviewHref,
  narrowed,
  initial,
}: {
  path: string
  interviewHref: string
  narrowed: boolean
  initial: Candidate[]
}) {
  const t = useTranslations("candidates")
  const statuses = useTranslations("candidateStatus")
  const locale = useLocale()
  const { items, loadMore } = usePagedList(path, byId, initial)

  if (items.length === 0) {
    return (
      <p className="py-16 text-center text-muted-foreground">
        {" "}
        {narrowed ? t("noMatches") : t("empty")}
      </p>
    )
  }

  return (
    <VirtualList
      items={items}
      getKey={byId}
      estimateSize={97}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(candidate) => (
        <Link
          href={`${interviewHref}/candidates/${candidate.id}`}
          className="flex flex-col gap-4 p-4 transition-colors hover:bg-muted/50 sm:flex-row sm:items-center sm:justify-between sm:p-6"
        >
          <span className="min-w-0 space-y-1">
            <span className="block text-lg font-medium break-all">
              {candidate.status === "deleted" ? t("deleted") : candidate.email}
            </span>
            <span className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
              <time dateTime={candidate.created_at} suppressHydrationWarning>
                {formatDate(candidate.created_at, locale)}
              </time>
              <CandidateSignals candidate={candidate} />
            </span>
          </span>
          <span className="flex shrink-0 items-center gap-6 sm:gap-10">
            <span className="w-20 text-center sm:w-24">
              <span className="block text-2xl font-light tabular-nums">
                {candidate.progress}%
              </span>
              <span className="block text-sm text-muted-foreground">
                {t("progress")}
              </span>
            </span>
            <span className="w-20 text-center sm:w-24">
              <span
                className={cn(
                  "block text-2xl font-light tabular-nums",
                  candidate.grade == null && "text-muted-foreground",
                  gradeTone(candidate.passed)
                )}
              >
                {candidate.grade == null ? "—" : `${candidate.grade}%`}
              </span>
              <span className="block text-sm text-muted-foreground">
                {t("grade")}
              </span>
            </span>
            <span className="flex justify-end sm:w-32">
              <Badge
                variant={
                  candidate.status === "undelivered" ? "destructive" : "outline"
                }
                className="h-7 px-3 text-sm font-light"
              >
                {statuses(candidate.status)}
              </Badge>
            </span>
          </span>
        </Link>
      )}
    />
  )
}
