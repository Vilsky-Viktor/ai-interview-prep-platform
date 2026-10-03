import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

// The order a round asks in: unanswered first, then the lowest latest scores.
const QUESTIONS = [
  { key: "first", status: "fresh", style: "text-primary" },
  { key: "second", status: "missed", style: "text-red-600 dark:text-red-400" },
  { key: "third", status: "right", style: "text-green-600 dark:text-green-400" },
] as const

export async function GapsSection() {
  const t = await getTranslations("landing.gaps")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <ol className={`${PANEL} divide-y divide-border/70`}>
          {QUESTIONS.map(({ key, status, style }, index) => (
            <li key={key} className="flex gap-4 px-5 py-4">
              <span className="text-muted-foreground tabular-nums">
                {index + 1}
              </span>
              <div className="min-w-0 space-y-1">
                <p>{t(`questions.${key}`)}</p>
                <p className={`flex items-center gap-1.5 text-xs ${style}`}>
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
