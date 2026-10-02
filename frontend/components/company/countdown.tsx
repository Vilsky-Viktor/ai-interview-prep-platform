"use client"

import { cn } from "cn"
import { TimerIcon } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import { COUNTDOWN_WARNING_SECONDS } from "@/constants/interviews"

function secondsLeft(deadline: string) {
  return Math.max(
    0,
    Math.ceil((new Date(deadline).getTime() - Date.now()) / 1000)
  )
}

function clock(seconds: number) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const rest = String(seconds % 60).padStart(2, "0")

  return hours > 0
    ? `${hours}:${String(minutes).padStart(2, "0")}:${rest}`
    : `${minutes}:${rest}`
}

/** Time left in a timed interview; calls onExpire once when it reaches zero. */
export function Countdown({
  deadline,
  onExpire,
}: {
  deadline: string
  onExpire: () => void
}) {
  const [left, setLeft] = useState(() => secondsLeft(deadline))
  const expired = useRef(false)

  useEffect(() => {
    // Recomputed from the deadline every tick, so a slow tab never drifts.
    const timer = window.setInterval(() => setLeft(secondsLeft(deadline)), 1000)

    return () => window.clearInterval(timer)
  }, [deadline])

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
