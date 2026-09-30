"use client"

import { cn } from "cn"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { useAuth } from "@/components/auth-provider"
import { NAV_LINKS } from "@/constants/navigation"

export function SiteNav() {
  const pathname = usePathname()
  const { user } = useAuth()

  return (
    <nav className="flex items-center gap-1" aria-label="Main">
      {NAV_LINKS.map((link) => {
        if (link.signedInOnly && !user) {
          return null
        }

        const current = pathname.startsWith(link.href)

        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={current ? "page" : undefined}
            className={cn(
              "rounded-md px-2.5 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground",
              current && "text-foreground",
              // On phones the account menu has these; Library stays for signed-out visitors.
              link.signedInOnly && "hidden sm:block"
            )}
          >
            {link.label}
          </Link>
        )
      })}
    </nav>
  )
}
