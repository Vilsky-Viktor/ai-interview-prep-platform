"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"

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
