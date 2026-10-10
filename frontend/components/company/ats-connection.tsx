"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { CandidateFlow } from "@/components/company/ats-candidate-flow"
import { ConnectAts } from "@/components/company/ats-connect"
import { AtsWebhook } from "@/components/company/ats-webhook"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { WEBHOOKS, type AtsProvider } from "@/constants/ats"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { AtsConnection } from "@/types/company"
import {
  INTEGRATION_LINK,
  INTEGRATION_LOGO,
  INTEGRATION_ROW,
} from "@/constants/lists"

/** An ATS's row on the integrations tab: its logo, name and whether it's connected, laid out
 * like the companies list; the row opens the ATS's page (its linked jobs), its buttons sit on
 * top. */
export function AtsConnectionRow({
  companyId,
  companyName,
  provider,
  connection,
  canEdit,
}: {
  companyId: string
  companyName: string
  provider: AtsProvider
  connection: AtsConnection | null
  canEdit: boolean
}) {
  return (
    <li className={INTEGRATION_ROW}>
      <Link
        href={`/companies/${companyId}/integrations/${provider.id}`}
        className={INTEGRATION_LINK}
      >
        {/* The ATS's own icon (public/ats), as the companies list shows a logo: a square the
            row's full height (24px padding twice, plus two lines), from its left border. */}
        <span className={INTEGRATION_LOGO}>
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
          <AtsAccount
            connection={connection}
            companyName={companyName}
            className="block text-base text-muted-foreground"
          />
        </span>
      </Link>
      {/* On phones the logo spans the row, with the name and then these buttons beside it,
          sharing their line equally (each on its own line where both don't fit). */}
      <span className="relative z-10 max-sm:col-span-2 max-sm:*:flex max-sm:*:w-full max-sm:*:flex-wrap max-sm:[&>*>*]:flex-1 max-sm:[&>*>*]:px-3 max-sm:[&>*>*:nth-child(3)]:basis-full">
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

/** What the company is connected as: its account in the ATS or, where the ATS names none
 * (Greenhouse), the company's own name; nothing before it's connected. */
export function AtsAccount({
  connection,
  companyName,
  className,
}: {
  connection: AtsConnection | null
  companyName: string
  className: string
}) {
  if (!connection) {
    return null
  }

  return <span className={className}>{connection.account || companyName}</span>
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
 * Connect (or Reconnect when its key stopped working) and Disconnect. Greenhouse's and
 * Teamtailor's web hooks are set up by hand: their steps are in the info dialog, which opens
 * once it's connected. */
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
  const hooked = provider.id in WEBHOOKS

  async function disconnect() {
    setBusy(true)

    try {
      await apiFetch(`/ats/${provider.id}?company_id=${companyId}`, {
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
        {canEdit && hooked && connection?.status === "connected" && (
          <AtsWebhook
            companyId={companyId}
            provider={provider as AtsProvider & { id: keyof typeof WEBHOOKS }}
          />
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
          onConnected={() => hooked && setInfo(true)}
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
