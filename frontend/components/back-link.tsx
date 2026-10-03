"use client"

import type { ReactNode } from "react"
import { ArrowLeftIcon } from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"

export function BackLink({
  href,
  children,
}: {
  href: string
  children: ReactNode
}) {
  const t = useTranslations("nav")
  const label = typeof children === "string" ? children : t("back")

  return (
    <Button
      variant="ghost"
      size="icon-lg"
      aria-label={label}
      // Beside the title only when the page margin fits it; above the title otherwise.
      // Centred with auto margins: the button's press effect replaces any translate, so a
      // translate-based centre would jump away from the cursor mid-click.
      className="mb-2 -ml-3 size-11 rounded-xl text-muted-foreground xl:absolute xl:inset-y-0 xl:right-[calc(100%+0.25rem)] xl:my-auto xl:ml-0 xl:size-14"
      render={<Link href={href} />}
      nativeButton={false}
    >
      <ArrowLeftIcon className="size-6 xl:size-8" />
    </Button>
  )
}
