import { cn } from "cn"
import { getLocale, getNow, getTranslations } from "next-intl/server"

import { LandingSection, Stage } from "@/components/landing/section"
import { formatDate } from "@/lib/format"

const ITEMS = ["first", "second"] as const
// The picture's two rounds: the last one, four days ago, and today's.
const SCORES = [50, 100]
const DAY_MS = 24 * 60 * 60 * 1000

/** One answer in the comparison, as compare-cell.tsx shows it. */
function Cell({
  correct,
  label,
  text,
}: {
  correct: boolean
  label: string
  text: string
}) {
  return (
    <div className="space-y-1 text-sm">
      <p
        className={cn(
          "font-medium",
          correct
            ? "text-green-600 dark:text-green-400"
            : "text-red-600 dark:text-red-400"
        )}
      >
        {label}
      </p>
      <p>{text}</p>
    </div>
  )
}

/** The round comparison as it really looks (app/rounds/compare), with its own labels: a
 * question missed in the last round and answered right in this one. */
export async function GapsSection() {
  const t = await getTranslations("landing.gaps")
  const rounds = await getTranslations("rounds")
  const locale = await getLocale()
  const now = (await getNow()).getTime()
  const dates = [now - 4 * DAY_MS, now].map((time) =>
    formatDate(new Date(time).toISOString(), locale)
  )

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className="space-y-4 text-start">
          <p className="font-heading text-xl font-medium tracking-tight lowercase">
            {rounds("compareTitle")}
            <span className="text-primary">.</span>
          </p>
          <div className="grid grid-cols-2 gap-3">
            {SCORES.map((score, index) => (
              <div key={score} className="rounded-2xl border bg-background p-5">
                <p className="font-heading text-2xl font-medium tabular-nums">
                  {score}%
                </p>
                <p className="text-sm text-muted-foreground">{dates[index]}</p>
              </div>
            ))}
          </div>
          <ul className="divide-y rounded-2xl border bg-background">
            {ITEMS.map((key) => (
              <li key={key} className="space-y-3 p-5">
                <p className="font-medium">{t(`items.${key}.question`)}</p>
                <div className="grid grid-cols-2 gap-3">
                  <Cell
                    correct={false}
                    label={rounds("incorrect")}
                    text={t(`items.${key}.wrong`)}
                  />
                  <Cell
                    correct
                    label={rounds("correct")}
                    text={t(`items.${key}.right`)}
                  />
                </div>
              </li>
            ))}
          </ul>
        </div>
      </Stage>
    </LandingSection>
  )
}
