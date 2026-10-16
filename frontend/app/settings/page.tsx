import { getLocale, getTranslations } from "next-intl/server"

import { AccountData } from "@/components/settings/account-data"
import { AccountId } from "@/components/settings/account-id"
import { EmailPreferencesSetting } from "@/components/settings/email-preferences"
import { LanguageSetting } from "@/components/settings/language-setting"
import { SettingsSection } from "@/components/settings/settings-section"
import type { Locale } from "@/constants/i18n"
import { serverFetch } from "@/lib/server-api"
import type { EmailPreferences } from "@/types/emails"

export default async function GeneralSettingsPage() {
  const t = await getTranslations("settings")
  const locale = (await getLocale()) as Locale
  const emails = await serverFetch<EmailPreferences>(
    "/library/me/email-preferences"
  )

  return (
    <>
      <SettingsSection title={t("language")} description={t("languageNote")}>
        <LanguageSetting current={locale} />
      </SettingsSection>
      {emails && (
        <SettingsSection
          title={t("emails.title")}
          description={t("emails.note")}
        >
          <EmailPreferencesSetting initial={emails} />
        </SettingsSection>
      )}
      {/* Side by side on desktop, one under the other otherwise. */}
      <div className="grid gap-8 lg:grid-cols-2">
        <SettingsSection title={t("account")} description={t("accountNote")}>
          <AccountId />
        </SettingsSection>
        <SettingsSection title={t("yourData")} description={t("yourDataNote")}>
          <AccountData />
        </SettingsSection>
      </div>
    </>
  )
}
