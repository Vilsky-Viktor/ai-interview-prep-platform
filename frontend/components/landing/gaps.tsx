import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

// The order a round asks in: unanswered first, then the lowest latest scores.
const QUESTIONS = [
  { key: "first", status: "fresh", style: "text-primary" },
  { key: "second", status: "missed", style: "text-foreground" },
  { key: "third", status: "right", style: "text-muted-foreground" },
] as const

export async function GapsSection() {
  const t = await getTranslations("landing.gaps")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <ol className={`${PANEL} divide-y divide-border/70`}>
          {QUESTIONS.map(({ key, status, style }, index) => (
            <li key={key} className="flex gap-4 px-6 py-5 text-base">
              <span className="text-muted-foreground tabular-nums">
                {index + 1}
              </span>
              <div className="min-w-0 space-y-1">
                <p>{t(`questions.${key}`)}</p>
                <p className={`flex items-center gap-2 text-sm ${style}`}>
                  <span className="size-1.5 rounded-full bg-current" />
                  {t(status)}
                </p>
              </div>
            </li>
          ))}
        </ol>
      </Stage>
    </LandingSection>
  )
}
