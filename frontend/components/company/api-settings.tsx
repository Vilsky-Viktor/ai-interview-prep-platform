"use client"

import { useLocale, useTranslations } from "next-intl"

import { CreateDialog, RemoveButton } from "@/components/company/api-dialogs"
import { MAX_KEY_NAME, MAX_WEBHOOK_URL } from "@/constants/api"
import { formatDate } from "@/lib/format"
import type { ApiKey, ApiWebhook } from "@/types/api-access"
import { LIST_BOX } from "@/constants/lists"

/** "New key", in the title row while the keys tab is open: a name and when it expires, then
 * the key itself, shown this once. */
export function NewKey({
  companyId,
  expiries,
}: {
  companyId: string
  expiries: string[]
}) {
  const t = useTranslations("api")

  return (
    <CreateDialog
      path={`/v1/manage/keys?company_id=${companyId}`}
      field="name"
      maxLength={MAX_KEY_NAME}
      label={t("newKey")}
      placeholder={t("keyName")}
      title={t("newKeyTitle")}
      failed={t("createFailed")}
      choice={{
        field: "expiry",
        label: t("expiresIn"),
        options: expiries.map((expiry) => ({
          value: expiry,
          label: t(`expiries.${expiry}`),
        })),
        warning: { value: "never", text: t("neverWarning") },
      }}
      shown={{
        value: "key",
        title: t("keyCreatedTitle"),
        text: t("keyCreatedText"),
        copy: t("copyKey"),
        copied: t("keyCopied"),
      }}
    />
  )
}

/** "Add web hook", in the title row while the web hooks tab is open: an HTTPS address, then its
 * signing secret, shown this once. */
export function AddWebhook({ companyId }: { companyId: string }) {
  const t = useTranslations("api")

  return (
    <CreateDialog
      path={`/v1/manage/webhooks?company_id=${companyId}`}
      field="url"
      type="url"
      maxLength={MAX_WEBHOOK_URL}
      label={t("addWebhook")}
      placeholder={t("webhookUrl")}
      title={t("addWebhookTitle")}
      failed={t("createFailed")}
      shown={{
        value: "secret",
        title: t("webhookCreatedTitle"),
        text: t("webhookCreatedText"),
        copy: t("copySecret"),
        copied: t("secretCopied"),
      }}
    />
  )
}

/** The company's API keys, in one list like the team's: each with its name, first characters,
 * when it was made, when it expires and when it was last used. Owners and admins delete them. */
export function ApiKeys({
  companyId,
  keys,
  canEdit,
}: {
  companyId: string
  keys: ApiKey[]
  canEdit: boolean
}) {
  const t = useTranslations("api")
  const locale = useLocale()
  const manage = `/v1/manage/keys`

  return (
    <Section
      text={t("keysText")}
      empty={t("noKeys")}
      rows={keys.map((key) => (
        <Row
          key={key.id}
          title={key.name}
          details={
            <>
              <span className="font-mono">{key.shown}…</span>
              {" · "}
              <time suppressHydrationWarning>
                {t("created", { date: formatDate(key.created_at, locale) })}
              </time>
              {" · "}
              {key.expired ? (
                <span className="text-destructive">{t("expired")}</span>
              ) : (
                <time suppressHydrationWarning>
                  {key.expires_at
                    ? t("expires", { date: formatDate(key.expires_at, locale) })
                    : t("neverExpires")}
                </time>
              )}
              {" · "}
              <time suppressHydrationWarning>
                {key.last_used_at
                  ? t("lastUsed", {
                      date: formatDate(key.last_used_at, locale),
                    })
                  : t("neverUsed")}
              </time>
            </>
          }
          remove={
            canEdit && (
              <RemoveButton
                path={`${manage}/${key.id}?company_id=${companyId}`}
                label={t("removeKey")}
                title={t("removeKeyTitle")}
                text={t("removeKeyText", { name: key.name })}
                failed={t("removeFailed")}
              />
            )
          }
        />
      ))}
    />
  )
}

/** The addresses that hear when a candidate finishes; owners and admins delete them. */
export function ApiWebhooks({
  companyId,
  webhooks,
  canEdit,
}: {
  companyId: string
  webhooks: ApiWebhook[]
  canEdit: boolean
}) {
  const t = useTranslations("api")
  const locale = useLocale()
  const manage = `/v1/manage/webhooks`

  return (
    <Section
      text={t("webhooksText")}
      empty={t("noWebhooks")}
      rows={webhooks.map((hook) => (
        <Row
          key={hook.id}
          title={hook.url}
          details={
            <>
              <time suppressHydrationWarning>
                {t("added", { date: formatDate(hook.created_at, locale) })}
              </time>
              {hook.failing && (
                <>
                  {" · "}
                  <span className="text-destructive">{t("failing")}</span>
                </>
              )}
            </>
          }
          remove={
            canEdit && (
              <RemoveButton
                path={`${manage}/${hook.id}?company_id=${companyId}`}
                label={t("removeWebhook")}
                title={t("removeWebhookTitle")}
                text={t("removeWebhookText", { url: hook.url })}
                failed={t("removeFailed")}
              />
            )
          }
        />
      ))}
    />
  )
}

/** What the tab is for, then its list, or a box saying it's empty. */
function Section({
  text,
  empty,
  rows,
}: {
  text: string
  empty: string
  rows: React.ReactNode[]
}) {
  return (
    <section className="space-y-6">
      <p className="text-base text-muted-foreground">{text}</p>
      {rows.length ? (
        <ul className={LIST_BOX}>{rows}</ul>
      ) : (
        <p className="rounded-2xl border p-6 text-muted-foreground">{empty}</p>
      )}
    </section>
  )
}

function Row({
  title,
  details,
  remove,
}: {
  title: string
  details: React.ReactNode
  remove: React.ReactNode
}) {
  return (
    <li className="flex items-center justify-between gap-4 p-6">
      <span className="min-w-0 space-y-1">
        <span className="block text-lg font-medium break-all">{title}</span>
        <span className="block text-sm text-muted-foreground">{details}</span>
      </span>
      {remove}
    </li>
  )
}
