"use client"

import { cn } from "cn"
import { UserRoundIcon } from "lucide-react"
import Link from "next/link"
import { useLocale, useTranslations } from "next-intl"
import type { ReactNode } from "react"

import { DoneBadge } from "@/components/preparations/done-badge"
import { PreparationStats } from "@/components/preparations/preparation-stats"
import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate } from "@/lib/format"
import type { PreparationSummary } from "@/types/preparation"

// My preparations carry whether the user owns each one and has mastered every topic.
type ListedPreparation = PreparationSummary & {
  owned?: boolean
  done?: boolean
}

type PreparationListProps = {
  // Where pages come from; `initial` is the first page, already rendered by the server.
  path: string
  initial: ListedPreparation[]
  className?: string
  empty: ReactNode
}

export function PreparationList({
  path,
  initial,
  className,
  empty,
}: PreparationListProps) {
  const t = useTranslations("preparations")
  const levels = useTranslations("levels")
  const locale = useLocale()
  const { items, loadMore } = usePagedList(path, initial)

  if (items.length === 0) {
    return empty
  }

  return (
    <VirtualList
      items={items}
      getKey={(preparation) => preparation.id}
      estimateSize={97}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(preparation) => {
        return (
          <Link
            href={`/preparations/${preparation.id}`}
            className={cn(
              "flex flex-col items-start gap-3 p-4 transition-colors hover:bg-muted/50 sm:flex-row sm:items-center sm:justify-between sm:gap-4",
              className
            )}
          >
            <span className="space-y-1">
              <span className="flex items-center gap-2">
                <span className="text-lg font-medium">{preparation.title}</span>
                {preparation.owned && (
                  <span
                    role="img"
                    aria-label={t("owner")}
                    className="text-muted-foreground"
                  >
                    <UserRoundIcon className="size-5" />
                  </span>
                )}
                {preparation.done && <DoneBadge />}
              </span>
              <span className="block text-sm text-muted-foreground">
                {t("topics", { count: preparation.topic_count })} ·{" "}
                <time
                  dateTime={preparation.created_at}
                  suppressHydrationWarning
                >
                  {formatDate(preparation.created_at, locale)}
                </time>
              </span>
            </span>
            <span className="flex shrink-0 items-center gap-4">
              <PreparationStats preparation={preparation} />
              <Badge
                variant="secondary"
                className="h-7 px-3 text-sm font-light capitalize"
              >
                {levels(preparation.level)}
              </Badge>
            </span>
          </Link>
        )
      }}
    />
  )
}
