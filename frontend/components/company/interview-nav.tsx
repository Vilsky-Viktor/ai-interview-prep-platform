"use client"

import { useTranslations } from "next-intl"

import { TabNav } from "@/components/tab-nav"

export function InterviewNav({
  href,
  current,
}: {
  href: string
  current: "topics" | "candidates" | "talents"
}) {
  const t = useTranslations("interviews")
  const items = [
    { id: "topics", href, label: t("interview") },
    {
      id: "candidates",
      href: `${href}?tab=candidates`,
      label: t("candidates"),
    },
    {
      id: "talents",
      href: `${href}?tab=talents`,
      label: t("talents"),
    },
  ] as const

  return <TabNav items={items} current={current} />
}
