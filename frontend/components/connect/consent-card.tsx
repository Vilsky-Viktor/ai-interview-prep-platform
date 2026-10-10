"use client"

import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { WarningCard } from "@/components/warning-card"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { ConnectAnswer, ConnectRequest } from "@/types/connections"

/** Asks the signed-in user whether an AI app may use their account: who asks, what it can and
 * can't do, a warning for an app prepza doesn't know, and Deny or Allow; either answer goes back
 * to the app. */
export function ConsentCard({
  requestId,
  request,
  email,
}: {
  requestId: string
  request: ConnectRequest
  email: string
}) {
  const t = useTranslations("connect")
  const common = useTranslations("common")
  const [busy, setBusy] = useState(false)
  const client = request.client_name

  async function answer(choice: "approve" | "deny") {
    setBusy(true)

    try {
      const { redirect_url } = await apiFetch<ConnectAnswer>(
        `/assistant/connect/${encodeURIComponent(requestId)}/${choice}`,
        { method: "POST" }
      )
      window.location.assign(redirect_url)
    } catch (error) {
      toast.error(apiErrorMessage(error, common("failed")))
      setBusy(false)
    }
  }

  return (
    <div className="w-full max-w-md space-y-6 rounded-2xl border p-6 sm:p-8">
      <div className="space-y-3">
        <h1 className="font-heading text-3xl font-medium tracking-tight text-balance">
          {t.rich("title", {
            client,
            name: (chunks) => <span className="normal-case">{chunks}</span>,
          })}
        </h1>
        <p className="text-base break-words text-muted-foreground">
          {t("who", { client, host: request.redirect_host, email })}
        </p>
      </div>
      <List title={t("canTitle")} items={t.raw("can") as string[]} />
      <List title={t("cantTitle")} items={t.raw("cant") as string[]} />
      {!request.known_client && <WarningCard>{t("unknown")}</WarningCard>}
      <div className="flex gap-3 max-sm:*:flex-1 sm:justify-end">
        <Button
          variant="outline"
          className="h-10 px-5 text-base"
          disabled={busy}
          onClick={() => answer("deny")}
        >
          {t("deny")}
        </Button>
        <Button
          className="h-10 px-5 text-base"
          disabled={busy}
          onClick={() => answer("approve")}
        >
          {t("allow")}
        </Button>
      </div>
      <p className="text-sm text-muted-foreground">{t("footnote")}</p>
    </div>
  )
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="space-y-2">
      <h3 className="text-lg font-medium">{title}</h3>
      <ul className="list-disc space-y-1.5 ps-5 text-base text-muted-foreground">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}
