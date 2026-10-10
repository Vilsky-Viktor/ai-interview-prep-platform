"use client"

import { usePathname } from "next/navigation"
import { type ReactNode, useSyncExternalStore } from "react"

import { TIMED_PAGE } from "@/constants/layout"
import { subscribeTimedPageOver, timedPageOver } from "@/lib/timed-page"

/** Its children everywhere but on a timed question's page while its questions run, where they
 * would only distract; back once they're over. */
export function NotOnTimedPage({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  const over = useSyncExternalStore(
    subscribeTimedPageOver,
    timedPageOver,
    () => false
  )

  if (TIMED_PAGE.test(pathname) && !over) {
    return null
  }

  return children
}
