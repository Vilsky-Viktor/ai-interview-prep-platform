"use client"

import Link from "next/link"
import { useLocale, useTranslations } from "next-intl"

import { CancelGeneration } from "@/components/generation/cancel-generation"
import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { formatDate } from "@/lib/format"
import type { GenerationSummary } from "@/types/generation"

// A failure shows as an error; every other status is neutral.
const BADGE_VARIANTS = {
  queued: "secondary",
  running: "secondary",
  awaiting_review: "secondary",
  done: "secondary",
  failed: "destructive",
  cancelled: "secondary",
} as const

/** Generations still running, waiting for topic review, or failed, so they stay reachable. */
export function UnfinishedGenerations({
  generations,
}: {
  // The first page, already rendered by the server; the rest load as the user scrolls.
  generations: GenerationSummary[]
}) {
  const t = useTranslations("generation")
  const statuses = useTranslations("generationStatus")
  const locale = useLocale()
  const { items, loadMore } = usePagedList("/generate/generations", generations)

  return (
    <section className="space-y-3">
      <h2 className="text-sm font-medium text-muted-foreground">
        {t("unfinished")}
      </h2>
      <VirtualList
        items={items}
        getKey={(generation) => generation.id}
        estimateSize={97}
        onEndReached={loadMore}
        className="divide-y rounded-2xl border"
        renderItem={(generation) => (
          // One hover surface: the link stretches over the whole row, Cancel sits on top of it.
          <div className="relative flex items-center gap-4 p-4 transition-colors hover:bg-muted/50 sm:p-6">
            <Link
              href={`/generate/${generation.id}`}
              className="flex min-w-0 flex-1 flex-col items-start gap-3 after:absolute after:inset-0 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
            >
              <span className="min-w-0 space-y-1">
                <span className="line-clamp-2 block font-medium">
                  {generation.preview}
                </span>
                <span className="block text-sm text-muted-foreground">
                  <time
                    dateTime={generation.created_at}
                    suppressHydrationWarning
                  >
                    {formatDate(generation.created_at, locale)}
                  </time>
                </span>
              </span>
              <Badge
                variant={BADGE_VARIANTS[generation.status]}
                className="h-7 shrink-0 px-3 text-sm font-light"
              >
                {statuses(generation.status)}
              </Badge>
            </Link>
            <div className="relative z-10 shrink-0">
              <CancelGeneration
                path={`/generate/generations/${generation.id}`}
                leaveTo="/preparations"
                iconOnly
              />
            </div>
          </div>
        )}
      />
    </section>
  )
}
