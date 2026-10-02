"use client"

import { XIcon } from "lucide-react"
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

export function CancelGeneration({
  path,
  leaveTo,
  iconOnly = false,
}: {
  path: string
  leaveTo: string
  // An X button for compact rows; a text button otherwise.
  iconOnly?: boolean
}) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  async function cancel() {
    setCancelling(true)

    try {
      await apiFetch(`${path}/cancel`, { method: "POST" })
      setOpen(false)
      // From the generation page this leaves it; on a list it reloads the list.
      router.push(leaveTo)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, "Couldn't cancel the generation. Please try again."))
      setCancelling(false)
    }
  }

  return (
    <>
      {/* type="button": on the topic review it sits inside the review form. */}
      {iconOnly ? (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label="Cancel generation"
          className="size-12 text-muted-foreground hover:text-destructive"
          onClick={() => setOpen(true)}
        >
          <XIcon className="size-6" />
        </Button>
      ) : (
        <Button
          type="button"
          variant="ghost"
          className="h-12 px-6 text-base text-muted-foreground hover:text-destructive"
          onClick={() => setOpen(true)}
        >
          Cancel generation
        </Button>
      )}
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (!cancelling) {
            setOpen(next)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="no-dot">Cancel this generation?</DialogTitle>
            <DialogDescription>
              It stops now, and nothing generated so far is kept.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={cancelling}
                />
              }
            >
              Keep
            </DialogClose>
            <Button
              type="button"
              variant="destructive"
              className="h-10 px-5 text-base"
              disabled={cancelling}
              onClick={cancel}
            >
              {cancelling ? "Cancelling…" : "Cancel"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
