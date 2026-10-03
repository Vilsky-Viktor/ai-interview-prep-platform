import { FlagIcon, RefreshCwIcon, ShieldCheckIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"

const STEPS = [
  { key: "flagged", icon: FlagIcon },
  { key: "checked", icon: ShieldCheckIcon },
  { key: "fixed", icon: RefreshCwIcon },
] as const

export async function QualitySection() {
  const t = await getTranslations("landing.quality")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Mockup>
        <ol className="space-y-3">
          {STEPS.map(({ key, icon: Icon }) => (
            <li
              key={key}
              className="flex items-center gap-4 rounded-2xl bg-muted/60 p-4"
            >
              <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Icon className="size-5" />
              </span>
              <span className="text-sm">{t(`steps.${key}`)}</span>
            </li>
          ))}
        </ol>
      </Mockup>
    </LandingSection>
  )
}
