"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { SessionPlay } from "@/components/company/session-play"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type {
  InterviewSession,
  SessionAnswerResult,
  SessionTopic,
} from "@/types/company"
import type { AnswerInput, NextQuestion } from "@/types/round"

type Step = [InterviewSession, NextQuestion | null]

function fetchStep(id: string): Promise<Step> {
  return Promise.all([
    apiFetch<InterviewSession>(`/rounds/sessions/${id}`),
    apiFetch<NextQuestion | null>(`/rounds/sessions/${id}/next`),
  ])
}

function openTopic(topics: SessionTopic[]) {
  return topics.find((topic) => topic.status !== "finished")
}

export function SessionView({ id }: { id: string }) {
  const { user, loading } = useAuth()
  const [session, setSession] = useState<InterviewSession | null>(null)
  const [question, setQuestion] = useState<NextQuestion | null>(null)
  const [result, setResult] = useState<SessionAnswerResult | null>(null)
  const [topics, setTopics] = useState<SessionTopic[]>([])
  const [topicsLoaded, setTopicsLoaded] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [missing, setMissing] = useState(false)
  const started = useRef(false)
  const [openAnswer, setOpenAnswer] = useState({
    canSubmit: false,
    grading: false,
  })
  const [finishing, setFinishing] = useState(false)

  const showStep = useCallback(([nextSession, nextQuestion]: Step) => {
    setSession(nextSession)
    setQuestion(nextQuestion)
    setResult(null)
  }, [])

  useEffect(() => {
    if (user) {
      fetchStep(id).then(showStep).catch(() => setMissing(true))
    }
  }, [user, id, showStep])

  useEffect(() => {
    if (!user || !session) {
      return
    }

    apiFetch<SessionTopic[]>(`/rounds/sessions/${session.id}/topics`)
      .then(setTopics)
      .catch(() => setTopics([]))
      .finally(() => setTopicsLoaded(true))
  }, [user, session?.id])

  useEffect(() => {
    if (user && session && !started.current) {
      started.current = true
      void begin()
    }
  }, [user, session])

  async function openSection(sectionId: string): Promise<void> {
    const step = await fetchStep(sectionId)

    if (step[1]) {
      showStep(step)
      setPlaying(true)

      return
    }

    const finished =
      step[0].status === "finished"
        ? step[0]
        : await apiFetch<InterviewSession>(`/rounds/sessions/${sectionId}/finish`, {
            method: "POST",
          })
    const list = await apiFetch<SessionTopic[]>(
      `/rounds/sessions/${finished.id}/topics`
    )
    const upcoming = openTopic(list)

    setTopics(list)
    setSession(finished)
    setQuestion(null)
    setResult(null)

    if (!upcoming || upcoming.id === sectionId) {
      setPlaying(false)

      return
    }

    await openSection(upcoming.id)
  }

  async function begin() {
    if (!session) {
      return
    }

    try {
      const list = topics.length
        ? topics
        : await apiFetch<SessionTopic[]>(`/rounds/sessions/${session.id}/topics`)
      const upcoming = openTopic(list)

      setTopics(list)
      setTopicsLoaded(true)

      if (!upcoming) {
        return
      }

      await openSection(upcoming.id)
    } catch {
      toast.error("Couldn't start the interview. Please try again.")
    }
  }

  async function answer(input: AnswerInput) {
    if (!session || !question) {
      return false
    }

    try {
      const next = await apiFetch<SessionAnswerResult>(
        `/rounds/sessions/${session.id}/answers`,
        {
          method: "POST",
          body: JSON.stringify({ question_id: question.question_id, ...input }),
        }
      )
      setResult({
        ...next,
        option_index: "option_index" in input ? input.option_index : null,
      })
      setSession(
        (current) =>
          current && {
            ...current,
            answered: next.answered,
            current_score: next.current_score ?? current.current_score,
          }
      )
      setTopics((current) =>
        current.map((topic) =>
          topic.id === session.id ? { ...topic, answered: next.answered } : topic
        )
      )

      return true
    } catch (error) {
      toast.error(
        apiErrorMessage(error, "Couldn't submit your answer. Please try again.")
      )

      return false
    }
  }

  async function finishInterview() {
    if (!session || finishing) {
      return
    }

    setFinishing(true)

    try {
      const list = topics.length
        ? topics
        : await apiFetch<SessionTopic[]>(`/rounds/sessions/${session.id}/topics`)
      const pending = list.filter((topic) => topic.status !== "finished")
      const ids = pending.length > 0 ? pending.map((topic) => topic.id) : [session.id]

      for (const sectionId of ids) {
        await apiFetch<InterviewSession>(`/rounds/sessions/${sectionId}/finish`, {
          method: "POST",
        })
      }

      setTopics(list.map((topic) => ({ ...topic, status: "finished" })))
      setSession((current) => current && { ...current, status: "finished" })
      setQuestion(null)
      setResult(null)
      setTopicsLoaded(true)
      setPlaying(false)
    } catch {
      toast.error("Couldn't finish the interview. Please try again.")
      setFinishing(false)
    }
  }

  async function advance() {
    if (!session) {
      return
    }

    try {
      await openSection(session.id)
    } catch {
      toast.error("Couldn't continue. Please try again.")
    }
  }

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
        sum.answered + (topic.id === session.id ? session.answered : topic.answered),
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
        <p className="text-muted-foreground">You have finished the interview. Good luck!</p>
      </div>
    )
  }

  return (
    <SessionPlay
      session={session}
      progress={progress}
      question={question}
      result={result}
      openAnswer={openAnswer}
      onAnswer={answer}
      onStatusChange={setOpenAnswer}
      onAdvance={advance}
      onFinish={finishInterview}
      finishing={finishing}
    />
  )
}
