"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { useAuth } from "@/components/auth-provider"
import { BackLink } from "@/components/back-link"
import { CompanyLogo } from "@/components/company/company-logo"
import { SessionPlay } from "@/components/company/session-play"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { useSessionPlayer } from "@/hooks/use-session-player"
import { apiFetch } from "@/lib/api"
import type { Brand, Company } from "@/types/company"

/** The test a candidate takes; for a company member's preview, `testHref` is the test's page:
 * while playing, the back arrow goes to its interview list, and once finished, a button does. */
export function SessionView({
  id,
  testHref,
}: {
  id: string
  testHref?: string
}) {
  const t = useTranslations("session")
  const interviews = useTranslations("interviews")
  const back = testHref && (
    <BackLink href={testHref.slice(0, testHref.lastIndexOf("/"))}>
      {interviews("title")}
    </BackLink>
  )
  const { user, loading } = useAuth()
  const {
    session,
    question,
    topics,
    topicsLoaded,
    playing,
    missing,
    finishing,
    answer,
    advance,
    finishInterview,
  } = useSessionPlayer(id)
  const [brand, setBrand] = useState<Brand | null>(null)
  const inviteId = session?.candidate_invite_id
  const practice = Boolean(session?.practice)
  const router = useRouter()
  // A practice round, once every section is finished, opens its results with every answer.
  const practiceDone =
    practice &&
    !playing &&
    topicsLoaded &&
    (topics.length
      ? topics.every((topic) => topic.status === "finished")
      : session?.status === "finished")

  useEffect(() => {
    if (practiceDone) {
      router.replace(`/practice/rounds/${inviteId}`)
    }
  }, [practiceDone, inviteId, router])

  // A member's preview comes from its test's page (/company/{id}/...), so its company is known;
  // a preview has no invite behind it.
  const previewCompany = testHref?.split("/")[2]

  // Who the interview is for, for the logo; without it the interview goes on as before.
  useEffect(() => {
    const brandOf = previewCompany
      ? apiFetch<Company>(`/companies/companies/${previewCompany}`).then(
          (company) => ({
            company: company.name,
            logo_url: company.logo_url ?? null,
          })
        )
      : inviteId && !practice
        ? apiFetch<Brand>(`/companies/candidates/${inviteId}/brand`)
        : null

    brandOf?.then(setBrand).catch(() => setBrand(null))
  }, [inviteId, previewCompany, practice])

  if (!loading && !user) {
    return <SignInPrompt message={t("signIn")} />
  }

  if (missing || !session) {
    return missing ? (
      <p className="py-24 text-center text-base text-muted-foreground">
        {t("missing")}
      </p>
    ) : null
  }

  const sections = topics.length
    ? topics
    : [
        {
          id: session.id,
          topic_title: session.topic_title,
          status: session.status,
          total: session.total,
          answered: session.answered,
        },
      ]
  const finished =
    topicsLoaded && sections.every((topic) => topic.status === "finished")
  const progress = sections.reduce(
    (sum, topic) => ({
      answered:
        sum.answered +
        (topic.id === session.id ? session.answered : topic.answered),
      total: sum.total + topic.total,
    }),
    { answered: 0, total: 0 }
  )

  if (!playing) {
    // A practice round goes on to its results instead.
    if (!finished || practice) {
      return null
    }

    return (
      // Centered on the screen, like the home page's start.
      <div className="flex min-h-[calc(100svh-3.5rem-6rem)] flex-col items-center justify-center gap-8 pb-24 text-center">
        <div className="space-y-3">
          <h1 className="font-heading text-3xl font-medium tracking-tight text-balance normal-case">
            {session.interview_title ?? session.topic_title}
          </h1>
          <p className="text-muted-foreground">{t("done")}</p>
        </div>
        {testHref && (
          <Button
            className="h-12 px-6 text-base"
            render={
              <Link href={testHref.slice(0, testHref.lastIndexOf("/"))} />
            }
            nativeButton={false}
          >
            {t("toTest")}
          </Button>
        )}
      </div>
    )
  }

  const section = {
    number: sections.findIndex((topic) => topic.id === session.id) + 1,
    count: sections.length,
  }

  return (
    <SessionPlay
      session={session}
      progress={progress}
      section={section}
      question={question}
      onAnswer={answer}
      onAdvance={advance}
      onFinish={finishInterview}
      finishing={finishing}
      back={back}
      brand={
        brand?.logo_url && (
          <CompanyLogo
            url={brand.logo_url}
            name={brand.company}
            className="h-14 w-auto max-w-32 shrink-0 rounded-xl object-contain"
          />
        )
      }
    />
  )
}
