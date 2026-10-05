import { getLocale, getTranslations } from "next-intl/server"

import { AccountData } from "@/components/settings/account-data"
import { LanguageSetting } from "@/components/settings/language-setting"
import { SettingsSection } from "@/components/settings/settings-section"
import { TalentLinkSetting } from "@/components/settings/talent-link-setting"
import type { Locale } from "@/constants/i18n"

export default async function GeneralSettingsPage() {
  const t = await getTranslations("settings")
  const locale = (await getLocale()) as Locale

  return (
    <>
      <SettingsSection title={t("language")} description={t("languageNote")}>
        <LanguageSetting current={locale} />
      </SettingsSection>
      <SettingsSection title={t("yourData")} description={t("yourDataNote")}>
        <AccountData />
      </SettingsSection>
      <TalentLinkSetting />
    </>
  )
}
