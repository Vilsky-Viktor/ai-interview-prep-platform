"use client"

import { cn } from "cn"
import Link from "next/link"
import { useLocale, useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate } from "@/lib/format"
import type { Balance, Entry } from "@/types/billing"

/** The learner's balance, a way to top up, and the history of every credit in and out. */
export function Credits({ balance }: { balance: Balance }) {
  const t = useTranslations("credits")
  const billing = useTranslations("billing")
  const locale = useLocale()
  const { items, loaded, loadMore } = usePagedList<Entry>("/billing/me/history")

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <p className="text-base">
          <span className="font-heading text-3xl font-medium tabular-nums">
            {balance.available}
          </span>{" "}
          <span className="text-muted-foreground">
            {t("available")}
            {balance.reserved > 0 &&
              ` · ${t("reserved", { count: balance.reserved })}`}
          </span>
        </p>
        <Button
          variant="outline"
          className="h-10 px-5"
          render={<Link href="/top-up" />}
          nativeButton={false}
        >
          {billing("topUp")}
        </Button>
      </div>

      <div className="space-y-3">
        <h3 className="font-medium">{t("history")}</h3>
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
                    <span className="text-muted-foreground">
                      {" "}
                      · {entry.note}
                    </span>
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
    </div>
  )
}
