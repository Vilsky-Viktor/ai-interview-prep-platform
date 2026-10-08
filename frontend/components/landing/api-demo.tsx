"use client"

import { cn } from "cn"
import { useEffect, useState } from "react"

import { Caret } from "@/components/landing/caret"
import { API_EXAMPLE } from "@/constants/api"

// The request's first lines, then its body, typed a letter each TYPE_MS; the answer comes
// ANSWER_MS later and shows for HOLD_MS before it starts again.
const TYPE_MS = 30
const BODY_PAUSE_MS = 300
const ANSWER_MS = 600
const HOLD_MS = 4000
const { request, response } = API_EXAMPLE
const TYPED = request.head.length + request.body.length

/** prepza's API at work, playing on a loop: a request typed out, its body, then the answer. Every
 * text keeps its place while it's typed, so the card never changes size. With reduced motion it
 * shows the whole exchange at once. */
export function ApiDemo() {
  const [letters, setLetters] = useState(0)
  const [answered, setAnswered] = useState(false)

  useEffect(() => {
    let typed = 0
    let timer: number

    // With reduced motion the whole exchange shows at once.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      timer = window.setTimeout(() => {
        setLetters(TYPED)
        setAnswered(true)
      }, 0)

      return () => window.clearTimeout(timer)
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

    timer = window.setTimeout(next, ANSWER_MS)

    return () => window.clearTimeout(timer)
  }, [])

  const head = Math.min(letters, request.head.length)
  const body = Math.max(0, letters - request.head.length)
  const typing = letters < TYPED

  return (
    <div className="divide-y overflow-x-auto font-mono leading-relaxed">
      <div className="grid gap-x-10 gap-y-2 p-5 sm:grid-cols-2">
        <Typed text={request.head} shown={head} caret={typing && body === 0} />
        <Typed text={request.body} shown={body} caret={typing && body > 0} />
      </div>
      {/* The answer, there all along so the card keeps its size, fades in once it comes. */}
      <div
        className={cn(
          "grid gap-x-10 gap-y-2 p-5 text-muted-foreground transition-opacity duration-500 sm:grid-cols-2",
          !answered && "opacity-0"
        )}
      >
        <pre>{response.head}</pre>
        <pre>{response.body}</pre>
      </div>
    </div>
  )
}

/** `text` with its first `shown` letters visible and the rest holding their place. */
function Typed({
  text,
  shown,
  caret,
}: {
  text: string
  shown: number
  caret: boolean
}) {
  return (
    <pre>
      {text.slice(0, shown)}
      {caret && <Caret />}
      <span className="invisible">{text.slice(shown)}</span>
    </pre>
  )
}
