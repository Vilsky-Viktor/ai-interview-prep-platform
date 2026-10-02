"use client"

import { cn } from "cn"
import { TimerIcon } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import { COUNTDOWN_WARNING_SECONDS } from "@/constants/interviews"

function secondsUntil(end: number) {
  return Math.max(0, Math.ceil((end - Date.now()) / 1000))
}

function clock(seconds: number) {
  const minutes = Math.floor(seconds / 60)
  const rest = String(seconds % 60).padStart(2, "0")

  return `${minutes}:${rest}`
}

/** Time left on a timed question; calls onExpire once when it reaches zero.

`seconds` comes from the server as time left, not a moment, so a wrong device clock doesn't
matter. Render it with a key per question, so each question starts its own clock. */
export function Countdown({
  seconds,
  onExpire,
}: {
  seconds: number
  onExpire: () => void
}) {
  const [end] = useState(() => Date.now() + seconds * 1000)
  const [left, setLeft] = useState(() => secondsUntil(end))
  const expired = useRef(false)

  useEffect(() => {
    // Recomputed from the end every tick, so a slow tab never drifts.
    const timer = window.setInterval(() => setLeft(secondsUntil(end)), 250)

    return () => window.clearInterval(timer)
  }, [end])

  useEffect(() => {
    if (left === 0 && !expired.current) {
      expired.current = true
      onExpire()
    }
  }, [left, onExpire])

  return (
    <span
      role="timer"
      aria-label={`Time left: ${clock(left)}`}
      className={cn(
        "flex items-center gap-1.5 font-medium tabular-nums",
        left <= COUNTDOWN_WARNING_SECONDS && "text-red-600 dark:text-red-400"
      )}
    >
      <TimerIcon aria-hidden className="size-4" />
      {clock(left)}
    </span>
  )
}
