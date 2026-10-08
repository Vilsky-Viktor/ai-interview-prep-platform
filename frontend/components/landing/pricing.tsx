import { getLocale, getTranslations } from "next-intl/server"

import { LandingSection, MoreLink } from "@/components/landing/section"
import { formatPrice, formatPriceRange } from "@/lib/format"
import { publicFetch } from "@/lib/server-api"
import type { Catalog } from "@/types/billing"

/** A candidate's price at each volume tier, as billing sets them, cheapest last. */
export async function PricingSection() {
  const t = await getTranslations("landing.pricing")
  const locale = await getLocale()
  // Without prices (billing is slow or down) the landing page leaves this section out.
  const catalog = await publicFetch<Catalog>("/billing/catalog").catch(
    () => null
  )

  if (!catalog) {
    return null
  }

  const see = (
    <div className="pt-2">
      <MoreLink href="/pricing">{t("see")}</MoreLink>
    </div>
  )

  return (
    <LandingSection
      title={t("title")}
      text={t("text", { free: catalog.free_candidates })}
      extra={see}
    >
      <ul className="mx-auto grid w-full max-w-3xl gap-4 sm:grid-cols-3">
        {catalog.candidate_prices.map((tier, index) => (
          <li
            key={tier.from_dollars}
            className="space-y-1 rounded-2xl border bg-background p-6 text-center"
          >
            <p className="font-heading text-5xl font-medium tracking-tight tabular-nums">
              {formatPrice(tier.cents, catalog.currency, locale)}
            </p>
            <p className="text-sm text-muted-foreground">{t("perCandidate")}</p>
            <p className="pt-3 text-base">
              {index === 0
                ? t("base")
                : t("volume", {
                    from: formatPrice(
                      tier.from_dollars * 100,
                      catalog.currency,
                      locale
                    ),
                  })}
            </p>
          </li>
        ))}
      </ul>
      {/* Per candidate, with no subscription: the main reason to switch. */}
      <p className="text-center text-xl font-medium text-balance">
        {t("compare", {
          range: formatPriceRange(
            catalog.candidate_cents_min,
            catalog.candidate_cents_max,
            catalog.currency,
            locale
          ),
        })}
      </p>
    </LandingSection>
  )
}
