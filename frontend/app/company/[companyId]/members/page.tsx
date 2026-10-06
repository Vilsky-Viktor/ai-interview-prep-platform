import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { CompanyHeader } from "@/components/company/company-header"
import { InviteAdmin } from "@/components/company/invite-admin"
import { MemberList } from "@/components/company/member-list"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Company, CompanyMember } from "@/types/company"

export const generateMetadata = () => translatedTitle("company", "team")

export default async function MembersPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const t = await getTranslations("company")
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const members = company
    ? await serverFetch<CompanyMember[]>(
        `/companies/members?company_id=${companyId}&limit=${PAGE_SIZE}`
      )
    : null

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={t("signInTeam")} />
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
        logoUrl={company.logo_url ?? null}
        verifiedDomain={company.verified_domain ?? null}
        websiteDomain={company.website_domain ?? null}
        current="members"
        canEdit={company.can_edit}
        action={
          company.role === "owner" ? (
            <InviteAdmin companyId={companyId} />
          ) : undefined
        }
      />
      <MemberList companyId={companyId} initial={members ?? []} />
    </main>
  )
}
