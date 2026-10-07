"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { CandidateFlow } from "@/components/company/ats-candidate-flow"
import { ConnectWorkable } from "@/components/company/ats-connect"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { AtsConnection } from "@/types/company"

/** Workable's row on the ATS tab: its logo, name and whether it's connected, laid out like the
 * companies list; the row opens Workable's page (its linked jobs), its buttons sit on top. */
export function AtsConnectionRow({
  companyId,
  connection,
  canEdit,
}: {
  companyId: string
  connection: AtsConnection | null
  canEdit: boolean
}) {
  return (
    <li className="relative flex items-center justify-between gap-6 py-6 pe-4 transition-colors hover:bg-muted/50 sm:pe-6">
      <Link
        href={`/companies/${companyId}/integrations/workable`}
        className="flex min-w-0 items-center gap-4 after:absolute after:inset-0"
      >
        {/* Workable's own icon (public/ats), as the companies list shows a logo: a square the
            row's full height (24px padding twice, plus two lines), from its left border. */}
        <span className="-my-6 me-2 flex size-[6.25rem] shrink-0 items-center justify-center overflow-hidden bg-muted">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/ats/workable.svg"
            alt=""
            className="size-full object-contain"
          />
        </span>
        <span className="min-w-0 space-y-1">
          <span className="flex items-center gap-3 text-lg font-medium">
            Workable
            <WorkableStatus connection={connection} />
          </span>
          {connection && (
            <span className="block text-base text-muted-foreground">
              {connection.account}
            </span>
          )}
        </span>
      </Link>
      <span className="relative z-10">
        <WorkableActions
          companyId={companyId}
          connection={connection}
          canEdit={canEdit}
        />
      </span>
    </li>
  )
}

/** "connected" beside Workable's name once it is, like an interview's status tag; nothing
 * otherwise (Connect or Reconnect says the rest). */
export function WorkableStatus({
  connection,
}: {
  connection: AtsConnection | null
}) {
  const t = useTranslations("ats")

  if (connection?.status !== "connected") {
    return null
  }

  return (
    <Badge className="h-7 shrink-0 px-3 text-sm font-light">
      {t("statusConnected")}
    </Badge>
  )
}

/** Workable's buttons, on its row and its page: how candidates flow, and for owners and admins
 * Connect (or Reconnect when its key stopped working) and Disconnect. */
export function WorkableActions({
  companyId,
  connection,
  canEdit,
}: {
  companyId: string
  connection: AtsConnection | null
  canEdit: boolean
}) {
  const t = useTranslations("ats")
  const router = useRouter()
  const [confirming, setConfirming] = useState(false)
  const [busy, setBusy] = useState(false)
  const broken = connection?.status === "broken"

  async function disconnect() {
    setBusy(true)

    try {
      await apiFetch(`/companies/ats/workable?company_id=${companyId}`, {
        method: "DELETE",
      })
      setConfirming(false)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("disconnectFailed")))
    } finally {
      setBusy(false)
    }
  }

  return (
    <span className="flex shrink-0 items-center gap-3">
      <CandidateFlow />
      {canEdit && connection && (
        <Button
          variant="outline"
          className="h-10 px-5 text-base"
          onClick={() => setConfirming(true)}
        >
          {t("disconnect")}
        </Button>
      )}
      {canEdit && (connection === null || broken) && (
        <ConnectWorkable companyId={companyId} again={broken} />
      )}
      <ConfirmDialog
        open={confirming}
        onOpenChange={setConfirming}
        title={t("disconnectTitle")}
        text={t("disconnectText")}
        confirm={t("disconnect")}
        busy={busy}
        onConfirm={disconnect}
      />
    </span>
  )
}
