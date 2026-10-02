"use client"

import { Trash2Icon } from "lucide-react"
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
import { apiFetch } from "@/lib/api"

export function DeletePreparation({
  preparationId,
  title,
}: {
  preparationId: string
  title: string
}) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch(`/library/preparations/${preparationId}`, { method: "DELETE" })
      router.push("/preparations")
      router.refresh()
    } catch {
      toast.error("Couldn't delete the preparation. Please try again.")
      setDeleting(false)
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="size-10 text-muted-foreground hover:text-destructive"
        aria-label={`Delete ${title}`}
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
            <DialogTitle className="no-dot">Delete {title}?</DialogTitle>
            <DialogDescription>
              Its topics and questions are deleted, and everyone who joined it loses
              access. This can&apos;t be undone.
            </DialogDescription>
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
              Keep
            </DialogClose>
            <Button
              variant="destructive"
              className="h-10 px-5 text-base"
              disabled={deleting}
              onClick={remove}
            >
              {deleting ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
