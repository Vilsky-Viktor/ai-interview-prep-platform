import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import { useState } from "react"

import { QuestionActions } from "@/components/questions/question-actions"
import { AnswerReveal } from "@/components/rounds/answer-reveal"
import { ChoiceOptions } from "@/components/rounds/choice-options"
import {
  OpenAnswerForm,
  type OpenAnswerStatus,
} from "@/components/rounds/open-answer-form"
import { RoundFooter } from "@/components/rounds/round-footer"
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
import { Progress } from "@/components/ui/progress"
import { MODE_LABELS, OPEN_ANSWER_FORM_ID } from "@/constants/rounds"
import { scorePassed } from "@/lib/rounds"
import type { InterviewSession, SessionAnswerResult } from "@/types/company"
import type { AnswerInput, AnswerResult, NextQuestion } from "@/types/round"

type SessionPlayProps = {
  session: InterviewSession
  progress: { answered: number; total: number }
  question: NextQuestion | null
  result: SessionAnswerResult | null
  openAnswer: OpenAnswerStatus
  onAnswer: (input: AnswerInput) => Promise<boolean>
  onStatusChange: (status: OpenAnswerStatus) => void
  onAdvance: () => void
  onFinish: () => void
  finishing: boolean
}

export function SessionPlay({
  session,
  progress,
  question,
  result,
  openAnswer,
  onAnswer,
  onStatusChange,
  onAdvance,
  onFinish,
  finishing,
}: SessionPlayProps) {
  const [confirmFinish, setConfirmFinish] = useState(false)
  const shown =
    result && session.share_results ? shownResult(session.mode, result) : null
  const allAnswered = progress.total > 0 && progress.answered === progress.total

  return (
    <div className="space-y-8 pb-28">
      <SessionHeader session={session} progress={progress} />
      {question && (
        <div key={question.question_id} className="space-y-6">
          <h1 className="text-2xl leading-snug font-medium">{question.text}</h1>
          {session.mode === "choice" && question.options ? (
            <ChoiceOptions
              options={question.options}
              result={shown}
              onAnswer={(option_index) => onAnswer({ option_index })}
            />
          ) : (
            <OpenAnswerForm
              answered={result !== null}
              onAnswer={(text) => onAnswer({ text })}
              onStatusChange={onStatusChange}
            />
          )}
          {shown && <AnswerReveal result={shown} />}
          <QuestionActions
            questionId={question.question_id}
            basePath={`/rounds/sessions/${session.id}/questions/${question.question_id}`}
          />
        </div>
      )}
      <RoundFooter>
        <Button
          variant="ghost"
          className="h-12 px-6 text-base"
          disabled={finishing}
          onClick={() => setConfirmFinish(true)}
        >
          {finishing ? "Finishing…" : "Finish interview"}
        </Button>
        <div className="flex items-center gap-3">
          {question && session.mode === "open" && !result && (
            <Button
              type="submit"
              form={OPEN_ANSWER_FORM_ID}
              className="h-12 px-6 text-base"
              disabled={!openAnswer.canSubmit}
            >
              {openAnswer.grading ? "Grading…" : "Submit answer"}
            </Button>
          )}
          {result && (
            <Button className="h-12 px-6 text-base" onClick={onAdvance}>
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
            <DialogTitle>Finish this interview?</DialogTitle>
            {!allAnswered && (
              <DialogDescription>
                Unanswered questions won&apos;t be scored.
              </DialogDescription>
            )}
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
              onClick={onFinish}
            >
              {finishing ? "Finishing…" : "Finish"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function SessionHeader({
  session,
  progress,
}: {
  session: InterviewSession
  progress: { answered: number; total: number }
}) {
  const score = session.current_score ?? 0

  return (
    <div className="space-y-3">
      <div className="flex min-w-0 items-center justify-between gap-4">
        <p className="min-w-0 text-sm text-muted-foreground">
          {session.topic_title} · {MODE_LABELS[session.mode]}
        </p>
        <p className="flex shrink-0 items-center text-sm text-muted-foreground tabular-nums">
          {progress.answered} / {progress.total}
          {session.share_results && (
            <>
              <MinusIcon
                aria-hidden
                className="mx-1.5 size-3.5 text-foreground/55"
              />
              <span
                className={cn(
                  "text-xl font-light",
                  scorePassed(score)
                    ? "text-green-600 dark:text-green-400"
                    : "text-red-600 dark:text-red-400"
                )}
              >
                {score}%
              </span>
            </>
          )}
        </p>
      </div>
      <Progress
        value={progress.total ? (progress.answered / progress.total) * 100 : 0}
      />
    </div>
  )
}

function shownResult(
  mode: "open" | "choice",
  result: SessionAnswerResult
): AnswerResult | null {
  if (result.score == null) {
    return null
  }

  const optionIndex = result.option_index ?? null

  return {
    answer_id: result.answer_id,
    correct: result.correct ?? null,
    score: result.score,
    feedback: result.feedback ?? null,
    reference_answer: "",
    correct_option_index: mode === "choice" && result.correct ? optionIndex : null,
    current_score: result.current_score ?? result.score,
    answered: result.answered,
    total: result.total,
    option_index: optionIndex,
  }
}
