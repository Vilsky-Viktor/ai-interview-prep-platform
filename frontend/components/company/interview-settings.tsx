"use client"

import { SettingsIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
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
import { apiErrorMessage, apiFetch } from "@/lib/api"

/** The interview's one setting: the time each question has. Every interview is timed, and
candidates never see their scores. */
export function InterviewSettings({
  interviewId,
  questionSeconds,
}: {
  interviewId: string
  questionSeconds: number
}) {
  const t = useTranslations("interviews")
  const router = useRouter()
  const [saved, setSaved] = useState(questionSeconds)
  const [seconds, setSeconds] = useState(String(questionSeconds))
  const [saving, setSaving] = useState(false)

  // The API checks the range; its message shows if the value doesn't fit.
  async function save() {
    const next = Number(seconds)

    if (saving || next === saved) {
      return
    }

    setSaving(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}/settings`, {
        method: "PATCH",
        body: JSON.stringify({ question_seconds: next }),
      })
      setSaved(next)
      router.refresh()
    } catch (error) {
      setSeconds(String(saved))
      toast.error(apiErrorMessage(error, t("settingsFailed")))
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
            aria-label={t("settings")}
          />
        }
      >
        <SettingsIcon className="size-6" />
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        className="sm:max-w-lg"
        aria-label={t("settings")}
      >
        <label className="flex items-center justify-between gap-4">
          <span className="text-lg font-medium">{t("timePerQuestion")}</span>
          {/* Same look as the app's other fields (library search, candidate invite). */}
          <span className="relative w-36 rounded-full border border-transparent transition-colors focus-within:border-ring">
            <Input
              type="number"
              inputMode="numeric"
              value={seconds}
              disabled={saving}
              aria-label={t("secondsLabel")}
              className="h-14 [appearance:textfield] border-0 ps-5 pe-14 text-lg focus-visible:ring-0 md:text-lg [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
              onChange={(event) => setSeconds(event.target.value)}
              onBlur={save}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.currentTarget.blur()
                }
              }}
            />
            <span className="pointer-events-none absolute end-5 top-1/2 -translate-y-1/2 text-lg text-muted-foreground">
              {t("secondsUnit")}
            </span>
          </span>
        </label>
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
