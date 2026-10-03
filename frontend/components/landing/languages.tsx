import { getLocale, getTranslations } from "next-intl/server"

import { LandingSection, Stage } from "@/components/landing/section"
import { LANGUAGE_NAMES, LOCALES } from "@/constants/i18n"

export async function LanguagesSection() {
  const t = await getTranslations("landing.languages")
  const locale = await getLocale()

  return (
    <LandingSection
      title={t("title")}
      text={t("text", { count: LOCALES.length })}
    >
      <Stage>
        <p className="flex flex-wrap justify-center gap-x-4 gap-y-2 text-center font-heading text-lg">
          {LOCALES.map((code) => (
            <span
              key={code}
              lang={code}
              className={code === locale ? "text-primary" : "text-muted-foreground"}
            >
              {LANGUAGE_NAMES[code]}
            </span>
          ))}
        </p>
      </Stage>
    </LandingSection>
  )
}
