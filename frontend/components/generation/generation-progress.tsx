import { LoaderCircleIcon } from "lucide-react"
import type { ReactNode } from "react"

import { BackLink } from "@/components/back-link"
import { Progress } from "@/components/ui/progress"
import type { Generation } from "@/types/generation"

export function GenerationProgress({
  generation,
  backHref,
  backLabel,
  action,
}: {
  generation: Generation
  backHref: string
  backLabel: string
  action?: ReactNode
}) {
  const progress = generation.progress
  const writing = progress !== null && progress.total > 0
  const percent = writing
    ? Math.min(100, Math.round((progress.done / progress.total) * 100))
    : 0

  return (
    <div className="flex min-h-[calc(100svh-3.5rem-6rem)] flex-col items-center justify-center space-y-8 text-center">
      <LoaderCircleIcon className="size-20 animate-spin text-primary" />
      <div className="space-y-4">
        <div className="relative">
          <BackLink href={backHref}>{backLabel}</BackLink>
          <h1 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
            {writing ? "Writing your questions" : "Drafting your topics"}
          </h1>
        </div>
        <p className="text-base text-muted-foreground">
          {writing
            ? "This takes a few minutes. You can leave this page; we keep going."
            : "Reading your goal and planning what to cover."}
        </p>
      </div>
      {writing && (
        <div className="mx-auto w-full max-w-2xl space-y-2">
          <Progress value={percent} />
          <p className="text-2xl font-light tabular-nums">{percent}%</p>
          {progress.topics !== undefined && (
            <p className="text-sm text-muted-foreground tabular-nums">
              {progress.topics_ready ?? 0} of {progress.topics}{" "}
              {progress.topics === 1 ? "topic" : "topics"} ready
            </p>
          )}
        </div>
      )}
      {action && <div className="flex justify-center pt-6">{action}</div>}
    </div>
  )
}
