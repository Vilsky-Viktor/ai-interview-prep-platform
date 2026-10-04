"use client"

import { cn } from "cn"
import {
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

/** A question's votes and reports, and its re-generate button, as question-row.tsx shows them. */
function Feedback({
  counts,
  flagged,
  button,
}: {
  counts: Counts
  flagged?: "pressed" | "open"
  button?: { label: string; spinning: boolean; pressed: boolean }
}) {
  return (
    <span className="col-start-2 flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground tabular-nums sm:col-start-auto sm:flex-col sm:items-end">
      <span className="flex items-center gap-3">
        <span className="flex items-center gap-1">
          <ThumbsUpIcon className="size-4" />
          {counts.likes}
        </span>
        <span className="flex items-center gap-1">
          <ThumbsDownIcon className="size-4" />
          {counts.dislikes}
        </span>
        <span
          className={cn(
            "-mx-1.5 flex items-center gap-1 rounded-md px-1.5 transition-colors",
            flagged === "open" && "bg-foreground/10 text-foreground",
            flagged === "pressed" && "bg-foreground/20 text-foreground"
          )}
        >
          <FlagIcon className="size-4" />
          {counts.reports}
        </span>
      </span>
      {button && (
        <span
          className={buttonVariants({
            variant: "outline",
            className: cn("lowercase", button.pressed && "bg-muted"),
          })}
        >
          <RefreshCwIcon className={cn(button.spinning && "animate-spin")} />
          {button.label}
        </span>
      )}
    </span>
  )
}

const ROW =
  "grid grid-cols-[1.5rem_minmax(0,1fr)] items-center gap-x-3 gap-y-2 p-4 sm:grid-cols-[2rem_1fr_auto]"

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
  labels: { regenerate: string; regenerating: string }
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
      <p className="font-heading text-lg font-medium tracking-tight lowercase">
        {title}
        <span className="text-primary">.</span>
      </p>
      {/* Room for the open report below the list, so the card keeps its size while the demo
          plays; the list itself only grows when the report opens. */}
      <div className="min-h-[395px] sm:min-h-[219px]">
        <ul className="divide-y rounded-xl border">
          <li className={ROW}>
            <span className="font-light text-muted-foreground tabular-nums">
              1
            </span>
            <span className="font-light">{good}</span>
            <Feedback counts={{ likes: 14, dislikes: 0, reports: 0 }} />
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
              />
            </div>
            {reportOpen && (
              <div className="space-y-1 bg-muted/40 px-4 py-3 ps-[2.75rem] text-sm sm:ps-[3.75rem]">
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
