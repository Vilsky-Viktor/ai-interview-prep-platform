"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/confirm-dialog"
import { InstructionsDialog } from "@/components/instructions-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SLACK } from "@/constants/slack"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { SlackOverview } from "@/types/notifications"
import {
  INTEGRATION_LINK,
  INTEGRATION_LOGO,
  INTEGRATION_ROW,
} from "@/constants/lists"

const STEPS = ["stepAdd", "stepChannel", "stepKinds", "stepPrivacy"] as const

/** Slack's row on the integrations tab, laid out like an ATS's: its mark, name, whether it's
 * connected and to which channel; the row opens Slack's page, its buttons sit on top. */
export function SlackRow({
  companyId,
  slack,
  canEdit,
}: {
  companyId: string
  slack: SlackOverview
  canEdit: boolean
}) {
  return (
    <li className={INTEGRATION_ROW}>
      <Link
        href={`/companies/${companyId}/integrations/slack`}
        className={INTEGRATION_LINK}
      >
        <span className={INTEGRATION_LOGO + " p-6 max-sm:p-2"}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={SLACK.logo} alt="" className="size-full object-contain" />
        </span>
        <span className="min-w-0 space-y-1">
          <span className="flex items-center gap-3 text-lg font-medium">
            {SLACK.name}
            <SlackStatus slack={slack} />
          </span>
          {slack.connected && (
            <span className="block text-base text-muted-foreground">
              {slack.team} · {slack.channel}
            </span>
          )}
        </span>
      </Link>
      {/* On phones the logo spans the row, with the name and then these buttons beside it,
          sharing their line equally (each on its own line where both don't fit). */}
      <span className="relative z-10 max-sm:col-span-2 max-sm:*:flex max-sm:*:w-full max-sm:*:flex-wrap max-sm:[&>*>*]:flex-1 max-sm:[&>*>*]:px-3 max-sm:[&>*>*:nth-child(3)]:basis-full">
        <SlackActions companyId={companyId} slack={slack} canEdit={canEdit} />
      </span>
    </li>
  )
}

/** "connected" beside Slack's name once it works, like an ATS's tag; nothing otherwise. */
export function SlackStatus({ slack }: { slack: SlackOverview }) {
  const t = useTranslations("ats")

  if (slack.status !== "connected") {
    return null
  }

  return (
    <Badge className="h-7 shrink-0 px-3 text-sm font-light">
      {t("statusConnected")}
    </Badge>
  )
}

/** Slack's buttons, on its row and its page: its Instructions, and for owners and admins Add to
 * Slack (or Reconnect when Slack stopped taking messages), which goes to Slack to pick a channel
 * and comes back, and Disconnect. */
export function SlackActions({
  companyId,
  slack,
  canEdit,
}: {
  companyId: string
  slack: SlackOverview
  canEdit: boolean
}) {
  const t = useTranslations("slack")
  const ats = useTranslations("ats")
  const router = useRouter()
  const [confirming, setConfirming] = useState(false)
  const [busy, setBusy] = useState(false)

  async function connect() {
    setBusy(true)

    try {
      const { url } = await apiFetch<{ url: string }>(
        `/notifications/slack/start?company_id=${companyId}`
      )
      window.location.assign(url)
    } catch (error) {
      toast.error(apiErrorMessage(error, t("connectFailed")))
      setBusy(false)
    }
  }

  async function disconnect() {
    setBusy(true)

    try {
      await apiFetch(`/notifications/slack?company_id=${companyId}`, {
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
      <InstructionsDialog
        title={t("instructionsTitle")}
        steps={STEPS.map((step) => t(step))}
      />
      {canEdit && slack.connected && (
        <Button
          variant="outline"
          className="h-10 px-5 text-base"
          onClick={() => setConfirming(true)}
        >
          {ats("disconnect")}
        </Button>
      )}
      {canEdit && (!slack.connected || slack.status !== "connected") && (
        <Button
          className="h-10 px-5 text-base"
          disabled={busy}
          onClick={connect}
        >
          {slack.connected ? ats("reconnect") : t("add")}
        </Button>
      )}
      <ConfirmDialog
        open={confirming}
        onOpenChange={setConfirming}
        title={t("disconnectTitle")}
        text={t("disconnectText")}
        confirm={ats("disconnect")}
        busy={busy}
        onConfirm={disconnect}
      />
    </span>
  )
}
