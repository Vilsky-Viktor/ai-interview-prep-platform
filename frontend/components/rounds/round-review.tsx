"use client"

import { useEffect, useState } from "react"

import { ReviewItem } from "@/components/rounds/review-item"
import { VirtualList } from "@/components/virtual-list"
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
    <VirtualList
      items={items}
      getKey={(item) => item.question_id}
      estimateSize={160}
      className="divide-y rounded-2xl border"
      renderItem={(item) => <ReviewItem item={item} />}
    />
  )
}
