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
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { apiErrorMessage, apiFetch } from "@/lib/api"

type Settings = {
  share_results: boolean
  timed: boolean
  time_limit_minutes: number
}

export function InterviewSettings({
  interviewId,
  initial,
  deletable,
  leaveTo,
}: {
  interviewId: string
  initial: Settings
  deletable: boolean
  leaveTo: string
}) {
  const router = useRouter()
  const [settings, setSettings] = useState(initial)
  const [minutes, setMinutes] = useState(String(initial.time_limit_minutes))
  const [saving, setSaving] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)

  // Every save sends all settings, so one change never resets another.
  async function save(change: Partial<Settings>) {
    const next = { ...settings, ...change }

    if (saving || JSON.stringify(next) === JSON.stringify(settings)) {
      return
    }

    const previous = settings
    setSettings(next)
    setSaving(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}/settings`, {
        method: "PATCH",
        body: JSON.stringify(next),
      })
      router.refresh()
    } catch (error) {
      setSettings(previous)
      setMinutes(String(previous.time_limit_minutes))
      toast.error(
        apiErrorMessage(error, "Couldn't save the interview settings.")
      )
    } finally {
      setSaving(false)
    }
  }

  // The API checks the range; its message shows if the value doesn't fit.
  function saveMinutes() {
    void save({ time_limit_minutes: Number(minutes) })
  }

  async function remove() {
    setDeleting(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}`, {
        method: "DELETE",
      })
      router.push(leaveTo)
      router.refresh()
    } catch (error) {
      toast.error(
        apiErrorMessage(
          error,
          "Couldn't delete the interview. Please try again."
        )
      )
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
              <DialogTitle className="no-dot">
                Delete this interview?
              </DialogTitle>
              <DialogDescription>
                Candidates lose access, and their results are deleted. This
                can&apos;t be undone.
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
              <span className="text-lg font-medium">
                Show scores to the candidate
              </span>
              <Switch
                checked={settings.share_results}
                disabled={saving}
                aria-label="Show scores to the candidate"
                onCheckedChange={(checked) => save({ share_results: checked })}
              />
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="space-y-1">
                <span className="block text-lg font-medium">
                  Timed interview
                </span>
                <span className="block text-sm text-muted-foreground">
                  The interview finishes by itself when time runs out.
                </span>
              </span>
              <Switch
                checked={settings.timed}
                disabled={saving}
                aria-label="Timed interview"
                onCheckedChange={(checked) => save({ timed: checked })}
              />
            </div>
            {settings.timed && (
              <label className="flex items-center justify-between gap-4">
                <span className="text-lg font-medium">Time limit</span>
                <span className="flex items-center gap-2 text-muted-foreground">
                  <Input
                    type="number"
                    inputMode="numeric"
                    value={minutes}
                    disabled={saving}
                    aria-label="Time limit in minutes"
                    className="h-10 w-24 text-right text-base"
                    onChange={(event) => setMinutes(event.target.value)}
                    onBlur={saveMinutes}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.currentTarget.blur()
                      }
                    }}
                  />
                  minutes
                </span>
              </label>
            )}
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
