"use client"

import { useTranslations } from "next-intl"

import { ReportActions } from "@/components/company/report-actions"
import { REPORT_ID } from "@/constants/report"
import { reportSummary } from "@/lib/report-summary"
import type { CandidateReportData } from "@/types/company"

/** A candidate's report: download or share it, from their page. */
export function CandidateReportActions({
  interviewId,
  inviteId,
  report,
}: {
  interviewId: string
  inviteId: string
  report: CandidateReportData
}) {
  const t = useTranslations("report")
  const candidates = useTranslations("candidates")

  return (
    <ReportActions
      reportId={REPORT_ID}
      fileName={t("fileName", { email: report.email })}
      emailPath={`/companies/interviews/${interviewId}/candidates/${inviteId}/report/email`}
      summary={reportSummary(report, (key, values) =>
        ["pageLeaves", "copies", "fastAnswers"].includes(key)
          ? candidates(key, values)
          : t(key, values)
      )}
    />
  )
}
