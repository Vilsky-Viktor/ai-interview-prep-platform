"use client"

import { useTranslations } from "next-intl"

import { TabNav } from "@/components/tab-nav"

/** The interview's tabs; settings only for those who can change them (owners and admins). */
export function InterviewNav({
  href,
  current,
  canEdit,
}: {
  href: string
  current: "topics" | "candidates" | "settings"
  canEdit: boolean
}) {
  const t = useTranslations("interviews")
  const items = [
    { id: "topics", href, label: t("topicsTab") },
    {
      id: "candidates",
      href: `${href}?tab=candidates`,
      label: t("candidates"),
    },
    ...(canEdit
      ? [
          {
            id: "settings",
            href: `${href}?tab=settings`,
            label: t("settings"),
          } as const,
        ]
      : []),
  ]

  return <TabNav items={items} current={current} />
}
