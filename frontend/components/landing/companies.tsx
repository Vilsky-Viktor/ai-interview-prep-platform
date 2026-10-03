import { CheckIcon } from "lucide-react"
import Link from "next/link"
import { getLocale, getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"
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
    <>
      <ul className="space-y-2 text-sm text-muted-foreground">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-2">
            <CheckIcon className="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{t(`points.${point}`)}</span>
          </li>
        ))}
      </ul>
      <Button
        className="h-10 px-5 text-base"
        render={<Link href="/company" />}
        nativeButton={false}
      >
        {t("start")}
      </Button>
    </>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={extra}>
      <Mockup>
        <div className="flex justify-between px-4 text-xs text-muted-foreground">
          <span>{t("candidate")}</span>
          <span>{t("score")}</span>
        </div>
        <ul className="space-y-2">
          {CANDIDATES.map(({ letter, score, flag }) => (
            <li
              key={letter}
              className="flex items-center gap-3 rounded-2xl bg-muted/60 p-4"
            >
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-medium text-primary">
                {letter}
              </span>
              <span className="min-w-0 flex-1">
                {flag && (
                  <span className="rounded-full bg-red-600/10 px-2.5 py-1 text-xs font-medium text-red-600 dark:text-red-400">
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
      </Mockup>
    </LandingSection>
  )
}
