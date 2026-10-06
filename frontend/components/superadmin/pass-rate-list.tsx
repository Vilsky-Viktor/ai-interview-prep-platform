"use client"

import { useTranslations } from "next-intl"

import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import type { PassRate } from "@/types/superadmin"

function rowKey(row: PassRate) {
  return row.interview_id
}

/** Company interviews with finished candidates, a page at a time in the API's order: the
 * interview and its company, how many finished, and how they did. The API marks those outside
 * the monitoring plan's triggers. */
export function PassRateList({
  path,
  initial,
}: {
  path: string
  initial: PassRate[]
}) {
  const t = useTranslations("superadmin")
  const interviews = useTranslations("interviews")
  const { items, loadMore } = usePagedList<PassRate>(path, rowKey, initial)

  if (items.length === 0) {
    return (
      <p className="py-10 text-center text-muted-foreground">
        {t("noPassRates")}
      </p>
    )
  }

  return (
    <VirtualList
      items={items}
      getKey={rowKey}
      estimateSize={120}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(row) => (
        <div className="flex items-center gap-6 p-6">
          <div className="min-w-0 flex-1 space-y-1">
            <p className="text-lg font-medium">
              {row.title ?? interviews("fallbackTitle")}
            </p>
            <p className="text-sm text-muted-foreground">{row.company}</p>
          </div>
          <div className="flex shrink-0 flex-col items-end gap-2 text-sm text-muted-foreground tabular-nums">
            {row.outside_triggers && (
              <Badge variant="outline" className="h-7 px-3 text-sm font-light">
                {t("outsideTriggers")}
              </Badge>
            )}
            <span>
              {t("finished", { count: row.finished })} ·{" "}
              {t("passed", { percent: row.pass_rate })}
            </span>
            <span>
              {t("passMark", { percent: row.pass_mark })} ·{" "}
              {t("averageGrade", { percent: row.average_grade })}
            </span>
            {row.timeout_share !== null && (
              <span>{t("timedOut", { percent: row.timeout_share })}</span>
            )}
          </div>
        </div>
      )}
    />
  )
}
