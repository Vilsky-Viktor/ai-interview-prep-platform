"use client"

import { useEffect, useState } from "react"

import { ReviewItem } from "@/components/rounds/review-item"
import { apiFetch } from "@/lib/api"
import type { ReviewItem as ReviewItemType } from "@/types/round"

export function RoundReview({ roundId }: { roundId: string }) {
  const [items, setItems] = useState<ReviewItemType[] | null>(null)

  useEffect(() => {
    apiFetch<ReviewItemType[]>(`/rounds/rounds/${roundId}/review`)
      .then(setItems)
      .catch(() => setItems([]))
  }, [roundId])

  if (!items) {
    return null
  }

  return (
    <ul className="divide-y rounded-2xl border">
      {items.map((item) => (
        <ReviewItem key={item.question_id} item={item} />
      ))}
    </ul>
  )
}
