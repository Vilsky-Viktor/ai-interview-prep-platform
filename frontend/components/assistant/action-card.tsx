"use client"

import { ArrowRightIcon, CheckIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { LocalizedLink } from "@/components/localized-link"
import { Button } from "@/components/ui/button"
import { previewValue } from "@/lib/action-values"
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
  // The company, unless the card is about it already.
  const named = card.company_id && actions.companyNames[card.company_id]
  const company = named !== card.subject ? named : null
  const fields = Object.entries(card.preview ?? {})

  return (
    <div className="space-y-3 rounded-2xl border p-4 text-sm">
      <div className="space-y-0.5">
        <p className="font-medium">
          {t.has(`titles.${tool}`) ? t(`titles.${tool}`) : t("generic")}
        </p>
        {card.subject && (
          <p className="bidi-auto break-words">{card.subject}</p>
        )}
      </div>
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
                {t.has(`fieldsOf.${tool}.${key}`)
                  ? t(`fieldsOf.${tool}.${key}`)
                  : t.has(`fields.${key}`)
                    ? t(`fields.${key}`)
                    : key}
              </dt>
              <dd className="bidi-auto break-words whitespace-pre-wrap">
                {previewValue(key, value, t("yes"), t("no"))}
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
                  // A name keeps its capitals in the lowercase button.
                  className={card.result_label ? "normal-case" : undefined}
                  render={<LocalizedLink href={href} onClick={onNavigate} />}
                  nativeButton={false}
                >
                  {card.result_label
                    ? t("openNamed", { name: card.result_label })
                    : pages.has(linkPage(href) ?? "")
                      ? pages(linkPage(href)!)
                      : pages("open")}
                  <ArrowRightIcon
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
