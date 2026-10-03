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
import { signOut } from "@/lib/auth"

export function DeleteAccount({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const t = useTranslations("deleteAccount")
  const common = useTranslations("common")
  const router = useRouter()
  const [deleting, setDeleting] = useState(false)

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch("/library/me", { method: "DELETE" })
      await signOut()
      onOpenChange(false)
      toast.success(t("deleted"))
      router.push("/")
    } catch (error) {
      toast.error(apiErrorMessage(error, t("failed")))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => !deleting && onOpenChange(next)}
    >
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="no-dot">{t("title")}</DialogTitle>
          <DialogDescription className="space-y-2 text-base">
            <span className="block">{t("everything")}</span>
            <span className="block">{t("company")}</span>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose
            render={
              <Button variant="outline" className="h-12 px-6 text-base" />
            }
            disabled={deleting}
          >
            {common("keep")}
          </DialogClose>
          <Button
            variant="destructive"
            className="h-12 px-6 text-base"
            disabled={deleting}
            onClick={remove}
          >
            {deleting ? common("deleting") : t("confirm")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
