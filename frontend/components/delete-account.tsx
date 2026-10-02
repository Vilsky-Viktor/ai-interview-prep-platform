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
import { signOut } from "@/lib/auth"

export function DeleteAccount({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const router = useRouter()
  const [deleting, setDeleting] = useState(false)

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch("/library/me", { method: "DELETE" })
      await signOut()
      onOpenChange(false)
      toast.success("Your account was deleted.")
      router.push("/")
    } catch (error) {
      toast.error(
        apiErrorMessage(
          error,
          "Couldn't delete your account. Please try again."
        )
      )
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
          <DialogTitle className="no-dot">Delete your account?</DialogTitle>
          <DialogDescription className="space-y-2 text-base">
            <span className="block">
              Everything goes: your preparations (also for people who joined
              them), progress, certificates, chats and interview results.
            </span>
            <span className="block">
              A company you alone own is deleted with its interviews. This
              can&apos;t be undone.
            </span>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose
            render={
              <Button variant="outline" className="h-12 px-6 text-base" />
            }
            disabled={deleting}
          >
            Keep
          </DialogClose>
          <Button
            variant="destructive"
            className="h-12 px-6 text-base"
            disabled={deleting}
            onClick={remove}
          >
            {deleting ? "Deleting…" : "Delete account"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
