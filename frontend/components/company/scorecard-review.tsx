"use client"

import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { InlineText } from "@/components/questions/inline-text"
import { QuestionText } from "@/components/questions/question-text"
import { VirtualList } from "@/components/virtual-list"
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
            <ScorecardSignals item={item} />
          </div>
        </div>
      )}
    />
  )
}

function ScorecardMark({ item }: { item: ReviewItem }) {
  const t = useTranslations("scorecard")
  const rounds = useTranslations("rounds")
  const answer = item.answer

  // Unanswered and timed-out questions count as wrong.
  if (!answer || answer.option_index == null) {
    return (
      <span className="shrink-0 text-lg font-light text-red-600 dark:text-red-400">
        {answer ? t("timeOut") : rounds("notAnswered")}
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
      {rounds(verdict(answer.correct))}
    </span>
  )
}

/** Page leaves and copy attempts while this question was open; nothing when there were none. */
function ScorecardSignals({ item }: { item: ReviewItem }) {
  const t = useTranslations("scorecard")
  const candidates = useTranslations("candidates")
  const signals = [
    item.tab_leaves > 0 && t("leftPage", { count: item.tab_leaves }),
    item.copies > 0 && candidates("copies", { count: item.copies }),
  ].filter(Boolean)

  if (signals.length === 0) {
    return null
  }

  return (
    <p className="flex flex-wrap items-center gap-x-1.5 text-sm text-amber-600 tabular-nums dark:text-amber-400">
      {signals.map((signal, index) => (
        <span key={String(signal)} className="flex items-center gap-x-1.5">
          {index > 0 && (
            <MinusIcon aria-hidden className="size-3.5 text-foreground" />
          )}
          {signal}
        </span>
      ))}
    </p>
  )
}

/** "45 s", "2 min 5 s". */
function useDuration() {
  const t = useTranslations("scorecard")

  return (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60

    if (m === 0) {
      return t("seconds", { s })
    }

    return s === 0 ? t("minutes", { m }) : t("minutesSeconds", { m, s })
  }
}

function ScorecardAnswer({ item }: { item: ReviewItem }) {
  const t = useTranslations("scorecard")
  const duration = useDuration()

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
          {t.rich("answeredIn", {
            time: duration(seconds),
            b: (chunks) => (
              <span
                className={cn(
                  "tabular-nums",
                  fast ? "font-medium" : "text-foreground"
                )}
              >
                {chunks}
              </span>
            ),
          })}
          {fast && t("tooFast")}
        </p>
      )}
    </div>
  )
}
