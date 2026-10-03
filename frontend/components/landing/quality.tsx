import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

const STEPS = ["flagged", "checked", "fixed"] as const

export async function QualitySection() {
  const t = await getTranslations("landing.quality")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <ol className={`${PANEL} p-6 text-base`}>
          {STEPS.map((key, index) => (
            <li key={key} className="relative flex gap-4 pb-8 last:pb-0">
              {index < STEPS.length - 1 && (
                <span className="absolute start-[4.5px] top-5 bottom-1 w-px bg-border" />
              )}
              <span
                className={
                  index === STEPS.length - 1
                    ? "mt-2 size-2.5 shrink-0 rounded-full bg-primary"
                    : "mt-2 size-2.5 shrink-0 rounded-full border-2 border-primary bg-background"
                }
              />
              <span>{t(`steps.${key}`)}</span>
            </li>
          ))}
        </ol>
      </Stage>
    </LandingSection>
  )
}
