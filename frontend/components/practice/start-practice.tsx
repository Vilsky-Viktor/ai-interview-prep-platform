"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { ApiError, apiErrorMessage } from "@/lib/api"
import { signIn } from "@/lib/auth"
import { answeredSuggest, startPracticeRound } from "@/lib/practice"

/** Starts a free practice round on the template: signs in with Google first when needed. A
 * talent who hasn't yet answered whether to be suggested to companies sees that page first,
 * once; after that, they go straight into the round. `label` names it (start, or practise
 * again). */
export function StartPractice({
  templateId,
  label,
}: {
  templateId: string
  label: string
}) {
  const t = useTranslations("practice")
  const signInText = useTranslations("signIn")
  const router = useRouter()
  const { user } = useAuth()
  const [starting, setStarting] = useState(false)

  async function start() {
    setStarting(true)

    if (!user && !(await signIn(signInText("failed")))) {
      setStarting(false)

      return
    }

    try {
      router.push(
        (await answeredSuggest())
          ? await startPracticeRound(templateId)
          : `/practice/${templateId}/start`
      )
    } catch (error) {
      // No practice questions yet: the API says so.
      const refused = error instanceof ApiError && error.status === 409
      toast.error(
        refused ? error.message : apiErrorMessage(error, t("startFailed"))
      )
      setStarting(false)
    }
  }

  return (
    <Button className="h-12 px-6 text-base" disabled={starting} onClick={start}>
      {label}
    </Button>
  )
}
