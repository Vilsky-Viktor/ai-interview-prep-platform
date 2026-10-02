"use client"

import { PlusIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { ApiError, apiFetch } from "@/lib/api"
import type { Candidate } from "@/types/company"

export function InviteCandidate({ interviewId }: { interviewId: string }) {
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
      toast.success(`Invite sent to ${candidate.email}`)
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
            ? "Check the email address and try again."
            : "Couldn't send the invite."
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <form onSubmit={send} className="flex">
      <InputAction
        type="email"
        required
        placeholder="candidate@example.com"
        aria-label="Candidate email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        action="Invite"
        icon={<PlusIcon className="size-5" />}
        disabled={sending || !email}
      />
    </form>
  )
}
