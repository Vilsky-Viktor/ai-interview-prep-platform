"use client"

import { cn } from "cn"
import { CheckIcon, MinusIcon, SquarePenIcon } from "lucide-react"
import { useEffect, useState } from "react"

import { Caret } from "@/components/landing/caret"
import { TopicEditDemo } from "@/components/landing/topic-edit-demo"
import { buttonVariants } from "@/components/ui/button"

// The demo's steps and how long each shows, in milliseconds. A step that types shows one more
// letter of its text each `ms`: the new subtopic, then the request for changes, which is then
// applied and adds a topic.
const STEPS = [
  { name: "view", ms: 1500 },
  { name: "pencil", ms: 400 },
  { name: "edit", ms: 600 },
  { name: "typing", ms: 70, types: "added" },
  { name: "add", ms: 400 },
  { name: "added", ms: 700 },
  { name: "done", ms: 400 },
  { name: "saved", ms: 800 },
  { name: "asking", ms: 55, types: "change" },
  { name: "asked", ms: 1200 },
  { name: "apply", ms: 400 },
  { name: "applying", ms: 1000 },
  { name: "applied", ms: 3000 },
] as const

type Topic = {
  key: string
  name: string
  subtopics: string[]
  checked: boolean
}

/** The topic review as it really looks (components/generation/topic-review.tsx), playing on a
 * loop: one topic edited by hand, then a change asked of the AI and applied, which adds a topic.
 * With reduced motion it stays still, as the review first shows. */
export function ReviewDemo({
  title,
  topics,
  editing,
  added,
  change,
  newTopic,
  labels,
}: {
  title: string
  topics: Topic[]
  editing: string
  added: string
  change: string
  // The topic the AI adds when the change is applied.
  newTopic: { name: string; subtopics: string[] }
  labels: {
    addSubtopic: string
    add: string
    done: string
    placeholder: string
    apply: string
  }
}) {
  const [index, setIndex] = useState(0)
  const [letters, setLetters] = useState({ added: 0, change: 0 })
  const step = STEPS[index].name

  useEffect(() => {
    // With reduced motion the demo doesn't play.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    let at = 0
    const typed = { added: 0, change: 0 }
    const texts = { added, change }
    let timer: number

    function next() {
      const current = STEPS[at]

      if (
        "types" in current &&
        typed[current.types] < texts[current.types].length
      ) {
        typed[current.types] += 1
      } else {
        at = (at + 1) % STEPS.length

        if (at === 0) {
          typed.added = 0
          typed.change = 0
        }
      }

      setIndex(at)
      setLetters({ ...typed })
      timer = window.setTimeout(next, STEPS[at].ms)
    }

    timer = window.setTimeout(next, STEPS[0].ms)

    return () => window.clearTimeout(timer)
  }, [added, change])

  const asking = ["asking", "asked", "apply", "applying"].includes(step)
  const applied = step === "applied"
  const shown = applied
    ? [...topics, { key: "new", checked: true, ...newTopic }]
    : topics

  return (
    // Room for the open editor, so the page doesn't move while the demo plays.
    <div className="min-h-[612px] space-y-4 text-start sm:min-h-[452px]">
      <p className="font-heading text-xl font-medium tracking-tight lowercase">
        {title}
        <span className="text-primary">.</span>
      </p>
      <ul className="divide-y rounded-2xl border bg-background">
        {shown.map((topic) =>
          topic.key === editing ? (
            <li key={topic.key}>
              <TopicEditDemo
                step={step}
                typed={letters.added}
                name={topic.name}
                subtopics={topic.subtopics}
                added={added}
                labels={labels}
              />
            </li>
          ) : (
            <li
              key={topic.key}
              className={cn(
                "flex items-center gap-4 px-6 py-4 transition-colors",
                topic.key === "new" && "bg-primary/5"
              )}
            >
              {topic.checked ? (
                <span className="flex size-5 shrink-0 items-center justify-center rounded-[6px] bg-primary text-primary-foreground">
                  <CheckIcon className="size-3.5" />
                </span>
              ) : (
                <span className="size-5 shrink-0 rounded-[6px] border border-input" />
              )}
              <span className="min-w-0 flex-1 space-y-0.5">
                <span className="block font-medium">{topic.name}</span>
                <span className="block text-sm text-muted-foreground">
                  {topic.subtopics.map((subtopic, position) => (
                    <span key={subtopic}>
                      {position > 0 && (
                        <MinusIcon className="mx-1.5 inline size-3.5 align-[-2px] text-foreground/55" />
                      )}
                      {subtopic}
                    </span>
                  ))}
                </span>
              </span>
              <span className="flex size-8 shrink-0 items-center justify-center">
                <SquarePenIcon className="size-4 text-muted-foreground" />
              </span>
            </li>
          )
        )}
      </ul>
      <div className="rounded-3xl border bg-card px-6 py-5">
        {asking ? (
          <span>
            {change.slice(0, letters.change)}
            <Caret />
          </span>
        ) : (
          // Lowercase, like every placeholder on the site.
          <span className="text-muted-foreground lowercase">
            {labels.placeholder}
          </span>
        )}
      </div>
      <div className="flex justify-end">
        <span
          aria-disabled={step === "applying" || undefined}
          className={buttonVariants({
            className: cn(
              "h-10 px-5 lowercase",
              step === "apply" && "ring-2 ring-ring/50",
              step === "applying" && "opacity-50"
            ),
          })}
        >
          {labels.apply}
        </span>
      </div>
    </div>
  )
}
