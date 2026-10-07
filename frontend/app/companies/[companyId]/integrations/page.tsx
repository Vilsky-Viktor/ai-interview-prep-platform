import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { AtsConnectionRow } from "@/components/company/ats-connection"
import { AtsJobLinks } from "@/components/company/ats-job-links"
import { CompanyHeader } from "@/components/company/company-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type {
  AtsIntegrations,
  AtsJobLink,
  Company,
  Interview,
} from "@/types/company"

export const generateMetadata = () => translatedTitle("company", "integrations")

/** The company's ATS connections and the ATS jobs linked to its interviews, laid out like the
 * team tab. Everyone in the company sees them; owners and admins change them. */
export default async function IntegrationsPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("ats")
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const [integrations, links, interviews] = company
    ? await Promise.all([
        serverFetch<AtsIntegrations>(`/companies/ats?company_id=${companyId}`),
        serverFetch<AtsJobLink[]>(
          `/companies/ats/links?company_id=${companyId}`
        ),
        serverFetch<Interview[]>(
          `/companies/interviews?company_id=${companyId}&limit=100`
        ),
      ])
    : [null, null, null]

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt />
      </main>
    )
  }

  if (!company) {
    redirect("/companies")
  }

  const workable =
    integrations?.connections.find((item) => item.provider === "workable") ??
    null

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <CompanyHeader
        companyId={companyId}
        name={company.name}
        logoUrl={company.logo_url ?? null}
        verifiedDomain={company.verified_domain ?? null}
        websiteDomain={company.website_domain ?? null}
        verificationStatus={company.verification_status}
        declineReason={company.decline_reason ?? null}
        current="integrations"
        canEdit={company.can_edit}
      />
      {integrations?.available ? (
        <>
          <ul className="divide-y overflow-hidden rounded-2xl border">
            <AtsConnectionRow
              companyId={companyId}
              connection={workable}
              canEdit={company.can_edit}
            />
          </ul>
          {workable && (
            <AtsJobLinks
              companyId={companyId}
              links={links ?? []}
              interviews={(interviews ?? []).filter((item) => item.set_id)}
              canEdit={company.can_edit && workable.status === "connected"}
            />
          )}
        </>
      ) : (
        <p className="rounded-2xl border p-6 text-muted-foreground">
          {t("unavailable")}
        </p>
      )}
    </main>
  )
}
