"use client"

import { useTranslations } from "next-intl"

import { TabNav } from "@/components/tab-nav"

export function CompanyNav({
  companyId,
  current,
}: {
  companyId: string
  current: "interviews" | "templates" | "members" | "referrals"
}) {
  const t = useTranslations("company")
  const items = [
    {
      id: "interviews",
      href: `/company/${companyId}/interviews`,
      label: t("interviews"),
    },
    {
      id: "templates",
      href: `/company/${companyId}/templates`,
      label: t("templates"),
    },
    {
      id: "members",
      href: `/company/${companyId}/members`,
      label: t("admins"),
    },
    {
      id: "referrals",
      href: `/company/${companyId}/referrals`,
      label: t("referrals"),
    },
  ] as const

  return <TabNav items={items} current={current} />
}
