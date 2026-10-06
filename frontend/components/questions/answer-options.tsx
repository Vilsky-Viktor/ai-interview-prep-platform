"use client"

import { cn } from "cn"
import { CheckIcon, XIcon } from "lucide-react"
import { useTranslations } from "next-intl"

/** A question's answer options: the right one with a green check, the wrong ones with a red
 * cross, in the scorecards' colors. `picked` marks the option a talent chose in practice. */
export function AnswerOptions({
  options,
  picked,
  className,
}: {
  options: { answer: string; correct: boolean }[]
  picked?: number | null
  className?: string
}) {
  const t = useTranslations("questions")

  return (
    <ul className={cn("space-y-1.5 text-sm", className)}>
      {options.map((option, index) => (
        <li
          key={index}
          className={cn(
            "flex gap-2",
            option.correct ? "text-foreground" : "text-muted-foreground"
          )}
        >
          {/* Right and wrong in the scorecards' colors. */}
          {option.correct ? (
            <CheckIcon
              className="mt-0.5 size-4 shrink-0 text-green-600 dark:text-green-400"
              role="img"
              aria-label={t("correct")}
            />
          ) : (
            <XIcon
              className="mt-0.5 size-4 shrink-0 text-red-600 dark:text-red-400"
              role="img"
              aria-label={t("wrong")}
            />
          )}
          <span className="bidi-auto">
            {option.answer}
            {picked === index && (
              <span className="ms-2 text-muted-foreground">
                {t("yourAnswer")}
              </span>
            )}
          </span>
        </li>
      ))}
    </ul>
  )
}
