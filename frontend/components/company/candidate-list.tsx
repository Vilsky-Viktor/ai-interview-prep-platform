"use client"

import { useTranslations } from "next-intl"

import { CandidateRow } from "@/components/company/candidate-row"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { byId } from "@/lib/paged-list"
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
        <CandidateRow
          candidate={candidate}
          href={`${interviewHref}/candidates/${candidate.id}`}
        />
      )}
    />
  )
}
