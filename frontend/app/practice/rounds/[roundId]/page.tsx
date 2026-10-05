import { cookies } from "next/headers"
import Link from "next/link"
import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { PageHeader } from "@/components/page-header"
import { PracticeActions } from "@/components/practice/practice-actions"
import { PracticeReview } from "@/components/practice/practice-review"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { PracticeRound } from "@/types/round"

export const generateMetadata = () => translatedTitle("practice", "results")

/** A talent's practice round: the grade, each topic's score, and every question with the
 * right answer and their own pick. An unfinished round offers to continue it. */
export default async function PracticeRoundPage({
  params,
}: {
  params: Promise<{ roundId: string }>
}) {
  const { roundId } = await params
  const t = await getTranslations("practice")

  if (!(await cookies()).has(TOKEN_COOKIE)) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={t("signIn")} />
      </main>
    )
  }

  const round = await serverFetch<PracticeRound>(
    `/rounds/practice/rounds/${roundId}`
  )

  if (!round) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-10 px-6 py-12">
      <PageHeader
        back={
          <BackLink href={`/practice/${round.template_id}`}>
            {t("title")}
          </BackLink>
        }
        title={
          <div className="flex items-start justify-between gap-4">
            <h1 className="min-w-0 flex-1 font-heading text-3xl font-medium tracking-tight text-balance normal-case">
              {round.title ?? t("title")}
            </h1>
            {round.finished && (
              <PracticeActions
                templateId={round.template_id}
                startLabel={t("again")}
              />
            )}
          </div>
        }
      />

      {!round.finished && round.open_session_id ? (
        <div className="space-y-6 py-12 text-center">
          <p className="text-base text-muted-foreground">{t("notFinished")}</p>
          <Button
            className="h-12 px-6 text-base"
            render={<Link href={`/sessions/${round.open_session_id}`} />}
            nativeButton={false}
          >
            {t("continue")}
          </Button>
        </div>
      ) : (
        <>
          {/* One centered double card, both halves transparent with a line between: the grade,
              and how many the talent picked an answer for. */}
          <div className="mx-auto flex w-fit flex-wrap items-stretch divide-x overflow-hidden rounded-2xl border">
            <div className="flex items-baseline gap-4 px-8 py-6">
              <p className="text-6xl font-light text-primary tabular-nums">
                {round.grade ?? 0}%
              </p>
              <p className="text-base text-muted-foreground">{t("grade")}</p>
            </div>
            <div className="flex items-baseline gap-4 px-8 py-6">
              <p className="text-6xl font-light text-primary tabular-nums">
                {round.answered}
                {/* The total smaller, so the answered count stands out. */}
                <span className="text-3xl">/{round.total}</span>
              </p>
              <p className="text-base text-muted-foreground">
                {t("answeredLabel")}
              </p>
            </div>
          </div>
          {round.topics.map((topic) => (
            <section key={topic.title} className="space-y-4">
              <div className="flex items-center justify-between gap-4">
                <h2 className="font-heading text-2xl font-medium normal-case">
                  {topic.title}
                </h2>
                <p className="w-24 text-center">
                  <span className="block text-4xl font-light tabular-nums">
                    {topic.score == null ? "—" : `${topic.score}%`}
                  </span>
                  <span className="block text-sm text-muted-foreground">
                    {t("gradeLabel")}
                  </span>
                </p>
              </div>
              <PracticeReview
                sessionId={topic.session_id}
                items={topic.review}
              />
            </section>
          ))}
        </>
      )}
    </main>
  )
}
