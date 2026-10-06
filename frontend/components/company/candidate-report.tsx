import { getTranslations } from "next-intl/server"
import { cn } from "cn"

import { CompanyLogo } from "@/components/company/company-logo"
import { IntegrityLine } from "@/components/company/integrity-line"
import { VerifiedBadge } from "@/components/company/verified-badge"
import { Wordmark } from "@/components/wordmark"
import { REPORT_ID } from "@/constants/report"
import type { CandidateReportData } from "@/types/company"

/** The candidate's report the PDF is made from: one compact A4-wide page with the logo, the
 * overall result and each topic's score and signals, never the questions. It sits off screen,
 * always in the light design. */
export async function CandidateReport({
  report,
}: {
  report: CandidateReportData
}) {
  const { company, logoUrl, title, email, grade, passed, passMark, sections } =
    report
  const t = await getTranslations("report")

  return (
    <div
      id={REPORT_ID}
      aria-hidden
      className="light-scope fixed top-0 -left-[10000px] w-[794px] space-y-5 bg-background p-[53px] text-foreground"
    >
      <div className="py-4 text-center">
        <Wordmark className="text-xl" />
      </div>
      {/* The logo on the left of the test and the candidate's email. */}
      <div className="flex items-center gap-5">
        {logoUrl && (
          <CompanyLogo
            url={logoUrl}
            name={company}
            className="h-16 w-auto max-w-40 shrink-0 rounded-2xl object-contain"
          />
        )}
        <div className="min-w-0 space-y-1">
          <p className="text-sm text-muted-foreground">
            {company}
            {report.verifiedDomain && (
              <VerifiedBadge
                domain={report.verifiedDomain}
                className="ms-1 size-4"
              />
            )}
            {title && ` · ${title}`}
          </p>
          <h1 className="font-heading text-2xl font-medium tracking-tight break-all">
            {email}
          </h1>
        </div>
      </div>
      <div className="flex items-baseline gap-3">
        <p
          className={cn(
            "text-4xl font-light tabular-nums",
            tone(passed),
            grade == null && "text-muted-foreground"
          )}
        >
          {grade == null ? "—" : `${grade}%`}
        </p>
        <p className="text-sm text-muted-foreground">
          {passed == null
            ? t("notFinished")
            : t(passed ? "passed" : "notPassed", { mark: passMark })}
        </p>
      </div>
      <ul className="divide-y rounded-xl border">
        {sections.map((section) => (
          <li
            key={section.id}
            className="flex break-inside-avoid items-center justify-between gap-4 px-4 py-2.5"
          >
            <div className="min-w-0 space-y-0.5">
              <h2 className="text-base font-medium">{section.topic_title}</h2>
              <IntegrityLine session={section} />
            </div>
            <p
              className={cn(
                "text-xl font-light tabular-nums",
                tone(section.passed),
                section.final_score == null && "text-muted-foreground"
              )}
            >
              {section.final_score == null ? "—" : `${section.final_score}%`}
            </p>
          </li>
        ))}
      </ul>
      <p className="text-xs text-muted-foreground">{t("humanReview")}</p>
    </div>
  )
}

function tone(passed: boolean | null) {
  if (passed === true) {
    return "text-green-600 dark:text-green-400"
  }

  if (passed === false) {
    return "text-red-600 dark:text-red-400"
  }

  return ""
}
