import { cn } from "cn"

import { answerText, verdict } from "@/lib/rounds"
import type { ReviewItem } from "@/types/round"

export function ScorecardReview({
  items,
  mode,
}: {
  items: ReviewItem[]
  mode: "open" | "choice"
}) {
  return (
    <ul className="divide-y rounded-2xl border">
      {items.map((item) => (
        <li key={item.question_id} className="flex items-start gap-4 p-6">
          <span className="w-16 shrink-0 font-heading text-4xl leading-none font-light text-muted-foreground tabular-nums">
            {item.number}.
          </span>
          <div className="min-w-0 flex-1 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <p className="text-lg font-light">{item.text}</p>
              <ScorecardMark item={item} mode={mode} />
            </div>
            <ScorecardAnswer item={item} />
          </div>
        </li>
      ))}
    </ul>
  )
}

function ScorecardMark({
  item,
  mode,
}: {
  item: ReviewItem
  mode: "open" | "choice"
}) {
  const answer = item.answer

  if (!answer) {
    return <span className="shrink-0 text-muted-foreground">Not answered</span>
  }

  const label =
    mode === "choice" ? verdict(answer.correct, answer.score) : `${answer.score}%`
  const incorrect = mode === "choice" && answer.correct !== true

  return (
    <span
      className={cn(
        "shrink-0 text-lg font-light tabular-nums",
        mode === "open"
          ? "text-blue-600 dark:text-blue-400"
          : incorrect
            ? "text-red-600 dark:text-red-400"
            : "text-green-600 dark:text-green-400"
      )}
    >
      {label}
    </span>
  )
}

function ScorecardAnswer({ item }: { item: ReviewItem }) {
  const answer = item.answer

  if (!answer) {
    return null
  }

  return (
    <p className="rounded-xl bg-muted px-5 py-4 text-lg leading-relaxed font-light whitespace-pre-wrap">
      {answerText(item)}
    </p>
  )
}
