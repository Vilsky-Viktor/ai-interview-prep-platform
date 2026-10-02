import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import Link from "next/link"

import { RoundChange } from "@/components/rounds/round-change"
import { RoundReview } from "@/components/rounds/round-review"
import { Button } from "@/components/ui/button"
import type { Round } from "@/types/round"

export function RoundSummary({ round }: { round: Round }) {
  const historyHref = `/preparations/${round.preparation_id}/topics/${round.topic_id}/history`
  const passed = round.passed
  const scoreColor = passed
    ? "text-green-600 dark:text-green-400"
    : "text-red-600 dark:text-red-400"

  return (
    <div className="space-y-12">
      <div className="space-y-8 py-8 text-center">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">{round.topic_title}</p>
          <p
            className={cn(
              "font-heading text-8xl font-light tabular-nums",
              scoreColor
            )}
          >
            {round.final_score ?? 0}%
          </p>
          <p className="flex items-center justify-center text-muted-foreground">
            Final score
            <MinusIcon
              aria-hidden
              className="mx-1.5 size-3.5 text-foreground/55"
            />
            {round.answered} of {round.total} answered
          </p>
        </div>
        <RoundChange round={round} />
        <div className="flex flex-wrap justify-center gap-3">
          {round.certificate_id && (
            <Button
              className="h-12 px-6 text-base"
              render={<Link href={`/certificates/${round.certificate_id}`} />}
              nativeButton={false}
            >
              Certificate
            </Button>
          )}
          <Button
            variant="outline"
            className="h-12 px-6 text-base"
            render={<Link href={historyHref} />}
            nativeButton={false}
          >
            History
          </Button>
          <Button
            variant="outline"
            className="h-12 px-6 text-base"
            render={<Link href={`/preparations/${round.preparation_id}`} />}
            nativeButton={false}
          >
            Preparation page
          </Button>
        </div>
      </div>
      <RoundReview roundId={round.id} />
    </div>
  )
}
