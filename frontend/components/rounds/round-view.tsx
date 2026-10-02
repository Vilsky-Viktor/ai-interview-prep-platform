"use client"

import { useState } from "react"

import { useAuth } from "@/components/auth-provider"
import { QuestionActions } from "@/components/questions/question-actions"
import { QuestionText } from "@/components/questions/question-text"
import { ChatPanel } from "@/components/rounds/chat-panel"
import { ChoiceOptions } from "@/components/rounds/choice-options"
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
import { useRoundPlayer } from "@/hooks/use-round-player"

export function RoundView({ id }: { id: string }) {
  const { user, loading } = useAuth()
  const {
    round,
    question,
    result,
    missing,
    finishing,
    loadNext,
    answer,
    finish,
  } = useRoundPlayer(id)
  const [confirmFinish, setConfirmFinish] = useState(false)

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
          <QuestionText
            heading
            text={question.text}
            className="text-2xl leading-snug font-medium"
          />
          <ChoiceOptions
            options={question.options}
            result={result}
            onAnswer={(option_index) => answer({ option_index })}
          />
          {/* Judged once the answer is revealed, not before. */}
          {result && <QuestionActions questionId={question.question_id} />}
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
            <DialogTitle className="no-dot">Finish this round?</DialogTitle>
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
