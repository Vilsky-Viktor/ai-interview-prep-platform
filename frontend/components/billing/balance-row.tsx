"use client"

import { useLocale, useTranslations } from "next-intl"

import { AutoTopUpSetting } from "@/components/billing/auto-top-up"
import { TopUpDialog } from "@/components/billing/top-up-dialog"
import type { Catalog } from "@/types/billing"

/** One balance on the top-up page: whose it is, how much, and a top-up next to it. */
export function BalanceRow({
  catalog,
  name,
  available,
  low,
  companyId,
}: {
  catalog: Catalog
  name: string
  available: number
  low: boolean
  companyId?: string
}) {
  const t = useTranslations("billing")
  const locale = useLocale()

  return (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-3 px-6 py-5">
      <div className="min-w-0 flex-1 space-y-1">
        <p className="truncate text-lg font-medium">{name}</p>
        {low && (
          <p className="text-sm text-amber-600 dark:text-amber-400">
            {t("low")}
          </p>
        )}
        <AutoTopUpSetting catalog={catalog} companyId={companyId} />
      </div>
      <div className="flex items-center gap-6">
        <p className="text-end">
          <span className="font-heading text-3xl font-medium tabular-nums">
            {available.toLocaleString(locale)}
          </span>{" "}
          <span className="text-sm text-muted-foreground">
            {t("creditsWord", { count: available })}
          </span>
        </p>
        <TopUpDialog catalog={catalog} title={name} companyId={companyId} />
      </div>
    </div>
  )
}
