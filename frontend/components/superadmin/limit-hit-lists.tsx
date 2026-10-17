"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { useLimitAmount } from "@/components/superadmin/ai-budgets"
import { AmountRows } from "@/components/superadmin/amount-rows"
import type { LimitHitLists as Hits, LimitHits } from "@/types/superadmin"

const LINK = "underline underline-offset-4 hover:text-foreground"

/** The limits hit in the period, ours and our providers' in two lists, most hit first: each
 * with its current value, and the companies and users that hit it most, opening their support
 * pages. */
export function LimitHitLists({ hits }: { hits: Hits }) {
  const t = useTranslations("superadmin")
  const amount = useLimitAmount()

  function rows(list: LimitHits[]) {
    return list.map((row) => ({
      key: `${row.kind}-${row.limit}`,
      title: t(`limitNames.${row.limit}`),
      details: [
        row.value !== null && row.value !== undefined
          ? t("limitValue", {
              value: amount(row.value, row.unit),
              window: row.window ? t(`limitWindows.${row.window}`) : "",
            })
          : t(`limitKinds.${row.kind.split(":").pop()}`),
        ...row.companies.map((company) => (
          <Link
            key={company.id}
            href={`/superadmin/support/companies/${company.id}`}
            className={LINK}
          >
            {t("limitHitter", {
              name: company.name ?? company.id,
              count: company.hits,
            })}
          </Link>
        )),
        ...row.users.map((user) => (
          <Link
            key={user.id}
            href={`/superadmin/support/users/${user.id}`}
            className={LINK}
          >
            {t("limitHitter", { name: user.name ?? user.id, count: user.hits })}
          </Link>
        )),
      ],
      amount: t("limitHits", { count: row.hits }),
    }))
  }

  return (
    <>
      <AmountRows
        title={t("limitsOursTitle")}
        empty={t("limitsNoHits")}
        rows={rows(hits.ours)}
      />
      <AmountRows
        title={t("limitsProvidersTitle")}
        empty={t("limitsNoHits")}
        rows={rows(hits.providers)}
      />
    </>
  )
}
