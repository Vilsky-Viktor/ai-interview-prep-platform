import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { ReferralLink } from "@/components/billing/referral-link"
import { CompanyHeader } from "@/components/company/company-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Referral } from "@/types/billing"
import type { Company } from "@/types/company"

export const generateMetadata = () => translatedTitle("company", "referrals")

export default async function ReferralsPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const t = await getTranslations("company")
  const referralText = await getTranslations("referral")
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const referral = company
    ? await serverFetch<Referral>(`/companies/companies/${companyId}/referral`)
    : null

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={t("signInReferrals")} />
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
        current="referrals"
      />
      {referral && (
        <section className="space-y-4">
          <div className="space-y-1">
            <h2 className="text-lg font-medium">
              {referralText("companyTitle")}
            </h2>
            <p className="text-sm text-muted-foreground">
              {referralText("companyNote", {
                reward: referral.reward,
                min: referral.min_dollars,
              })}
            </p>
          </div>
          <ReferralLink referral={referral} path="/company" />
        </section>
      )}
    </main>
  )
}
