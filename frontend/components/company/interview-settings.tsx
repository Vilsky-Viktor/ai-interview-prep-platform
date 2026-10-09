"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { InterviewSettingsData } from "@/types/company"
import { LIST_BOX } from "@/constants/lists"

/** The interview's settings tab: the time each question has, the pass mark, and whether the
company hired, one row each in a list like the topics'. Every interview is timed, and
candidates never see their scores. */
export function InterviewSettings({
  interviewId,
  questionSeconds,
  passMark,
  hired,
}: {
  interviewId: string
  questionSeconds: number
  passMark: number
  hired: boolean
}) {
  const t = useTranslations("interviews")
  const router = useRouter()
  const [saved, setSaved] = useState<InterviewSettingsData>({
    question_seconds: questionSeconds,
    hired,
    pass_mark: passMark,
  })
  const [seconds, setSeconds] = useState(String(questionSeconds))
  const [mark, setMark] = useState(String(passMark))
  const [saving, setSaving] = useState(false)

  // Every setting goes together, so saving one never resets the others. The API checks the
  // ranges; its message shows if a value doesn't fit, and the field goes back.
  async function save(change: Partial<InterviewSettingsData>) {
    const next = { ...saved, ...change }

    if (saving || JSON.stringify(next) === JSON.stringify(saved)) {
      return
    }

    setSaving(true)

    try {
      await apiFetch(`/companies/interviews/${interviewId}/settings`, {
        method: "PATCH",
        body: JSON.stringify(next),
      })
      setSaved(next)
      router.refresh()
    } catch (error) {
      setSeconds(String(saved.question_seconds))
      setMark(String(saved.pass_mark))
      toast.error(apiErrorMessage(error, t("settingsFailed")))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className={LIST_BOX}>
      <NumberSetting
        label={t("timePerQuestion")}
        fieldLabel={t("secondsLabel")}
        unit={t("secondsUnit")}
        value={seconds}
        disabled={saving}
        onChange={setSeconds}
        onSave={() => save({ question_seconds: Number(seconds) })}
      />
      <NumberSetting
        label={t("passMark")}
        fieldLabel={t("passMarkLabel")}
        unit="%"
        value={mark}
        disabled={saving}
        onChange={setMark}
        onSave={() => save({ pass_mark: Number(mark) })}
      />
      <label className="flex cursor-pointer items-center justify-between gap-4 p-4 sm:p-6">
        <span className="text-lg font-light">{t("markHired")}</span>
        {/* Centred under the fields above. */}
        <span className="flex w-36 justify-center">
          <Checkbox
            className="size-7 shrink-0 [&_[data-slot=checkbox-indicator]>svg]:size-5"
            checked={saved.hired}
            disabled={saving}
            onCheckedChange={(checked) => save({ hired: checked })}
          />
        </span>
      </label>
    </div>
  )
}

/** A number setting: its name, and a field with its unit that saves when left. */
function NumberSetting({
  label,
  fieldLabel,
  unit,
  value,
  disabled,
  onChange,
  onSave,
}: {
  label: string
  fieldLabel: string
  unit: string
  value: string
  disabled: boolean
  onChange: (value: string) => void
  onSave: () => void
}) {
  return (
    <label className="flex items-center justify-between gap-4 p-4 sm:p-6">
      <span className="text-lg font-light">{label}</span>
      {/* Same look as the app's other fields (library search, candidate invite). */}
      <span className="relative w-36 rounded-full border border-transparent transition-colors focus-within:border-ring">
        <Input
          type="number"
          inputMode="numeric"
          value={value}
          disabled={disabled}
          aria-label={fieldLabel}
          className="h-14 [appearance:textfield] border-0 ps-5 pe-14 text-lg focus-visible:ring-0 md:text-lg [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
          onChange={(event) => onChange(event.target.value)}
          onBlur={onSave}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.currentTarget.blur()
            }
          }}
        />
        <span className="pointer-events-none absolute end-5 top-1/2 -translate-y-1/2 text-lg text-muted-foreground">
          {unit}
        </span>
      </span>
    </label>
  )
}
