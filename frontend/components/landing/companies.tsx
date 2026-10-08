import { cn } from "cn"
import { getLocale, getNow, getTranslations } from "next-intl/server"

import { CandidateSignals } from "@/components/company/candidate-signals"
import { CandidateStatsDemo } from "@/components/landing/candidate-stats-demo"
import { LandingSection, Stage } from "@/components/landing/section"
import { Badge } from "@/components/ui/badge"
import { DEMO_PASS_MARK } from "@/constants/landing"
import { formatDate } from "@/lib/format"
import { gradeTone } from "@/lib/grade-tone"
import type { Candidate } from "@/types/company"

const POINTS = ["own", "timed", "flags", "answers"] as const
const DAY_MS = 24 * 60 * 60 * 1000

// The in-process candidate's progress and grade after each answer, as the demo plays them.
const LIVE = [
  { progress: 40, grade: 75 },
  { progress: 41, grade: 72 },
  { progress: 42, grade: 74 },
]

// The picture's candidates: one passed, one under way, one below the passing grade.
const CANDIDATES = [
  {
    email: "anna@example.com",
    daysAgo: 3,
    progress: 100,
    grade: 86,
    status: "finished",
    signals: { tab_leaves: 0, copies: 0, fast_answers: 0 },
  },
  {
    email: "mark@example.com",
    daysAgo: 1,
    progress: 40,
    grade: null,
    status: "in_process",
    signals: { tab_leaves: 0, copies: 0, fast_answers: 0 },
  },
  {
    email: "lee@example.com",
    daysAgo: 2,
    progress: 100,
    grade: 58,
    status: "finished",
    // Left the page, copied text and answered too fast, each a different number of times.
    signals: { tab_leaves: 2, copies: 1, fast_answers: 3 },
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

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className="rounded-2xl border bg-background text-start">
          {/* The test and its passing grade, which colors each finished grade. */}
          <p className="border-b px-8 py-5 text-sm text-muted-foreground">
            {t("role", { mark: DEMO_PASS_MARK })}
          </p>
          <ul className="divide-y">
            {CANDIDATES.map(
              ({ email, daysAgo, progress, grade, status, signals }) => (
                <li
                  key={email}
                  className="flex flex-col gap-4 px-8 py-5 sm:flex-row sm:items-center sm:justify-between"
                >
                  <span className="min-w-0 space-y-1">
                    <span className="block text-lg font-medium break-all">
                      {email}
                    </span>
                    {/* The date, then any signals, as in the real list. */}
                    <span className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                      {formatDate(
                        new Date(now - daysAgo * DAY_MS).toISOString(),
                        locale
                      )}
                      <CandidateSignals candidate={signals as Candidate} />
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
                            className={cn(
                              "block text-2xl font-light tabular-nums",
                              grade == null && "text-muted-foreground",
                              gradeTone(
                                grade == null ? null : grade >= DEMO_PASS_MARK
                              )
                            )}
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
              )
            )}
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
