"use client"

import { SettingsIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { apiErrorMessage, apiFetch } from "@/lib/api"

export function InterviewSettings({
  interviewId,
  shareResults,
  deletable,
  leaveTo,
}: {
  interviewId: string
  shareResults: boolean
  deletable: boolean
  leaveTo: string
}) {
  const router = useRouter()
  const [shared, setShared] = useState(shareResults)
  const [saving, setSaving] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function save(next: boolean) {
    if (saving || next === shared) {
      return
    }

    setShared(next)
    setSaving(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}/settings`, {
        method: "PATCH",
        body: JSON.stringify({ share_results: next }),
      })
      router.refresh()
    } catch (error) {
      setShared(!next)
      toast.error(apiErrorMessage(error, "Couldn't save the interview settings."))
    } finally {
      setSaving(false)
    }
  }

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}`, { method: "DELETE" })
      router.push(leaveTo)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, "Couldn't delete the interview. Please try again."))
      setDeleting(false)
    }
  }

  return (
    <Dialog
      onOpenChange={(open) => {
        if (!open) {
          setConfirming(false)
        }
      }}
    >
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            size="icon"
            className="size-12 shrink-0 text-muted-foreground"
            aria-label="Settings"
          />
        }
      >
        <SettingsIcon className="size-6" />
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        className="sm:max-w-lg"
        aria-label="Settings"
      >
        {confirming ? (
          <>
            <DialogHeader>
              <DialogTitle className="no-dot">Delete this interview?</DialogTitle>
              <DialogDescription>
                Candidates lose access, and their results are deleted. This can&apos;t
                be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                className="h-10 px-5 text-base"
                disabled={deleting}
                onClick={() => setConfirming(false)}
              >
                Keep
              </Button>
              <Button
                variant="destructive"
                className="h-10 px-5 text-base"
                disabled={deleting}
                onClick={remove}
              >
                {deleting ? "Deleting…" : "Delete"}
              </Button>
            </DialogFooter>
          </>
        ) : (
          <>
            <div className="flex items-center justify-between gap-4">
              <span className="text-lg font-medium">Show scores to the candidate</span>
              <Switch
                checked={shared}
                disabled={saving}
                aria-label="Show scores to the candidate"
                onCheckedChange={save}
              />
            </div>
            {deletable && (
              <div className="flex items-center justify-between gap-4">
                <span className="text-lg font-medium">Delete interview</span>
                <Button
                  variant="destructive"
                  className="h-10 px-5 text-base"
                  onClick={() => setConfirming(true)}
                >
                  Delete
                </Button>
              </div>
            )}
            <DialogFooter showCloseButton />
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
