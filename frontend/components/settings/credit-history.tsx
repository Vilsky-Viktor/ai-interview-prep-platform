"use client"

import { cn } from "cn"
import { useLocale, useTranslations } from "next-intl"

import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate } from "@/lib/format"
import type { Entry } from "@/types/billing"

/** Every credit in and out of the learner's wallet, newest first. */
export function CreditHistory() {
  const t = useTranslations("credits")
  const billing = useTranslations("billing")
  const locale = useLocale()
  const { items, loaded, loadMore } = usePagedList<Entry>("/billing/me/history")

  return (
    <div className="space-y-3">
      {loaded && items.length === 0 && (
        <p className="text-sm text-muted-foreground">{t("noHistory")}</p>
      )}
      <VirtualList
        items={items}
        getKey={(entry) =>
          `${entry.created_at}:${entry.reason}:${entry.amount}`
        }
        estimateSize={56}
        onEndReached={loadMore}
        scrollClassName="max-h-96 overflow-y-auto"
        className="divide-y rounded-xl border"
        renderItem={(entry) => (
          <div className="flex items-center justify-between gap-4 px-5 py-3 text-sm">
            <span className="min-w-0">
              <span className="block">
                {t.has(`reasons.${entry.reason}`)
                  ? t(`reasons.${entry.reason}`)
                  : entry.reason}
                {entry.note && (
                  <span className="text-muted-foreground"> · {entry.note}</span>
                )}
              </span>
              <time
                dateTime={entry.created_at}
                className="block text-muted-foreground"
                suppressHydrationWarning
              >
                {formatDate(entry.created_at, locale)}
              </time>
            </span>
            <span
              className={cn(
                "shrink-0 font-medium tabular-nums",
                entry.amount > 0 && "text-green-600 dark:text-green-400"
              )}
            >
              {entry.amount > 0 ? "+" : "−"}
              {billing("credits", { count: Math.abs(entry.amount) })}
            </span>
          </div>
        )}
      />
    </div>
  )
}
