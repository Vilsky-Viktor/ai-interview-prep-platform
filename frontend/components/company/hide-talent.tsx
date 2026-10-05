"use client"

import { EyeOffIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"

/** Hides a suggested talent who doesn't fit from the test's list, for the whole company. */
export function HideTalent({
  interviewId,
  url,
}: {
  interviewId: string
  url: string
}) {
  const t = useTranslations("talents")
  const router = useRouter()
  const [busy, setBusy] = useState(false)

  async function hide() {
    setBusy(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}/suggestions/hide`, {
        method: "POST",
        body: JSON.stringify({ url }),
      })
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("hideFailed")))
      setBusy(false)
    }
  }

  return (
    <Button
      variant="ghost"
      size="icon-lg"
      aria-label={t("hide")}
      disabled={busy}
      onClick={hide}
      className="shrink-0 text-muted-foreground"
    >
      <EyeOffIcon className="size-6" />
    </Button>
  )
}
