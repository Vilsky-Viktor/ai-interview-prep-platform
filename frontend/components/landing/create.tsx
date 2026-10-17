import { getTranslations } from "next-intl/server"

import { CreateFlow } from "@/components/landing/create-flow"
import { CreateTemplateDemo } from "@/components/landing/create-template-demo"
import { DEMO_BAND, DemoLabel } from "@/components/landing/demo-panel"
import { LandingSection } from "@/components/landing/section"

/** How an interview is created, in two ways, each in its own group of panels playing on their
 * own: a job description typed, leading into its topics being adjusted; or a template used.
 * Side by side from laptops up, with "or" on the line between; one under the other below. */
export async function CreateSection() {
  const t = await getTranslations("landing.create")

  return (
    <LandingSection id="how" title={t("title")} text={t("text")}>
      <div className="grid lg:grid-cols-[minmax(0,2fr)_auto_minmax(0,1fr)]">
        {/* The panels' own labels line up with the template group's heading. */}
        <div className={DEMO_BAND}>
          <div className="grid flex-1 lg:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]">
            <CreateFlow
              labels={{
                describe: t("describe"),
                adjust: t("adjust"),
                ask: t("ask"),
              }}
            />
          </div>
        </div>
        {/* A line between the groups with "or" on it: down from laptops up, across below. */}
        <div className="relative flex items-center justify-center py-6 lg:px-5 lg:py-0">
          <div className="absolute inset-x-0 top-1/2 h-px bg-border lg:inset-x-auto lg:inset-y-0 lg:left-1/2 lg:h-auto lg:w-px" />
          <span className="relative rounded-full border bg-background px-3 py-1 font-heading text-base text-muted-foreground lowercase">
            {t("or")}
          </span>
        </div>
        <div className={DEMO_BAND}>
          <DemoLabel>{t("fromTemplate")}</DemoLabel>
          <CreateTemplateDemo />
        </div>
      </div>
    </LandingSection>
  )
}
