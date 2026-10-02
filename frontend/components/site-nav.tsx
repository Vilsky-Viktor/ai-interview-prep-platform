"use client"

import { cn } from "cn"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { useAuth } from "@/components/auth-provider"
import { NAV_LINKS } from "@/constants/navigation"

export function SiteNav() {
  const pathname = usePathname()
  const { user, loading } = useAuth()

  return (
    // The negative margin cancels the first link's padding, so the separator sits evenly.
    <nav className="-ml-1.5 flex h-8 items-center sm:-ml-2.5" aria-label="Main">
      {NAV_LINKS.map((link) => {
        if (link.signedInOnly && (loading || !user)) {
          return null
        }

        const current = pathname.startsWith(link.href)

        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={current ? "page" : undefined}
            className={cn(
              "rounded-md px-1.5 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground sm:px-2.5",
              current && "text-foreground"
            )}
          >
            {link.label}
          </Link>
        )
      })}
    </nav>
  )
}
