"use client"

import { useLocale, useTranslations } from "next-intl"

import { TopUpDialog } from "@/components/billing/top-up-dialog"
import type { Catalog } from "@/types/billing"

/** The company's credits for candidates, with a top-up next to them. */
export function CompanyCredits({
  companyId,
  companyName,
  credits,
  catalog,
}: {
  companyId: string
  companyName: string
  credits: number
  catalog: Catalog
}) {
  const t = useTranslations("company")
  const locale = useLocale()

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border px-6 py-4">
      <p className="text-base">
        <span className="font-heading text-2xl font-medium tabular-nums">
          {credits.toLocaleString(locale)}
        </span>{" "}
        <span className="text-muted-foreground">
          {t("creditsLeft", {
            count: credits,
            candidate: catalog.candidate_credits,
          })}
        </span>
      </p>
      <TopUpDialog
        catalog={catalog}
        title={companyName}
        companyId={companyId}
      />
    </div>
  )
}
