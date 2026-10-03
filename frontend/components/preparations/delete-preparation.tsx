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
import { apiFetch } from "@/lib/api"

export function DeletePreparation({
  preparationId,
  title,
}: {
  preparationId: string
  title: string
}) {
  const t = useTranslations("preparations")
  const common = useTranslations("common")
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch(`/library/preparations/${preparationId}`, {
        method: "DELETE",
      })
      router.push("/preparations")
      router.refresh()
    } catch {
      toast.error(t("deleteFailed"))
      setDeleting(false)
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="size-10 text-muted-foreground hover:text-destructive"
        aria-label={t("deleteLabel", { title })}
        onClick={() => setOpen(true)}
      >
        <Trash2Icon className="size-5" />
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
            <DialogTitle className="no-dot">
              {t("deleteTitle", { title })}
            </DialogTitle>
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
