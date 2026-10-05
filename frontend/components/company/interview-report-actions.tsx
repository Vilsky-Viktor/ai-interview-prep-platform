"use client"

import { useTranslations } from "next-intl"

import { ReportActions } from "@/components/company/report-actions"
import { INTERVIEW_REPORT_ID } from "@/constants/report"
import { candidatesSummary } from "@/lib/report-summary"
import type { InterviewReportData } from "@/types/company"

/** The report of all a test's candidates: download or share it, from its candidates tab. */
export function InterviewReportActions({
  interviewId,
  report,
}: {
  interviewId: string
  report: InterviewReportData
}) {
  const t = useTranslations("report")
  const candidates = useTranslations("candidates")

  return (
    <ReportActions
      reportId={INTERVIEW_REPORT_ID}
      fileName={t("candidatesFileName", { title: report.title ?? "" })}
      emailPath={`/companies/interviews/${interviewId}/report/email`}
      summary={candidatesSummary(report, (key, values) =>
        ["pageLeaves", "copies", "fastAnswers"].includes(key)
          ? candidates(key, values)
          : t(key, values)
      )}
      pages
    />
  )
}
