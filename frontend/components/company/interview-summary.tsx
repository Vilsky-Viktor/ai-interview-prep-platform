"use client"

import { UsersIcon } from "lucide-react"
import { useLocale, useTranslations } from "next-intl"

import { InterviewStatus } from "@/components/company/interview-status"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { formatDate } from "@/lib/format"

/** An interview's row content: its title and date, then its status (when it has one) and how
 * many candidates it has. */
export function InterviewSummary({
  title,
  createdAt,
  status,
  candidateCount,
}: {
  title: string
  createdAt: string
  status: string | null
  candidateCount: number
}) {
  const t = useTranslations("interviews")
  const locale = useLocale()

  return (
    <>
      <span className="min-w-0 space-y-1">
        <span className="block text-lg font-medium">{title}</span>
        <span className="block text-sm text-muted-foreground">
          <time dateTime={createdAt} suppressHydrationWarning>
            {formatDate(createdAt, locale)}
          </time>
        </span>
      </span>
      <span className="flex shrink-0 items-center gap-6">
        {status && <InterviewStatus status={status} />}
        <Tooltip>
          {/* Above the row's link overlay, so hovering it shows the tooltip. */}
          <TooltipTrigger
            render={
              <span
                className="relative z-10 flex w-12 shrink-0 items-center justify-end gap-1.5 text-sm text-muted-foreground tabular-nums"
                aria-label={t("candidateCount", { count: candidateCount })}
              />
            }
          >
            <UsersIcon aria-hidden className="size-5" />
            {candidateCount}
          </TooltipTrigger>
          <TooltipContent>
            {t("candidateCount", { count: candidateCount })}
          </TooltipContent>
        </Tooltip>
      </span>
    </>
  )
}
