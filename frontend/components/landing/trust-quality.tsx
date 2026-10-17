import {
  HistoryIcon,
  ScaleIcon,
  ShieldCheckIcon,
  UserRoundCheckIcon,
} from "lucide-react"
import { getTranslations } from "next-intl/server"

import { DEMO_GROUP } from "@/components/landing/demo-panel"
import { IconCard } from "@/components/landing/icon-card"
import { QualityLoop } from "@/components/landing/quality-loop"
import { LandingSection } from "@/components/landing/section"
import { LocalizedLink } from "@/components/localized-link"
import {
  QUALITY_STEPS,
  type QualityStep,
  TRUST_CARDS,
} from "@/constants/trust-quality-demo"

const ICONS = {
  person: UserRoundCheckIcon,
  fair: ScaleIcon,
  laws: ShieldCheckIcon,
  log: HistoryIcon,
}

const DOCUMENT_LINK = "underline underline-offset-4 hover:text-foreground"

/** Trust, quality and compliance: the loop that keeps questions good, and what keeps the
 * hiring fair and lawful under it, with links to the documents. */
export async function TrustQualitySection() {
  const t = await getTranslations("landing.trustQuality")
  const steps = (part: "labels" | "lines") =>
    Object.fromEntries(
      QUALITY_STEPS.map((key) => [key, t(`steps.${key}.${part}`)])
    ) as Record<QualityStep, string>
  const link = (href: string) =>
    function DocumentLink(chunks: React.ReactNode) {
      return (
        <LocalizedLink href={href} className={DOCUMENT_LINK}>
          {chunks}
        </LocalizedLink>
      )
    }

  return (
    <LandingSection id="trust" title={t("title")} text={t("text")}>
      <div className="flex flex-col gap-14">
        <div className={DEMO_GROUP}>
          <QualityLoop labels={steps("labels")} lines={steps("lines")} />
        </div>
        <ul className="grid gap-3 sm:grid-cols-2">
          {TRUST_CARDS.map((key) => (
            <IconCard
              key={key}
              icon={ICONS[key]}
              title={t(`cards.${key}.title`)}
            >
              {key === "laws"
                ? t.rich("cards.laws.text", {
                    documents: link("/documents"),
                  })
                : t(`cards.${key}.text`)}
            </IconCard>
          ))}
        </ul>
      </div>
    </LandingSection>
  )
}
