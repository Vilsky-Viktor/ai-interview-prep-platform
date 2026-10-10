import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BalanceRow } from "@/components/billing/balance-row"
import { CreditHistory } from "@/components/billing/credit-history"
import { RefreshOnFocus } from "@/components/billing/refresh-on-focus"
import { ReservedList } from "@/components/billing/reserved-list"
import { CompanyHeader } from "@/components/company/company-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TabNav } from "@/components/tab-nav"
import { InfoCard } from "@/components/warning-card"
import { TOKEN_COOKIE } from "@/constants/auth"
import { LIST_BOX, PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Catalog, CompanyCredits } from "@/types/billing"
import type {
  Company,
  CreditCandidate,
  CreditHistoryEntry,
} from "@/types/company"

export const generateMetadata = () => translatedTitle("company", "billing")

export default async function BillingPage({
  params,
  searchParams,
}: {
  params: Promise<{ companyId: string }>
  searchParams: Promise<{ tab?: string }>
}) {
  const { companyId } = await params
  // History opens first; the reserved candidates have their own tab, so a long list of them
  // never pushes the history out of sight.
  const tab = (await searchParams).tab === "reserved" ? "reserved" : "history"
  const t = await getTranslations("companyBilling")
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const billing = `/companies/companies/${companyId}/billing`
  const href = `/companies/${companyId}/billing`
  const [credits, catalog, reserved, history] = company?.can_edit
    ? await Promise.all([
        serverFetch<CompanyCredits>(
          `/companies/companies/${companyId}/credits`
        ),
        serverFetch<Catalog>("/billing/catalog"),
        // Only the open tab's first page.
        tab === "reserved"
          ? serverFetch<CreditCandidate[]>(
              `${billing}/reserved?limit=${PAGE_SIZE}`
            )
          : null,
        tab === "history"
          ? serverFetch<CreditHistoryEntry[]>(
              `${billing}/history?limit=${PAGE_SIZE}`
            )
          : null,
      ])
    : [null, null, null, null]

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

  // Viewers don't see the company's billing.
  if (!company.can_edit) {
    redirect(`/companies/${companyId}/interviews`)
  }

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <RefreshOnFocus />
      <CompanyHeader
        companyId={companyId}
        name={company.name}
        logoUrl={company.logo_url ?? null}
        verifiedDomain={company.verified_domain ?? null}
        websiteDomain={company.website_domain ?? null}
        verificationStatus={company.verification_status}
        declineReason={company.decline_reason ?? null}
        current="billing"
        canEdit={company.can_edit}
      />
      {credits && catalog && (
        <div className={LIST_BOX}>
          <BalanceRow
            catalog={catalog}
            name={company.name}
            available={credits.available}
            reserved={credits.reserved}
            low={credits.low}
            companyId={companyId}
          />
        </div>
      )}
      <div className="space-y-6">
        <TabNav
          items={[
            { id: "history", href: href, label: t("history") },
            {
              id: "reserved",
              href: `${href}?tab=reserved`,
              label: t("reservedTab", {
                count: credits?.reserved_candidates ?? 0,
              }),
            },
          ]}
          current={tab}
        />
        {tab === "reserved" ? (
          <div className="space-y-4">
            <InfoCard className="max-sm:-mx-6 max-sm:rounded-none">
              {t("reservedNote")}
            </InfoCard>
            {reserved && reserved.length > 0 ? (
              <ReservedList companyId={companyId} initial={reserved} />
            ) : (
              <p className="py-16 text-center text-muted-foreground">
                {t("reservedEmpty")}
              </p>
            )}
          </div>
        ) : (
          <CreditHistory companyId={companyId} initial={history ?? []} />
        )}
      </div>
    </main>
  )
}
