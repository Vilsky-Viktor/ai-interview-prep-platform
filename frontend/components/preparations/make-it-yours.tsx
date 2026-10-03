"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"

/** On someone else's public kit: an own kit is built from the learner's own job ad. */
export function MakeItYours() {
  const t = useTranslations("rounds")

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl bg-muted/50 px-6 py-4">
      <p className="text-base">{t("makeItYours")}</p>
      <Button
        className="h-10 px-5"
        render={<Link href="/" />}
        nativeButton={false}
      >
        {t("makeItYoursAction")}
      </Button>
    </div>
  )
}
