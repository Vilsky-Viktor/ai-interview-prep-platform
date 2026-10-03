"use client"

import { CheckIcon } from "lucide-react"
import { useTranslations } from "next-intl"

export function DoneBadge() {
  const t = useTranslations("preparations")

  return (
    <span
      role="img"
      aria-label={t("mastered")}
      title={t("masteredTitle")}
      className="text-emerald-600 dark:text-emerald-400"
    >
      <CheckIcon className="size-5" />
    </span>
  )
}
