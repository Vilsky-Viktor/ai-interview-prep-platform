"use client"

import { useEffect, useState } from "react"

const WORDS = ["an interview", "a certification", "an exam", "a test", "a promotion"]
const TYPE_MS = 70
const DELETE_MS = 40
const HOLD_MS = 1600

export function HomeTitle() {
  const [index, setIndex] = useState(0)
  const [text, setText] = useState(WORDS[0])
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)")

    if (media.matches) {
      return
    }

    const word = WORDS[index]
    const typed = text === word
    const cleared = deleting && text === ""
    let delay = TYPE_MS

    if (deleting) {
      delay = DELETE_MS
    } else if (typed) {
      delay = HOLD_MS
    }

    const timer = window.setTimeout(() => {
      if (cleared) {
        setDeleting(false)
        setIndex((current) => (current + 1) % WORDS.length)

        return
      }

      if (deleting) {
        setText(word.slice(0, text.length - 1))

        return
      }

      if (typed) {
        setDeleting(true)

        return
      }

      setText(word.slice(0, text.length + 1))
    }, delay)

    return () => window.clearTimeout(timer)
  }, [text, deleting, index])

  return (
    <h1
      aria-label={`Preparing for ${WORDS[index]}?`}
      className="no-dot text-center font-heading text-3xl font-medium tracking-tight sm:text-5xl sm:whitespace-nowrap"
    >
      <span aria-hidden>
        Preparing for{" "}
        <span className="inline-grid text-left">
          <span className="invisible col-start-1 row-start-1">
            self-education
            <span className="mx-2 inline-block w-0.5" />?
          </span>
          <span className="col-start-1 row-start-1">
            <span className="text-primary">{text}</span>
            <span className="mx-2 inline-block h-[0.85em] w-0.5 translate-y-[0.08em] animate-[caret-blink_0.5s_steps(1,end)_infinite] bg-current align-middle motion-reduce:hidden" />
            ?
          </span>
        </span>
      </span>
    </h1>
  )
}
