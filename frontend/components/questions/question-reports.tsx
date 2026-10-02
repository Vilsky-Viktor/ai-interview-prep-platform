"use client"

import { VirtualList } from "@/components/virtual-list"
import { REPORT_REASONS } from "@/constants/feedback"
import { usePagedList } from "@/hooks/use-paged-list"
import type { QuestionReport } from "@/types/feedback"

/** A question's reports in their own scroll box, loading more as the user scrolls it. */
export function QuestionReports({ path }: { path: string }) {
  const { items, loaded, loadMore } = usePagedList<QuestionReport>(path)

  if (!loaded) {
    return <p className="text-sm text-muted-foreground">Loading…</p>
  }

  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">No reports.</p>
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
              {REPORT_REASONS[report.reason as keyof typeof REPORT_REASONS] ??
                report.reason}
            </span>
            <span className="text-muted-foreground">
              {new Date(report.created_at).toLocaleDateString(undefined, {
                dateStyle: "medium",
              })}
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
