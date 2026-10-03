import { getLocale, getTranslations } from "next-intl/server"

import { GoalForm } from "@/components/goal-form"
import { HomeTitle } from "@/components/home-title"

export default async function HomePage() {
  const t = await getTranslations("home")
  // A new language restarts the typing animation with its own words.
  const locale = await getLocale()

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 pb-24">
      <div className="inline-grid max-w-full gap-16">
        <div className="space-y-4 text-center">
          <HomeTitle key={locale} />
          <p className="text-left text-base text-balance text-muted-foreground">
            {t("tagline")}
          </p>
        </div>
        <div className="min-w-0">
          <GoalForm />
        </div>
      </div>
    </main>
  )
}
