import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"
import { LANGUAGE_NAMES, LOCALES } from "@/constants/i18n"

export async function LanguagesSection() {
  const t = await getTranslations("landing.languages")

  return (
    <LandingSection
      title={t("title")}
      text={t("text", { count: LOCALES.length })}
      reverse
    >
      <Mockup className="flex flex-wrap gap-2 space-y-0">
        {LOCALES.map((code) => (
          <span
            key={code}
            lang={code}
            className="bidi-auto rounded-full bg-muted/60 px-3 py-1.5 text-sm"
          >
            {LANGUAGE_NAMES[code]}
          </span>
        ))}
      </Mockup>
    </LandingSection>
  )
}
