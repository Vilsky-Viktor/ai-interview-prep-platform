"use client"

import { useTranslations } from "next-intl"

import { InlineText } from "@/components/questions/inline-text"
import { QuestionText } from "@/components/questions/question-text"
import { CompareCell } from "@/components/rounds/compare-cell"
import { VirtualList } from "@/components/virtual-list"
import { correctText } from "@/lib/rounds"
import type { ReviewItem } from "@/types/round"

/** Two rounds' answers side by side, question by question. */
export function CompareList({
  first,
  second,
}: {
  first: ReviewItem[]
  second: ReviewItem[]
}) {
  const t = useTranslations("rounds")
  const secondByQuestion = new Map(
    second.map((item) => [item.question_id, item])
  )

  return (
    <VirtualList
      items={first}
      getKey={(item) => item.question_id}
      estimateSize={180}
      className="divide-y rounded-2xl border"
      renderItem={(item) => {
        const other = secondByQuestion.get(item.question_id)
        const correct = correctText(item) ?? correctText(other)

        return (
          <div className="space-y-4 p-5">
            <QuestionText text={item.text} className="font-medium" />
            <div className="grid gap-4 sm:grid-cols-2">
              <CompareCell item={item} />
              <CompareCell item={other} />
            </div>
            {correct && (
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">
                  {t("correctAnswer")}:{" "}
                </span>
                <InlineText text={correct} />
              </p>
            )}
          </div>
        )
      }}
    />
  )
}
