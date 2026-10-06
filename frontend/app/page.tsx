import { ArrowDownIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { BrandSection } from "@/components/landing/brand"
import { Closing } from "@/components/landing/closing"
import { CompaniesSection } from "@/components/landing/companies"
import { ControlSection } from "@/components/landing/control"
import { HowItWorks } from "@/components/landing/how-it-works"
import { JobAdLinkSection } from "@/components/landing/job-ad-link"
import { PricingSection } from "@/components/landing/pricing"
import { TrustSection } from "@/components/landing/trust"
import { QualitySection } from "@/components/landing/quality"
import { ReportsSection } from "@/components/landing/reports"
import { TryFirstSection } from "@/components/landing/try-first"
import { StartTest } from "@/components/start-test"
import { serverFetch } from "@/lib/server-api"
import type { Catalog } from "@/types/billing"

export default async function HomePage() {
  const t = await getTranslations("home")
  const landing = await getTranslations("landing")
  const catalog = await serverFetch<Catalog>("/billing/catalog")
  // The candidates a first company's welcome credits cover.
  const freeCandidates = catalog
    ? Math.floor(catalog.welcome_company / catalog.candidate_credits)
    : null

  return (
    <main className="mx-auto max-w-5xl px-6">
      {/* The promise and the box to start in fill the first screen, under the 3.5rem header. */}
      <div className="relative flex min-h-[calc(100svh-3.5rem)] flex-col items-center justify-center pb-24">
        <div className="w-full max-w-176 space-y-10">
          <div className="space-y-4">
            {/* Two lines, each ending with the logo's blue dot. */}
            <h1 className="no-dot font-heading text-5xl font-medium tracking-tight text-balance sm:text-6xl">
              {t("title")
                .split("\n")
                .map((line) => (
                  <span key={line} className="block">
                    {line}
                    <span className="text-primary">.</span>
                  </span>
                ))}
            </h1>
            <p className="text-lg text-balance text-muted-foreground">
              {t("text")}
            </p>
          </div>
          <StartTest freeCandidates={freeCandidates} />
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
      <CompaniesSection />
      <TryFirstSection />
      <ReportsSection />
      <ControlSection />
      <QualitySection />
      <JobAdLinkSection />
      <BrandSection />
      <TrustSection />
      <PricingSection />
      <Closing />
    </main>
  )
}
