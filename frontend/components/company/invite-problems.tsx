"use client"

import { cn } from "cn"
import { useTranslations } from "next-intl"

import { SHOWN_LINE_PROBLEMS } from "@/constants/invites"
import type { BulkInviteResult } from "@/types/company"

/** What the invite dialog couldn't do, in red: the API's refusal (`error`), each line it
 * couldn't use with its reason (the first few, then how many more), and why emails weren't
 * invited. Centered under a centered tab (`center`). */
export function InviteProblems({
  error,
  problems,
  skipped,
  center = false,
}: {
  error: string
  problems: BulkInviteResult["problems"]
  skipped: BulkInviteResult["skipped"]
  center?: boolean
}) {
  const t = useTranslations("interviews")
  const reasons = [...new Set(skipped.map((row) => row.reason))]
  const more = problems.length - SHOWN_LINE_PROBLEMS
  const rows = [
    ...(error ? [error] : []),
    ...problems
      .slice(0, SHOWN_LINE_PROBLEMS)
      .map((row) => t(`lineProblems.${row.reason}`, { line: row.line })),
    ...(more > 0 ? [t("lineProblems.more", { count: more })] : []),
    ...reasons.map((reason) =>
      t(`skip.${reason}`, {
        count: skipped.filter((row) => row.reason === reason).length,
      })
    ),
  ]

  if (rows.length === 0) {
    return null
  }

  return (
    <ul
      className={cn(
        "space-y-1 px-6 text-sm break-words text-destructive",
        center && "text-center"
      )}
    >
      {rows.map((row, index) => (
        <li key={index}>{row}</li>
      ))}
    </ul>
  )
}
