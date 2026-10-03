"use client"

import { useTranslations } from "next-intl"
import type { ComponentProps } from "react"

import { TopicLimit } from "@/components/questions/topic-limit"
import { TopicQuestions } from "@/components/questions/topic-questions"

export function TopicQuestionLimit({
  limit,
  limitPath,
  caption,
  ...questions
}: ComponentProps<typeof TopicQuestions> & {
  limit: number | null
  limitPath?: string
  caption: string
}) {
  const t = useTranslations("questions")

  if (!limitPath && limit == null) {
    return <TopicQuestions {...questions} />
  }

  return (
    <span className="flex shrink-0 items-center gap-2">
      {limitPath ? (
        // Remounts with the saved value after each change.
        <TopicLimit
          key={limit ?? "all"}
          path={limitPath}
          count={questions.count}
          limit={limit}
        />
      ) : (
        <span className="text-lg tabular-nums">{limit}</span>
      )}
      <span className="flex flex-col items-end leading-none">
        <span className="flex items-baseline gap-1 text-sm text-muted-foreground">
          {t("of")}
          <TopicQuestions {...questions} alignCount />
        </span>
        <span className="-mt-0.5 text-xs text-muted-foreground/60">
          {caption}
        </span>
      </span>
    </span>
  )
}
