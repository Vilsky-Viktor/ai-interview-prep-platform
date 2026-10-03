import type { Metadata } from "next"
import { cookies } from "next/headers"
import { getTranslations } from "next-intl/server"

import { SettingsNav } from "@/components/settings/settings-nav"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("settings")

  return { title: t("title") }
}

export default async function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("settings")

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <h1 className="font-heading text-3xl font-medium tracking-tight">
        {t("title")}
      </h1>

      {signedIn ? (
        <div className="grid gap-8 md:grid-cols-[12rem_minmax(0,1fr)]">
          <SettingsNav />
          <div className="space-y-8">{children}</div>
        </div>
      ) : (
        <SignInPrompt message={t("signIn")} />
      )}
    </main>
  )
}
