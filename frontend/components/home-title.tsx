"use client"

import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"

const TYPE_MS = 70
const DELETE_MS = 40
const HOLD_MS = 1600

export function HomeTitle() {
  const t = useTranslations("home")
  const words = t.raw("words") as string[]
  const [index, setIndex] = useState(0)
  const [text, setText] = useState(words[0])
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)")

    if (media.matches) {
      return
    }

    const word = words[index]
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
        setIndex((current) => (current + 1) % words.length)

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
  }, [text, deleting, index, words])

  return (
    <h1
      aria-label={`${t("preparingFor")} ${words[index]}${t("mark")}`}
      className="no-dot text-center font-heading text-3xl font-medium tracking-tight sm:text-5xl sm:whitespace-nowrap"
    >
      <span aria-hidden>
        {t("preparingFor")}{" "}
        <span className="inline-grid text-start">
          <span className="invisible col-start-1 row-start-1">
            {t("widest")}
            <span className="mx-2 inline-block w-0.5" />
            {t("mark")}
          </span>
          <span className="col-start-1 row-start-1">
            <span className="text-primary">{text}</span>
            <span className="mx-2 inline-block h-[0.85em] w-0.5 translate-y-[0.08em] animate-[caret-blink_0.5s_steps(1,end)_infinite] bg-current align-middle motion-reduce:hidden" />
            {t("mark")}
          </span>
        </span>
      </span>
    </h1>
  )
}
