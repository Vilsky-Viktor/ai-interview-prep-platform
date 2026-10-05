import { MinusIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { type ReactNode, useState } from "react"

import { Countdown } from "@/components/company/countdown"
import { QuestionActions } from "@/components/questions/question-actions"
import { QuestionText } from "@/components/questions/question-text"
import { ChoiceOptions } from "@/components/session/choice-options"
import { RoundFooter } from "@/components/session/round-footer"
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
import { useIntegritySignals } from "@/hooks/use-integrity-signals"
import type { InterviewSession, SessionAnswerResult } from "@/types/company"
import type { AnswerInput, NextQuestion } from "@/types/round"

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
  // A company member's preview: the way back, beside the header.
  back?: ReactNode
  // The company's logo, small, before the section's title.
  brand?: ReactNode
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
  back,
  brand,
}: SessionPlayProps) {
  const t = useTranslations("session")
  const rounds = useTranslations("rounds")
  const common = useTranslations("common")
  const [confirmFinish, setConfirmFinish] = useState(false)
  useIntegritySignals(session.id, session.status === "in_progress")
  const allAnswered = progress.total > 0 && progress.answered === progress.total

  return (
    <div className="space-y-8 pb-28">
      <div className="relative">
        {back}
        <SessionHeader
          brand={brand}
          session={session}
          progress={progress}
          section={section}
          question={result ? null : question}
          // Quietly on to the next question: a message would only distract.
          onTimeUp={onAdvance}
        />
      </div>
      {question && (
        <div key={question.question_id} className="space-y-6">
          <QuestionText
            heading
            text={question.text}
            className="text-2xl leading-snug font-medium"
          />
          {/* Candidates never learn whether they were right: their pick only stays marked. */}
          <ChoiceOptions
            options={question.options}
            onAnswer={(option_index) => onAnswer({ option_index })}
          />
          {/* Judged once answered, not mid-question. */}
          {result && (
            <QuestionActions
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
          {finishing ? rounds("finishing") : t("finish")}
        </Button>
        <div className="flex items-center gap-3">
          {result && (
            <Button className="h-12 px-6 text-base" onClick={onAdvance}>
              {rounds("next")}
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
            <DialogTitle className="no-dot">{t("finishTitle")}</DialogTitle>
            <DialogDescription>
              {section.count > 1
                ? t("endsAll", { count: section.count })
                : t("endsOne")}
              {!allAnswered &&
                ` ${t("unscored", { count: progress.total - progress.answered })}`}
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
              {common("cancel")}
            </DialogClose>
            <Button
              className="h-10 px-5 text-base"
              disabled={finishing}
              onClick={onFinish}
            >
              {finishing ? rounds("finishing") : rounds("finish")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function SessionHeader({
  brand,
  session,
  progress,
  section,
  question,
  onTimeUp,
}: {
  brand?: ReactNode
  session: InterviewSession
  progress: { answered: number; total: number }
  section: { number: number; count: number }
  // The question waiting for an answer, with its clock.
  question: NextQuestion | null
  // Called when the question's clock reaches zero: the server counts it as wrong, and the
  // next one opens.
  onTimeUp: () => void
}) {
  const t = useTranslations("session")

  // The company's logo on the left of the section's title and the progress bar.
  return (
    <div className="flex items-center gap-4">
      {brand}
      <div className="min-w-0 flex-1 space-y-3">
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
                  {t("section", {
                    number: section.number,
                    count: section.count,
                  })}
                </span>
              </>
            )}
          </p>
          <p className="flex shrink-0 items-center text-sm text-muted-foreground tabular-nums">
            {question?.seconds_left != null && (
              <>
                <Countdown
                  key={question.question_id}
                  seconds={question.seconds_left}
                  onExpire={onTimeUp}
                />
                <MinusIcon
                  aria-hidden
                  className="mx-1.5 size-3.5 text-foreground/55"
                />
              </>
            )}
            {progress.answered} / {progress.total}
          </p>
        </div>
        <Progress
          value={
            progress.total ? (progress.answered / progress.total) * 100 : 0
          }
        />
      </div>
    </div>
  )
}
