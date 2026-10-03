"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Switch } from "@/components/ui/switch"
import { apiFetch } from "@/lib/api"
import type { PreparationSummary } from "@/types/preparation"

export function VisibilityToggle({
  preparation,
}: {
  preparation: PreparationSummary
}) {
  const t = useTranslations("preparations")
  const router = useRouter()
  const [saving, setSaving] = useState(false)

  async function change(isPublic: boolean) {
    setSaving(true)

    try {
      await apiFetch(`/library/preparations/${preparation.id}`, {
        method: "PATCH",
        body: JSON.stringify({ visibility: isPublic ? "public" : "private" }),
      })
      toast.success(isPublic ? t("nowPublic") : t("nowPrivate"))
      router.refresh()
    } catch {
      toast.error(t("visibilityFailed"))
    } finally {
      setSaving(false)
    }
  }

  return (
    <label className="flex items-center gap-2 text-sm">
      <Switch
        checked={preparation.visibility === "public"}
        disabled={saving}
        onCheckedChange={change}
      />
      {t("public")}
    </label>
  )
}
