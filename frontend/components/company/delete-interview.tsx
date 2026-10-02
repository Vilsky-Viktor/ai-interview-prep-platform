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
      toast.error(
        apiErrorMessage(
          error,
          "Couldn't delete the interview. Please try again."
        )
      )
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
        aria-label={`Delete ${title}`}
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
            <DialogTitle className="no-dot">Delete this interview?</DialogTitle>
            <DialogDescription>
              Candidates lose access, and their results are deleted. This
              can&apos;t be undone.
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
