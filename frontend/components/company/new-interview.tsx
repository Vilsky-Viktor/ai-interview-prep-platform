"use client"

import { ArrowUpIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useLocale, useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { GenerateIn } from "@/components/generate-in"
import { Button } from "@/components/ui/button"
import type { Locale } from "@/constants/i18n"
import { Textarea } from "@/components/ui/textarea"
import { MAX_GOAL_LENGTH } from "@/constants/limits"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { isSubmitShortcut } from "@/lib/keys"
import type { Interview } from "@/types/company"

export function NewInterview({ companyId }: { companyId: string }) {
  const t = useTranslations("interviews")
  const common = useTranslations("common")
  const router = useRouter()
  const [text, setText] = useState("")
  // Starts on the interface's language; any supported one can be chosen.
  const [generateIn, setGenerateIn] = useState(useLocale() as Locale)
  const [saving, setSaving] = useState(false)

  async function create(event: React.FormEvent) {
    event.preventDefault()
    setSaving(true)

    try {
      const interview = await apiFetch<Interview>(
        `/companies/interviews?company_id=${companyId}`,
        {
          method: "POST",
          body: JSON.stringify({ text, generate_in: generateIn }),
        }
      )
      router.push(
        `/generate/${interview.generation_id}?next=/company/${companyId}/interviews/${interview.id}`
      )
    } catch (error) {
      toast.error(apiErrorMessage(error, t("startFailed")))
      setSaving(false)
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (isSubmitShortcut(event)) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <form
      onSubmit={create}
      className="rounded-3xl border border-transparent bg-muted p-3 transition-colors focus-within:border-ring dark:bg-card"
    >
      <Textarea
        maxLength={MAX_GOAL_LENGTH}
        required
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={t("pasteJob")}
        aria-label={t("jobDescription")}
        className="max-h-72 min-h-40 resize-none border-0 bg-transparent p-2 text-base shadow-none focus-visible:ring-0 md:text-base dark:bg-transparent"
      />
      <div className="flex flex-wrap items-center justify-between gap-4 ps-2 pt-2">
        <p className="text-xs text-muted-foreground">{common("submitHint")}</p>
        <div className="ms-auto flex items-center gap-3">
          <GenerateIn value={generateIn} onChange={setGenerateIn} />
          <Button
            type="submit"
            size="icon-lg"
            className="rounded-full"
            disabled={saving || !text.trim()}
            aria-label={t("generate")}
          >
            <ArrowUpIcon />
          </Button>
        </div>
      </div>
    </form>
  )
}
