"use client"

import { cn } from "cn"
import { StarIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useRef, useState } from "react"
import { toast } from "sonner"

import { MAX_RATING } from "@/constants/feedback"
import { ApiError, apiFetch } from "@/lib/api"

export function RatingStars({
  preparationId,
  myRating,
}: {
  preparationId: string
  myRating: number | null
}) {
  const router = useRouter()
  const [hovered, setHovered] = useState(0)
  const [saving, setSaving] = useState(false)
  const [rating, setRating] = useState(myRating)
  const rated = useRef(myRating !== null)
  const shown = hovered || rating || 0
  const locked = rating !== null || saving

  async function rate(value: number) {
    if (rated.current || saving) {
      return
    }

    rated.current = true
    setSaving(true)
    setRating(value)

    try {
      await apiFetch(`/library/preparations/${preparationId}/rating`, {
        method: "PUT",
        body: JSON.stringify({ value }),
      })
      toast.success("Thanks for rating")
      router.refresh()
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        return
      }

      rated.current = false
      setRating(null)
      toast.error("Couldn't save your rating. Please try again.")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex items-center gap-3">
      {!rating && (
        <span className="text-sm text-muted-foreground">Rate it</span>
      )}
      <div
        className="flex"
        onMouseLeave={() => {
          if (!locked) {
            setHovered(0)
          }
        }}
      >
        {Array.from({ length: MAX_RATING }, (_, index) => index + 1).map(
          (value) => (
            <button
              key={value}
              type="button"
              aria-label={`Rate ${value} of ${MAX_RATING}`}
              disabled={locked}
              onMouseEnter={() => {
                if (!locked) {
                  setHovered(value)
                }
              }}
              onClick={() => rate(value)}
              className="rounded-sm p-0.5 text-muted-foreground transition-colors outline-none enabled:hover:text-yellow-600 focus-visible:ring-2 focus-visible:ring-ring"
            >
              <StarIcon
                className={cn(
                  "size-5",
                  value <= shown && "fill-yellow-500 text-yellow-600"
                )}
              />
            </button>
          )
        )}
      </div>
    </div>
  )
}
