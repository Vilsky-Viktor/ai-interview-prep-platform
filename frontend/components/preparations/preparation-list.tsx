import { cn } from "cn"
import { UserRoundIcon } from "lucide-react"
import Link from "next/link"

import { DoneBadge } from "@/components/preparations/done-badge"
import { PreparationStats } from "@/components/preparations/preparation-stats"
import { Badge } from "@/components/ui/badge"
import { formatDate, plural } from "@/lib/format"
import type { PreparationSummary } from "@/types/preparation"

type ListedPreparation = PreparationSummary & { owned?: boolean; done?: boolean }

export function PreparationList({
  preparations,
  className,
}: {
  preparations: ListedPreparation[]
  className?: string
}) {
  return (
    <ul className="divide-y rounded-2xl border">
      {preparations.map((preparation) => (
        <li key={preparation.id}>
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
                {preparation.done && <DoneBadge />}
              </span>
              <span className="block text-sm text-muted-foreground">
                {plural(preparation.topic_count, "topic")} ·{" "}
                {formatDate(preparation.created_at)}
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
        </li>
      ))}
    </ul>
  )
}
