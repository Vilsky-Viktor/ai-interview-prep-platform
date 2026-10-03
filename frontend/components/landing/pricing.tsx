import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"
import { serverFetch } from "@/lib/server-api"
import type { Catalog } from "@/types/billing"

export async function PricingSection() {
  const t = await getTranslations("landing.pricing")
  // The amounts come from billing, which decides them; without it, only the general points.
  const catalog = await serverFetch<Catalog>("/billing/catalog")
  const points = [
    ...(catalog
      ? [
          t("welcome", { count: catalog.welcome_user }),
          t("company", { count: catalog.welcome_company }),
        ]
      : []),
    t("never"),
    t("failed"),
  ]

  const see = (
    <Link
      href="/pricing"
      className="inline-block text-primary underline-offset-4 hover:underline"
    >
      {t("see")} →
    </Link>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={see}>
      <Stage>
        <ul className={`${PANEL} divide-y divide-border/70`}>
          {points.map((point) => (
            <li key={point} className="flex items-center gap-3 px-5 py-4">
              <span className="size-1.5 shrink-0 rounded-full bg-primary" />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </Stage>
    </LandingSection>
  )
}
