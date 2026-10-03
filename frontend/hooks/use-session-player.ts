"use client"

import { useTranslations } from "next-intl"
import { useCallback, useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import { fetchStep, openTopic, type Step } from "@/lib/sessions"
import type {
  InterviewSession,
  SessionAnswerResult,
  SessionTopic,
} from "@/types/company"
import type { AnswerInput, NextQuestion } from "@/types/round"

/** A candidate's interview: its sections, the current question, answering, moving on through
sections and finishing. */
export function useSessionPlayer(id: string) {
  const t = useTranslations("session")
  const rounds = useTranslations("rounds")
  const { user } = useAuth()
  const [session, setSession] = useState<InterviewSession | null>(null)
  const [question, setQuestion] = useState<NextQuestion | null>(null)
  const [result, setResult] = useState<SessionAnswerResult | null>(null)
  const [topics, setTopics] = useState<SessionTopic[]>([])
  const [topicsLoaded, setTopicsLoaded] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [missing, setMissing] = useState(false)
  const started = useRef(false)
  const [finishing, setFinishing] = useState(false)

  const showStep = useCallback(([nextSession, nextQuestion]: Step) => {
    setSession(nextSession)
    setQuestion(nextQuestion)
    setResult(null)
  }, [])

  useEffect(() => {
    if (user) {
      fetchStep(id)
        .then(showStep)
        .catch(() => setMissing(true))
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
        : await apiFetch<InterviewSession>(
            `/rounds/sessions/${sectionId}/finish`,
            {
              method: "POST",
            }
          )
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
        : await apiFetch<SessionTopic[]>(
            `/rounds/sessions/${session.id}/topics`
          )
      const upcoming = openTopic(list)

      setTopics(list)
      setTopicsLoaded(true)

      if (!upcoming) {
        return
      }

      await openSection(upcoming.id)
    } catch {
      toast.error(t("startFailed"))
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
        option_index: input.option_index,
      })
      setSession(
        (current) =>
          current && {
            ...current,
            answered: next.answered,
          }
      )
      setTopics((current) =>
        current.map((topic) =>
          topic.id === session.id
            ? { ...topic, answered: next.answered }
            : topic
        )
      )

      return true
    } catch (error) {
      toast.error(apiErrorMessage(error, rounds("submitFailed")))

      // Refused because the question's time ran out: the next one opens.
      if (error instanceof ApiError && error.status === 409) {
        await advance()
      }

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
        : await apiFetch<SessionTopic[]>(
            `/rounds/sessions/${session.id}/topics`
          )
      const pending = list.filter((topic) => topic.status !== "finished")
      const ids =
        pending.length > 0 ? pending.map((topic) => topic.id) : [session.id]

      for (const sectionId of ids) {
        await apiFetch<InterviewSession>(
          `/rounds/sessions/${sectionId}/finish`,
          {
            method: "POST",
          }
        )
      }

      setTopics(list.map((topic) => ({ ...topic, status: "finished" })))
      setSession((current) => current && { ...current, status: "finished" })
      setQuestion(null)
      setResult(null)
      setTopicsLoaded(true)
      setPlaying(false)
    } catch {
      toast.error(t("finishFailed"))
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
      toast.error(t("continueFailed"))
    }
  }

  return {
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
  }
}
