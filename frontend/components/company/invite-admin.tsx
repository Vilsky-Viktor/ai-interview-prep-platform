"use client"

import { PlusIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { apiFetch } from "@/lib/api"
import type { CompanyMember } from "@/types/company"

export function InviteAdmin({ companyId }: { companyId: string }) {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [sending, setSending] = useState(false)

  async function send(event: React.FormEvent) {
    event.preventDefault()
    setSending(true)

    try {
      await apiFetch<CompanyMember>(
        `/companies/members?company_id=${companyId}`,
        {
          method: "POST",
          body: JSON.stringify({ email }),
        }
      )
      setEmail("")
      router.refresh()
    } catch {
      toast.error("Couldn't invite that admin. Please try again.")
    } finally {
      setSending(false)
    }
  }

  return (
    <form onSubmit={send} className="flex">
      <InputAction
        type="email"
        required
        placeholder="admin@example.com"
        aria-label="Admin email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        action="Add admin"
        icon={<PlusIcon className="size-5" />}
        disabled={sending || !email}
      />
    </form>
  )
}
