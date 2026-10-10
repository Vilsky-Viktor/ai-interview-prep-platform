"use client"

import Link from "next/link"

import { NoName } from "@/components/company/no-name"
import { VirtualList } from "@/components/virtual-list"
import { LIST_BOX } from "@/constants/lists"
import { usePagedList } from "@/hooks/use-paged-list"
import type { CreditCandidate } from "@/types/company"

function byInvite(candidate: CreditCandidate) {
  return candidate.invite_id
}

/** Candidates invited who haven't finished, whose credits are set aside, newest first; each
 * opens the candidate. `initial` is the server's first page. */
export function ReservedList({
  companyId,
  initial,
}: {
  companyId: string
  initial: CreditCandidate[]
}) {
  const { items, loadMore } = usePagedList(
    `/companies/companies/${companyId}/billing/reserved`,
    byInvite,
    initial
  )

  return (
    <VirtualList
      items={items}
      getKey={byInvite}
      estimateSize={105}
      onEndReached={loadMore}
      className={LIST_BOX}
      renderItem={(candidate) => (
        <Link
          href={`/companies/${companyId}/interviews/${candidate.interview_id}/candidates/${candidate.invite_id}`}
          className="block space-y-1 p-6 transition-colors hover:bg-muted/50 active:bg-muted/50"
        >
          <span className="block text-lg font-medium break-all">
            {candidate.email}
          </span>
          <span className="block text-sm break-all text-muted-foreground">
            {candidate.name ?? <NoName hint="list" />}
            {candidate.interview_title && (
              <span className="normal-case">
                {` · ${candidate.interview_title}`}
              </span>
            )}
          </span>
        </Link>
      )}
    />
  )
}
