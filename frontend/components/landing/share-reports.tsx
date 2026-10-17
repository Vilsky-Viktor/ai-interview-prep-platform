import { getTranslations } from "next-intl/server"

import { DEMO_BAND } from "@/components/landing/demo-panel"
import { ReportsDemo } from "@/components/landing/reports-demo"
import { LandingSection } from "@/components/landing/section"
import { StartButton } from "@/components/landing/start-button"

/** Detailed reports and quick sharing: the candidates list and a candidate's report, each
 * shared, played in one panel; then the button to create an interview. */
export async function ShareReportsSection() {
  const t = await getTranslations("landing")

  return (
    <LandingSection
      id="reports"
      title={t("shareReports.title")}
      text={t("shareReports.text")}
    >
      <div className={DEMO_BAND}>
        <ReportsDemo />
      </div>
      <div className="flex justify-center">
        <StartButton label={t("closing.start")} />
      </div>
    </LandingSection>
  )
}
