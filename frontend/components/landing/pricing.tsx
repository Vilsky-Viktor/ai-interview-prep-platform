import { CheckIcon } from "lucide-react"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"
import { Button } from "@/components/ui/button"
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
    <Button
      variant="outline"
      className="h-10 px-5 text-base"
      render={<Link href="/pricing" />}
      nativeButton={false}
    >
      {t("see")}
    </Button>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={see}>
      <Mockup>
        <ul className="space-y-3">
          {points.map((point) => (
            <li
              key={point}
              className="flex items-center gap-3 rounded-2xl bg-muted/60 p-4 text-sm"
            >
              <CheckIcon className="size-4 shrink-0 text-primary" />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </Mockup>
    </LandingSection>
  )
}
