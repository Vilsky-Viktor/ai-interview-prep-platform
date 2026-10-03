"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import type { Round } from "@/types/round"

// Starting a topic with an unfinished round resumes that round.
export function StartRound({
  topicId,
  inProgress = false,
}: {
  topicId: string
  inProgress?: boolean
}) {
  const t = useTranslations("rounds")
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
    } catch (error) {
      // Over the day's new public topics: the message offers a kit of their own.
      const limited = error instanceof ApiError && error.status === 429
      toast.error(
        apiErrorMessage(error, t("startFailed")),
        limited
          ? {
              action: {
                label: t("makeItYoursAction"),
                onClick: () => router.push("/"),
              },
            }
          : undefined
      )
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
      {inProgress ? t("continue") : t("start")}
    </Button>
  )
}
