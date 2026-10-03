import { cookies } from "next/headers"
import Link from "next/link"
import { getLocale, getTranslations } from "next-intl/server"

import { BuyButton } from "@/components/billing/buy-button"
import { Button } from "@/components/ui/button"
import { TOKEN_COOKIE } from "@/constants/auth"
import { formatDate, formatPrice } from "@/lib/format"
import { productName } from "@/lib/products"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Catalog, Plan, Product } from "@/types/billing"

export const generateMetadata = () => translatedTitle("pricing", "title")

function PriceCard({
  title,
  price,
  note,
  children,
}: {
  title: string
  price: string
  note: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col justify-between gap-6 rounded-2xl border p-6">
      <div className="space-y-2">
        <p className="text-lg font-medium">{title}</p>
        <p className="font-heading text-4xl font-medium tabular-nums">
          {price}
        </p>
        <p className="text-sm text-muted-foreground">{note}</p>
      </div>
      {children}
    </div>
  )
}

export default async function PricingPage() {
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("pricing")
  const products = await getTranslations("products")
  const locale = await getLocale()
  const [catalog, plan] = await Promise.all([
    serverFetch<Catalog>("/billing/catalog"),
    signedIn ? serverFetch<Plan>("/billing/me") : null,
  ])

  if (!catalog) {
    return null
  }

  const price = (product: Product) =>
    formatPrice(product.price_cents, catalog.currency, locale)
  const name = (product: Product) => products(...productName(product))
  const learner = catalog.products.filter((product) => product.owner === "user")
  const company = catalog.products.filter(
    (product) => product.owner === "company"
  )

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <h1 className="font-heading text-4xl font-medium tracking-tight">
        {t("title")}
      </h1>

      <section className="space-y-6">
        <div className="space-y-2">
          <h2 className="font-heading text-2xl font-medium">{t("learners")}</h2>
          {plan && (
            <p className="text-base text-muted-foreground">
              {plan.pass_until
                ? t("passUntil", { date: formatDate(plan.pass_until, locale) })
                : plan.generation_credits
                  ? t("freeAndExtraLeft", {
                      count: plan.free_generations_left,
                      extra: plan.generation_credits,
                    })
                  : t("freeLeft", { count: plan.free_generations_left })}
            </p>
          )}
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <PriceCard
            title={t("free")}
            price={formatPrice(0, catalog.currency, locale)}
            note={t("freeNote", { count: catalog.free_generations_per_month })}
          >
            <Button
              variant="outline"
              className="h-12 px-6 text-base"
              render={<Link href="/" />}
              nativeButton={false}
            >
              {t("start")}
            </Button>
          </PriceCard>
          {learner.map((product) => (
            <PriceCard
              key={product.key}
              title={name(product)}
              price={price(product)}
              note={
                product.pass_days
                  ? t("passNote", { days: product.pass_days })
                  : t("creditsNote", { count: product.generation_credits })
              }
            >
              <BuyButton catalog={catalog} product={product} />
            </PriceCard>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <div className="space-y-2">
          <h2 className="font-heading text-2xl font-medium">
            {t("companies")}
          </h2>
          <p className="text-base text-muted-foreground">
            {t("companiesNote", { count: catalog.free_candidates })}
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {company.map((product) => (
            <PriceCard
              key={product.key}
              title={name(product)}
              price={price(product)}
              note={t("perCandidate", {
                price: formatPrice(
                  product.price_cents / product.candidate_credits,
                  catalog.currency,
                  locale
                ),
              })}
            >
              <Button
                variant="outline"
                className="h-12 px-6 text-base"
                render={<Link href="/company" />}
                nativeButton={false}
              >
                {t("buyFromCompany")}
              </Button>
            </PriceCard>
          ))}
        </div>
      </section>
    </main>
  )
}
