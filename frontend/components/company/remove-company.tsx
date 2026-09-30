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

export function RemoveCompany({
  companyId,
  name,
}: {
  companyId: string
  name: string
}) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [removing, setRemoving] = useState(false)

  async function remove() {
    setRemoving(true)

    try {
      await apiFetch(`/companies/companies/${companyId}`, { method: "DELETE" })
      setOpen(false)
      router.refresh()
    } catch {
      toast.error("Couldn't remove the company.")
    } finally {
      setRemoving(false)
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="size-12 text-muted-foreground hover:text-destructive"
        aria-label={`Remove ${name}`}
        onClick={() => setOpen(true)}
      >
        <Trash2Icon className="size-6" />
      </Button>
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (!removing) {
            setOpen(next)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>Remove {name}?</DialogTitle>
            <DialogDescription>
              Its interviews and invites will be deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={removing}
                />
              }
            >
              Cancel
            </DialogClose>
            <Button
              variant="destructive"
              className="h-10 px-5 text-base"
              disabled={removing}
              onClick={remove}
            >
              Remove
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
