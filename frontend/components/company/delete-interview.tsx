"use client"

import { Trash2Icon } from "lucide-react"
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

export function DeleteInterview({
  interviewId,
  title,
  leaveTo,
}: {
  interviewId: string
  title: string
  // Where to go once deleted, from the interview's own page; a list just refreshes.
  leaveTo?: string
}) {
  const t = useTranslations("interviews")
  const common = useTranslations("common")
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}`, {
        method: "DELETE",
      })
      setOpen(false)

      if (leaveTo) {
        router.push(leaveTo)
      }

      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("deleteFailed")))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="size-12 shrink-0 text-muted-foreground hover:text-destructive"
        aria-label={t("deleteLabel", { title })}
        tooltip={common("delete")}
        onClick={() => setOpen(true)}
      >
        <Trash2Icon className="size-6" />
      </Button>
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (!deleting) {
            setOpen(next)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="no-dot">{t("deleteTitle")}</DialogTitle>
            <DialogDescription>{t("deleteText")}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={deleting}
                />
              }
            >
              {common("keep")}
            </DialogClose>
            <Button
              variant="destructive"
              className="h-10 px-5 text-base"
              disabled={deleting}
              onClick={remove}
            >
              {deleting ? common("deleting") : common("delete")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
