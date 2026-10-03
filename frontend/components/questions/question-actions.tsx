"use client"

import { useTranslations } from "next-intl"

import { QuestionRating } from "@/components/questions/question-rating"
import { ReportDialog } from "@/components/questions/report-dialog"

export function QuestionActions({
  questionId,
  basePath = `/library/questions/${questionId}`,
}: {
  questionId: string
  basePath?: string
}) {
  const t = useTranslations("questions")

  return (
    <div className="space-y-2 text-center">
      <p className="text-sm text-muted-foreground">{t("goodQuestion")}</p>
      <div className="mx-auto grid h-14 w-60 grid-cols-3 overflow-hidden rounded-xl border">
        <QuestionRating basePath={basePath} />
        <ReportDialog basePath={basePath} />
      </div>
    </div>
  )
}
