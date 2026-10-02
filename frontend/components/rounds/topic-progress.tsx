import { cn } from "cn"

import { Progress } from "@/components/ui/progress"
import { scorePassed } from "@/lib/rounds"
import type { TopicProgress as Progressed } from "@/types/round"

const PASSED_BAR = "[&_[data-slot=progress-indicator]]:bg-green-600 dark:[&_[data-slot=progress-indicator]]:bg-green-400"
const FAILED_BAR = "[&_[data-slot=progress-indicator]]:bg-red-600 dark:[&_[data-slot=progress-indicator]]:bg-red-400"

/** Progress towards the certificate: every question answered, then 70% of them correct. */
export function TopicProgress({
  progress,
  total,
}: {
  progress: Progressed | undefined
  total: number
}) {
  const answered = Math.min(progress?.answered ?? 0, total)
  const score = progress?.score ?? null
  const complete = total > 0 && answered >= total
  const passed =
    Boolean(progress?.certificate_id) ||
    (complete && score !== null && scorePassed(score))

  return (
    <Progress
      value={total ? (answered / total) * 100 : 0}
      aria-label="Questions answered towards the certificate"
      className={cn("w-full", complete && (passed ? PASSED_BAR : FAILED_BAR))}
    />
  )
}
