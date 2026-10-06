"use client"

import { MemberRow } from "@/components/company/member-row"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import type { CompanyMember } from "@/types/company"

/** A company's owner and admins, a page at a time; `initial` is the server's first page. */
export function MemberList({
  companyId,
  initial,
}: {
  companyId: string
  initial: CompanyMember[]
}) {
  const { items, setItems, loadMore } = usePagedList(
    `/companies/members?company_id=${companyId}`,
    initial
  )

  return (
    <VirtualList
      items={items}
      getKey={(member) => member.email}
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
