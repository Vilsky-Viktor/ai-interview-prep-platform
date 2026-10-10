"use client"

import { useTranslations } from "next-intl"

import { TabNav } from "@/components/tab-nav"

export type CompanyTab =
  | "interviews"
  | "templates"
  | "members"
  | "integrations"
  | "referrals"
  | "billing"

/** A company's tabs; billing only for owners and admins (`canEdit`), who top up. */
export function CompanyNav({
  companyId,
  current,
  canEdit,
}: {
  companyId: string
  current: CompanyTab
  canEdit: boolean
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
      id: "integrations",
      href: `/companies/${companyId}/integrations`,
      label: t("integrations"),
    },
    ...(canEdit
      ? [
          {
            id: "billing",
            href: `/companies/${companyId}/billing`,
            label: t("billing"),
          },
        ]
      : []),
    {
      id: "referrals",
      href: `/companies/${companyId}/referrals`,
      label: t("referrals"),
    },
  ]

  return <TabNav items={items} current={current} />
}
