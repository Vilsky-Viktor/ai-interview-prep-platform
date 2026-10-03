"use client"

import { useTranslations } from "next-intl"

import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import type { Share } from "@/types/sharing"

/** Who a preparation was shared with, in its own scroll box, loading more as it scrolls. */
export function ShareList({ path }: { path: string }) {
  const t = useTranslations("share")
  const { items, loadMore } = usePagedList<Share>(path)

  if (items.length === 0) {
    return null
  }

  return (
    <VirtualList
      items={items}
      getKey={(share) => share.email}
      estimateSize={64}
      onEndReached={loadMore}
      scrollClassName="max-h-72 overflow-y-auto"
      renderItem={(share) => (
        <div className="pb-2">
          <div className="flex items-center justify-between gap-2 rounded-lg bg-black/5 px-5 py-4 dark:bg-black/40">
            <span className="truncate">{share.email}</span>
            {share.accepted ? (
              <Badge variant="secondary">{t("joined")}</Badge>
            ) : share.undelivered ? (
              <Badge variant="destructive">{t("undelivered")}</Badge>
            ) : (
              <Badge variant="outline">{t("invited")}</Badge>
            )}
          </div>
        </div>
      )}
    />
  )
}
