import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { Button } from "@/components/ui/button"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Catalog } from "@/types/billing"

export const generateMetadata = () => translatedTitle("pricing", "title")

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
  const catalog = await serverFetch<Catalog>("/billing/catalog")

  if (!catalog) {
    return null
  }

  const credits = (count: number) => t("credits", { count })

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
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

      <section className="space-y-4">
        <h2 className="font-heading text-2xl font-medium">{t("learners")}</h2>
        <ul className="divide-y rounded-xl border">
          <PriceRow what={t("kit")} price={credits(catalog.kit_credits)} />
          <PriceRow
            what={t("chat", { free: catalog.chat_free_turns })}
            price={t("perTurn", { count: catalog.chat_turn_credits })}
          />
          <PriceRow what={t("ownCertificate")} price={t("free")} />
          <PriceRow
            what={t("publicCertificate")}
            price={credits(catalog.certificate_credits)}
          />
          <PriceRow what={t("publicPractice")} price={t("free")} />
          <PriceRow
            what={t("welcome")}
            price={t("gift", { count: catalog.welcome_user })}
          />
        </ul>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="font-heading text-2xl font-medium">
            {t("companies")}
          </h2>
          <Button
            variant="outline"
            className="h-12 px-6 text-base"
            render={<Link href="/company" />}
            nativeButton={false}
          >
            {t("openCompanies")}
          </Button>
        </div>
        <ul className="divide-y rounded-xl border">
          <PriceRow what={t("interview")} price={t("free")} />
          <PriceRow
            what={t("candidate")}
            price={credits(catalog.candidate_credits)}
          />
          <PriceRow
            what={t("companyWelcome")}
            price={t("gift", { count: catalog.welcome_company })}
          />
        </ul>
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
            what={t("referral")}
            price={t("each", { count: catalog.referral_user })}
          />
          <PriceRow
            what={t("companyReferral", {
              min: catalog.referral_company_min_dollars,
            })}
            price={t("each", { count: catalog.referral_company })}
          />
        </ul>
      </section>
    </main>
  )
}
