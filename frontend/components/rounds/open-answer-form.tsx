"use client"

import { ArrowUpIcon } from "lucide-react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { SUBMIT_HINT } from "@/constants/keys"
import { MAX_ANSWER_LENGTH, OPEN_ANSWER_FORM_ID } from "@/constants/rounds"
import { isSubmitShortcut } from "@/lib/keys"

export type OpenAnswerStatus = {
  canSubmit: boolean
  grading: boolean
}

type OpenAnswerFormProps = {
  answered: boolean
  initialText?: string
  onAnswer: (text: string) => Promise<boolean>
  onStatusChange?: (status: OpenAnswerStatus) => void
}

export function OpenAnswerForm({
  answered,
  initialText = "",
  onAnswer,
  onStatusChange,
}: OpenAnswerFormProps) {
  const [text, setText] = useState(initialText)
  const [grading, setGrading] = useState(false)

  useEffect(() => {
    onStatusChange?.({
      canSubmit: Boolean(text.trim()) && !grading && !answered,
      grading,
    })
  }, [text, grading, answered, onStatusChange])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!text.trim() || answered || grading) {
      return
    }

    setGrading(true)
    await onAnswer(text.trim())
    setGrading(false)
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (isSubmitShortcut(event)) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <form
      id={OPEN_ANSWER_FORM_ID}
      onSubmit={handleSubmit}
      className="w-full rounded-2xl border border-transparent bg-card p-3 transition-colors focus-within:border-ring"
    >
      <Textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        readOnly={answered || grading}
        maxLength={MAX_ANSWER_LENGTH}
        placeholder="Write your answer here ..."
        aria-label="Your answer"
        className="max-h-72 min-h-32 resize-none border-0 bg-transparent p-2 text-base shadow-none focus-visible:ring-0 md:text-base dark:bg-transparent"
      />
      {!answered && (
        <div className="flex items-center justify-between gap-4 pt-2 pl-2">
          <p className="text-xs text-muted-foreground">{SUBMIT_HINT}</p>
          <Button
            type="submit"
            size="icon-lg"
            className="rounded-full"
            disabled={!text.trim() || grading}
            aria-label="Submit answer"
          >
            <ArrowUpIcon />
          </Button>
        </div>
      )}
    </form>
  )
}
