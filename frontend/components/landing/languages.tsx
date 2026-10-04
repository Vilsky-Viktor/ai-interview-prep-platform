import { cn } from "cn"
import { getLocale, getTranslations } from "next-intl/server"

import { LandingSection } from "@/components/landing/section"
import { LANGUAGE_NAMES, LOCALES } from "@/constants/i18n"

// Each card's tilt (degrees) and lift (pixels), picked by its place in the list. Fixed, so
// the scatter looks random but is the same for everyone and on every render.
const TILTS = [-6, 3, -2, 5, -4, 2, -5, 4, -3, 6, -1, 3]
const LIFTS = [6, -8, 2, -4, 10, -6, 4, -10, 8, -2, 0, -6, 6]

export async function LanguagesSection() {
  const t = await getTranslations("landing.languages")
  const locale = await getLocale()

  return (
    <LandingSection
      title={t("title")}
      text={t("text", { count: LOCALES.length })}
    >
      {/* The cards sit on the page itself; screen readers skip them, the text says it. */}
      <div aria-hidden className="mx-auto w-full max-w-4xl">
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-6 py-4">
          {LOCALES.map((code, index) => (
            <span
              key={code}
              lang={code}
              className={cn(
                "rounded-xl bg-muted px-4 py-2 text-base",
                code === locale && "text-primary"
              )}
              style={{
                transform: `translateY(${LIFTS[index % LIFTS.length]}px) rotate(${TILTS[index % TILTS.length]}deg)`,
              }}
            >
              {LANGUAGE_NAMES[code]}
            </span>
          ))}
        </div>
      </div>
    </LandingSection>
  )
}
