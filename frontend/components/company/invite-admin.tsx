"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { MAX_EMAIL_LENGTH } from "@/constants/limits"
import { apiFetch } from "@/lib/api"
import type { CompanyMember } from "@/types/company"

/** "Add admin" beside the page title, opening a dialog for the email, as "new company" does. */
export function InviteAdmin({ companyId }: { companyId: string }) {
  const t = useTranslations("interviews")
  const common = useTranslations("common")
  const router = useRouter()
  const [open, setOpen] = useState(false)
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
      setOpen(false)
      router.refresh()
    } catch {
      toast.error(t("adminFailed"))
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !sending && setOpen(next)}>
      <DialogTrigger render={<Button className="h-12 px-6 text-base" />}>
        {t("addAdmin")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("addAdmin")}</DialogTitle>
        </DialogHeader>
        <form id="invite-admin-form" onSubmit={send}>
          <div className="rounded-full border border-transparent transition-colors focus-within:border-ring">
            <Input
              type="email"
              required
              maxLength={MAX_EMAIL_LENGTH}
              placeholder="admin@example.com"
              aria-label={t("adminEmail")}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"
            />
          </div>
        </form>
        <DialogFooter>
          <DialogClose
            render={
              <Button
                variant="outline"
                className="h-10 px-5 text-base"
                disabled={sending}
              />
            }
          >
            {common("cancel")}
          </DialogClose>
          <Button
            type="submit"
            form="invite-admin-form"
            className="h-10 px-5 text-base"
            disabled={sending || !email}
          >
            {t("addAdmin")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
