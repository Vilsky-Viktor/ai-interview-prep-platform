"use client"

import { cn } from "cn"
import { ArrowLeftIcon } from "lucide-react"
import type { ReactNode } from "react"
import { useTranslations } from "next-intl"

import { LocalizedLink } from "@/components/localized-link"
import { Button } from "@/components/ui/button"

export function BackLink({
  href,
  className,
  children,
}: {
  href: string
  // For a title much larger than usual, to line the arrow up with its lowercase letters.
  className?: string
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
      className={cn(
        "-ms-3 mb-2 size-11 rounded-xl text-muted-foreground xl:absolute xl:inset-y-0 xl:end-[calc(100%+0.25rem)] xl:my-auto xl:ms-0 xl:size-14",
        className
      )}
      render={<LocalizedLink href={href} />}
      nativeButton={false}
    >
      <ArrowLeftIcon className="size-6 xl:size-8 rtl:-scale-x-100" />
    </Button>
  )
}
