"use client"

import { cn } from "cn"
import { UserRoundIcon } from "lucide-react"
import Link from "next/link"
import type { ReactNode } from "react"

import { DoneBadge } from "@/components/preparations/done-badge"
import { PreparationStats } from "@/components/preparations/preparation-stats"
import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate, plural } from "@/lib/format"
import { isPreparationDone } from "@/lib/rounds"
import type { PreparationSummary } from "@/types/preparation"

type ListedPreparation = PreparationSummary & { owned?: boolean }

type PreparationListProps = {
  // Where pages come from; `initial` is the first page, already rendered by the server.
  path: string
  initial: ListedPreparation[]
  // Mastered topics per preparation, to mark finished ones (my preparations only).
  mastered?: Record<string, number>
  className?: string
  empty: ReactNode
}

export function PreparationList({
  path,
  initial,
  mastered,
  className,
  empty,
}: PreparationListProps) {
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
        const done =
          mastered !== undefined &&
          isPreparationDone(
            preparation.topic_count,
            mastered[preparation.id] ?? 0
          )

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
                    aria-label="Owner"
                    className="text-muted-foreground"
                  >
                    <UserRoundIcon className="size-5" />
                  </span>
                )}
                {done && <DoneBadge />}
              </span>
              <span className="block text-sm text-muted-foreground">
                {plural(preparation.topic_count, "topic")} ·{" "}
                <time
                  dateTime={preparation.created_at}
                  suppressHydrationWarning
                >
                  {formatDate(preparation.created_at)}
                </time>
              </span>
            </span>
            <span className="flex shrink-0 items-center gap-4">
              <PreparationStats preparation={preparation} />
              <Badge
                variant="secondary"
                className="h-7 px-3 text-sm font-light capitalize"
              >
                {preparation.level}
              </Badge>
            </span>
          </Link>
        )
      }}
    />
  )
}
