import Link from "next/link"
import { getLocale, getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"
import { Button } from "@/components/ui/button"

const POINTS = ["own", "timed", "flags", "private"] as const

// The picture's scorecards: one clean, two with flags.
const CANDIDATES = [
  { letter: "A", score: 0.86, flag: null },
  { letter: "B", score: 0.72, flag: "left" },
  { letter: "C", score: 0.41, flag: "rushed" },
] as const

export async function CompaniesSection() {
  const t = await getTranslations("landing.companies")
  const percent = new Intl.NumberFormat(await getLocale(), { style: "percent" })

  const extra = (
    <div className="space-y-4 pt-1">
      <ul className="mx-auto w-fit space-y-1.5 text-start text-base text-muted-foreground sm:text-lg">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-3">
            <span className="mt-3 size-1.5 shrink-0 rounded-full bg-primary" />
            <span>{t(`points.${point}`)}</span>
          </li>
        ))}
      </ul>
      <Button
        className="h-11 px-7 text-base"
        render={<Link href="/company" />}
        nativeButton={false}
      >
        {t("start")}
      </Button>
    </div>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={extra}>
      <Stage>
        <div className={`${PANEL} text-base`}>
          <div className="flex justify-between px-6 py-2.5 text-sm text-muted-foreground">
            <span>{t("candidate")}</span>
            <span>{t("score")}</span>
          </div>
          <ul className="divide-y divide-border/70 border-t border-border/70">
            {CANDIDATES.map(({ letter, score, flag }) => (
              <li key={letter} className="flex items-center gap-4 px-6 py-3">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-sm">
                  {letter}
                </span>
                <span className="min-w-0 flex-1">
                  {flag && (
                    <span className="rounded-full border px-2.5 py-1 text-sm text-muted-foreground">
                      {t(flag)}
                    </span>
                  )}
                </span>
                <span className="font-medium tabular-nums">
                  {percent.format(score)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </Stage>
    </LandingSection>
  )
}
