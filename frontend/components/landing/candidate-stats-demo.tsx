"use client"

import { cn } from "cn"
import { useEffect, useState } from "react"

// How long each answer's numbers show, in milliseconds, before the next answer arrives.
const STEP_MS = 1600

/** A candidate's progress and grade as the candidate list shows them
 * (components/company/candidate-list.tsx), updating answer by answer on a loop. Each change
 * flashes for a moment. With reduced motion it shows the first numbers, still. */
export function CandidateStatsDemo({
  steps,
  labels,
}: {
  // Progress and grade after each answer, in percent.
  steps: { progress: number; grade: number }[]
  labels: { progress: string; grade: string }
}) {
  const [index, setIndex] = useState(0)
  const [flash, setFlash] = useState(false)
  const { progress, grade } = steps[index]

  useEffect(() => {
    // With reduced motion the demo doesn't play.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    let at = 0
    let timer: number
    let unflash: number

    function next() {
      at = (at + 1) % steps.length
      setIndex(at)
      setFlash(true)
      unflash = window.setTimeout(() => setFlash(false), 500)
      // The last numbers hold a little longer before it starts over.
      timer = window.setTimeout(
        next,
        at === steps.length - 1 ? STEP_MS * 2 : STEP_MS
      )
    }

    timer = window.setTimeout(next, STEP_MS)

    return () => {
      window.clearTimeout(timer)
      window.clearTimeout(unflash)
    }
  }, [steps.length])

  const number = cn(
    "block text-2xl font-light tabular-nums transition-colors duration-500",
    flash && "text-primary"
  )

  return (
    <>
      <span className="w-20 text-center sm:w-24">
        <span className={number}>{progress}%</span>
        <span className="block text-sm text-muted-foreground">
          {labels.progress}
        </span>
      </span>
      <span className="w-20 text-center sm:w-24">
        <span className={number}>{grade}%</span>
        <span className="block text-sm text-muted-foreground">
          {labels.grade}
        </span>
      </span>
    </>
  )
}
