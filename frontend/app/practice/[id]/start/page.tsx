import { cookies } from "next/headers"
import { getTranslations } from "next-intl/server"

import { PracticeConsent } from "@/components/practice/practice-consent"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("suggest", "title")

/** Shown once, after signing in and before a talent's first practice round: whether to be
 * suggested to companies. Centered, like a test's start. */
export default async function PracticeStartPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const t = await getTranslations("practice")

  if (!(await cookies()).has(TOKEN_COOKIE)) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={t("signIn")} />
      </main>
    )
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <PracticeConsent templateId={id} />
    </main>
  )
}
