"use client"

import { useRouter } from "next/navigation"
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
  const router = useRouter()
  const [busy, setBusy] = useState(false)
  const [confirmRevoke, setConfirmRevoke] = useState(false)
  const path = `/companies/interviews/${interviewId}/candidates`

  async function resend() {
    setBusy(true)

    try {
      // Inviting the same email again sends the same link again.
      await apiFetch(path, { method: "POST", body: JSON.stringify({ email }) })
      toast.success(`Invite sent again to ${email}`)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, "Couldn't resend the invite."))
    } finally {
      setBusy(false)
    }
  }

  async function revoke() {
    setBusy(true)

    try {
      await apiFetch(`${path}/${inviteId}`, { method: "DELETE" })
      toast.success(`Invite for ${email} revoked`)
      router.push(backHref)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, "Couldn't revoke the invite."))
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
        Resend invite
      </Button>
      {(status === "invited" || status === "undelivered") && (
        <Button
          variant="destructive"
          disabled={busy}
          onClick={() => setConfirmRevoke(true)}
        >
          Revoke invite
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
            <DialogTitle className="no-dot">Revoke the invite?</DialogTitle>
            <DialogDescription>
              The link sent to {email} stops working. You can invite them again
              later.
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
              Keep
            </DialogClose>
            <Button
              variant="destructive"
              className="h-10 px-5 text-base"
              disabled={busy}
              onClick={revoke}
            >
              Revoke
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
