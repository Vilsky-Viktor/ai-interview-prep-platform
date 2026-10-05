"use client"

import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { SettingsSection } from "@/components/settings/settings-section"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ApiError, apiFetch } from "@/lib/api"
import { saveTalentLink, TALENT_LINK_PATH } from "@/lib/practice"
import type { TalentLink } from "@/types/round"

/** In settings, its own section: the link a talent shares to be suggested to companies, to change or withdraw at
 * any time (they're asked once, before their first practice round). */
export function TalentLinkSetting() {
  const t = useTranslations("suggest")
  const [link, setLink] = useState<TalentLink | null>(null)
  const [url, setUrl] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiFetch<TalentLink>(TALENT_LINK_PATH)
      .then(setLink)
      .catch(() => setLink(null))
  }, [])

  async function save(next: string | null) {
    setSaving(true)

    try {
      setLink(await saveTalentLink(next))
      setUrl("")
      toast.success(next ? t("saved") : t("withdrawn"))
    } catch (error) {
      const invalid = error instanceof ApiError && error.status === 422
      toast.error(invalid ? t("invalid") : t("failed"))
    } finally {
      setSaving(false)
    }
  }

  if (!link) {
    return null
  }

  // The withdraw button on the right of the whole section; the link field fills it otherwise.
  return (
    <SettingsSection
      title={t("title")}
      description={t("consent")}
      action={
        link.url && (
          <Button
            variant="outline"
            className="h-10 shrink-0 px-5 text-base"
            disabled={saving}
            onClick={() => save(null)}
          >
            {t("withdraw")}
          </Button>
        )
      }
    >
      {link.url ? (
        // The shared link in a plain read-only field, like the site's other inputs.
        <Input
          readOnly
          value={link.url}
          aria-label={t("link")}
          className="h-16 border-0 px-6 text-center text-lg text-muted-foreground focus-visible:ring-0 md:text-lg"
        />
      ) : (
        <form
          onSubmit={(event) => {
            event.preventDefault()
            save(url)
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
            action={t("share")}
            disabled={saving || !url}
          />
        </form>
      )}
    </SettingsSection>
  )
}
