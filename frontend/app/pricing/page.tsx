import type { Metadata } from "next"
import { cookies } from "next/headers"
import Link from "next/link"

import { BuyButton } from "@/components/billing/buy-button"
import { Button } from "@/components/ui/button"
import { TOKEN_COOKIE } from "@/constants/auth"
import { formatDate, formatPrice, plural } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import type { Catalog, Plan, Product } from "@/types/billing"

export const metadata: Metadata = { title: "Pricing" }

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
  const [catalog, plan] = await Promise.all([
    serverFetch<Catalog>("/billing/catalog"),
    signedIn ? serverFetch<Plan>("/billing/me") : null,
  ])

  if (!catalog) {
    return null
  }

  const price = (product: Product) =>
    formatPrice(product.price_cents, catalog.currency)
  const learner = catalog.products.filter((product) => product.owner === "user")
  const company = catalog.products.filter(
    (product) => product.owner === "company"
  )

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <h1 className="font-heading text-4xl font-medium tracking-tight">
        Pricing
      </h1>

      <section className="space-y-6">
        <div className="space-y-2">
          <h2 className="font-heading text-2xl font-medium">For learners</h2>
          {plan && (
            <p className="text-base text-muted-foreground">
              {plan.pass_until
                ? `Your Job Search Pass runs until ${formatDate(plan.pass_until)}.`
                : `This month you have ${plural(plan.free_generations_left, "free preparation")} left${
                    plan.generation_credits
                      ? `, plus ${plural(plan.generation_credits, "extra preparation")}`
                      : ""
                  }.`}
            </p>
          )}
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <PriceCard
            title="Free"
            price={formatPrice(0, catalog.currency)}
            note={`${plural(catalog.free_generations_per_month, "private preparation")} a month, practice with the AI tutor, certificates and the public library.`}
          >
            <Button
              variant="outline"
              className="h-12 px-6 text-base"
              render={<Link href="/" />}
              nativeButton={false}
            >
              Start
            </Button>
          </PriceCard>
          {learner.map((product) => (
            <PriceCard
              key={product.key}
              title={product.title}
              price={price(product)}
              note={
                product.pass_days
                  ? `Unlimited preparations for ${product.pass_days} days. Paid once, no renewal.`
                  : `${plural(product.generation_credits, "more private preparation")}, used when the free one is gone. They don't expire.`
              }
            >
              <BuyButton catalog={catalog} product={product} />
            </PriceCard>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <div className="space-y-2">
          <h2 className="font-heading text-2xl font-medium">For companies</h2>
          <p className="text-base text-muted-foreground">
            Your first {plural(catalog.free_candidates, "candidate")} are free.
            Creating interviews is always free; you pay per candidate you
            invite, and credits never expire.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {company.map((product) => (
            <PriceCard
              key={product.key}
              title={product.title}
              price={price(product)}
              note={`${formatPrice(
                product.price_cents / product.candidate_credits,
                catalog.currency
              )} per candidate`}
            >
              <Button
                variant="outline"
                className="h-12 px-6 text-base"
                render={<Link href="/company" />}
                nativeButton={false}
              >
                Buy from your company
              </Button>
            </PriceCard>
          ))}
        </div>
      </section>
    </main>
  )
}
