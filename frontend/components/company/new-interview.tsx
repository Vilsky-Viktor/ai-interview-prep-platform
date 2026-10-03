"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { Interview } from "@/types/company"

export function NewInterview({ companyId }: { companyId: string }) {
  const t = useTranslations("interviews")
  const router = useRouter()
  const [text, setText] = useState("")
  const [shareResults, setShareResults] = useState(false)
  const [saving, setSaving] = useState(false)

  async function create(event: React.FormEvent) {
    event.preventDefault()
    setSaving(true)

    try {
      const interview = await apiFetch<Interview>(
        `/companies/interviews?company_id=${companyId}`,
        {
          method: "POST",
          body: JSON.stringify({
            text,
            share_results: shareResults,
          }),
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

  return (
    <form
      onSubmit={create}
      className="rounded-2xl border border-transparent bg-card p-3 transition-colors focus-within:border-ring"
    >
      <Textarea
        required
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder={t("pasteJob")}
        aria-label={t("jobDescription")}
        className="max-h-72 min-h-40 resize-none border-0 bg-transparent p-2 text-base shadow-none focus-visible:ring-0 md:text-base dark:bg-transparent"
      />
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2 pl-2">
        <div className="flex flex-wrap items-center gap-4 sm:ml-auto">
          <label className="flex items-center gap-3 text-sm">
            {t("showScores")}
            <Switch checked={shareResults} onCheckedChange={setShareResults} />
          </label>
          <Button
            type="submit"
            className="h-12 px-6 text-base"
            disabled={saving || !text.trim()}
          >
            {t("generate")}
          </Button>
        </div>
      </div>
    </form>
  )
}
