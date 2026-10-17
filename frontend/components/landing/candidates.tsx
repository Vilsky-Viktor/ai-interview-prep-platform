import { getTranslations } from "next-intl/server"

import { CandidatesDemo } from "@/components/landing/candidates-demo"
import { DEMO_BAND } from "@/components/landing/demo-panel"
import { LandingSection } from "@/components/landing/section"

/** What candidates see: the invitation accepted and three kinds of question answered, played in
 * one panel. */
export async function CandidatesSection() {
  const t = await getTranslations("landing.candidates")

  return (
    <LandingSection id="candidates" title={t("title")} text={t("text")}>
      <div className={DEMO_BAND}>
        <CandidatesDemo />
      </div>
    </LandingSection>
  )
}
