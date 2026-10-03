"use client"

import { cn } from "cn"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTranslations } from "next-intl"

import { useAuth } from "@/components/auth-provider"
import { NAV_LINKS } from "@/constants/navigation"

export function SiteNav() {
  const t = useTranslations("nav")
  const pathname = usePathname()
  const { user, loading } = useAuth()

  return (
    // The negative margin cancels the first link's padding, so the separator sits evenly.
    // globals.css finds it by data-slot to add the blue dots; the label is translated.
    <nav
      data-slot="main-nav"
      className="-ms-1.5 flex h-8 items-center sm:-ms-2.5"
      aria-label={t("main")}
    >
      {NAV_LINKS.map((link) => {
        if (link.signedInOnly && (loading || !user)) {
          return null
        }

        const current = link.exact
          ? pathname === link.href
          : pathname.startsWith(link.href)

        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={current ? "page" : undefined}
            className={cn(
              "rounded-md px-1.5 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground sm:px-2.5",
              current && "text-foreground",
              link.wide && "hidden sm:inline"
            )}
          >
            {t(link.label)}
          </Link>
        )
      })}
    </nav>
  )
}
