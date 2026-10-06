"use client"

import { useTranslations } from "next-intl"

import { TabNav } from "@/components/tab-nav"

export function InterviewNav({
  href,
  current,
}: {
  href: string
  current: "topics" | "candidates"
}) {
  const t = useTranslations("interviews")
  const items = [
    { id: "topics", href, label: t("interview") },
    {
      id: "candidates",
      href: `${href}?tab=candidates`,
      label: t("candidates"),
    },
  ] as const

  return <TabNav items={items} current={current} />
}
