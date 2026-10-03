"use client"

import { useLocale, useTranslations } from "next-intl"

import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate } from "@/lib/format"
import type { QuestionReport } from "@/types/feedback"

/** A question's reports in their own scroll box, loading more as the user scrolls it. */
export function QuestionReports({ path }: { path: string }) {
  const t = useTranslations("questions")
  const common = useTranslations("common")
  const reasons = useTranslations("reportReasons")
  const locale = useLocale()
  const { items, loaded, loadMore } = usePagedList<QuestionReport>(path)

  if (!loaded) {
    return <p className="text-sm text-muted-foreground">{common("loading")}</p>
  }

  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("noReports")}</p>
  }

  return (
    <VirtualList
      items={items}
      getKey={(report) => report.id}
      estimateSize={52}
      onEndReached={loadMore}
      scrollClassName="max-h-64 overflow-y-auto"
      renderItem={(report) => (
        <div className="space-y-1 pb-3 text-sm">
          <p className="flex flex-wrap items-baseline justify-between gap-2">
            <span className="font-medium">
              {reasons.has(report.reason)
                ? reasons(report.reason)
                : report.reason}
            </span>
            <span className="text-muted-foreground">
              {formatDate(report.created_at, locale)}
            </span>
          </p>
          {report.comment && (
            <p className="font-light whitespace-pre-line text-muted-foreground">
              {report.comment}
            </p>
          )}
        </div>
      )}
    />
  )
}
