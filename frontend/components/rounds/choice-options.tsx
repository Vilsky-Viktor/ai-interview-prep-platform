"use client"

import { cn } from "cn"
import { useState } from "react"

import { InlineText } from "@/components/questions/inline-text"
import type { AnswerResult } from "@/types/round"

type ChoiceOptionsProps = {
  options: string[]
  result: AnswerResult | null
  onAnswer: (optionIndex: number) => Promise<boolean>
}

export function ChoiceOptions({ options, result, onAnswer }: ChoiceOptionsProps) {
  const [chosen, setChosen] = useState<number | null>(result?.option_index ?? null)
  const picked = result?.option_index ?? chosen

  async function choose(index: number) {
    setChosen(index)

    if (!(await onAnswer(index))) {
      setChosen(null)
    }
  }

  function optionClass(index: number) {
    if (!result) {
      return chosen === index
        ? "border-ring bg-muted"
        : "hover:border-ring hover:bg-muted/50"
    }

    if (index === result.correct_option_index) {
      return "border-green-600 bg-green-600/15 dark:border-green-400 dark:bg-green-400/15"
    }

    if (index === picked) {
      return "border-destructive bg-destructive/10"
    }

    return "opacity-60"
  }

  return (
    <ul className="space-y-2">
      {options.map((option, index) => (
        <li key={option}>
          <button
            type="button"
            disabled={picked !== null}
            onClick={() => choose(index)}
            className={cn(
              "flex w-full items-start gap-3 rounded-2xl border p-4 text-left text-lg leading-7 font-light transition-colors disabled:cursor-default",
              optionClass(index)
            )}
          >
            <span className="w-4 shrink-0 text-muted-foreground">
              {String.fromCharCode(65 + index)}
            </span>
            <span className="min-w-0">
              <InlineText text={option} />
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
