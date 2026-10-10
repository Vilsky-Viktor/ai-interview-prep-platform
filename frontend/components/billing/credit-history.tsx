"use client"

import { useTranslations } from "next-intl"

import { HistoryRow } from "@/components/billing/history-row"
import { VirtualList } from "@/components/virtual-list"
import { LIST_BOX } from "@/constants/lists"
import { usePagedList } from "@/hooks/use-paged-list"
import type { CreditHistoryEntry } from "@/types/company"

function byId(entry: CreditHistoryEntry) {
  return entry.id
}

/** Every movement of a company's credits, newest first, a page at a time; `initial` is the
 * server's first page. */
export function CreditHistory({
  companyId,
  initial,
}: {
  companyId: string
  initial: CreditHistoryEntry[]
}) {
  const t = useTranslations("companyBilling")
  const { items, loadMore } = usePagedList(
    `/companies/companies/${companyId}/billing/history`,
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
      estimateSize={105}
      onEndReached={loadMore}
      className={LIST_BOX}
      renderItem={(entry) => <HistoryRow companyId={companyId} entry={entry} />}
    />
  )
}
