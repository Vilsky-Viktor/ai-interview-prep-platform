"use client"

import { UserRoundSearchIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { ApiError, apiErrorMessage } from "@/lib/api"
import { saveTalentLink, startPracticeRound } from "@/lib/practice"

/** Asked once, before a talent's first practice round: share a LinkedIn link to be
 * suggested to companies, or start without. Either answer starts the round; it can be changed
 * later in settings. */
export function PracticeConsent({ templateId }: { templateId: string }) {
  const t = useTranslations("suggest")
  const practice = useTranslations("practice")
  const router = useRouter()
  const [url, setUrl] = useState("")
  const [busy, setBusy] = useState(false)

  async function answer(link: string | null) {
    setBusy(true)

    try {
      await saveTalentLink(link)
      router.push(await startPracticeRound(templateId))
    } catch (error) {
      const invalid = error instanceof ApiError && error.status === 422
      // No practice questions yet: the API says so.
      const refused = error instanceof ApiError && error.status === 409
      toast.error(
        invalid
          ? t("invalid")
          : refused
            ? error.message
            : apiErrorMessage(error, practice("startFailed"))
      )
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl space-y-8 text-center">
      <div className="space-y-4">
        <UserRoundSearchIcon
          aria-hidden
          className="mx-auto size-16 text-primary"
        />
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-base text-muted-foreground">{t("consent")}</p>
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          answer(url)
        }}
        className="flex"
      >
        <InputAction
          type="url"
          required
          maxLength={300}
          placeholder="https://www.linkedin.com/in/…"
          aria-label={t("link")}
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          action={t("shareAndStart")}
          disabled={busy || !url}
        />
      </form>
      {/* Plain text, quieter than agreeing. */}
      <button
        type="button"
        className="cursor-pointer text-sm text-muted-foreground transition-colors hover:text-foreground disabled:cursor-default disabled:opacity-50"
        disabled={busy}
        onClick={() => answer(null)}
      >
        {t("startWithout")}
      </button>
    </div>
  )
}
