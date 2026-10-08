"use client"

import { ArrowUpRightIcon, CheckIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { LocalizedLink } from "@/components/localized-link"
import { Button } from "@/components/ui/button"
import { linkPage } from "@/lib/assistant"
import type { AssistantBlock } from "@/types/assistant"

export type CardActions = {
  onConfirm: (actionId: string) => void
  onCancel: (actionId: string) => void
  // While an answer streams, nothing can be confirmed.
  busy: boolean
  companyNames: Record<string, string>
}

/** An action the assistant prepared: what will happen, with exactly the values it runs with
 * (and a warning when it can't be undone), Confirm and Cancel; then how it ended, with the page
 * it made. */
export function ActionCard({
  card,
  actions,
  onNavigate,
}: {
  card: AssistantBlock
  actions: CardActions
  onNavigate: () => void
}) {
  const t = useTranslations("assistant.actions")
  const pages = useTranslations("assistant.pages")
  const tool = card.tool ?? ""
  const state = card.state ?? "pending"
  const company = card.company_id && actions.companyNames[card.company_id]
  const fields = Object.entries(card.preview ?? {})

  return (
    <div className="space-y-3 rounded-2xl border p-4 text-sm">
      <p className="font-medium">
        {t.has(`titles.${tool}`) ? t(`titles.${tool}`) : t("generic")}
      </p>
      {(company || fields.length > 0) && (
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
          {company && (
            <>
              <dt className="text-muted-foreground">{t("fields.company")}</dt>
              <dd className="bidi-auto break-words">{company}</dd>
            </>
          )}
          {fields.map(([key, value]) => (
            <div key={key} className="contents">
              <dt className="text-muted-foreground">
                {t.has(`fields.${key}`) ? t(`fields.${key}`) : key}
              </dt>
              <dd className="bidi-auto break-words whitespace-pre-wrap">
                {String(value)}
              </dd>
            </div>
          ))}
        </dl>
      )}
      {card.destructive && state === "pending" && (
        <p className="text-destructive">{t("cantUndo")}</p>
      )}
      {(state === "pending" || state === "running") && (
        <div className="flex flex-wrap gap-2">
          <Button
            variant={card.destructive ? "destructive" : "default"}
            className="h-9 px-4"
            disabled={state === "running" || actions.busy}
            onClick={() => actions.onConfirm(card.action_id!)}
          >
            {state === "running" ? t("running") : t("confirm")}
          </Button>
          <Button
            variant="outline"
            className="h-9 px-4"
            disabled={state === "running" || actions.busy}
            onClick={() => actions.onCancel(card.action_id!)}
          >
            {t("cancel")}
          </Button>
        </div>
      )}
      {state === "done" && (
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <CheckIcon aria-hidden className="size-4" />
            {t("done")}
          </span>
          {card.links.map(
            (href) =>
              href && (
                <Button
                  key={href}
                  variant="outline"
                  size="sm"
                  render={<LocalizedLink href={href} onClick={onNavigate} />}
                  nativeButton={false}
                >
                  {pages.has(linkPage(href) ?? "")
                    ? pages(linkPage(href)!)
                    : pages("open")}
                  <ArrowUpRightIcon
                    data-icon="inline-end"
                    className="rtl:-scale-x-100"
                  />
                </Button>
              )
          )}
        </div>
      )}
      {state === "failed" && (
        <p className="text-destructive">{card.detail ?? t("failed")}</p>
      )}
      {state === "cancelled" && (
        <p className="text-muted-foreground">{t("cancelled")}</p>
      )}
    </div>
  )
}
