import { ArrowDownIcon } from "lucide-react"
import { getLocale, getTranslations } from "next-intl/server"

import { GoalForm } from "@/components/goal-form"
import { HomeTitle } from "@/components/home-title"
import { Closing } from "@/components/landing/closing"
import { CompaniesSection } from "@/components/landing/companies"
import { ControlSection } from "@/components/landing/control"
import { GapsSection } from "@/components/landing/gaps"
import { HowItWorks } from "@/components/landing/how-it-works"
import { LanguagesSection } from "@/components/landing/languages"
import { PricingSection } from "@/components/landing/pricing"
import { ProofSection } from "@/components/landing/proof"
import { QualitySection } from "@/components/landing/quality"
import { ShareSection } from "@/components/landing/share"
import { TutorSection } from "@/components/landing/tutor"

export default async function HomePage() {
  const t = await getTranslations("home")
  const landing = await getTranslations("landing")
  // A new language restarts the typing animation with its own words.
  const locale = await getLocale()

  return (
    <main className="mx-auto max-w-5xl px-6">
      {/* The input fills the first screen, under the 3.5rem header. */}
      <div className="relative flex min-h-[calc(100svh-3.5rem)] flex-col items-center justify-center pb-24">
        <div className="inline-grid max-w-full gap-16">
          <div className="space-y-4 text-center">
            <HomeTitle key={locale} />
            <p className="text-start text-base text-balance text-muted-foreground">
              {t("tagline")}
            </p>
          </div>
          <div className="min-w-0">
            <GoalForm />
          </div>
        </div>
        <a
          href="#how"
          className="absolute bottom-8 flex items-center gap-2 text-lg text-muted-foreground lowercase hover:text-foreground"
        >
          {landing("more")}
          <ArrowDownIcon className="size-5" />
        </a>
      </div>
      <HowItWorks />
      <ControlSection />
      <GapsSection />
      <TutorSection />
      <ProofSection />
      <QualitySection />
      <ShareSection />
      <CompaniesSection />
      <LanguagesSection />
      <PricingSection />
      <Closing />
    </main>
  )
}
