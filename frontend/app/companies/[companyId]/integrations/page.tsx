import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { AtsConnectionRow } from "@/components/company/ats-connection"
import { SlackRow } from "@/components/company/slack-connection"
import { CompanyHeader } from "@/components/company/company-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { ATS_PROVIDERS } from "@/constants/ats"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { AtsIntegrations, Company } from "@/types/company"
import type { SlackOverview } from "@/types/notifications"

export const generateMetadata = () => translatedTitle("company", "integrations")

/** The company's integrations: its ATSs and Slack, a row each laid out like the companies list,
 * in two groups, messaging first; each opens its own page. Everyone in the company sees them; owners and admins change them. */
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
  const [integrations, slack] = company
    ? await Promise.all([
        serverFetch<AtsIntegrations>(
          `/ats/connections?company_id=${companyId}`
        ),
        serverFetch<SlackOverview>(
          `/notifications/slack?company_id=${companyId}`
        ),
      ])
    : [null, null]

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
      {slack && (
        <section className="space-y-6">
          <h2 className="font-heading text-2xl font-medium">
            {t("messagingGroup")}
          </h2>
          <ul className="divide-y overflow-hidden rounded-2xl border">
            <SlackRow
              companyId={companyId}
              slack={slack}
              canEdit={company.can_edit}
            />
          </ul>
        </section>
      )}
      <section className="space-y-6">
        {/* An acronym: its capitals stay, though titles are lowercase. */}
        <h2 className="font-heading text-2xl font-medium normal-case">
          {t("atsGroup")}
        </h2>
        {integrations?.available ? (
          <ul className="divide-y overflow-hidden rounded-2xl border">
            {ATS_PROVIDERS.map((provider) => (
              <AtsConnectionRow
                key={provider.id}
                companyId={companyId}
                provider={provider}
                connection={
                  integrations.connections.find(
                    (item) => item.provider === provider.id
                  ) ?? null
                }
                canEdit={company.can_edit}
              />
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl border p-6 text-muted-foreground">
            {t("unavailable")}
          </p>
        )}
      </section>
    </main>
  )
}
