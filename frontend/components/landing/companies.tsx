import Link from "next/link"
import { getLocale, getNow, getTranslations } from "next-intl/server"

import { CandidateStatsDemo } from "@/components/landing/candidate-stats-demo"
import { LandingSection, Stage } from "@/components/landing/section"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/format"

const POINTS = ["own", "timed", "flags", "private"] as const
const DAY_MS = 24 * 60 * 60 * 1000

// The in-process candidate's progress and grade after each answer, as the demo plays them.
const LIVE = [
  { progress: 40, grade: 75 },
  { progress: 41, grade: 72 },
  { progress: 42, grade: 74 },
]

// The picture's candidates: one finished, one under way, one not started yet.
const CANDIDATES = [
  {
    email: "anna@example.com",
    daysAgo: 3,
    progress: 100,
    grade: 86,
    status: "finished",
  },
  {
    email: "mark@example.com",
    daysAgo: 1,
    progress: 40,
    grade: null,
    status: "in_process",
  },
  {
    email: "lee@example.com",
    daysAgo: 0,
    progress: 0,
    grade: null,
    status: "invited",
  },
] as const

/** An interview's candidates as the company really sees them
 * (components/company/candidate-list.tsx), then what keeps the interview fair. */
export async function CompaniesSection() {
  const t = await getTranslations("landing.companies")
  const candidates = await getTranslations("candidates")
  const statuses = await getTranslations("candidateStatus")
  const locale = await getLocale()
  const now = (await getNow()).getTime()

  const start = (
    <div className="pt-2">
      <Button
        className="h-11 px-6 text-base"
        render={<Link href="/company" />}
        nativeButton={false}
      >
        {t("start")}
      </Button>
    </div>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={start}>
      <Stage>
        <ul className="divide-y rounded-2xl border bg-background text-start">
          {CANDIDATES.map(({ email, daysAgo, progress, grade, status }) => (
            <li
              key={email}
              className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
            >
              <span className="min-w-0 space-y-1">
                <span className="block text-lg font-medium break-all">
                  {email}
                </span>
                <span className="block text-sm text-muted-foreground">
                  {formatDate(
                    new Date(now - daysAgo * DAY_MS).toISOString(),
                    locale
                  )}
                </span>
              </span>
              <span className="flex shrink-0 items-center gap-6">
                {status === "in_process" ? (
                  <CandidateStatsDemo
                    steps={LIVE}
                    labels={{
                      progress: candidates("progress"),
                      grade: candidates("grade"),
                    }}
                  />
                ) : (
                  <>
                    <span className="w-20 text-center sm:w-24">
                      <span className="block text-2xl font-light tabular-nums">
                        {progress}%
                      </span>
                      <span className="block text-sm text-muted-foreground">
                        {candidates("progress")}
                      </span>
                    </span>
                    <span className="w-20 text-center sm:w-24">
                      <span
                        className={
                          grade == null
                            ? "block text-2xl font-light text-muted-foreground tabular-nums"
                            : "block text-2xl font-light tabular-nums"
                        }
                      >
                        {grade == null ? "—" : `${grade}%`}
                      </span>
                      <span className="block text-sm text-muted-foreground">
                        {candidates("grade")}
                      </span>
                    </span>
                  </>
                )}
                <span className="flex w-28 justify-end">
                  <Badge
                    variant="outline"
                    className="h-7 px-3 text-sm font-light"
                  >
                    {statuses(status)}
                  </Badge>
                </span>
              </span>
            </li>
          ))}
        </ul>
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
