import { getTranslations } from "next-intl/server"

import { CreditHistory } from "@/components/settings/credit-history"
import { SettingsSection } from "@/components/settings/settings-section"

export default async function BillingSettingsPage() {
  const t = await getTranslations("settings")

  return (
    <SettingsSection title={t("history")} description={t("historyNote")}>
      <CreditHistory />
    </SettingsSection>
  )
}
