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
    | "stats"
    | "controls"
    | "emails"
    | "news"
  action?: ReactNode
}) {
  const t = useTranslations("superadmin")

  return (
    <div className="space-y-4">
      {/* On phones the action takes its own line under the title, at full width. */}
      <div className="flex min-h-14 items-center max-sm:flex-wrap">
        <h1 className="min-w-0 flex-1 font-heading text-3xl font-medium tracking-tight max-sm:basis-full">
          {t("zone")}
        </h1>
        {action && (
          <div className="max-sm:my-4 max-sm:basis-full max-sm:*:w-full">
            {action}
          </div>
        )}
      </div>
      <TabNav
        items={[
          {
            id: "templates",
            href: "/superadmin/templates",
            label: t("templates"),
          },
          { id: "news", href: "/superadmin/news", label: t("news") },
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
          { id: "stats", href: "/superadmin/stats", label: t("stats") },
          { id: "emails", href: "/superadmin/emails", label: t("emails") },
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
