import { cn } from "cn"
import {
  CheckIcon,
  MinusIcon,
  SquarePenIcon,
  PlusIcon,
  XIcon,
} from "lucide-react"

import { Caret } from "@/components/landing/caret"
import { buttonVariants } from "@/components/ui/button"

const CHIP =
  "flex items-center gap-1 rounded-full bg-muted py-1 ps-3 pe-1.5 text-sm"
const FIELD = "flex h-10 items-center rounded-full border border-input px-4"
// The steps with the editor open; the rest show the topic's row.
const EDITING = ["edit", "typing", "add", "added", "done"]
// From "added" on, the new subtopic is among the topic's.
const WITH_NEW = [
  "added",
  "done",
  "saved",
  "asking",
  "asked",
  "apply",
  "applying",
  "applied",
]

/** A checked topic of the review at one step of the demo, as the real editor shows it
 * (components/generation/topic-editor.tsx): its row, the pencil pressed, then the editor with a
 * subtopic typed, added and Done. */
export function TopicEditDemo({
  step,
  typed,
  name,
  subtopics,
  added,
  labels,
}: {
  step: string
  typed: number
  name: string
  subtopics: string[]
  added: string
  labels: { addSubtopic: string; add: string; done: string }
}) {
  const chips = WITH_NEW.includes(step) ? [...subtopics, added] : subtopics
  const draft = step === "typing" || step === "add" ? added.slice(0, typed) : ""

  if (EDITING.includes(step)) {
    return (
      <div className="space-y-4 p-6">
        <div className={cn(FIELD, "font-medium")}>{name}</div>
        <ul className="flex flex-wrap gap-2">
          {chips.map((subtopic) => (
            <li key={subtopic} className={CHIP}>
              {subtopic}
              <XIcon className="size-3.5 text-muted-foreground" />
            </li>
          ))}
        </ul>
        <div className="flex items-center gap-2">
          <div className={cn(FIELD, "min-w-0 flex-1")}>
            {draft ? (
              <span>
                {draft}
                <Caret />
              </span>
            ) : (
              <span className="text-muted-foreground">
                {labels.addSubtopic}
              </span>
            )}
          </div>
          {/* Dimmed like the real button while nothing is typed, and marked so. */}
          <span
            aria-disabled={!draft || undefined}
            className={buttonVariants({
              variant: "outline",
              className: cn(
                "h-10 gap-1 px-3 lowercase",
                !draft && "opacity-50",
                step === "add" && "bg-muted"
              ),
            })}
          >
            <PlusIcon />
            {labels.add}
          </span>
          <span
            className={buttonVariants({
              variant: "secondary",
              className: cn(
                "h-10 px-4 lowercase",
                step === "done" && "ring-2 ring-ring/50"
              ),
            })}
          >
            {labels.done}
          </span>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-4 px-6 py-4">
      <span className="flex size-5 shrink-0 items-center justify-center rounded-[6px] bg-primary text-primary-foreground">
        <CheckIcon className="size-3.5" />
      </span>
      <span className="min-w-0 flex-1 space-y-0.5">
        <span className="block font-medium">{name}</span>
        <span className="block text-sm text-muted-foreground">
          {chips.map((subtopic, index) => (
            <span key={subtopic}>
              {index > 0 && (
                <MinusIcon className="mx-1.5 inline size-3.5 align-[-2px] text-foreground/55" />
              )}
              {subtopic}
            </span>
          ))}
        </span>
      </span>
      <span
        className={cn(
          "flex size-8 shrink-0 items-center justify-center rounded-md transition-colors",
          step === "pencil" && "bg-muted"
        )}
      >
        <SquarePenIcon className="size-4 text-muted-foreground" />
      </span>
    </div>
  )
}
