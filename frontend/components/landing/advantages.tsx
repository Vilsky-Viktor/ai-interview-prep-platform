import {
  DollarSignIcon,
  LanguagesIcon,
  ListOrderedIcon,
  TimerIcon,
  UsersRoundIcon,
  ZapIcon,
} from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection } from "@/components/landing/section"

// prepza's advantages, each with its icon, in the trust section's cards (trust.tsx). Only
// what's true today, without comparisons to named tools.
const POINTS = [
  { key: "speed", Icon: ZapIcon },
  { key: "anyRole", Icon: UsersRoundIcon },
  { key: "cheating", Icon: TimerIcon },
  { key: "price", Icon: DollarSignIcon },
  { key: "results", Icon: ListOrderedIcon },
  { key: "languages", Icon: LanguagesIcon },
] as const

/** What a company gets with prepza, at a glance, before the sections that show each part. */
export async function AdvantagesSection() {
  const t = await getTranslations("landing.advantages")

  return (
    <LandingSection id="advantages" title={t("title")} text={t("text")}>
      <ul className="mx-auto mt-8 grid w-full max-w-5xl gap-8 pe-4 sm:grid-cols-2 sm:pe-0 lg:grid-cols-3">
        {POINTS.map(({ key, Icon }) => (
          <li
            key={key}
            className="relative rounded-2xl border bg-background p-6"
          >
            {/* On the card's top end corner, over its border: a circle in the page's background
                that hides the line; titles are short enough to end before it, and the text keeps the
                card's usual padding. */}
            <span className="absolute -end-7 -top-7 flex size-20 items-center justify-center rounded-full bg-background">
              <Icon aria-hidden className="size-12 text-primary" />
            </span>
            <span className="block space-y-1">
              {/* One line, lowercase with the logo's blue dot, like the site's titles. */}
              <span className="block text-base font-medium whitespace-nowrap lowercase">
                {t(`points.${key}.title`)}
                <span className="text-primary">.</span>
              </span>
              <span className="block text-base text-muted-foreground">
                {t(`points.${key}.text`)}
              </span>
            </span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}
