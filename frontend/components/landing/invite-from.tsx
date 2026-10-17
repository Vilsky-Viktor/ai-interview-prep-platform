import { getTranslations } from "next-intl/server"

import { DEMO_GROUP } from "@/components/landing/demo-panel"
import { InviteStage } from "@/components/landing/invite-stage"
import { LandingSection } from "@/components/landing/section"
import { INVITE_SOURCES, type InviteSource } from "@/constants/invite-demo"

/** Every way candidates come into an interview, around it, each wired to it. */
export async function InviteFromSection() {
  const t = await getTranslations("landing.sources")
  const labels = Object.fromEntries(
    INVITE_SOURCES.map(({ key }) => [key, t(`labels.${key}`)])
  ) as Record<InviteSource["key"], string>

  return (
    <LandingSection id="invite" title={t("title")} text={t("text")}>
      <div className={DEMO_GROUP}>
        <InviteStage labels={labels} interview={t("interview")} />
      </div>
    </LandingSection>
  )
}
