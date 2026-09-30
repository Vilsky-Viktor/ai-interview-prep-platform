import { cn } from "cn"

import { MODE_ICONS, MODE_LABELS, ROUND_MODES } from "@/constants/rounds"
import { scorePassed } from "@/lib/rounds"
import type { TopicPass } from "@/types/round"

export function TopicPasses({ passes, total }: { passes: TopicPass[]; total: number }) {
  const shown = ROUND_MODES.flatMap((mode) =>
    passes.filter((item) => item.mode === mode)
  )

  if (shown.length === 0) {
    return null
  }

  return (
    <div className="inline-flex divide-x overflow-hidden rounded-lg border">
      {shown.map((pass) => {
        const Icon = MODE_ICONS[pass.mode]

        return (
          <span
            key={pass.mode}
            title={MODE_LABELS[pass.mode]}
            className={cn(
              "flex h-10 items-center gap-1.5 px-3 text-lg font-light whitespace-nowrap tabular-nums",
              scorePassed(pass.score)
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            )}
          >
            <Icon aria-label={MODE_LABELS[pass.mode]} className="size-5 stroke-[1.5]" />
            {pass.score}%
            <span
              aria-label={`${pass.answered} of ${total} questions answered`}
              className="ml-1 text-sm text-muted-foreground"
            >
              {pass.answered}/{total}
            </span>
          </span>
        )
      })}
    </div>
  )
}
