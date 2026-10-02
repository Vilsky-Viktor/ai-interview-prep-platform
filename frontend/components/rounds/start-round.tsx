"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/api"
import type { Round } from "@/types/round"

// Starting a topic with an unfinished round resumes that round.
export function StartRound({
  topicId,
  inProgress = false,
}: {
  topicId: string
  inProgress?: boolean
}) {
  const router = useRouter()
  const [starting, setStarting] = useState(false)

  async function start() {
    setStarting(true)

    try {
      const round = await apiFetch<Round>("/rounds/rounds", {
        method: "POST",
        body: JSON.stringify({ topic_id: topicId }),
      })
      router.push(`/rounds/${round.id}`)
    } catch {
      toast.error("Couldn't start the round. Please try again.")
      setStarting(false)
    }
  }

  return (
    <Button
      size="lg"
      className="h-12 px-8 text-base"
      disabled={starting}
      onClick={start}
    >
      {inProgress ? "Continue" : "Start"}
    </Button>
  )
}
