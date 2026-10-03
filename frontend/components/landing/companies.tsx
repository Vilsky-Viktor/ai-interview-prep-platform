import Link from "next/link"
import { getLocale, getTranslations } from "next-intl/server"

import { Button } from "@/components/ui/button"

const POINTS = ["own", "timed", "flags", "private"] as const

// The picture's scorecards: one clean, two with flags.
const CANDIDATES = [
  { letter: "A", score: 0.86, flag: null },
  { letter: "B", score: 0.72, flag: "left" },
  { letter: "C", score: 0.41, flag: "rushed" },
] as const

/** The hiring side, on a dark panel of its own so companies see it's for them. */
export async function CompaniesSection() {
  const t = await getTranslations("landing.companies")
  const percent = new Intl.NumberFormat(await getLocale(), { style: "percent" })

  return (
    <section className="grid gap-12 rounded-[2rem] bg-foreground p-8 text-background sm:p-14 md:grid-cols-2">
      <div className="space-y-6">
        <h2 className="font-heading text-3xl font-medium tracking-tight text-balance sm:text-4xl">
          {t("title")}
        </h2>
        <p className="text-lg leading-relaxed text-background/70">{t("text")}</p>
        <ul className="space-y-3 text-background/70">
          {POINTS.map((point) => (
            <li key={point} className="flex gap-3">
              <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-primary" />
              <span>{t(`points.${point}`)}</span>
            </li>
          ))}
        </ul>
        <Button
          variant="secondary"
          className="h-11 px-6 text-base"
          render={<Link href="/company" />}
          nativeButton={false}
        >
          {t("start")}
        </Button>
      </div>
      <div aria-hidden className="self-center">
        <div className="rounded-2xl border border-background/15 text-sm">
          <div className="flex justify-between px-5 py-3 text-xs text-background/50">
            <span>{t("candidate")}</span>
            <span>{t("score")}</span>
          </div>
          <ul className="divide-y divide-background/15 border-t border-background/15">
            {CANDIDATES.map(({ letter, score, flag }) => (
              <li key={letter} className="flex items-center gap-3 px-5 py-4">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-background/10 text-xs">
                  {letter}
                </span>
                <span className="min-w-0 flex-1 text-xs text-red-400">
                  {flag && t(flag)}
                </span>
                <span className="font-medium tabular-nums">
                  {percent.format(score)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
