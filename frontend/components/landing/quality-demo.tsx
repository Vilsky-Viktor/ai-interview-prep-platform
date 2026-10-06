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
    <span className="col-start-2 flex flex-wrap items-center justify-between gap-3 text-sm whitespace-nowrap text-muted-foreground tabular-nums sm:col-start-auto sm:flex-col sm:items-end">
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

const ROW =
  "grid grid-cols-[1.5rem_minmax(0,1fr)] items-center gap-x-3 gap-y-3 p-4 sm:grid-cols-[2.5rem_1fr_auto] sm:gap-x-5 sm:p-5"

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
  good: string
  weak: string
  better: string
  report: { reason: string; date: string; comment: string }
  labels: {
    regenerate: string
    regenerating: string
    wrongAnswer: string
    showOptions: string
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
      {/* The topic's name and the answer options' toggle, as the questions dialog has them
          (components/questions/topic-questions.tsx). */}
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
        <p className="font-heading text-xl leading-none font-medium">
          {title}
          <span className="text-primary">.</span>
        </p>
        <span
          className={buttonVariants({
            size: "sm",
            className: "h-8 shrink-0 px-3 text-sm lowercase",
          })}
        >
          {labels.showOptions}
        </span>
      </div>
      {/* Room for the open report below the list, so the card keeps its size while the demo
          plays; the list itself only grows when the report opens. */}
      <div className="min-h-[540px] sm:min-h-[384px]">
        <ul className="divide-y rounded-xl border">
          <li className={ROW}>
            <span className="font-light text-muted-foreground tabular-nums">
              1
            </span>
            <span className="font-light">{good}</span>
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
              <span className="font-light text-muted-foreground tabular-nums">
                2
              </span>
              <span className={cn("font-light", regenerating && "opacity-50")}>
                {replaced ? better : weak}
              </span>
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
              <div className="space-y-1 bg-muted/40 px-4 py-4 ps-[2.75rem] text-sm sm:py-5 sm:ps-[5rem] sm:pe-6">
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
