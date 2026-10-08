"use client"

import { cn } from "cn"
import {
  CircleAlertIcon,
  FlagIcon,
  RefreshCwIcon,
  ThumbsDownIcon,
  ThumbsUpIcon,
} from "lucide-react"
import { useEffect, useState } from "react"

import { AnswerOptions } from "@/components/questions/answer-options"
import { buttonVariants } from "@/components/ui/button"

// The demo's steps and how long each shows, in milliseconds. It starts with the weak question's
// report open, which is also what shows with reduced motion.
const STEPS = [
  { name: "open", ms: 2400 },
  { name: "press", ms: 400 },
  { name: "regenerating", ms: 2000 },
  { name: "regenerated", ms: 4000 },
  { name: "closed", ms: 1500 },
  { name: "flag", ms: 400 },
] as const

type Counts = { likes: number; dislikes: number; reports: number }

/** A question's votes and reports, and its re-generate and wrong-answer buttons, as
 * question-row.tsx shows them. */
function Feedback({
  counts,
  flagged,
  button,
  wrongAnswer,
}: {
  counts: Counts
  flagged?: "pressed" | "open"
  button: { label: string; spinning: boolean; pressed: boolean }
  wrongAnswer: string
}) {
  return (
    <span className="flex flex-wrap items-center justify-between gap-3 text-sm whitespace-nowrap text-muted-foreground tabular-nums sm:flex-col sm:items-end">
      <span className="flex items-center gap-4">
        <span className="flex items-center gap-1.5">
          <ThumbsUpIcon className="size-4" />
          {counts.likes}
        </span>
        <span className="flex items-center gap-1.5">
          <ThumbsDownIcon className="size-4" />
          {counts.dislikes}
        </span>
        <span
          className={cn(
            "-mx-2 -my-1 flex items-center gap-1.5 rounded-md px-2 py-1 transition-colors",
            flagged === "open" && "bg-foreground/10 text-foreground",
            flagged === "pressed" && "bg-foreground/20 text-foreground"
          )}
        >
          <FlagIcon className="size-4" />
          {counts.reports}
        </span>
      </span>
      <span className="flex flex-wrap gap-2 sm:flex-col sm:items-end sm:gap-3">
        <span
          className={buttonVariants({
            variant: "outline",
            className: cn("lowercase", button.pressed && "bg-muted"),
          })}
        >
          <RefreshCwIcon className={cn(button.spinning && "animate-spin")} />
          {button.label}
        </span>
        <span
          className={buttonVariants({
            variant: "outline",
            className: "lowercase",
          })}
        >
          <CircleAlertIcon />
          {wrongAnswer}
        </span>
      </span>
    </span>
  )
}

export type DemoQuestion = {
  text: string
  options: { answer: string; correct: boolean }[]
}

/** A question with its answer options, as question-row.tsx shows them. */
function QuestionCell({
  question,
  dimmed = false,
}: {
  question: DemoQuestion
  dimmed?: boolean
}) {
  return (
    <span className={cn("block font-light", dimmed && "opacity-50")}>
      {question.text}
      <AnswerOptions options={question.options} className="mt-3" />
    </span>
  )
}

const ROW =
  "grid grid-cols-[minmax(0,1fr)] items-start gap-x-3 gap-y-3 p-4 sm:grid-cols-[1fr_auto] sm:gap-x-5 sm:p-5"

/** A topic's questions as their owner sees them (components/questions/question-row.tsx),
 * playing on a loop: a weak question's report opened, then the question re-generated. */
export function QualityDemo({
  title,
  good,
  weak,
  better,
  report,
  labels,
}: {
  title: string
  good: DemoQuestion
  weak: DemoQuestion
  better: DemoQuestion
  report: { reason: string; date: string; comment: string }
  labels: {
    regenerate: string
    regenerating: string
    wrongAnswer: string
  }
}) {
  const [index, setIndex] = useState(0)
  const step = STEPS[index].name

  useEffect(() => {
    // With reduced motion the demo doesn't play; the open report stays.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    let at = 0
    let timer: number

    function next() {
      at = (at + 1) % STEPS.length
      setIndex(at)
      timer = window.setTimeout(next, STEPS[at].ms)
    }

    timer = window.setTimeout(next, STEPS[0].ms)

    return () => window.clearTimeout(timer)
  }, [])

  const replaced = step === "regenerated"
  const reportOpen = ["open", "press", "regenerating"].includes(step)
  const regenerating = step === "regenerating"

  return (
    <div className="space-y-4 rounded-2xl border bg-background p-6 text-start">
      {/* The topic's name, as the questions dialog has it (components/questions/topic-questions.tsx). */}
      <p className="font-heading text-xl leading-none font-medium">
        {title}
        <span className="text-primary">.</span>
      </p>
      {/* Room for the open report below the list, so the card keeps its size while the demo
          plays; the list itself only grows when the report opens. */}
      <div className="min-h-[800px] sm:min-h-[436px]">
        <ul className="divide-y rounded-xl border">
          <li className={ROW}>
            <QuestionCell question={good} />
            <Feedback
              counts={{ likes: 14, dislikes: 0, reports: 0 }}
              button={{
                label: labels.regenerate,
                spinning: false,
                pressed: false,
              }}
              wrongAnswer={labels.wrongAnswer}
            />
          </li>
          <li>
            <div className={ROW}>
              <QuestionCell
                question={replaced ? better : weak}
                dimmed={regenerating}
              />
              <Feedback
                counts={
                  replaced
                    ? { likes: 0, dislikes: 0, reports: 0 }
                    : { likes: 1, dislikes: 9, reports: 3 }
                }
                flagged={
                  step === "flag" ? "pressed" : reportOpen ? "open" : undefined
                }
                button={{
                  label: regenerating ? labels.regenerating : labels.regenerate,
                  spinning: regenerating,
                  pressed: step === "press",
                }}
                wrongAnswer={labels.wrongAnswer}
              />
            </div>
            {reportOpen && (
              <div className="space-y-1 bg-muted/40 p-4 text-sm sm:p-5 sm:pe-6">
                <p className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-medium">{report.reason}</span>
                  <span className="text-muted-foreground">{report.date}</span>
                </p>
                <p className="font-light text-muted-foreground">
                  {report.comment}
                </p>
              </div>
            )}
          </li>
        </ul>
      </div>
    </div>
  )
}
