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
      href: `/companies/${companyId}/interviews`,
      label: t("interviews"),
    },
    {
      id: "templates",
      href: `/companies/${companyId}/templates`,
      label: t("templates"),
    },
    {
      id: "members",
      href: `/companies/${companyId}/members`,
      label: t("team"),
    },
    {
      id: "referrals",
      href: `/companies/${companyId}/referrals`,
      label: t("referrals"),
    },
  ] as const

  return <TabNav items={items} current={current} />
}
