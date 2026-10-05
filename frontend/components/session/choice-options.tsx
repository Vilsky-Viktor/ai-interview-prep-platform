"use client"

import { cn } from "cn"
import { useState } from "react"

import { InlineText } from "@/components/questions/inline-text"

type ChoiceOptionsProps = {
  options: string[]
  onAnswer: (optionIndex: number) => Promise<boolean>
}

/** A question's options. The one picked stays marked; candidates never see which is right. */
export function ChoiceOptions({ options, onAnswer }: ChoiceOptionsProps) {
  const [chosen, setChosen] = useState<number | null>(null)

  async function choose(index: number) {
    setChosen(index)

    if (!(await onAnswer(index))) {
      setChosen(null)
    }
  }

  return (
    <ul className="space-y-2">
      {options.map((option, index) => (
        <li key={option}>
          <button
            type="button"
            disabled={chosen !== null}
            onClick={() => choose(index)}
            className={cn(
              "flex w-full items-start gap-3 rounded-2xl border p-4 text-start text-lg leading-7 font-light normal-case transition-colors disabled:cursor-default",
              chosen === index
                ? "border-ring bg-muted"
                : "hover:border-ring hover:bg-muted/50"
            )}
          >
            <span className="w-4 shrink-0 text-muted-foreground">
              {String.fromCharCode(65 + index)}
            </span>
            <span className="bidi-auto min-w-0 flex-1">
              <InlineText text={option} />
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
