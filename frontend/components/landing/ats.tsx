import { cn } from "cn"
import { getTranslations } from "next-intl/server"

import { LandingSection } from "@/components/landing/section"
import { ATS_PROVIDERS } from "@/constants/ats"

const POINTS = ["move", "back"] as const

/** The ATSs a company can connect, as their own full logos in their colors. */
export async function AtsSection() {
  const t = await getTranslations("landing.ats")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <ul className="mx-auto mt-16 flex w-full max-w-4xl flex-wrap items-center justify-center gap-y-12">
        {ATS_PROVIDERS.map((provider) => (
          <li
            key={provider.id}
            className="flex basis-1/2 justify-center px-4 sm:basis-1/3"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={provider.wordmark}
              alt={provider.name}
              className={cn(
                "h-10 w-auto max-w-full object-contain sm:h-12",
                provider.darkWhite && "dark:brightness-0 dark:invert"
              )}
            />
          </li>
        ))}
      </ul>
      <ul className="mx-auto mt-20 grid w-full max-w-4xl gap-x-12 gap-y-3 text-muted-foreground sm:grid-cols-2">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-3">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-primary" />
            <span>{t(`points.${point}`)}</span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}
