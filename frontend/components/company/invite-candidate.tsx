"use client"

import { PlusIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { MAX_EMAIL_LENGTH } from "@/constants/limits"
import { ApiError, apiFetch } from "@/lib/api"
import type { Candidate } from "@/types/company"

export function InviteCandidate({ interviewId }: { interviewId: string }) {
  const t = useTranslations("interviews")
  const share = useTranslations("share")
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [sending, setSending] = useState(false)

  async function send(event: React.FormEvent) {
    event.preventDefault()
    setSending(true)

    try {
      const candidate = await apiFetch<Candidate>(
        `/companies/interviews/${interviewId}/candidates`,
        { method: "POST", body: JSON.stringify({ email }) }
      )
      toast.success(share("sent", { email: candidate.email }))
      setEmail("")
      router.refresh()
    } catch (error) {
      // Out of candidate credits: billing's message says how to get more.
      const noCredits = error instanceof ApiError && error.status === 402
      const invalid = error instanceof ApiError && error.status < 500
      toast.error(
        noCredits
          ? error.message
          : invalid
            ? share("checkEmail")
            : share("failed")
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <form onSubmit={send} className="flex">
      <InputAction
        maxLength={MAX_EMAIL_LENGTH}
        type="email"
        required
        placeholder="candidate@example.com"
        aria-label={t("candidateEmail")}
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        action={t("invite")}
        icon={<PlusIcon className="size-5" />}
        disabled={sending || !email}
      />
    </form>
  )
}
