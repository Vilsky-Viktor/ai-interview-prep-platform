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
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { apiErrorMessage, apiFetch } from "@/lib/api"

type CandidateActionsProps = {
  interviewId: string
  inviteId: string
  email: string
  status: string
  // Where to go once the invite is revoked.
  backHref: string
}

/** Resend the invite email, or revoke an invite the candidate hasn't used yet. */
export function CandidateActions({
  interviewId,
  inviteId,
  email,
  status,
  backHref,
}: CandidateActionsProps) {
  const t = useTranslations("candidates")
  const common = useTranslations("common")
  const router = useRouter()
  const [busy, setBusy] = useState(false)
  const [confirmRevoke, setConfirmRevoke] = useState(false)
  const path = `/companies/interviews/${interviewId}/candidates`

  async function resend() {
    setBusy(true)

    try {
      // Inviting the same email again sends the same link again.
      await apiFetch(path, { method: "POST", body: JSON.stringify({ email }) })
      toast.success(t("resent", { email }))
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("resendFailed")))
    } finally {
      setBusy(false)
    }
  }

  async function revoke() {
    setBusy(true)

    try {
      await apiFetch(`${path}/${inviteId}`, { method: "DELETE" })
      toast.success(t("revoked", { email }))
      router.push(backHref)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("revokeFailed")))
      setBusy(false)
      setConfirmRevoke(false)
    }
  }

  if (status === "finished") {
    return null
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" disabled={busy} onClick={resend}>
        {t("resend")}
      </Button>
      {(status === "invited" ||
        status === "undelivered" ||
        status === "expired") && (
        <Button
          variant="destructive"
          disabled={busy}
          onClick={() => setConfirmRevoke(true)}
        >
          {t("revoke")}
        </Button>
      )}
      <Dialog
        open={confirmRevoke}
        onOpenChange={(open) => {
          if (!open && !busy) {
            setConfirmRevoke(false)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="no-dot">{t("revokeTitle")}</DialogTitle>
            <DialogDescription>{t("revokeText", { email })}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={busy}
                />
              }
            >
              {common("keep")}
            </DialogClose>
            <Button
              variant="destructive"
              className="h-10 px-5 text-base"
              disabled={busy}
              onClick={revoke}
            >
              {t("revokeConfirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
