import type { Metadata } from "next"
import { cookies } from "next/headers"
import { getLocale, getTranslations } from "next-intl/server"

import { SignInPrompt } from "@/components/sign-in-prompt"
import { AccountData } from "@/components/settings/account-data"
import { Credits } from "@/components/settings/credits"
import { LanguageSetting } from "@/components/settings/language-setting"
import { TOKEN_COOKIE } from "@/constants/auth"
import type { Locale } from "@/constants/i18n"
import { serverFetch } from "@/lib/server-api"
import type { Balance } from "@/types/billing"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("settings")

  return { title: t("title") }
}

function Section({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <section className="space-y-4 rounded-2xl border p-6">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {children}
    </section>
  )
}

export default async function SettingsPage() {
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("settings")
  const locale = (await getLocale()) as Locale
  const balance = signedIn ? await serverFetch<Balance>("/billing/me") : null

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <h1 className="font-heading text-3xl font-medium tracking-tight">
        {t("title")}
      </h1>

      {!signedIn && <SignInPrompt message={t("signIn")} />}

      {signedIn && (
        <>
          {balance && (
            <Section title={t("credits")} description={t("creditsNote")}>
              <Credits balance={balance} />
            </Section>
          )}
          <Section title={t("language")} description={t("languageNote")}>
            <LanguageSetting current={locale} />
          </Section>
          <Section title={t("yourData")} description={t("yourDataNote")}>
            <AccountData />
          </Section>
        </>
      )}
    </main>
  )
}
