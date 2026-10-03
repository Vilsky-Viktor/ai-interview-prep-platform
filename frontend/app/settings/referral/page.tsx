import { cookies } from "next/headers"
import { getTranslations } from "next-intl/server"

import { ReferralLink } from "@/components/billing/referral-link"
import { SettingsSection } from "@/components/settings/settings-section"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import type { Referral } from "@/types/billing"

export default async function ReferralSettingsPage() {
  const t = await getTranslations("referral")
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const referral = signedIn
    ? await serverFetch<Referral>("/billing/me/referral")
    : null

  if (!referral) {
    return null
  }

  return (
    <SettingsSection
      title={t("title")}
      description={t("note", { reward: referral.reward })}
    >
      <ReferralLink referral={referral} path="/" />
    </SettingsSection>
  )
}
