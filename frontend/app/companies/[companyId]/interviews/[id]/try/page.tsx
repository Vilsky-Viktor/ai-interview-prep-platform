import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { InviteIntro } from "@/components/company/invite-intro"
import { StartPreview } from "@/components/company/start-preview"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Company, InterviewDetail } from "@/types/company"

export const generateMetadata = () => translatedTitle("invite", "title")

/** A company member tries their test: the same intro a candidate gets, then the test, free. */
export default async function TryInterviewPage({
  params,
}: {
  params: Promise<{ companyId: string; id: string }>
}) {
  const { companyId, id } = await params
  const interviews = await getTranslations("interviews")
  const [company, interview] = await Promise.all([
    serverFetch<Company>(`/companies/companies/${companyId}`),
    serverFetch<InterviewDetail>(`/companies/interviews/${id}`),
  ])

  if (!company || !interview?.set_id) {
    notFound()
  }

  // Laid out like the candidate's invite page.
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      {/* Only a member's preview has a way back, beside the intro as on other pages. */}
      <div className="relative w-full">
        <BackLink
          href={`/companies/${companyId}/interviews`}
          help="tryInterview"
        >
          {interviews("title")}
        </BackLink>
        <InviteIntro
          company={company.name}
          logoUrl={company.logo_url}
          verifiedDomain={company.verified_domain}
          title={interview.title}
          questionSeconds={interview.question_seconds}
          finished={false}
          action={<StartPreview companyId={companyId} interviewId={id} />}
        />
      </div>
    </main>
  )
}
