import { getTranslations } from "next-intl/server"

import { AutomateStage } from "@/components/landing/automate-stage"
import { DEMO_GROUP } from "@/components/landing/demo-panel"
import { LandingSection } from "@/components/landing/section"
import { AUTOMATE_CARDS, type AutomateCard } from "@/constants/automate-demo"

/** Automate your hiring: your platform, AI apps and job boards wired to prepza, and Slack after
 * it. */
export async function AutomateSection() {
  const t = await getTranslations("landing.automate")
  const labels = Object.fromEntries(
    AUTOMATE_CARDS.map((key) => [key, t(`labels.${key}`)])
  ) as Record<AutomateCard, string>

  return (
    <LandingSection id="automate" title={t("title")} text={t("text")}>
      <div className={DEMO_GROUP}>
        <AutomateStage labels={labels} />
      </div>
    </LandingSection>
  )
}
