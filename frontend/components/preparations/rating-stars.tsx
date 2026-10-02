"use client"

import { cn } from "cn"
import { StarIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { apiFetch } from "@/lib/api"

export function RatingStars({
  preparationId,
  myRating,
  scale,
}: {
  preparationId: string
  myRating: number | null
  // Stars a rating can give; the API sets the scale.
  scale: number
}) {
  const router = useRouter()
  const [hovered, setHovered] = useState(0)
  const [saving, setSaving] = useState(false)
  const [rating, setRating] = useState(myRating)
  const shown = hovered || rating || 0
  const locked = saving

  // Rating again changes the rating.
  async function rate(value: number) {
    if (saving || value === rating) {
      return
    }

    const previous = rating
    setSaving(true)
    setRating(value)
    setHovered(0)

    try {
      await apiFetch(`/library/preparations/${preparationId}/rating`, {
        method: "PUT",
        body: JSON.stringify({ value }),
      })
      toast.success(previous === null ? "Thanks for rating" : "Rating updated")
      router.refresh()
    } catch {
      setRating(previous)
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
        {Array.from({ length: scale }, (_, index) => index + 1).map((value) => (
          <button
            key={value}
            type="button"
            aria-label={`Rate ${value} of ${scale}`}
            disabled={locked}
            onMouseEnter={() => {
              if (!locked) {
                setHovered(value)
              }
            }}
            onClick={() => rate(value)}
            className="rounded-sm p-0.5 text-muted-foreground transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring enabled:hover:text-yellow-600"
          >
            <StarIcon
              className={cn(
                "size-5",
                value <= shown && "fill-yellow-500 text-yellow-600"
              )}
            />
          </button>
        ))}
      </div>
    </div>
  )
}
