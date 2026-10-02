import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import { useState } from "react"

import { QuestionActions } from "@/components/questions/question-actions"
import { QuestionText } from "@/components/questions/question-text"
import { ChoiceOptions } from "@/components/rounds/choice-options"
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
import { scorePassed } from "@/lib/rounds"
import type { InterviewSession, SessionAnswerResult } from "@/types/company"
import type { AnswerInput, AnswerResult, NextQuestion } from "@/types/round"

type SessionPlayProps = {
  session: InterviewSession
  progress: { answered: number; total: number }
  // This topic's place among the interview's sections.
  section: { number: number; count: number }
  question: NextQuestion | null
  result: SessionAnswerResult | null
  onAnswer: (input: AnswerInput) => Promise<boolean>
  onAdvance: () => void
  onFinish: () => void
  finishing: boolean
}

export function SessionPlay({
  session,
  progress,
  section,
  question,
  result,
  onAnswer,
  onAdvance,
  onFinish,
  finishing,
}: SessionPlayProps) {
  const [confirmFinish, setConfirmFinish] = useState(false)
  const shown = result && session.share_results ? shownResult(result) : null
  const allAnswered = progress.total > 0 && progress.answered === progress.total

  return (
    <div className="space-y-8 pb-28">
      <SessionHeader session={session} progress={progress} section={section} />
      {question && (
        <div key={question.question_id} className="space-y-6">
          <QuestionText
            heading
            text={question.text}
            className="text-2xl leading-snug font-medium"
          />
          <ChoiceOptions
            options={question.options}
            result={shown}
            onAnswer={(option_index) => onAnswer({ option_index })}
          />
          {/* Judged once answered, not mid-question. */}
          {result && (
            <QuestionActions
              questionId={question.question_id}
              basePath={`/rounds/sessions/${session.id}/questions/${question.question_id}`}
            />
          )}
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
            <DialogTitle className="no-dot">Finish the whole interview?</DialogTitle>
            <DialogDescription>
              {section.count > 1
                ? `This ends all ${section.count} sections, not only this one.`
                : "This ends the interview."}
              {!allAnswered &&
                ` ${progress.total - progress.answered} unanswered ${
                  progress.total - progress.answered === 1
                    ? "question"
                    : "questions"
                } won't be scored.`}
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
  section,
}: {
  session: InterviewSession
  progress: { answered: number; total: number }
  section: { number: number; count: number }
}) {
  const score = session.current_score ?? 0

  return (
    <div className="space-y-3">
      <div className="flex min-w-0 items-center justify-between gap-4">
        <p className="flex min-w-0 items-center text-sm text-muted-foreground">
          <span className="truncate">{session.topic_title}</span>
          {section.count > 1 && (
            <>
              <MinusIcon
                aria-hidden
                className="mx-1.5 size-3.5 shrink-0 text-foreground/55"
              />
              <span className="shrink-0 tabular-nums">
                Section {section.number} of {section.count}
              </span>
            </>
          )}
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

/** Candidates learn only whether they were right; the right option stays hidden. */
function shownResult(result: SessionAnswerResult): AnswerResult | null {
  if (result.correct == null) {
    return null
  }

  const optionIndex = result.option_index ?? null

  return {
    answer_id: result.answer_id,
    correct: result.correct,
    correct_option_index: result.correct ? optionIndex : null,
    current_score: result.current_score ?? 0,
    answered: result.answered,
    total: result.total,
    option_index: optionIndex,
  }
}
