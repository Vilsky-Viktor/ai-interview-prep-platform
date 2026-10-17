import { getLocale, getTranslations } from "next-intl/server"

import { formatUsd } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import type { AiSpend } from "@/types/superadmin"

/** A support page's line about what AI cost for the company or user (`query`, the API's
 * company_id= or user_id=) over the last days the API counts; nothing when it doesn't answer. */
export async function AiSpendLine({ query }: { query: string }) {
  const [spend, t, locale] = await Promise.all([
    serverFetch<AiSpend>(`/billing/superadmin/ai-spend?${query}`),
    getTranslations("superadmin"),
    getLocale(),
  ])

  if (!spend) {
    return null
  }

  return (
    <p className="text-lg" data-testid="ai-spend">
      {t("supportAiSpend", {
        spend: formatUsd(spend.spend, locale),
        days: spend.days,
        count: spend.calls,
      })}
    </p>
  )
}
