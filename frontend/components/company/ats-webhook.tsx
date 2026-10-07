"use client"

import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { Chips } from "@/components/company/ats-steps"
import { CopyValue } from "@/components/copy-field"
import {
  GREENHOUSE_WEBHOOK_EVENT,
  GREENHOUSE_WEBHOOK_PATH,
} from "@/constants/ats"
import { apiErrorMessage, apiFetch } from "@/lib/api"

/** Setting up Greenhouse's web hook, which tells us a candidate moved stage: where, which
 * event, and the address and secret key to paste, each with a copy button. */
export function GreenhouseWebhook({ companyId }: { companyId: string }) {
  const t = useTranslations("ats")
  const [webhook, setWebhook] = useState<{ url: string; secret: string }>()

  useEffect(() => {
    apiFetch<{ url: string; secret: string }>(
      `/ats/greenhouse/webhook?company_id=${companyId}`
    )
      .then(setWebhook)
      .catch((error) =>
        toast.error(
          apiErrorMessage(error, t("loadFailed", { ats: "Greenhouse" }))
        )
      )
  }, [companyId, t])

  return (
    <section className="space-y-3">
      <div className="space-y-1">
        <h3 className="text-lg font-medium">{t("webhookTitle")}</h3>
        <p className="text-base text-muted-foreground">{t("webhookText")}</p>
      </div>
      <ol className="list-decimal space-y-3 ps-5 text-base text-muted-foreground">
        <li className="space-y-1.5">
          <span className="block">{t("stepOpen", { ats: "Greenhouse" })}</span>
          <Chips items={GREENHOUSE_WEBHOOK_PATH} path />
        </li>
        <li className="space-y-1.5">
          <span className="block">{t("webhookEvent")}</span>
          <Chips items={[GREENHOUSE_WEBHOOK_EVENT]} />
        </li>
        <li className="space-y-2">
          <span className="block">{t("webhookUrl")}</span>
          <CopyValue
            value={webhook?.url ?? ""}
            label={t("copyUrl")}
            copied={t("copied")}
          />
        </li>
        <li className="space-y-2">
          <span className="block">{t("webhookSecret")}</span>
          <CopyValue
            value={webhook?.secret ?? ""}
            label={t("copySecret")}
            copied={t("copied")}
          />
        </li>
      </ol>
    </section>
  )
}
