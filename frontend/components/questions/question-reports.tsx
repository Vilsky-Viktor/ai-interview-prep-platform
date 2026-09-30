"use client"

import { useEffect, useState } from "react"

import { REPORT_REASONS } from "@/constants/feedback"
import { apiFetch } from "@/lib/api"
import type { QuestionReport } from "@/types/feedback"

export function QuestionReports({ path }: { path: string }) {
  const [reports, setReports] = useState<QuestionReport[] | null>(null)
  const [missing, setMissing] = useState(false)

  useEffect(() => {
    apiFetch<QuestionReport[]>(path)
      .then(setReports)
      .catch(() => setMissing(true))
  }, [path])

  if (!reports) {
    return (
      <p className="text-sm text-muted-foreground">
        {missing ? "Couldn't load the reports." : "Loading…"}
      </p>
    )
  }

  if (reports.length === 0) {
    return <p className="text-sm text-muted-foreground">No reports.</p>
  }

  return (
    <ul className="space-y-3">
      {reports.map((report) => (
        <li key={report.id} className="space-y-1 text-sm">
          <p className="flex flex-wrap items-baseline justify-between gap-2">
            <span className="font-medium">
              {REPORT_REASONS[report.reason as keyof typeof REPORT_REASONS] ?? report.reason}
            </span>
            <span className="text-muted-foreground">
              {new Date(report.created_at).toLocaleDateString(undefined, {
                dateStyle: "medium",
              })}
            </span>
          </p>
          {report.comment && (
            <p className="font-light whitespace-pre-line text-muted-foreground">
              {report.comment}
            </p>
          )}
        </li>
      ))}
    </ul>
  )
}
