"use client"

import { MemberRow } from "@/components/company/member-row"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import type { CompanyMember } from "@/types/company"

function byEmail(member: CompanyMember) {
  return member.email
}

/** A company's owner, admins and viewers, a page at a time; `initial` is the server's first page. */
export function MemberList({
  companyId,
  initial,
}: {
  companyId: string
  initial: CompanyMember[]
}) {
  const { items, setItems, loadMore } = usePagedList(
    `/companies/members?company_id=${companyId}`,
    byEmail,
    initial
  )

  return (
    <VirtualList
      items={items}
      getKey={byEmail}
      estimateSize={89}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(member) => (
        <MemberRow
          companyId={companyId}
          member={member}
          onRemoved={() =>
            setItems((current) =>
              current.filter((item) => item.id !== member.id)
            )
          }
        />
      )}
    />
  )
}
