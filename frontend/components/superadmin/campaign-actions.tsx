"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/confirm-dialog"
import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { Campaign } from "@/types/campaigns"

const BUTTON = "h-10 px-5 text-base"

/** Sending a campaign, beside its recipients: while it's a draft, send a test (in the language
 * shown) to oneself, or send it (after confirming with how many get it); while it's going out,
 * stop it. Editing and deleting are on its title's line. The API refuses what's no longer allowed and says why. */
export function CampaignActions({
  campaign,
  language,
  recipients,
  onChanged,
}: {
  campaign: Campaign
  language: string
  recipients: number | null
  onChanged: (campaign: Campaign) => void
}) {
  const t = useTranslations("superadmin")
  const router = useRouter()
  const [asking, setAsking] = useState<"send" | "stop" | null>(null)
  const [busy, setBusy] = useState(false)
  const path = `/notifications/superadmin/campaigns/${campaign.id}`

  async function act(run: () => Promise<void>) {
    setBusy(true)

    try {
      await run()
      setAsking(null)
    } catch (error) {
      toast.error(apiErrorMessage(error, t("actionFailed")))
    } finally {
      setBusy(false)
    }
  }

  const sendTest = () =>
    act(async () => {
      await apiFetch(`${path}/test?language=${language}`, { method: "POST" })
      toast.success(t("testSent"))
    })

  const confirmed = () =>
    act(async () => {
      onChanged(
        await apiFetch<Campaign>(`${path}/${asking}`, { method: "POST" })
      )
      router.refresh()
    })

  if (campaign.status === "sent" || campaign.status === "stopped") {
    return null
  }

  return (
    // On phones the two fill a line, 70/30.
    <div className="flex items-center gap-3 max-sm:w-full">
      {campaign.status === "draft" ? (
        <>
          <Button
            variant="outline"
            className={`${BUTTON} max-sm:flex-[7_1_0%]`}
            disabled={busy}
            onClick={sendTest}
            data-testid="send-test"
          >
            {t("sendTest")}
          </Button>
          <Button
            className={`${BUTTON} max-sm:flex-[3_1_0%]`}
            disabled={busy}
            onClick={() => setAsking("send")}
            data-testid="send-campaign"
          >
            {t("sendCampaign")}
          </Button>
        </>
      ) : (
        <Button
          variant="outline"
          className={BUTTON}
          onClick={() => setAsking("stop")}
          data-testid="stop-campaign"
        >
          {t("stopCampaign")}
        </Button>
      )}
      <ConfirmDialog
        open={asking !== null}
        onOpenChange={(open) => !open && setAsking(null)}
        title={asking ? t(`campaignConfirm.${asking}.title`) : ""}
        text={
          asking === "send" && recipients === null
            ? t("campaignConfirm.send.unknown")
            : asking
              ? t(`campaignConfirm.${asking}.text`, { count: recipients ?? 0 })
              : ""
        }
        confirm={asking ? t(`campaignConfirm.${asking}.confirm`) : ""}
        busy={busy}
        onConfirm={confirmed}
      />
    </div>
  )
}
