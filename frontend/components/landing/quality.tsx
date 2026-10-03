import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

const STEPS = ["flagged", "checked", "fixed"] as const

export async function QualitySection() {
  const t = await getTranslations("landing.quality")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <ol className={`${PANEL} space-y-0 p-5`}>
          {STEPS.map((key, index) => (
            <li key={key} className="flex gap-4">
              <div className="flex flex-col items-center">
                <span
                  className={
                    index === STEPS.length - 1
                      ? "mt-1.5 size-2.5 rounded-full bg-primary"
                      : "mt-1.5 size-2.5 rounded-full border-2 border-primary"
                  }
                />
                {index < STEPS.length - 1 && (
                  <span className="my-1 w-px flex-1 bg-border" />
                )}
              </div>
              <span className="pb-6 last:pb-0">{t(`steps.${key}`)}</span>
            </li>
          ))}
        </ol>
      </Stage>
    </LandingSection>
  )
}
