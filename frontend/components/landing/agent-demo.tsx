"use client"

import { MicIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useEffect, useRef, useState } from "react"

import { ActionCard } from "@/components/assistant/action-card"
import { ChatBubble } from "@/components/chat-bubble"
import { ChatInput } from "@/components/chat-input"
import { PANEL } from "@/components/landing/section"
import { Button } from "@/components/ui/button"
import type { AssistantBlock } from "@/types/assistant"

// The card the assistant prepares for the question, as the panel shows it.
const CARD: AssistantBlock = {
  kind: "confirm",
  items: [],
  links: [],
  action_id: "demo",
  tool: "invite_candidate",
  subject: "Architect",
  preview: { email: "ann.lee@example.com", name: "Ann Lee" },
  company_id: null,
  destructive: false,
  state: "pending",
}

// Per letter typed and erased, and the pauses on a full question and an empty input, in ms.
const TYPE_MS = 45
const ERASE_MS = 20
const HOLD_MS = 1800
const EMPTY_MS = 500

/** The text the input shows: each question typed letter by letter, held, erased, then the
 * next. With reduced motion, nothing: the input shows its placeholder. */
function useTypedText(questions: string[]) {
  const [text, setText] = useState("")

  useEffect(() => {
    // With reduced motion nothing is typed: the input shows its placeholder.
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    // Letters as the reader sees them, so Thai or Hindi marks never show on their own.
    const segmenter = new Intl.Segmenter()
    const letters = questions.map((question) =>
      Array.from(segmenter.segment(question), (part) => part.segment)
    )
    let index = 0
    let length = 0
    let erasing = false
    let timer: ReturnType<typeof setTimeout>

    function step() {
      const current = letters[index]
      length += erasing ? -1 : 1
      setText(current.slice(0, length).join(""))

      if (!erasing && length === current.length) {
        erasing = true
        timer = setTimeout(step, HOLD_MS)

        return
      }

      if (erasing && length === 0) {
        erasing = false
        index = (index + 1) % letters.length
        timer = setTimeout(step, EMPTY_MS)

        return
      }

      timer = setTimeout(step, erasing ? ERASE_MS : TYPE_MS)
    }

    timer = setTimeout(step, EMPTY_MS)

    return () => clearTimeout(timer)
  }, [questions])

  return text
}

/** The end of `text` that fits in `room` pixels: like a real input, the field shows the end
 * being typed, and it stops before the buttons. */
function lastFitting(text: string, room: number, font: string) {
  const context = document.createElement("canvas").getContext("2d")

  if (!context) {
    return text
  }

  context.font = font
  const letters = Array.from(
    new Intl.Segmenter().segment(text),
    (part) => part.segment
  )
  let start = 0

  while (
    start < letters.length &&
    context.measureText(letters.slice(start).join("")).width > room
  ) {
    start += 1
  }

  return letters.slice(start).join("")
}

/** The assistant's panel as it looks after a request: the question, the card waiting for
 * Confirm, and the input with the voice button, built from the panel's own pieces. A picture:
 * nothing in it can be used. Its input types more questions, one after another, on one line. */
export function AgentDemo({
  question,
  typed,
}: {
  question: string
  typed: string[]
}) {
  const t = useTranslations("assistant")
  const text = useTypedText(typed)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // The room for text before the buttons, and the font it's drawn in.
  const [box, setBox] = useState<{ room: number; font: string } | null>(null)

  useEffect(() => {
    const input = inputRef.current

    if (!input) {
      return
    }

    const observer = new ResizeObserver(() => {
      const style = getComputedStyle(input)
      setBox({
        room:
          input.clientWidth -
          parseFloat(style.paddingInlineStart) -
          parseFloat(style.paddingInlineEnd),
        font: `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`,
      })
    })
    observer.observe(input)

    return () => observer.disconnect()
  }, [])

  return (
    <div
      inert
      className={`${PANEL} mx-auto max-w-xl space-y-4 p-5 text-start sm:px-8 sm:py-6 [&_textarea]:overflow-hidden [&_textarea]:whitespace-pre [&_textarea::placeholder]:whitespace-pre`}
    >
      <ul>
        <ChatBubble role="user" content={question} />
      </ul>
      <ActionCard
        card={CARD}
        actions={{
          onConfirm: () => {},
          onCancel: () => {},
          busy: false,
          companyNames: {},
        }}
        onNavigate={() => {}}
      />
      <ChatInput
        value={box ? lastFitting(text, box.room, box.font) : text}
        onChange={() => {}}
        onSubmit={() => {}}
        label={t("placeholder")}
        placeholder={t("placeholder")}
        streaming={false}
        inputRef={inputRef}
      >
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className="size-10 rounded-full"
        >
          <MicIcon className="size-5" />
        </Button>
      </ChatInput>
    </div>
  )
}
