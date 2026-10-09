"use client"

import { usePathname } from "next/navigation"
import type { ReactNode } from "react"

import { TIMED_PAGE } from "@/constants/layout"

/** Its children everywhere but on a timed question's page, where they would only distract. */
export function NotOnTimedPage({ children }: { children: ReactNode }) {
  const pathname = usePathname()

  if (TIMED_PAGE.test(pathname)) {
    return null
  }

  return children
}
