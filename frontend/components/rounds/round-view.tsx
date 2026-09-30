"use client"

import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { QuestionActions } from "@/components/questions/question-actions"
import { AnswerReveal } from "@/components/rounds/answer-reveal"
import { ChatPanel } from "@/components/rounds/chat-panel"
import { ChoiceOptions } from "@/components/rounds/choice-options"
import { OpenAnswerForm } from "@/components/rounds/open-answer-form"
import { RoundFooter } from "@/components/rounds/round-footer"
import { RoundHeader } from "@/components/rounds/round-header"
import { RoundSummary } from "@/components/rounds/round-summary"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { OPEN_ANSWER_FORM_ID } from "@/constants/rounds"
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

export function RoundView({ id }: { id: string }) {
  const { user, loading } = useAuth()
  const [round, setRound] = useState<Round | null>(null)
  const [question, setQuestion] = useState<NextQuestion | null>(null)
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [missing, setMissing] = useState(false)
  const [openAnswer, setOpenAnswer] = useState({
    canSubmit: false,
    grading: false,
  })
  const [confirmFinish, setConfirmFinish] = useState(false)
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
          body: JSON.stringify({ question_id: question?.question_id, ...input }),
        }
      )
      clearRoundCursor(id)
      setResult({
        ...next,
        option_index: "option_index" in input ? input.option_index : null,
        text: "text" in input ? input.text : null,
      })
      setRound(
        (current) =>
          current && {
            ...current,
            answered: next.answered,
            current_score: next.current_score,
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

  if (!loading && !user) {
    return <SignInPrompt message="Sign in to continue this round." />
  }

  if (missing) {
    return (
      <p className="py-24 text-center text-base text-muted-foreground">
        This round doesn&apos;t exist.
      </p>
    )
  }

  if (!round) {
    return null
  }

  if (round.status === "finished") {
    return <RoundSummary round={round} />
  }

  const allAnswered = round.answered === round.total

  return (
    <div className="space-y-8 pb-28">
      <RoundHeader round={round} />

      {question ? (
        <div key={question.question_id} className="space-y-6">
          <h1 className="text-2xl leading-snug font-medium">
            {question.text}
          </h1>
          {round.mode === "choice" && question.options ? (
            <ChoiceOptions
              options={question.options}
              result={result}
              onAnswer={(option_index) => answer({ option_index })}
            />
          ) : (
            <OpenAnswerForm
              answered={result !== null}
              initialText={result?.text ?? ""}
              onAnswer={(text) => answer({ text })}
              onStatusChange={setOpenAnswer}
            />
          )}
          {result && <AnswerReveal result={result} />}
          <QuestionActions questionId={question.question_id} />
          {result && <ChatPanel answerId={result.answer_id} />}
        </div>
      ) : (
        <p className="py-16 text-center text-muted-foreground">
          You answered every question in this round.
        </p>
      )}

      <RoundFooter>
        <Button
          variant={allAnswered ? "default" : "ghost"}
          className="h-12 px-6 text-base"
          disabled={finishing}
          onClick={() => (allAnswered ? finish() : setConfirmFinish(true))}
        >
          {finishing ? "Finishing…" : "Finish round"}
        </Button>
        <div className="flex items-center gap-3">
          {question && round.mode === "open" && !result && (
            <Button
              type="submit"
              form={OPEN_ANSWER_FORM_ID}
              className="h-12 px-6 text-base"
              disabled={!openAnswer.canSubmit}
            >
              {openAnswer.grading ? "Grading…" : "Submit answer"}
            </Button>
          )}
          {result && !allAnswered && (
            <Button className="h-12 px-6 text-base" onClick={() => loadNext()}>
              Next question
            </Button>
          )}
        </div>
      </RoundFooter>
      <Dialog
        open={confirmFinish}
        onOpenChange={(open) => {
          if (!open && !finishing) {
            setConfirmFinish(false)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>Finish this round?</DialogTitle>
            <DialogDescription>
              Unanswered questions won&apos;t be scored.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={finishing}
                />
              }
            >
              Cancel
            </DialogClose>
            <Button
              className="h-10 px-5 text-base"
              disabled={finishing}
              onClick={finish}
            >
              {finishing ? "Finishing…" : "Finish"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
