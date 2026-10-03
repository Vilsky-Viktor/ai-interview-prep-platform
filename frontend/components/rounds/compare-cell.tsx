"use client"

import { cn } from "cn"
import { useTranslations } from "next-intl"

import { InlineText } from "@/components/questions/inline-text"
import { answerText, verdict } from "@/lib/rounds"
import type { ReviewItem } from "@/types/round"

export function CompareCell({ item }: { item: ReviewItem | undefined }) {
  const t = useTranslations("rounds")
  const answer = item?.answer

  if (!item || !answer) {
    return <p className="text-sm text-muted-foreground">{t("notAnswered")}</p>
  }

  return (
    <div className="space-y-1 text-sm">
      <p
        className={cn(
          "font-medium tabular-nums",
          answer.correct
            ? "text-green-600 dark:text-green-400"
            : "text-red-600 dark:text-red-400"
        )}
      >
        {t(verdict(answer.correct))}
      </p>
      <p className="leading-relaxed whitespace-pre-wrap">
        <InlineText text={answerText(item)} />
      </p>
    </div>
  )
}
