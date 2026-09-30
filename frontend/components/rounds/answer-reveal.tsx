import { cn } from "cn"

import { scorePassed } from "@/lib/rounds"
import type { AnswerResult } from "@/types/round"

function verdict(result: AnswerResult) {
  if (result.correct === null) {
    return `Score ${result.score}%`
  }

  return result.correct ? "Correct" : "Not quite"
}

export function AnswerReveal({ result }: { result: AnswerResult }) {
  const good = result.correct ?? scorePassed(result.score)

  return (
    <div className="space-y-4 rounded-2xl border bg-card p-5">
      <p
        className={cn(
          "text-lg font-medium",
          good
            ? "text-green-600 dark:text-green-400"
            : "text-red-600 dark:text-red-400"
        )}
      >
        {verdict(result)}
      </p>
      {result.feedback && (
        <p className="text-sm italic">{result.feedback}</p>
      )}
      {result.reference_answer && (
        <p className="text-sm leading-relaxed">{result.reference_answer}</p>
      )}
    </div>
  )
}
