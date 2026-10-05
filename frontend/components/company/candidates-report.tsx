import { InterviewReport } from "@/components/company/interview-report"
import { InterviewReportActions } from "@/components/company/interview-report-actions"
import { serverFetch } from "@/lib/server-api"
import type { InterviewReportData } from "@/types/company"

/** The candidates tab's report of all its candidates: the hidden page the PDF is made from and
 * its download and share icons, once there's a candidate. */
export async function CandidatesReport({
  interviewId,
}: {
  interviewId: string
}) {
  const report = await serverFetch<InterviewReportData>(
    `/companies/interviews/${interviewId}/report`
  )

  if (!report?.candidates.length) {
    return null
  }

  return (
    <>
      <InterviewReport report={report} />
      <InterviewReportActions interviewId={interviewId} report={report} />
    </>
  )
}
