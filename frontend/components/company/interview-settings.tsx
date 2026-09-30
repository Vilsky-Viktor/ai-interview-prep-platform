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
import { Switch } from "@/components/ui/switch"
import { MODE_LABELS, ROUND_MODES } from "@/constants/rounds"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { RoundMode } from "@/types/round"

export function InterviewSettings({
  interviewId,
  mode,
  shareResults,
}: {
  interviewId: string
  mode: RoundMode
  shareResults: boolean
}) {
  const router = useRouter()
  const [currentMode, setCurrentMode] = useState(mode)
  const [shared, setShared] = useState(shareResults)
  const [saving, setSaving] = useState(false)

  async function save(nextMode: RoundMode, nextShared: boolean) {
    if (saving || (nextMode === currentMode && nextShared === shared)) {
      return
    }

    const previousMode = currentMode
    const previousShared = shared

    setCurrentMode(nextMode)
    setShared(nextShared)
    setSaving(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}/settings`, {
        method: "PATCH",
        body: JSON.stringify({ mode: nextMode, share_results: nextShared }),
      })
      router.refresh()
    } catch (error) {
      setCurrentMode(previousMode)
      setShared(previousShared)
      toast.error(apiErrorMessage(error, "Couldn't save the interview settings."))
    } finally {
      setSaving(false)
    }
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
        <div className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <span className="text-lg font-medium">Mode</span>
            <div className="inline-flex shrink-0 rounded-lg border p-1">
              {ROUND_MODES.map((value) => (
                <Button
                  key={value}
                  type="button"
                  variant={currentMode === value ? "secondary" : "ghost"}
                  className="h-10 px-5 text-base"
                  disabled={saving}
                  onClick={() => save(value, shared)}
                >
                  {MODE_LABELS[value]}
                </Button>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-lg font-medium">Show scores to the candidate</span>
            <Switch
              checked={shared}
              disabled={saving}
              aria-label="Show scores to the candidate"
              onCheckedChange={(checked) => save(currentMode, checked)}
            />
          </div>
        </div>
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
