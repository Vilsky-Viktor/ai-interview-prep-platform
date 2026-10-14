"use client"

import { ShieldCheckIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Switch } from "@/components/ui/switch"
import { apiErrorMessage, apiFetch } from "@/lib/api"

/** Whether members may use the company's data from the AI apps they connected, as the
 * shareable link's card: owners and admins turn it on or off; a viewer only sees it. */
export function AiAppsSwitch({
  companyId,
  allowed,
  canEdit,
}: {
  companyId: string
  allowed: boolean
  canEdit: boolean
}) {
  const t = useTranslations("aiApps")
  const [on, setOn] = useState(allowed)
  const [saving, setSaving] = useState(false)

  async function toggle(next: boolean) {
    setSaving(true)

    try {
      await apiFetch(`/companies/companies/${companyId}/ai-apps`, {
        method: "PUT",
        body: JSON.stringify({ allowed: next }),
      })
      setOn(next)
    } catch (error) {
      toast.error(apiErrorMessage(error, t("allowFailed")))
    } finally {
      setSaving(false)
    }
  }

  return (
    <label className="flex cursor-pointer items-center gap-4 rounded-2xl border p-5 text-base">
      <ShieldCheckIcon aria-hidden className="size-7 shrink-0 text-primary" />
      <span className="min-w-0 flex-1 space-y-1">
        <span className="block font-medium lowercase">{t("allowTitle")}</span>
        <span className="block text-sm text-muted-foreground">
          {t("allowText")}
        </span>
      </span>
      <Switch
        checked={on}
        disabled={saving || !canEdit}
        onCheckedChange={toggle}
      />
    </label>
  )
}
