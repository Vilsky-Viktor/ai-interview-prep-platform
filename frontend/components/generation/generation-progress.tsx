import { LoaderCircleIcon } from "lucide-react"

import { BackLink } from "@/components/back-link"
import { Progress } from "@/components/ui/progress"
import { formatCost } from "@/lib/format"
import type { Generation } from "@/types/generation"

export function GenerationProgress({
  generation,
  backHref,
  backLabel,
}: {
  generation: Generation
  backHref: string
  backLabel: string
}) {
  const progress = generation.progress
  const writing = progress !== null && progress.total > 0

  return (
    <div className="flex min-h-[calc(100svh-3.5rem-6rem)] flex-col items-center justify-center space-y-8 text-center">
      <LoaderCircleIcon className="size-8 animate-spin text-primary" />
      <div className="space-y-4">
        <div className="relative">
          <BackLink href={backHref}>{backLabel}</BackLink>
          <h1 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
            {writing ? "Writing questions and answers" : "Drafting your topics"}
          </h1>
        </div>
        <p className="text-base text-muted-foreground">
          {writing
            ? "This takes a few minutes. You can leave this page; we keep going."
            : "Reading your goal and planning what to cover."}
        </p>
      </div>
      {writing && (
        <div className="mx-auto max-w-sm space-y-2">
          <Progress value={(progress.done / progress.total) * 100} />
          <p className="text-sm text-muted-foreground tabular-nums">
            {progress.done} of {progress.total} steps
          </p>
        </div>
      )}
      {generation.cost_usd != null && (
        <p className="text-sm text-muted-foreground tabular-nums">
          AI cost so far: {formatCost(generation.cost_usd)}
        </p>
      )}
    </div>
  )
}
