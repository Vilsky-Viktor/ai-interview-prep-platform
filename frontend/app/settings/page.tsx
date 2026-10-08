import { getLocale, getTranslations } from "next-intl/server"

import { AccountData } from "@/components/settings/account-data"
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
      <SettingsSection title={t("yourData")} description={t("yourDataNote")}>
        <AccountData />
      </SettingsSection>
    </>
  )
}
