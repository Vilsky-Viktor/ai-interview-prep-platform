"use client"

import { ArrowUpIcon } from "lucide-react"
import { useLocale, useTranslations } from "next-intl"
import { useState } from "react"

import { GenerateIn } from "@/components/generate-in"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import type { Locale } from "@/constants/i18n"
import { MAX_GOAL_LENGTH } from "@/constants/limits"
import { isSubmitShortcut } from "@/lib/keys"

/** The box a test starts from, as on the home page: the pasted description, the language to
 * generate in, and the send arrow. `onSubmit` returns once the page moves on, or after an error,
 * which re-enables the box. */
export function DescriptionBox({
  placeholder,
  label,
  submitLabel,
  onSubmit,
}: {
  placeholder: string
  label: string
  submitLabel: string
  onSubmit: (text: string, generateIn: Locale) => Promise<void>
}) {
  const common = useTranslations("common")
  const [text, setText] = useState("")
  // Starts on the interface's language; any supported one can be chosen.
  const [generateIn, setGenerateIn] = useState(useLocale() as Locale)
  const [busy, setBusy] = useState(false)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setBusy(true)
    await onSubmit(text.trim(), generateIn)
    setBusy(false)
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (isSubmitShortcut(event)) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <form
      onSubmit={submit}
      className="w-full rounded-3xl border border-transparent bg-muted p-3 transition-colors focus-within:border-ring dark:bg-card"
    >
      <Textarea
        maxLength={MAX_GOAL_LENGTH}
        required
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        aria-label={label}
        className="max-h-72 min-h-40 resize-none border-0 bg-transparent p-2 text-base shadow-none focus-visible:ring-0 md:text-base dark:bg-transparent"
        autoFocus
      />
      <div className="flex flex-wrap items-center justify-between gap-4 ps-2 pt-2">
        <p className="text-xs text-muted-foreground">{common("submitHint")}</p>
        <div className="ms-auto flex items-center gap-3">
          <GenerateIn value={generateIn} onChange={setGenerateIn} />
          <Button
            type="submit"
            size="icon-lg"
            className="rounded-full"
            disabled={busy || !text.trim()}
            aria-label={submitLabel}
          >
            <ArrowUpIcon />
          </Button>
        </div>
      </div>
    </form>
  )
}
