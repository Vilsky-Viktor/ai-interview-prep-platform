"use client"

import { cn } from "cn"
import { ThumbsDownIcon, ThumbsUpIcon } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { FEEDBACK_HOVER_CLASS } from "@/constants/feedback"
import { ApiError, apiFetch } from "@/lib/api"

type Thumb = 1 | -1

export function QuestionRating({ basePath }: { basePath: string }) {
  const [value, setValue] = useState<Thumb | null>(null)
  const [saving, setSaving] = useState(false)
  const voted = useRef(false)

  useEffect(() => {
    voted.current = false
    apiFetch<{ value: Thumb | null }>(`${basePath}/rating`)
      .then((body) => {
        if (voted.current) {
          return
        }

        voted.current = body.value !== null
        setValue(body.value)
      })
      .catch(() => {})
  }, [basePath])

  async function rate(next: Thumb) {
    if (voted.current || saving) {
      return
    }

    voted.current = true
    setValue(next)
    setSaving(true)

    try {
      await apiFetch(`${basePath}/rating`, {
        method: "PUT",
        body: JSON.stringify({ value: next }),
      })
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        return
      }

      voted.current = false
      setValue(null)
      toast.error("Couldn't save your rating. Please try again.")
    } finally {
      setSaving(false)
    }
  }

  const locked = value !== null || saving

  return (
    <div className="contents">
      <Button
        type="button"
        variant="ghost"
        size="icon-lg"
        aria-label="Helpful question"
        className={cn(FEEDBACK_HOVER_CLASS, "h-full w-full rounded-none")}
        aria-pressed={value === 1}
        disabled={locked}
        onClick={() => rate(1)}
      >
        <ThumbsUpIcon
          className={cn("size-6", value === 1 && "fill-primary text-primary")}
        />
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="icon-lg"
        aria-label="Unhelpful question"
        className={cn(FEEDBACK_HOVER_CLASS, "h-full w-full rounded-none")}
        aria-pressed={value === -1}
        disabled={locked}
        onClick={() => rate(-1)}
      >
        <ThumbsDownIcon
          className={cn("size-6", value === -1 && "fill-primary text-primary")}
        />
      </Button>
    </div>
  )
}
