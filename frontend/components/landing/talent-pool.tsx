import { EyeOffIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"
import { LinkedInIcon } from "@/components/linkedin-icon"

const POINTS = ["free", "practice", "first", "link"] as const

// The picture's suggested talents: their name and first score on a similar template.
const TALENTS = [
  { name: "Maria Kovac", score: 94 },
  { name: "Tom Wright", score: 91 },
  { name: "Aisha Rahman", score: 88 },
] as const

/** Talents suggested for a company's test from free practice (Phase 6 of docs/company-plan.md). */
export async function TalentPoolSection() {
  const t = await getTranslations("landing.talent")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className={`${PANEL} text-start`}>
          <p className="border-b p-5 text-sm text-muted-foreground">
            {t("suggested")}
          </p>
          <ul className="divide-y">
            {TALENTS.map(({ name, score }) => (
              <li
                key={name}
                className="flex items-center gap-3 p-4 sm:gap-6 sm:p-5"
              >
                <span className="min-w-0 flex-1 truncate text-lg">{name}</span>
                {/* Its own column, so the icons line up whatever the name's length. */}
                <span className="shrink-0 text-muted-foreground">
                  <LinkedInIcon />
                </span>
                <span className="w-16 shrink-0 text-center sm:w-24">
                  <span className="block text-2xl font-light tabular-nums">
                    {score}%
                  </span>
                  <span className="block text-sm text-muted-foreground">
                    {t("score")}
                  </span>
                </span>
                {/* Hide, for a talent who doesn't fit, as on a test's suggestions. */}
                <span className="flex size-9 shrink-0 items-center justify-center text-muted-foreground">
                  <EyeOffIcon className="size-6" />
                </span>
              </li>
            ))}
          </ul>
        </div>
      </Stage>
      <ul className="mx-auto grid w-full max-w-2xl gap-x-8 gap-y-3 text-muted-foreground sm:grid-cols-2">
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
