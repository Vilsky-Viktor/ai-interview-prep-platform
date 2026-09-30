"use client"

import { FlagIcon, RefreshCwIcon, ThumbsDownIcon, ThumbsUpIcon } from "lucide-react"
import { cn } from "cn"
import { useState } from "react"

import { QuestionReports } from "@/components/questions/question-reports"
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
  const [showReports, setShowReports] = useState(false)
  const canViewReports = Boolean(reportsPath)

  return (
    <>
      <tr className="align-top">
        <td className="w-14 px-4 py-3 font-light text-muted-foreground tabular-nums">
          {number}
        </td>
        <td className={cn("w-full px-4 py-3 font-light", regenerating && "opacity-50")}>
          {question.text}
        </td>
        <td className="py-3 pr-5 pl-4 align-middle text-sm whitespace-nowrap text-muted-foreground tabular-nums">
          <span className="flex flex-col items-end gap-3">
            <span className="flex items-center gap-4">
              <span className="flex items-center gap-1.5" title="Likes">
                <ThumbsUpIcon className="size-4" />
                {question.likes}
              </span>
              <span className="flex items-center gap-1.5" title="Dislikes">
                <ThumbsDownIcon className="size-4" />
                {question.dislikes}
              </span>
              {canViewReports ? (
                <button
                  type="button"
                  aria-expanded={showReports}
                  onClick={() => setShowReports((shown) => !shown)}
                  aria-label={`Show reports (${question.reports})`}
                  className={cn(
                    "-mx-2 -my-1 flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1 aria-expanded:bg-foreground/10 aria-expanded:text-foreground",
                    FEEDBACK_HOVER_CLASS
                  )}
                >
                  <FlagIcon className="size-4" />
                  {question.reports}
                </button>
              ) : (
                <span className="flex items-center gap-1.5" title="Reports">
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
                {regenerating ? "Re-generating…" : "Re-generate"}
              </Button>
            )}
          </span>
        </td>
      </tr>
      {canViewReports && showReports && (
        <tr className="bg-muted/40">
          <td />
          <td colSpan={2} className="px-4 py-4 pr-5">
            <QuestionReports path={`${reportsPath}/${question.id}/reports`} />
          </td>
        </tr>
      )}
    </>
  )
}
