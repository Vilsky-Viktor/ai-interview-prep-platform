"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"

/** The preview's "accept & start": a free run of the test as a candidate, kept out of the
 * candidate list; the player links back to the test it came from. */
export function StartPreview({
  companyId,
  interviewId,
}: {
  companyId: string
  interviewId: string
}) {
  const t = useTranslations("invite")
  const interviews = useTranslations("interviews")
  const router = useRouter()
  const [starting, setStarting] = useState(false)

  async function start() {
    setStarting(true)

    try {
      const preview = await apiFetch<{ session_id: string }>(
        `/companies/interviews/${interviewId}/preview`,
        { method: "POST" }
      )
      router.push(
        `/sessions/${preview.session_id}?from=/companies/${companyId}/interviews/${interviewId}`
      )
    } catch (error) {
      toast.error(apiErrorMessage(error, interviews("tryFailed")))
      setStarting(false)
    }
  }

  return (
    <Button className="h-12 px-6 text-base" disabled={starting} onClick={start}>
      {t("start")}
    </Button>
  )
}
