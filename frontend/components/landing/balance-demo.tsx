"use client"

import { cn } from "cn"
import Link from "next/link"
import { useEffect, useState } from "react"

import { buttonVariants } from "@/components/ui/button"

// One loop of the demo, in milliseconds, the same for every balance so they stay apart; how
// long the button looks pressed, and how long the count up takes.
const CYCLE_MS = 6000
const PRESS_MS = 400
const COUNT_MS = 1200

/** One balance as the top-up page's BalanceRow shows it (components/billing/balance-row.tsx),
 * wrapped as on a narrow screen, counting up as a top-up arrives on a loop: after the button is
 * pressed, or by itself for an automatic top-up. With reduced motion it shows the start, still. */
export function BalanceDemo({
  name,
  automatic,
  start,
  added,
  startAt,
  pressed,
  words,
  action,
  locale,
}: {
  name: string
  automatic: string
  start: number
  added: number
  // When in the loop the top-up arrives, in milliseconds; a press comes just before it.
  startAt: number
  pressed: boolean
  words: string
  action: string
  locale: string
}) {
  const [credits, setCredits] = useState(start)
  const [phase, setPhase] = useState<"still" | "press" | "count">("still")

  useEffect(() => {
    // With reduced motion the demo doesn't play.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    const timers: number[] = []
    let frame = 0

    function count() {
      setPhase("count")
      const began = performance.now()

      function tick(now: number) {
        const done = Math.min((now - began) / COUNT_MS, 1)
        // Fast at first, easing into the new balance.
        const eased = 1 - (1 - done) ** 3
        setCredits(Math.round(start + added * eased))

        if (done < 1) {
          frame = requestAnimationFrame(tick)
        } else {
          setPhase("still")
        }
      }

      frame = requestAnimationFrame(tick)
    }

    function loop() {
      setCredits(start)

      if (pressed) {
        timers.push(
          window.setTimeout(() => setPhase("press"), startAt - PRESS_MS)
        )
      }

      timers.push(window.setTimeout(count, startAt))
      timers.push(window.setTimeout(loop, CYCLE_MS))
    }

    loop()

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer))
      cancelAnimationFrame(frame)
    }
  }, [start, added, startAt, pressed])

  return (
    <div className="space-y-4 rounded-2xl border bg-background px-6 py-5">
      <div className="space-y-1">
        <p className="text-lg font-medium">{name}</p>
        <p className="text-sm text-muted-foreground">{automatic}</p>
      </div>
      <div className="flex items-center justify-between gap-5">
        <p>
          <span
            className={cn(
              "font-heading text-3xl font-medium tabular-nums transition-colors duration-500",
              phase === "count" && "text-primary"
            )}
          >
            {credits.toLocaleString(locale)}
          </span>{" "}
          <span className="text-sm text-muted-foreground">{words}</span>
        </p>
        <Link
          href="/top-up"
          className={buttonVariants({
            className: cn(
              "h-10 px-5 lowercase",
              phase === "press" && "ring-2 ring-ring/50"
            ),
          })}
        >
          {action}
        </Link>
      </div>
    </div>
  )
}
