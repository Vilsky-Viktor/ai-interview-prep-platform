"use client"

import { useTranslations } from "next-intl"

import { TabNav } from "@/components/tab-nav"

/** The API page's tabs: its keys, and its web hooks. */
export function ApiNav({
  href,
  current,
}: {
  href: string
  current: "keys" | "webhooks"
}) {
  const t = useTranslations("api")
  const items = [
    { id: "keys", href, label: t("keysTitle"), keepCase: true },
    { id: "webhooks", href: `${href}?tab=webhooks`, label: t("webhooksTitle") },
  ]

  return <TabNav items={items} current={current} />
}
