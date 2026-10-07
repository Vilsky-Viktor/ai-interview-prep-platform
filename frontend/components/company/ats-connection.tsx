"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { CandidateFlow } from "@/components/company/ats-candidate-flow"
import { ConnectAts } from "@/components/company/ats-connect"
import { GreenhouseWebhook } from "@/components/company/ats-webhook"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { AtsProvider } from "@/constants/ats"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { AtsConnection } from "@/types/company"

/** An ATS's row on the integrations tab: its logo, name and whether it's connected, laid out
 * like the companies list; the row opens the ATS's page (its linked jobs), its buttons sit on
 * top. */
export function AtsConnectionRow({
  companyId,
  provider,
  connection,
  canEdit,
}: {
  companyId: string
  provider: AtsProvider
  connection: AtsConnection | null
  canEdit: boolean
}) {
  return (
    <li className="relative flex items-center justify-between gap-6 py-6 pe-4 transition-colors hover:bg-muted/50 sm:pe-6">
      <Link
        href={`/companies/${companyId}/integrations/${provider.id}`}
        className="flex min-w-0 items-center gap-4 after:absolute after:inset-0"
      >
        {/* The ATS's own icon (public/ats), as the companies list shows a logo: a square the
            row's full height (24px padding twice, plus two lines), from its left border. */}
        <span className="-my-6 me-2 flex size-[6.25rem] shrink-0 items-center justify-center overflow-hidden bg-muted">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={provider.logo}
            alt=""
            className="size-full object-contain"
          />
        </span>
        <span className="min-w-0 space-y-1">
          <span className="flex items-center gap-3 text-lg font-medium">
            {provider.name}
            <AtsStatus connection={connection} />
          </span>
          {connection && (
            <span className="block text-base text-muted-foreground">
              {connection.account}
            </span>
          )}
        </span>
      </Link>
      <span className="relative z-10">
        <AtsActions
          companyId={companyId}
          provider={provider}
          connection={connection}
          canEdit={canEdit}
        />
      </span>
    </li>
  )
}

/** "connected" beside the ATS's name once it is, like an interview's status tag; nothing
 * otherwise (Connect or Reconnect says the rest). */
export function AtsStatus({
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

/** An ATS's buttons, on its row and its page: how candidates flow, and for owners and admins
 * Connect (or Reconnect when its key stopped working) and Disconnect. Greenhouse's web hook is
 * set up by hand: its steps are in the info dialog, which opens once it's connected. */
export function AtsActions({
  companyId,
  provider,
  connection,
  canEdit,
}: {
  companyId: string
  provider: AtsProvider
  connection: AtsConnection | null
  canEdit: boolean
}) {
  const t = useTranslations("ats")
  const router = useRouter()
  const [confirming, setConfirming] = useState(false)
  const [busy, setBusy] = useState(false)
  const [info, setInfo] = useState(false)
  const broken = connection?.status === "broken"
  const greenhouse = provider.id === "greenhouse"

  async function disconnect() {
    setBusy(true)

    try {
      await apiFetch(`/companies/ats/${provider.id}?company_id=${companyId}`, {
        method: "DELETE",
      })
      setConfirming(false)
      router.refresh()
    } catch (error) {
      toast.error(
        apiErrorMessage(error, t("disconnectFailed", { ats: provider.name }))
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <span className="flex shrink-0 items-center gap-3">
      <CandidateFlow provider={provider} open={info} onOpenChange={setInfo}>
        {canEdit && greenhouse && connection?.status === "connected" && (
          <GreenhouseWebhook companyId={companyId} />
        )}
      </CandidateFlow>
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
        <ConnectAts
          companyId={companyId}
          provider={provider}
          again={broken}
          onConnected={() => greenhouse && setInfo(true)}
        />
      )}
      <ConfirmDialog
        open={confirming}
        onOpenChange={setConfirming}
        title={t("disconnectTitle", { ats: provider.name })}
        text={t("disconnectText")}
        confirm={t("disconnect")}
        busy={busy}
        onConfirm={disconnect}
      />
    </span>
  )
}
