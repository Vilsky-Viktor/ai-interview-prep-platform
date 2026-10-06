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

/** Resend the invite email, or revoke an invite the candidate hasn't used yet. A candidate who
 * started or finished can be deleted for good instead, for example when they ask to have their
 * data erased. */
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
  // An invite not used yet is revoked; a candidate who started is deleted with their results.
  const unused = ["invited", "undelivered", "expired"].includes(status)

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
      toast.success(t(unused ? "revoked" : "erased", { email }))
      router.push(backHref)
      router.refresh()
    } catch (error) {
      toast.error(
        apiErrorMessage(error, t(unused ? "revokeFailed" : "eraseFailed"))
      )
      setBusy(false)
      setConfirmRevoke(false)
    }
  }

  return (
    <div className="flex items-center gap-2">
      {status !== "finished" && (
        <Button variant="outline" disabled={busy} onClick={resend}>
          {t("resend")}
        </Button>
      )}
      <Button
        variant="destructive"
        disabled={busy}
        onClick={() => setConfirmRevoke(true)}
      >
        {t(unused ? "revoke" : "erase")}
      </Button>
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
            <DialogTitle className="no-dot">
              {t(unused ? "revokeTitle" : "eraseTitle")}
            </DialogTitle>
            <DialogDescription>
              {t(unused ? "revokeText" : "eraseText", { email })}
            </DialogDescription>
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
              {t(unused ? "revokeConfirm" : "eraseConfirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
