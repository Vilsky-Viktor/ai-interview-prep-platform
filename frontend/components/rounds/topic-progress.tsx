import { cn } from "cn"

import { Progress } from "@/components/ui/progress"
import type { TopicProgress as Progressed } from "@/types/round"

const PASSED_BAR = "[&_[data-slot=progress-indicator]]:bg-green-600 dark:[&_[data-slot=progress-indicator]]:bg-green-400"
const FAILED_BAR = "[&_[data-slot=progress-indicator]]:bg-red-600 dark:[&_[data-slot=progress-indicator]]:bg-red-400"

/** Progress towards the certificate; whether it's complete and passes comes from the API. */
export function TopicProgress({
  progress,
  total,
}: {
  progress: Progressed | undefined
  total: number
}) {
  const answered = Math.min(progress?.answered ?? 0, total)
  const complete = progress?.complete ?? false
  const passed = progress?.passed ?? false

  return (
    <Progress
      value={total ? (answered / total) * 100 : 0}
      aria-label="Questions answered towards the certificate"
      className={cn("w-full", complete && (passed ? PASSED_BAR : FAILED_BAR))}
    />
  )
}
