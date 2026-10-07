"use client"

import { PlayIcon } from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"

/** Opens the test's preview: the candidate's intro page, then the test itself, free. */
export function TryInterview({
  companyId,
  interviewId,
  title,
}: {
  companyId: string
  interviewId: string
  title: string
}) {
  const t = useTranslations("interviews")

  return (
    <Button
      variant="ghost"
      size="icon"
      className="size-12 shrink-0 text-muted-foreground hover:text-foreground"
      aria-label={t("tryLabel", { title })}
      tooltip={t("try")}
      render={
        <Link href={`/companies/${companyId}/interviews/${interviewId}/try`} />
      }
      nativeButton={false}
    >
      <PlayIcon className="size-6" />
    </Button>
  )
}
