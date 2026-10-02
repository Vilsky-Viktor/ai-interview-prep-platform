"use client"

import { cn } from "cn"

import { InlineText } from "@/components/questions/inline-text"
import { QuestionText } from "@/components/questions/question-text"
import { VirtualList } from "@/components/virtual-list"
import { formatSeconds } from "@/lib/format"
import { answerText, verdict } from "@/lib/rounds"
import type { ReviewItem } from "@/types/round"

export function ScorecardReview({ items }: { items: ReviewItem[] }) {
  return (
    <VirtualList
      items={items}
      getKey={(item) => item.question_id}
      estimateSize={160}
      className="divide-y rounded-2xl border"
      renderItem={(item) => (
        <div className="flex items-start gap-4 p-6">
          <span className="w-16 shrink-0 font-heading text-4xl leading-none font-light text-muted-foreground tabular-nums">
            {item.number}.
          </span>
          <div className="min-w-0 flex-1 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <QuestionText
                text={item.text}
                className="min-w-0 text-lg font-light"
              />
              <ScorecardMark item={item} />
            </div>
            <ScorecardAnswer item={item} />
          </div>
        </div>
      )}
    />
  )
}

function ScorecardMark({ item }: { item: ReviewItem }) {
  const answer = item.answer

  // Unanswered and timed-out questions count as wrong.
  if (!answer || answer.option_index == null) {
    return (
      <span className="shrink-0 text-lg font-light text-red-600 dark:text-red-400">
        {answer ? "Time ran out" : "Not answered"}
      </span>
    )
  }

  return (
    <span
      className={cn(
        "shrink-0 text-lg font-light",
        answer.correct
          ? "text-green-600 dark:text-green-400"
          : "text-red-600 dark:text-red-400"
      )}
    >
      {verdict(answer.correct)}
    </span>
  )
}

function ScorecardAnswer({ item }: { item: ReviewItem }) {
  if (!item.answer || item.answer.option_index == null) {
    return null
  }

  const { seconds, fast } = item.answer

  return (
    <div className="space-y-2">
      <p className="rounded-xl bg-muted px-5 py-4 text-lg leading-relaxed font-light whitespace-pre-wrap">
        <InlineText text={answerText(item)} />
      </p>
      {/* Not known for answers given before timing was recorded. */}
      {seconds != null && (
        <p
          className={cn(
            "text-sm text-muted-foreground",
            fast && "text-amber-600 dark:text-amber-400"
          )}
        >
          Answered in{" "}
          <span
            className={cn(
              "tabular-nums",
              fast ? "font-medium" : "text-foreground"
            )}
          >
            {formatSeconds(seconds)}
          </span>
          {fast && ": too fast to have read the question"}
        </p>
      )}
    </div>
  )
}
