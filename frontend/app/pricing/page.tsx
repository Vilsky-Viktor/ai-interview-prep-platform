import { InfoIcon } from "lucide-react"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { JsonLd } from "@/components/json-ld"
import { Button } from "@/components/ui/button"
import { publicFetch } from "@/lib/server-api"
import { pageMetadata, siteUrl } from "@/lib/site"
import { softwareData } from "@/lib/structured-data"
import type { Catalog } from "@/types/billing"

export async function generateMetadata() {
  const t = await getTranslations("pricing")

  return pageMetadata(t("title"), t("intro"), "/pricing", true)
}

function PriceRow({ what, price }: { what: string; price: string }) {
  return (
    <li className="flex items-baseline justify-between gap-6 px-5 py-4">
      <span>{what}</span>
      <span className="shrink-0 text-end font-medium tabular-nums">
        {price}
      </span>
    </li>
  )
}

export default async function PricingPage() {
  const t = await getTranslations("pricing")
  const catalog = await publicFetch<Catalog>("/billing/catalog")

  if (!catalog) {
    return null
  }

  // The candidates a first company's welcome credits cover.
  const freeCandidates = Math.floor(
    catalog.welcome_company / catalog.candidate_credits
  )
  const [standard, ...volume] = catalog.candidate_prices

  return (
    <main className="mx-auto max-w-5xl space-y-16 px-6 py-12">
      <JsonLd data={softwareData(siteUrl(), t("intro"), catalog)} />
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-4">
          <h1 className="font-heading text-4xl font-medium tracking-tight">
            {t("title")}
          </h1>
          <Button
            className="h-12 px-6 text-base"
            render={<Link href="/top-up" />}
            nativeButton={false}
          >
            {t("topUp")}
          </Button>
        </div>
        <p className="text-base text-muted-foreground">{t("intro")}</p>
      </div>

      <section className="space-y-10">
        <ul className="divide-y rounded-xl border">
          <PriceRow what={t("test")} price={t("free")} />
          <PriceRow
            what={t("welcome", { count: freeCandidates })}
            price={t("free")}
          />
          <PriceRow
            what={t("candidate")}
            price={t("perCandidate", { dollars: standard.cents / 100 })}
          />
          {/* Volume prices: large top-ups buy more credits per dollar (billing decides). */}
          {volume.map((tier) => (
            <PriceRow
              key={tier.from_dollars}
              what={t("candidateVolume", { from: tier.from_dollars })}
              price={t("perCandidate", { dollars: tier.cents / 100 })}
            />
          ))}
        </ul>
        <div className="mx-auto flex w-fit items-center gap-3 rounded-2xl bg-muted px-5 py-4 text-base text-muted-foreground">
          <InfoIcon aria-hidden className="size-6 shrink-0 text-primary" />
          <p>{t("credits")}</p>
        </div>
      </section>

      <section className="space-y-4">
        <div className="space-y-1">
          <h2 className="font-heading text-2xl font-medium">
            {t("referrals")}
          </h2>
          <p className="text-base text-muted-foreground">
            {t("referralsNote")}
          </p>
        </div>
        <ul className="divide-y rounded-xl border">
          <PriceRow
            what={t("companyReferral")}
            price={t("each", { count: catalog.referral_company })}
          />
        </ul>
      </section>
    </main>
  )
}
