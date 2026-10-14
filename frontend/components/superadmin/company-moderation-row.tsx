"use client"

import { PencilIcon, Trash2Icon } from "lucide-react"
import { useLocale, useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { VerifiedBadge } from "@/components/company/verified-badge"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { RenameCompanyDialog } from "@/components/superadmin/rename-company-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { formatDate } from "@/lib/format"
import type { SuperadminCompany } from "@/types/superadmin"

type Step = "suspend" | "delete" | "rename"

/** One company on the companies tab: its name and badges, who's in it and since when, and what
 * a superadmin can do about it. `onChanged` reads the list again. */
export function CompanyModerationRow({
  company,
  onChanged,
}: {
  company: SuperadminCompany
  onChanged: () => void
}) {
  const t = useTranslations("superadmin")
  const locale = useLocale()
  const [asking, setAsking] = useState<Step>()
  const [busy, setBusy] = useState(false)
  const path = `/companies/superadmin/companies/${company.id}`

  async function act(method: string, url: string, done: string) {
    setBusy(true)

    try {
      await apiFetch(url, { method })
      toast.success(done)
      setAsking(undefined)
      onChanged()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("actionFailed")))
    } finally {
      setBusy(false)
    }
  }

  return (
    <li className="flex items-center gap-4 p-6 max-sm:flex-wrap">
      <span className="min-w-0 flex-1 max-sm:basis-full">
        <span className="flex items-center gap-2 text-lg font-medium break-words">
          {company.name}
          {company.verified_domain && (
            <VerifiedBadge
              domain={company.verified_domain}
              className="size-4"
            />
          )}
          {company.suspended && (
            <Badge
              variant="destructive"
              className="h-6 px-2 text-xs font-light"
            >
              {t("suspended")}
            </Badge>
          )}
        </span>
        <span className="text-sm text-muted-foreground">
          {t("companyDetails", {
            members: company.members,
            date: formatDate(company.created_at, locale),
          })}
        </span>
      </span>
      <span className="flex items-center gap-2">
        {company.suspended ? (
          <Button
            variant="outline"
            className="h-10 px-5 text-base"
            disabled={busy}
            onClick={() => act("POST", `${path}/unsuspend`, t("unsuspended"))}
          >
            {t("unsuspend")}
          </Button>
        ) : (
          <Button
            variant="outline"
            className="h-10 px-5 text-base"
            disabled={busy}
            onClick={() => setAsking("suspend")}
          >
            {t("suspend")}
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="size-10 text-muted-foreground"
          aria-label={t("renameCompany", { name: company.name })}
          onClick={() => setAsking("rename")}
        >
          <PencilIcon className="size-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="size-10 text-muted-foreground hover:text-destructive"
          aria-label={t("deleteCompany", { name: company.name })}
          onClick={() => setAsking("delete")}
        >
          <Trash2Icon className="size-5" />
        </Button>
      </span>
      <ConfirmDialog
        open={asking === "suspend"}
        onOpenChange={(open) => !open && setAsking(undefined)}
        title={t("suspendTitle", { name: company.name })}
        text={t("suspendText")}
        confirm={t("suspend")}
        busy={busy}
        onConfirm={() => act("POST", `${path}/suspend`, t("suspendedDone"))}
      />
      <ConfirmDialog
        open={asking === "delete"}
        onOpenChange={(open) => !open && setAsking(undefined)}
        title={t("deleteCompanyTitle", { name: company.name })}
        text={t("deleteCompanyText")}
        confirm={t("deleteCompanyConfirm")}
        busy={busy}
        onConfirm={() => act("DELETE", path, t("companyDeleted"))}
      />
      <RenameCompanyDialog
        company={company}
        open={asking === "rename"}
        onOpenChange={(open) => !open && setAsking(undefined)}
        onRenamed={onChanged}
      />
    </li>
  )
}
