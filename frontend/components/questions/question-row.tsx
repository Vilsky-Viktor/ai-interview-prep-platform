"use client"

import {
  FlagIcon,
  RefreshCwIcon,
  ThumbsDownIcon,
  ThumbsUpIcon,
} from "lucide-react"
import { cn } from "cn"
import { useTranslations } from "next-intl"
import { useState } from "react"

import { QuestionReports } from "@/components/questions/question-reports"
import { QuestionText } from "@/components/questions/question-text"
import { Button } from "@/components/ui/button"
import { FEEDBACK_HOVER_CLASS } from "@/constants/feedback"
import type { QuestionStats } from "@/types/feedback"

export function QuestionRow({
  question,
  number,
  canRegenerate,
  reportsPath,
  regenerating,
  busy,
  onRegenerate,
}: {
  question: QuestionStats
  number: number
  canRegenerate: boolean
  reportsPath?: string
  regenerating: boolean
  busy: boolean
  onRegenerate: () => void
}) {
  const t = useTranslations("questions")
  const [showReports, setShowReports] = useState(false)
  const canViewReports = Boolean(reportsPath)

  return (
    // Columns: number, question, then feedback and actions; reports open in a row below.
    <div className="grid grid-cols-[3.5rem_1fr_auto]">
      <div className="px-5 py-5 font-light text-muted-foreground tabular-nums">
        {number}
      </div>
      <div
        className={cn(
          "min-w-0 px-5 py-5 font-light",
          regenerating && "opacity-50"
        )}
      >
        <QuestionText text={question.text} />
      </div>
      <div className="self-center py-5 ps-5 pe-6 text-sm whitespace-nowrap text-muted-foreground tabular-nums">
        <span className="flex flex-col items-end gap-3">
          <span className="flex items-center gap-4">
            <span className="flex items-center gap-1.5" title={t("likes")}>
              <ThumbsUpIcon className="size-4" />
              {question.likes}
            </span>
            <span className="flex items-center gap-1.5" title={t("dislikes")}>
              <ThumbsDownIcon className="size-4" />
              {question.dislikes}
            </span>
            {canViewReports ? (
              <button
                type="button"
                aria-expanded={showReports}
                onClick={() => setShowReports((shown) => !shown)}
                aria-label={t("showReports", { count: question.reports })}
                className={cn(
                  "-mx-2 -my-1 flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1 aria-expanded:bg-foreground/10 aria-expanded:text-foreground",
                  FEEDBACK_HOVER_CLASS
                )}
              >
                <FlagIcon className="size-4" />
                {question.reports}
              </button>
            ) : (
              <span className="flex items-center gap-1.5" title={t("reports")}>
                <FlagIcon className="size-4" />
                {question.reports}
              </span>
            )}
          </span>
          {canRegenerate && (
            <Button variant="outline" disabled={busy} onClick={onRegenerate}>
              <RefreshCwIcon
                data-icon="inline-start"
                className={cn(regenerating && "animate-spin")}
              />
              {regenerating ? t("regenerating") : t("regenerate")}
            </Button>
          )}
        </span>
      </div>
      {canViewReports && showReports && (
        <div className="col-span-3 bg-muted/40 py-5 ps-[4.75rem] pe-6">
          <QuestionReports path={`${reportsPath}/${question.id}/reports`} />
        </div>
      )}
    </div>
  )
}
