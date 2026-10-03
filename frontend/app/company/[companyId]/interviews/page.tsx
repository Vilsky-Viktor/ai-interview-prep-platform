import { PlusIcon } from "lucide-react"
import { cookies } from "next/headers"
import Link from "next/link"
import { getTranslations } from "next-intl/server"
import { redirect } from "next/navigation"

import { CompanyCredits as CreditsPanel } from "@/components/company/company-credits"
import { CompanyHeader } from "@/components/company/company-header"
import { InterviewList } from "@/components/company/interview-list"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { TOKEN_COOKIE } from "@/constants/auth"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Catalog, CompanyCredits } from "@/types/billing"
import type { Company, Interview } from "@/types/company"

export const generateMetadata = () => translatedTitle("interviews", "title")

export default async function InterviewsPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const t = await getTranslations("interviews")
  const companyText = await getTranslations("company")
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const [interviews, credits, catalog] = company
    ? await Promise.all([
        serverFetch<Interview[]>(
          `/companies/interviews?company_id=${companyId}&limit=${PAGE_SIZE}`
        ),
        serverFetch<CompanyCredits>(
          `/companies/companies/${companyId}/credits`
        ),
        serverFetch<Catalog>("/billing/catalog"),
      ])
    : [null, null, null]

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={companyText("signInInterviews")} />
      </main>
    )
  }

  if (!company) {
    redirect("/company")
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <CompanyHeader
        companyId={companyId}
        name={company.name}
        current="interviews"
        action={
          <Button
            render={<Link href={`/company/${companyId}/interviews/new`} />}
            nativeButton={false}
            size="icon"
            className="size-14 rounded-full"
            aria-label={t("new")}
          >
            <PlusIcon className="size-6" />
          </Button>
        }
      />

      {credits != null && catalog && (
        <CreditsPanel
          companyId={companyId}
          companyName={company.name}
          credits={credits.available}
          low={credits.low}
          catalog={catalog}
        />
      )}

      {interviews && (
        <InterviewList companyId={companyId} initial={interviews} />
      )}
    </main>
  )
}
