"use client"

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
import type { CompanyMember } from "@/types/company"

/** Removes an admin, or withdraws an invite they haven't accepted yet, after a confirmation. */
export function RemoveMember({
  companyId,
  member,
  onRemoved,
}: {
  companyId: string
  member: CompanyMember
  onRemoved: () => void
}) {
  const t = useTranslations("members")
  const common = useTranslations("common")
  const [busy, setBusy] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const email = member.email

  async function remove() {
    setBusy(true)

    try {
      await apiFetch(
        `/companies/members/${member.id}?company_id=${companyId}`,
        { method: "DELETE" }
      )
      toast.success(t("removed", { email }))
      onRemoved()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("removeFailed")))
      setBusy(false)
      setConfirming(false)
    }
  }

  return (
    <>
      <Button
        variant="destructive"
        disabled={busy}
        onClick={() => setConfirming(true)}
      >
        {t("remove")}
      </Button>
      <Dialog
        open={confirming}
        onOpenChange={(open) => {
          if (!open && !busy) {
            setConfirming(false)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="no-dot">{t("removeTitle")}</DialogTitle>
            <DialogDescription>
              {t(member.joined ? "removeText" : "removeInviteText", { email })}
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
              onClick={remove}
            >
              {t("removeConfirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
