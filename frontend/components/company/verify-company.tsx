"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ApiError, apiFetch } from "@/lib/api"
import type { Verification } from "@/types/company"

/** "Verify" beside an unverified company's name: its website, verified once an owner or admin
 * signs in with a work email on that domain (right away when it's theirs). */
export function VerifyCompany({
  companyId,
  websiteDomain,
}: {
  companyId: string
  websiteDomain: string | null
}) {
  const t = useTranslations("verify")
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [website, setWebsite] = useState(websiteDomain ?? "")
  const [saving, setSaving] = useState(false)

  async function save(event: React.FormEvent) {
    event.preventDefault()
    setSaving(true)

    try {
      const result = await apiFetch<Verification>(
        `/companies/companies/${companyId}/website`,
        { method: "PUT", body: JSON.stringify({ website }) }
      )
      toast.success(
        result.verified_domain
          ? t("done", { domain: result.verified_domain })
          : t("pending", { domain: result.website_domain ?? website })
      )
      setOpen(false)
      router.refresh()
    } catch (error) {
      // Not a website, or a free mail service: the API says which.
      const invalid = error instanceof ApiError && error.status === 422
      toast.error(invalid ? error.message : t("failed"))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !saving && setOpen(next)}>
      <DialogTrigger
        render={
          <button
            type="button"
            className="shrink-0 cursor-pointer text-sm text-primary transition-opacity hover:opacity-70"
          />
        }
      >
        {t("verify")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("title")}</DialogTitle>
          <DialogDescription>{t("text")}</DialogDescription>
        </DialogHeader>
        <form onSubmit={save} className="flex">
          <InputAction
            required
            maxLength={253}
            placeholder="acme.com"
            aria-label={t("website")}
            value={website}
            onChange={(event) => setWebsite(event.target.value)}
            action={t("save")}
            disabled={saving || !website.trim()}
          />
        </form>
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
