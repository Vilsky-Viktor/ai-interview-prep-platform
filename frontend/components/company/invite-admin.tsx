"use client"

import { PlusIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { MAX_EMAIL_LENGTH } from "@/constants/limits"
import { apiFetch } from "@/lib/api"
import type { CompanyMember } from "@/types/company"

export function InviteAdmin({ companyId }: { companyId: string }) {
  const t = useTranslations("interviews")
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
      toast.error(t("adminFailed"))
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
        placeholder="admin@example.com"
        aria-label={t("adminEmail")}
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        action={t("addAdmin")}
        icon={<PlusIcon className="size-5" />}
        disabled={sending || !email}
      />
    </form>
  )
}
