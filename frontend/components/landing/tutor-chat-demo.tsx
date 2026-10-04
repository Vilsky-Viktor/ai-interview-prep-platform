"use client"

import { cn } from "cn"
import { ArrowUpIcon } from "lucide-react"
import { useEffect, useState } from "react"

import { ChatBubble, ThinkingBubble } from "@/components/chat-bubble"
import { Caret } from "@/components/landing/caret"

// The demo's steps and how long each shows, in milliseconds. It starts on the finished
// conversation, which is also what shows with reduced motion. "typing" shows one more letter
// of the question each `ms`, "streaming" one more word of the answer.
const STEPS = [
  { name: "shown", ms: 3000 },
  { name: "idle", ms: 900 },
  { name: "typing", ms: 60 },
  { name: "send", ms: 350 },
  { name: "thinking", ms: 1400 },
  { name: "streaming", ms: 90 },
] as const

/** A follow-up question to the tutor as the real chat shows it (components/rounds/chat-panel.tsx):
 * typed, sent, the tutor thinking, then its answer arriving word by word. */
export function TutorChatDemo({
  ask,
  answer,
  placeholder,
  thinking,
}: {
  ask: string
  answer: string
  placeholder: string
  thinking: string
}) {
  const words = answer.split(" ")
  const [index, setIndex] = useState(0)
  const [letters, setLetters] = useState(0)
  const [shownWords, setShownWords] = useState(words.length)
  const step = STEPS[index].name

  useEffect(() => {
    // With reduced motion the demo doesn't play; the finished conversation stays.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    const total = answer.split(" ").length
    let at = 0
    let typed = 0
    let streamed = total
    let timer: number

    function next() {
      const current = STEPS[at].name

      if (current === "typing" && typed < ask.length) {
        typed += 1
      } else if (current === "streaming" && streamed < total) {
        streamed += 1
      } else {
        at = (at + 1) % STEPS.length

        if (STEPS[at].name === "idle") {
          typed = 0
          streamed = 0
        }
      }

      setIndex(at)
      setLetters(typed)
      setShownWords(streamed)
      timer = window.setTimeout(next, STEPS[at].ms)
    }

    timer = window.setTimeout(next, STEPS[0].ms)

    return () => window.clearTimeout(timer)
  }, [ask, answer])

  const sent = ["thinking", "streaming", "shown"].includes(step)
  const draft =
    step === "typing" || step === "send" ? ask.slice(0, letters) : ""

  return (
    <div className="space-y-4">
      {/* Room for both messages, so the card keeps its size while the demo plays. */}
      <ul className="min-h-28 space-y-3">
        {sent && <ChatBubble role="user" content={ask} />}
        {step === "thinking" && <ThinkingBubble label={thinking} />}
        {(step === "streaming" || step === "shown") && (
          <ChatBubble
            role="assistant"
            content={words.slice(0, shownWords).join(" ")}
          />
        )}
      </ul>
      <div className="relative rounded-[2rem] bg-muted">
        <p className="px-6 py-4 pe-20 text-lg">
          {draft ? (
            <span>
              {draft}
              <Caret />
            </span>
          ) : (
            <span className="text-muted-foreground">{placeholder}</span>
          )}
        </p>
        <span
          className={cn(
            "absolute end-3 top-1/2 flex size-10 -translate-y-1/2 items-center justify-center rounded-full bg-primary text-primary-foreground transition-opacity",
            !draft && "opacity-50",
            step === "send" && "ring-2 ring-ring/50"
          )}
        >
          <ArrowUpIcon className="size-5" />
        </span>
      </div>
    </div>
  )
}
