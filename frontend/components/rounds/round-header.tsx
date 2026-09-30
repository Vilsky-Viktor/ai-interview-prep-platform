import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import Link from "next/link"

import { BackLink } from "@/components/back-link"
import { Progress } from "@/components/ui/progress"
import { MODE_LABELS } from "@/constants/rounds"
import { scorePassed } from "@/lib/rounds"
import type { Round } from "@/types/round"

export function RoundHeader({ round }: { round: Round }) {
  const score = round.current_score ?? 0

  return (
    <div className="space-y-3">
      <div className="relative">
        <BackLink href={`/preparations/${round.preparation_id}`}>
          Preparation page
        </BackLink>
        <div className="flex min-w-0 items-center justify-between gap-4">
          <Link
            href={`/preparations/${round.preparation_id}`}
            className="min-w-0 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {round.topic_title} · {MODE_LABELS[round.mode]}
          </Link>
          <p className="flex shrink-0 items-center text-sm text-muted-foreground tabular-nums">
            {round.answered} / {round.total}
            <MinusIcon
              aria-hidden
              className="mx-1.5 size-3.5 text-foreground/55"
            />
            <span
              className={cn(
                "text-xl font-light",
                scorePassed(score)
                  ? "text-green-600 dark:text-green-400"
                  : "text-red-600 dark:text-red-400"
              )}
            >
              {score}%
            </span>
          </p>
        </div>
      </div>
      <Progress value={(round.answered / round.total) * 100} />
    </div>
  )
}
