"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"

/** The settings menu: a column beside the page, a row above it on phones. */
export function SettingsNav() {
  const t = useTranslations("settings")
  const pathname = usePathname()
  const items = [
    { href: "/settings", label: t("general") },
    { href: "/settings/billing", label: t("billing") },
    { href: "/settings/referral", label: t("referral") },
  ]

  return (
    <nav className="flex gap-1 md:flex-col">
      {items.map((item) => {
        const current = pathname === item.href

        return (
          <Button
            key={item.href}
            variant={current ? "secondary" : "ghost"}
            className="h-11 flex-1 justify-center px-4 text-base md:flex-none md:justify-start"
            nativeButton={false}
            render={<Link href={item.href} />}
            aria-current={current ? "page" : undefined}
          >
            {item.label}
          </Button>
        )
      })}
    </nav>
  )
}
