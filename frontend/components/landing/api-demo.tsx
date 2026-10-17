"use client"

import { cn } from "cn"
import { useEffect, useState } from "react"

import { Caret } from "@/components/landing/caret"
import { API_EXAMPLE } from "@/constants/api"
import { type CodeToken, useHighlight } from "@/hooks/use-highlight"

// The request's first lines, then its body, typed a letter each TYPE_MS; the answer comes
// ANSWER_MS later and shows for HOLD_MS before it starts again.
const TYPE_MS = 30
const BODY_PAUSE_MS = 300
const ANSWER_MS = 600
const HOLD_MS = 4000
const { request, response } = API_EXAMPLE
const TYPED = request.head.length + request.body.length

/** prepza's API at work, playing on a loop: a request typed out, its body, then the answer. Every
 * text keeps its place while it's typed, so the card never changes size. Without scripts or with
 * reduced motion it shows the whole exchange. */
export function ApiDemo() {
  // The whole exchange until the loop starts: without scripts or with reduced motion, it stays.
  const [letters, setLetters] = useState(TYPED)
  const [answered, setAnswered] = useState(true)

  useEffect(() => {
    let typed = 0
    let timer: number

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    function next() {
      if (typed < TYPED) {
        typed += 1
        setLetters(typed)
        // A short pause between the first lines and the body, as if moving to it.
        timer = window.setTimeout(
          next,
          typed === request.head.length ? BODY_PAUSE_MS : TYPE_MS
        )

        return
      }

      setAnswered(true)
      timer = window.setTimeout(() => {
        typed = 0
        setLetters(0)
        setAnswered(false)
        timer = window.setTimeout(next, ANSWER_MS)
      }, HOLD_MS)
    }

    // The loop starts from an empty request.
    timer = window.setTimeout(() => {
      setLetters(0)
      setAnswered(false)
      timer = window.setTimeout(next, ANSWER_MS)
    }, 0)

    return () => window.clearTimeout(timer)
  }, [])

  const head = Math.min(letters, request.head.length)
  const body = Math.max(0, letters - request.head.length)
  const typing = letters < TYPED

  return (
    <div className="divide-y overflow-x-auto font-mono leading-relaxed">
      <div className="grid gap-x-10 gap-y-2 p-5 sm:grid-cols-2">
        <Typed
          text={request.head}
          language="http"
          shown={head}
          caret={typing && body === 0}
        />
        <Typed
          text={request.body}
          language="json"
          shown={body}
          caret={typing && body > 0}
        />
      </div>
      {/* The answer, there all along so the card keeps its size, fades in once it comes. */}
      <div
        className={cn(
          "grid gap-x-10 gap-y-2 p-5 text-muted-foreground transition-opacity duration-500 sm:grid-cols-2",
          !answered && "opacity-0"
        )}
      >
        <Typed text={response.head} language="http" />
        <Typed text={response.body} language="json" />
      </div>
    </div>
  )
}

/** `text` in its language's colors, with its first `shown` letters visible (all by default) and
 * the rest holding their place. */
function Typed({
  text,
  language,
  shown = text.length,
  caret = false,
}: {
  text: string
  language: string
  shown?: number
  caret?: boolean
}) {
  const lines = useHighlight(text, language)
  const tokens: CodeToken[] = lines
    ? lines.flatMap((line, index) =>
        index > 0 ? [{ content: "\n" }, ...line] : line
      )
    : [{ content: text }]
  // Where each token starts in the text, and the token the caret ends.
  const starts = tokens.map((_, index) =>
    tokens.slice(0, index).reduce((sum, token) => sum + token.content.length, 0)
  )
  const caretAt = tokens.findIndex(
    (token, index) => starts[index] + token.content.length >= shown
  )

  return (
    <pre>
      {tokens.map((token, index) => {
        const start = starts[index]
        const visible = token.content.slice(0, Math.max(0, shown - start))
        const hidden = token.content.slice(visible.length)

        return (
          <span
            key={index}
            style={token.style}
            className="text-(--shiki-light) dark:text-(--shiki-dark)"
          >
            {visible}
            {caret && index === caretAt && <Caret />}
            {hidden && <span className="invisible">{hidden}</span>}
          </span>
        )
      })}
    </pre>
  )
}
