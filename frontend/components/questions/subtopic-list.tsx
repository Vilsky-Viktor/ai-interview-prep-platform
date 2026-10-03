"use client"

import { cn } from "cn"
import { MinusIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useEffect, useRef, useState } from "react"

export function SubtopicList({ subtopics }: { subtopics: string[] }) {
  const t = useTranslations("questions")
  const listRef = useRef<HTMLSpanElement>(null)
  const [expanded, setExpanded] = useState(false)
  const [overflows, setOverflows] = useState(false)

  useEffect(() => {
    const list = listRef.current

    if (!list || expanded) {
      return
    }

    const observer = new ResizeObserver(() =>
      setOverflows(list.scrollHeight > list.clientHeight + 1)
    )
    observer.observe(list)

    return () => observer.disconnect()
  }, [expanded])

  if (subtopics.length === 0) {
    return null
  }

  return (
    <span className="block space-y-1">
      <span
        ref={listRef}
        className={cn(
          "block text-sm text-muted-foreground",
          !expanded && "line-clamp-2"
        )}
      >
        {subtopics.map((subtopic, index) => (
          <span key={subtopic}>
            {index > 0 && (
              <MinusIcon
                aria-hidden
                className="mx-1.5 inline size-3.5 align-[-2px] text-foreground/55"
              />
            )}
            {subtopic}
          </span>
        ))}
      </span>
      {(overflows || expanded) && (
        <button
          type="button"
          onClick={() => setExpanded((current) => !current)}
          className="cursor-pointer text-sm text-foreground transition-colors hover:text-primary"
        >
          {expanded ? t("showLess") : t("showAll")}
        </button>
      )}
    </span>
  )
}
