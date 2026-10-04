import { getLocale, getTranslations } from "next-intl/server"

import { BalanceDemo } from "@/components/landing/balance-demo"
import { LandingSection, MoreLink, Stage } from "@/components/landing/section"
import { serverFetch } from "@/lib/server-api"
import type { Catalog } from "@/types/billing"

// The picture's balances. The learner tops up by hand; the company's balance has just fallen
// under its automatic top-up level, so it tops up by itself. The company's top-up comes later
// in the loop, so the two don't count at once.
const LEARNER_CREDITS = 1240
const COMPANY_CREDITS = 860
const COMPANY_THRESHOLD = 900
const LEARNER_AT = 1800
const COMPANY_AT = 3600

/** The top-up page as it really looks (app/top-up/page.tsx): a learner's credits and a
 * company's, side by side. */
export async function PricingSection() {
  const t = await getTranslations("landing.pricing")
  const topUp = await getTranslations("topUp")
  const billing = await getTranslations("billing")
  const automatic = await getTranslations("autoTopUp")
  const locale = await getLocale()
  // A real top-up amount from billing for the company's automatic top-up.
  const catalog = await serverFetch<Catalog>("/billing/catalog")
  const product = catalog?.products[1] ?? catalog?.products[0]
  const number = (count: number) => count.toLocaleString(locale)
  // Both balances grow by this real top-up, with its bonus.
  const added = product ? product.credits + product.bonus_credits : 0

  const see = (
    <div className="pt-2">
      <MoreLink href="/pricing">{t("see")}</MoreLink>
    </div>
  )
  const heading = (title: string, note: string) => (
    <div className="space-y-1">
      <p className="font-heading text-lg font-medium tracking-tight lowercase">
        {title}
        <span className="text-primary">.</span>
      </p>
      <p className="text-sm text-muted-foreground">{note}</p>
    </div>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={see}>
      {/* The top-up buttons are real links, so screen readers keep the picture. */}
      <Stage wide decorative={false}>
        <div className="grid items-start gap-8 text-start md:grid-cols-2 md:gap-5">
          <div className="space-y-3">
            {heading(t("learner"), t("personal"))}
            <BalanceDemo
              name={topUp("yours")}
              automatic={automatic("off")}
              start={LEARNER_CREDITS}
              added={added}
              startAt={LEARNER_AT}
              pressed
              words={billing("creditsWord", { count: LEARNER_CREDITS + added })}
              action={billing("topUp")}
              locale={locale}
            />
          </div>
          <div className="space-y-3">
            {heading(topUp("companies"), topUp("companiesNote"))}
            <BalanceDemo
              name={t("company")}
              automatic={
                product
                  ? automatic("on", {
                      amount: product.title,
                      threshold: number(COMPANY_THRESHOLD),
                    })
                  : automatic("off")
              }
              start={COMPANY_CREDITS}
              added={added}
              startAt={COMPANY_AT}
              pressed={false}
              words={billing("creditsWord", { count: COMPANY_CREDITS + added })}
              action={billing("topUp")}
              locale={locale}
            />
          </div>
        </div>
      </Stage>
    </LandingSection>
  )
}
