"use client"

import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import {
  advancedQuestionId,
  clearRoundCursor,
  markAdvancedTo,
  questionFromReview,
  resultFromReview,
} from "@/lib/round-cursor"
import type {
  AnswerInput,
  AnswerResult,
  NextQuestion,
  ReviewItem,
  Round,
} from "@/types/round"

type Step = [Round, NextQuestion | null]

function fetchStep(id: string): Promise<Step> {
  return Promise.all([
    apiFetch<Round>(`/rounds/rounds/${id}`),
    apiFetch<NextQuestion | null>(`/rounds/rounds/${id}/next`),
  ])
}

/** A round's state and actions: loading it (back where the user left off), answering,
moving on and finishing. */
export function useRoundPlayer(id: string) {
  const { user } = useAuth()
  const [round, setRound] = useState<Round | null>(null)
  const [question, setQuestion] = useState<NextQuestion | null>(null)
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [missing, setMissing] = useState(false)
  const [finishing, setFinishing] = useState(false)

  const showStep = useCallback(([nextRound, nextQuestion]: Step) => {
    setRound(nextRound)
    setQuestion(nextQuestion)
    setResult(null)
  }, [])

  useEffect(() => {
    if (!user) {
      return
    }

    Promise.all([
      fetchStep(id),
      apiFetch<ReviewItem[]>(`/rounds/rounds/${id}/review`),
    ])
      .then(([[nextRound, nextQuestion], review]) => {
        setRound(nextRound)
        const cursor = advancedQuestionId(id)
        const last = [...review].reverse().find((item) => item.answer)

        if (cursor && nextQuestion?.question_id === cursor) {
          setQuestion(nextQuestion)
          setResult(null)

          return
        }

        if (last) {
          const restored = resultFromReview(last, nextRound)

          if (restored) {
            setQuestion(questionFromReview(last))
            setResult(restored)

            return
          }
        }

        setQuestion(nextQuestion)
        setResult(null)
      })
      .catch(() => setMissing(true))
  }, [user, id])

  async function loadNext() {
    try {
      const step = await fetchStep(id)

      if (step[1]) {
        markAdvancedTo(id, step[1].question_id)
      }

      showStep(step)
    } catch {
      toast.error("Couldn't load the next question. Please try again.")
    }
  }

  async function answer(input: AnswerInput) {
    try {
      const next = await apiFetch<AnswerResult>(
        `/rounds/rounds/${id}/answers`,
        {
          method: "POST",
          body: JSON.stringify({
            question_id: question?.question_id,
            ...input,
          }),
        }
      )
      clearRoundCursor(id)
      setResult({
        ...next,
        option_index: input.option_index,
      })
      setRound(
        (current) =>
          current && {
            ...current,
            answered: next.answered,
            current_score: next.current_score,
            passed: next.passed,
          }
      )

      return true
    } catch (error) {
      toast.error(
        apiErrorMessage(error, "Couldn't submit your answer. Please try again.")
      )

      return false
    }
  }

  async function finish() {
    setFinishing(true)

    try {
      clearRoundCursor(id)
      setRound(
        await apiFetch<Round>(`/rounds/rounds/${id}/finish`, { method: "POST" })
      )
    } catch {
      toast.error("Couldn't finish the round. Please try again.")
      setFinishing(false)
    }
  }

  return {
    round,
    question,
    result,
    missing,
    finishing,
    loadNext,
    answer,
    finish,
  }
}
