import { cn } from "cn"
import { StarIcon, UsersIcon } from "lucide-react"

import type { PreparationSummary } from "@/types/preparation"

export function PreparationStats({
  preparation,
}: {
  preparation: PreparationSummary
}) {
  return (
    <span className="flex items-center gap-4 text-sm text-muted-foreground tabular-nums">
      <span
        className="flex items-center gap-1.5 text-yellow-600"
        title="Average rating and number of ratings"
      >
        <StarIcon
          className={cn(
            "size-5",
            preparation.rating_avg != null && "fill-yellow-500"
          )}
        />
        {preparation.rating_avg?.toFixed(1) ?? "–"}
        {preparation.rating_count > 0 && (
          <span className="text-muted-foreground">
            ({preparation.rating_count})
          </span>
        )}
      </span>
      <span className="flex items-center gap-1.5">
        <UsersIcon className="size-5" />
        {preparation.join_count}
      </span>
    </span>
  )
}
