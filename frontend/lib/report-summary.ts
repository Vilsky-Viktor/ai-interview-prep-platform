import type { CandidateReportData, InterviewReportData } from "@/types/company"

type Translate = (
  key: string,
  values?: Record<string, string | number>
) => string

/** The candidate's result as a short chat message, for WhatsApp and Telegram, which can't carry
 * the PDF: the test, the overall result, then each topic's score and any signals. */
export function reportSummary(report: CandidateReportData, t: Translate) {
  const result =
    report.passed == null
      ? t("notFinished")
      : t(report.passed ? "passed" : "notPassed", { mark: report.passMark })
  const topics = report.sections.map((section) => {
    const signals = [
      section.tab_leaves && t("pageLeaves", { count: section.tab_leaves }),
      section.copies && t("copies", { count: section.copies }),
      section.fast_answers && t("fastAnswers", { count: section.fast_answers }),
    ].filter(Boolean)
    const score = section.final_score == null ? "—" : `${section.final_score}%`

    return `• ${section.topic_title}: ${[score, ...signals].join(", ")}`
  })

  return [
    [report.company, report.title].filter(Boolean).join(" · "),
    `${report.email}: ${report.grade == null ? "—" : `${report.grade}%`}, ${result}`,
    "",
    ...topics,
    "",
    t("via"),
  ].join("\n")
}

/** All of a test's candidates as a short chat message: the test and its passing grade, then
 * each candidate's grade, progress and any signals, best first. */
export function candidatesSummary(report: InterviewReportData, t: Translate) {
  const rows = report.candidates.map((candidate) => {
    const signals = [
      candidate.tab_leaves && t("pageLeaves", { count: candidate.tab_leaves }),
      candidate.copies && t("copies", { count: candidate.copies }),
      candidate.fast_answers &&
        t("fastAnswers", { count: candidate.fast_answers }),
    ].filter(Boolean)
    const grade = candidate.grade == null ? "—" : `${candidate.grade}%`

    return `• ${candidate.email}: ${[grade, t("progressOf", { progress: candidate.progress }), ...signals].join(", ")}`
  })

  return [
    [report.company, report.title].filter(Boolean).join(" · "),
    t("passMark", { mark: report.pass_mark }),
    "",
    ...rows,
    "",
    t("via"),
  ].join("\n")
}
