"use client"

import { SettingsIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { apiErrorMessage, apiFetch } from "@/lib/api"

type Settings = {
  share_results: boolean
  timed: boolean
  question_seconds: number
}

export function InterviewSettings({
  interviewId,
  initial,
}: {
  interviewId: string
  initial: Settings
}) {
  const router = useRouter()
  const [settings, setSettings] = useState(initial)
  const [seconds, setSeconds] = useState(String(initial.question_seconds))
  const [saving, setSaving] = useState(false)

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
      setSeconds(String(previous.question_seconds))
      toast.error(
        apiErrorMessage(error, "Couldn't save the interview settings.")
      )
    } finally {
      setSaving(false)
    }
  }

  // The API checks the range; its message shows if the value doesn't fit.
  function saveSeconds() {
    void save({ question_seconds: Number(seconds) })
  }

  return (
    <Dialog>
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
            <span className="block text-lg font-medium">Timed interview</span>
            <span className="block text-sm text-muted-foreground">
              A question left unanswered when its time runs out is wrong.
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
            <span className="text-lg font-medium">Time per question</span>
            {/* Same look as the app's other fields (library search, candidate invite). */}
            <span className="relative w-36 rounded-lg border border-transparent transition-colors focus-within:border-ring">
              <Input
                type="number"
                inputMode="numeric"
                value={seconds}
                disabled={saving}
                aria-label="Time per question in seconds"
                className="h-14 [appearance:textfield] border-0 pr-14 pl-5 text-lg focus-visible:ring-0 md:text-lg [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                onChange={(event) => setSeconds(event.target.value)}
                onBlur={saveSeconds}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.currentTarget.blur()
                  }
                }}
              />
              <span className="pointer-events-none absolute top-1/2 right-5 -translate-y-1/2 text-lg text-muted-foreground">
                s
              </span>
            </span>
          </label>
        )}
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
