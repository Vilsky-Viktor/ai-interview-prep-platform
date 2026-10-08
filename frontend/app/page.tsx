import { ArrowDownIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { AdvantagesSection } from "@/components/landing/advantages"
import { AtsSection } from "@/components/landing/ats"
import { BrandSection } from "@/components/landing/brand"
import { Closing } from "@/components/landing/closing"
import { CompaniesSection } from "@/components/landing/companies"
import { ControlSection } from "@/components/landing/control"
import { HowItWorks } from "@/components/landing/how-it-works"
import { PricingSection } from "@/components/landing/pricing"
import { TrustSection } from "@/components/landing/trust"
import { QualitySection } from "@/components/landing/quality"
import { ReportsSection } from "@/components/landing/reports"
import { InviteWaysSection } from "@/components/landing/invite-ways"
import { TryFirstSection } from "@/components/landing/try-first"
import { JsonLd } from "@/components/json-ld"
import { StartTest } from "@/components/start-test"
import { SITE_NAME } from "@/constants/seo"
import { publicFetch } from "@/lib/server-api"
import { pageMetadata, siteUrl } from "@/lib/site"
import { organizationData } from "@/lib/structured-data"
import type { Catalog } from "@/types/billing"

export async function generateMetadata() {
  const t = await getTranslations("site")

  // The layout's title template doesn't reach its own segment's page: the brand is added here.
  return pageMetadata(
    `${t("homeTitle")} · ${SITE_NAME}`,
    t("description"),
    "/",
    true
  )
}

export default async function HomePage() {
  const t = await getTranslations("home")
  const site = await getTranslations("site")
  const landing = await getTranslations("landing")
  // Without prices (billing is slow or down) the page still shows, without the free offer.
  const catalog = await publicFetch<Catalog>("/billing/catalog").catch(
    () => null
  )
  const freeCandidates = catalog?.free_candidates ?? null

  return (
    <main className="mx-auto max-w-5xl px-6">
      <JsonLd data={organizationData(siteUrl(), site("description"))} />
      {/* The promise and the box to start in fill the first screen, under the 3.5rem header. */}
      <div className="relative flex min-h-[calc(100svh-3.5rem)] flex-col items-center justify-center pb-24">
        <div className="w-full max-w-176 space-y-10">
          <div className="space-y-4">
            {/* Two lines, each ending with the logo's blue dot. */}
            <h1 className="no-dot font-heading text-[min(3rem,10.5vw)] font-medium tracking-tight text-balance sm:text-6xl">
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
      <AdvantagesSection />
      <CompaniesSection />
      <TryFirstSection />
      <InviteWaysSection />
      <ReportsSection />
      <ControlSection />
      <QualitySection />
      <AtsSection />
      <BrandSection />
      <TrustSection />
      <PricingSection />
      <Closing />
    </main>
  )
}
