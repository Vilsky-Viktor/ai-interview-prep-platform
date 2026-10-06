import { cn } from "cn"

import { InlineText } from "@/components/questions/inline-text"

type ChoiceOptionsProps = {
  options: string[]
  chosen: number | null
  disabled: boolean
  onChoose: (optionIndex: number) => void
}

/** A question's options. The one picked stays marked and can be changed until it's sent;
 * candidates never see which is right. */
export function ChoiceOptions({
  options,
  chosen,
  disabled,
  onChoose,
}: ChoiceOptionsProps) {
  return (
    <ul className="space-y-2">
      {options.map((option, index) => (
        // By place: two options can read the same, and the list never reorders.
        <li key={index}>
          <button
            type="button"
            disabled={disabled}
            aria-pressed={chosen === index}
            onClick={() => onChoose(index)}
            className={cn(
              "flex w-full items-start gap-3 rounded-2xl border p-4 text-start text-lg leading-7 font-light normal-case transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default",
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
