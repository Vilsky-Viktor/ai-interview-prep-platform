import { cn } from "cn"
import { getTranslations } from "next-intl/server"

import { CompanyLogo } from "@/components/company/company-logo"
import { VerifiedBadge } from "@/components/company/verified-badge"
import { Wordmark } from "@/components/wordmark"
import { INTERVIEW_REPORT_ID } from "@/constants/report"
import type { InterviewReportData } from "@/types/company"

/** All of a test's candidates with their totals, best first, for the PDF: like a candidate's
 * report, a row per candidate instead of a row per topic. It sits off screen, always in the
 * light design, and runs over as many A4 pages as it needs. */
export async function InterviewReport({
  report,
}: {
  report: InterviewReportData
}) {
  const t = await getTranslations("report")
  const candidates = await getTranslations("candidates")

  return (
    <div
      id={INTERVIEW_REPORT_ID}
      aria-hidden
      className="light-scope fixed top-0 -left-[10000px] w-[794px] space-y-5 bg-background p-[53px] text-foreground"
    >
      <div className="py-4 text-center">
        <Wordmark className="text-xl" />
      </div>
      {/* The logo on the left of the company and the test, as in a candidate's report. */}
      <div className="flex items-center gap-5">
        {report.logo_url && (
          <CompanyLogo
            url={report.logo_url}
            name={report.company}
            className="h-16 w-auto max-w-40 shrink-0 rounded-2xl object-contain"
          />
        )}
        <div className="min-w-0 space-y-1">
          <p className="text-sm text-muted-foreground">
            {report.company}
            {report.verified_domain && (
              <VerifiedBadge
                domain={report.verified_domain}
                className="ms-1 size-4"
              />
            )}
            {" · "}
            {t("candidateCount", { count: report.candidates.length })}
            {" · "}
            {t("passMark", { mark: report.pass_mark })}
          </p>
          <h1 className="font-heading text-2xl font-medium tracking-tight normal-case">
            {report.title}
          </h1>
        </div>
      </div>
      <ul className="divide-y rounded-xl border">
        {report.candidates.map((candidate) => {
          // In words: a PDF has no tooltips to explain icons.
          const signals = [
            candidate.tab_leaves &&
              candidates("pageLeaves", { count: candidate.tab_leaves }),
            candidate.copies &&
              candidates("copies", { count: candidate.copies }),
            candidate.fast_answers &&
              candidates("fastAnswers", { count: candidate.fast_answers }),
          ].filter(Boolean)

          return (
            <li
              key={candidate.id}
              className="flex break-inside-avoid items-center justify-between gap-4 px-4 py-2.5"
            >
              <div className="min-w-0 space-y-0.5">
                <p className="text-base font-medium break-all">
                  {candidate.email}
                </p>
                {signals.length > 0 && (
                  <p className="text-sm text-amber-600">
                    {signals.join(" · ")}
                  </p>
                )}
              </div>
              <div className="flex shrink-0 items-center gap-6">
                <Total label={candidates("progress")}>
                  {candidate.progress}%
                </Total>
                <Total
                  label={candidates("grade")}
                  className={cn(
                    candidate.grade == null && "text-muted-foreground",
                    candidate.passed === true && "text-green-600",
                    candidate.passed === false && "text-red-600"
                  )}
                >
                  {candidate.grade == null ? "—" : `${candidate.grade}%`}
                </Total>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function Total({
  label,
  className,
  children,
}: {
  label: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className="w-20 text-center">
      <p className={cn("text-xl font-light tabular-nums", className)}>
        {children}
      </p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}
