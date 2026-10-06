import { MinusIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { type ReactNode, useEffect, useRef, useState } from "react"

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
import type { InterviewSession } from "@/types/company"
import type { AnswerInput, NextQuestion } from "@/types/round"

type SessionPlayProps = {
  session: InterviewSession
  progress: { answered: number; total: number }
  // This topic's place among the interview's sections.
  section: { number: number; count: number }
  question: NextQuestion | null
  onAnswer: (input: AnswerInput) => Promise<boolean>
  onAdvance: () => Promise<void>
  onFinish: () => Promise<void>
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
  // The question whose clock ran out, announced to screen readers; the screen moves on quietly.
  const [timedOut, setTimedOut] = useState<string | null>(null)
  // The option picked on the question on screen: it can change until it's sent, on Next, on
  // finishing or when the time runs out.
  const [pick, setPick] = useState<{ question: string; option: number } | null>(
    null
  )
  const [sending, setSending] = useState(false)
  useIntegritySignals(session.id, session.status === "in_progress")
  const questionRef = useRef<HTMLDivElement>(null)
  const questionId = question?.question_id
  const chosen = pick && pick.question === questionId ? pick.option : null
  const answered = progress.answered + (chosen === null ? 0 : 1)
  const allAnswered = progress.total > 0 && answered === progress.total

  // Each new question takes focus, so the keyboard and screen readers start from it.
  useEffect(() => {
    if (questionId) {
      questionRef.current?.querySelector<HTMLElement>("[role=heading]")?.focus()
    }
  }, [questionId])

  // Saves the pick, if there is one, then does `then`; when saving fails, only if `always`.
  // Nothing can be picked and the clock can't move on while it's sent, so neither Next nor the
  // clock can move on twice; a failed send keeps the question's real time left.
  async function sendThen(then: () => Promise<void>, always = false) {
    setSending(true)

    try {
      const saved =
        chosen === null || (await onAnswer({ option_index: chosen }))

      if (saved || always) {
        await then()
      }
    } finally {
      setSending(false)
    }
  }

  const sendAndAdvance = () => sendThen(onAdvance)

  return (
    <div className="space-y-8 pb-28">
      <div className="relative">
        {back}
        <SessionHeader
          brand={brand}
          session={session}
          progress={progress}
          section={section}
          question={question}
          sending={sending}
          // The pick counts, and quietly on to the next question: a message would only distract.
          onTimeUp={() => {
            setTimedOut(question?.question_id ?? null)
            // The question's time is over even if its pick can't be saved: the next opens.
            void sendThen(onAdvance, true)
          }}
        />
      </div>
      <p aria-live="polite" className="sr-only">
        {timedOut && <span key={timedOut}>{t("timeUp")}</span>}
      </p>
      {question && (
        <div key={question.question_id} ref={questionRef} className="space-y-6">
          {/* In the interview's own language, so screen readers read it with the right voice. */}
          <div lang={session.language ?? undefined} className="space-y-6">
            <QuestionText
              heading
              text={question.text}
              className="text-2xl leading-snug font-medium"
            />
            {/* Candidates never learn whether they were right: their pick only stays marked. */}
            <ChoiceOptions
              options={question.options}
              chosen={chosen}
              disabled={sending}
              onChoose={(option) =>
                setPick({ question: question.question_id, option })
              }
            />
          </div>
          {/* Judged once picked, not before. */}
          {chosen !== null && (
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
          disabled={finishing || sending}
          onClick={() => setConfirmFinish(true)}
        >
          {finishing ? rounds("finishing") : t("finish")}
        </Button>
        <div className="flex items-center gap-3">
          {chosen !== null && (
            // Focus stays on the pick, so it can still be changed; Next is the following stop.
            <Button
              className="h-12 px-6 text-base"
              disabled={sending}
              onClick={sendAndAdvance}
            >
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
                ` ${t("unscored", { count: progress.total - answered })}`}
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
              // The pick on screen is saved first, so it counts; finishing goes ahead even when
              // it can't be saved.
              onClick={() => sendThen(onFinish, true)}
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
  sending,
  onTimeUp,
}: {
  brand?: ReactNode
  session: InterviewSession
  progress: { answered: number; total: number }
  section: { number: number; count: number }
  // The question waiting for an answer, with its clock.
  question: NextQuestion | null
  // The pick is being sent: the clock runs on, but moves on only once that's done.
  sending: boolean
  // Called when the question's clock reaches zero: the server counts it as wrong, and the
  // next one opens.
  onTimeUp: () => void
}) {
  const t = useTranslations("session")
  const candidates = useTranslations("candidates")

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
                  paused={sending}
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
          aria-label={candidates("progress")}
          value={
            progress.total ? (progress.answered / progress.total) * 100 : 0
          }
        />
      </div>
    </div>
  )
}
