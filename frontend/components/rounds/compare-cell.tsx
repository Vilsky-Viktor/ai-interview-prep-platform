import { cn } from "cn"

import { answerText, scorePassed, verdict } from "@/lib/rounds"
import type { ReviewItem } from "@/types/round"

export function CompareCell({ item }: { item: ReviewItem | undefined }) {
  const answer = item?.answer

  if (!item || !answer) {
    return <p className="text-sm text-muted-foreground">Not answered</p>
  }

  const good = answer.correct ?? scorePassed(answer.score)

  return (
    <div className="space-y-1 text-sm">
      <p
        className={cn(
          "font-medium tabular-nums",
          good
            ? "text-green-600 dark:text-green-400"
            : "text-red-600 dark:text-red-400"
        )}
      >
        {verdict(answer.correct, answer.score)}
      </p>
      <p className="leading-relaxed whitespace-pre-wrap">{answerText(item)}</p>
    </div>
  )
}
