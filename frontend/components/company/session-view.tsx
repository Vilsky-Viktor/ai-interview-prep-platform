"use client"

import { useAuth } from "@/components/auth-provider"
import { SessionPlay } from "@/components/company/session-play"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { useSessionPlayer } from "@/hooks/use-session-player"

export function SessionView({ id }: { id: string }) {
  const { user, loading } = useAuth()
  const {
    session,
    question,
    result,
    topics,
    topicsLoaded,
    playing,
    missing,
    finishing,
    answer,
    advance,
    finishInterview,
  } = useSessionPlayer(id)

  if (!loading && !user) {
    return <SignInPrompt message="Sign in to continue this interview." />
  }

  if (missing || !session) {
    return missing ? (
      <p className="py-24 text-center text-base text-muted-foreground">
        This session doesn&apos;t exist.
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
    if (!finished) {
      return null
    }

    return (
      <div className="space-y-8">
        <h1 className="font-heading text-3xl font-medium tracking-tight text-balance">
          {session.interview_title ?? session.topic_title}
        </h1>
        <p className="text-muted-foreground">
          You have finished the interview. Good luck!
        </p>
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
      result={result}
      onAnswer={answer}
      onAdvance={advance}
      onFinish={finishInterview}
      finishing={finishing}
    />
  )
}
