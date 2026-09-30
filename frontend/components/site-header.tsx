"use client"

import Link from "next/link"

import { useAuth } from "@/components/auth-provider"
import { SiteNav } from "@/components/site-nav"
import { ThemeModes } from "@/components/theme-toggle"
import { UserMenu } from "@/components/user-menu"
import { Wordmark } from "@/components/wordmark"

export function SiteHeader() {
  const { user, loading } = useAuth()

  return (
    <header className="border-b">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex items-center gap-4 sm:gap-6">
          <Link href="/" aria-label="prepza. home">
            <Wordmark className="text-xl" />
          </Link>
          <SiteNav />
        </div>
        <div className="flex items-center gap-3">
          {!loading && !user && (
            <div className="hidden w-32 sm:block">
              <ThemeModes />
            </div>
          )}
          <UserMenu />
        </div>
      </div>
    </header>
  )
}
