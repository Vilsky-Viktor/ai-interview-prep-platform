import { cookies } from "next/headers"
import Link from "next/link"
import { getLocale, getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { PageHeader } from "@/components/page-header"
import { StartPractice } from "@/components/practice/start-practice"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { PracticeRoundSummary } from "@/types/round"
import type { Template } from "@/types/superadmin"

export const generateMetadata = () => translatedTitle("practice", "history")

/** A talent's rounds on one practice test, newest first, with their grades, to see progress.
 * Each opens its results. */
export default async function PracticeHistoryPage({
  params,
}: {
  params: Promise<{ templateId: string }>
}) {
  const { templateId } = await params
  const t = await getTranslations("practice")
  const locale = await getLocale()

  if (!(await cookies()).has(TOKEN_COOKIE)) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={t("signIn")} />
      </main>
    )
  }

  const [template, rounds] = await Promise.all([
    serverFetch<Template>(`/library/templates/${templateId}`),
    serverFetch<PracticeRoundSummary[]>(
      `/rounds/practice/${templateId}/rounds`
    ),
  ])

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={
          <BackLink href={`/practice/${templateId}`}>{t("title")}</BackLink>
        }
        title={
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1 space-y-1">
              <h1 className="font-heading text-3xl font-medium tracking-tight">
                {t("history")}
              </h1>
              {template && (
                <p className="text-base text-muted-foreground normal-case">
                  {template.title}
                </p>
              )}
            </div>
            <StartPractice templateId={templateId} label={t("again")} />
          </div>
        }
      />

      {!rounds?.length ? (
        <p className="py-16 text-center text-muted-foreground">
          {t("noRounds")}
        </p>
      ) : (
        <ul className="divide-y rounded-2xl border">
          {rounds.map((round) => (
            <li key={round.round_id}>
              <Link
                href={`/practice/rounds/${round.round_id}`}
                className="flex items-center justify-between gap-4 p-6 transition-colors hover:bg-muted/50"
              >
                <time
                  dateTime={round.started_at}
                  className="text-lg"
                  suppressHydrationWarning
                >
                  {formatDate(round.started_at, locale)}
                </time>
                {/* Progress and grade, labelled like the candidate list's numbers. */}
                <span className="flex shrink-0 items-center gap-6 sm:gap-10">
                  <span className="w-20 text-center sm:w-24">
                    <span className="block text-2xl font-light tabular-nums">
                      {round.progress}%
                    </span>
                    <span className="block text-sm text-muted-foreground">
                      {t("progressLabel")}
                    </span>
                  </span>
                  <span className="w-20 text-center sm:w-24">
                    <span
                      className={
                        round.grade == null
                          ? "block text-2xl font-light text-muted-foreground"
                          : "block text-2xl font-light tabular-nums"
                      }
                    >
                      {round.grade == null ? "—" : `${round.grade}%`}
                    </span>
                    <span className="block text-sm text-muted-foreground">
                      {t("gradeLabel")}
                    </span>
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
