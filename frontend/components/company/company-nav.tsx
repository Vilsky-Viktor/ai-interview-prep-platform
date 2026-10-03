"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"

export function CompanyNav({
  companyId,
  current,
}: {
  companyId: string
  current: "interviews" | "members" | "referrals"
}) {
  const t = useTranslations("company")
  const items = [
    {
      id: "interviews",
      href: `/company/${companyId}/interviews`,
      label: t("interviews"),
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

  return (
    <nav className="flex w-full rounded-lg border p-2">
      {items.map((item) => (
        <Button
          key={item.id}
          variant={item.id === current ? "secondary" : "ghost"}
          className="h-12 flex-1 px-6 text-base"
          nativeButton={false}
          render={<Link href={item.href} />}
          aria-current={item.id === current ? "page" : undefined}
        >
          {item.label}
        </Button>
      ))}
    </nav>
  )
}
