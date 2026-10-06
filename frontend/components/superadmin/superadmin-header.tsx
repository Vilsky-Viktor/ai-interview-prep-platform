"use client"

import { useTranslations } from "next-intl"
import type { ReactNode } from "react"

import { TabNav } from "@/components/tab-nav"

/** The admin zone's title and tabs, as a company's pages have them, with `action` on the right. */
export function SuperadminHeader({
  current,
  action,
}: {
  current:
    | "templates"
    | "flagged"
    | "replaced"
    | "pass-rates"
    | "verification"
    | "controls"
  action?: ReactNode
}) {
  const t = useTranslations("superadmin")

  return (
    <div className="space-y-4">
      <div className="flex min-h-14 items-center">
        <h1 className="min-w-0 flex-1 font-heading text-3xl font-medium tracking-tight">
          {t("zone")}
        </h1>
        {action}
      </div>
      <TabNav
        items={[
          {
            id: "templates",
            href: "/superadmin/templates",
            label: t("templates"),
          },
          { id: "flagged", href: "/superadmin/flagged", label: t("flagged") },
          {
            id: "replaced",
            href: "/superadmin/replaced",
            label: t("replaced"),
          },
          {
            id: "pass-rates",
            href: "/superadmin/pass-rates",
            label: t("passRates"),
          },
          {
            id: "verification",
            href: "/superadmin/verification",
            label: t("verification"),
          },
          {
            id: "controls",
            href: "/superadmin/controls",
            label: t("controls"),
          },
        ]}
        current={current}
      />
    </div>
  )
}
