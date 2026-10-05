"use client"

import { useTranslations } from "next-intl"

import { Badge } from "@/components/ui/badge"

/** A test's status as companies decides it: new, in process or hired. Hired stands out. */
export function InterviewStatus({ status }: { status: string }) {
  const t = useTranslations("interviewStatus")

  return (
    <Badge
      variant={status === "hired" ? "default" : "outline"}
      className="h-7 shrink-0 px-3 text-sm font-light"
    >
      {t(status)}
    </Badge>
  )
}
