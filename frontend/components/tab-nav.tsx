"use client"

import { cn } from "cn"
import type { LucideIcon } from "lucide-react"
import Link from "next/link"
import { useEffect, useRef } from "react"

/** A page's slim tabs under its title: the current one over a blue line. Labels are lowercase
 * like the site's other tabs; `keepCase` keeps an abbreviation's capitals (ATS). Tabs wider than
 * the screen scroll in their own row, with the current one brought into view. With `onSelect`
 * they're tabs within a page or a dialog (buttons) rather than links, fitting its width; an
 * item's `icon` goes before its label, in the label's colour. */
export function TabNav({
  items,
  current,
  onSelect,
}: {
  items: readonly {
    id: string
    href?: string
    label: string
    keepCase?: boolean
    icon?: LucideIcon
  }[]
  current: string
  onSelect?: (id: string) => void
}) {
  const active = useRef<HTMLAnchorElement & HTMLButtonElement>(null)

  useEffect(() => {
    active.current?.scrollIntoView({ block: "nearest", inline: "nearest" })
  }, [current])

  return (
    // The row scrolls; the line under the tabs is the inner row's, so the current tab's blue
    // line isn't clipped.
    <div className="[scrollbar-width:none] overflow-x-auto">
      <nav
        role={onSelect ? "tablist" : undefined}
        // Tabs inside a dialog fit its width: closer together on a phone, a long label wraps.
        className={cn(
          "flex border-b",
          onSelect
            ? "w-full items-end gap-3 sm:gap-5"
            : "w-max min-w-full gap-8"
        )}
      >
        {items.map((item) => {
          const className = cn(
            "-mb-px border-b-2 pb-3 transition-colors",
            // In a dialog on a phone, a step smaller, and a long word breaks.
            onSelect
              ? "text-start text-sm hyphens-auto sm:text-base"
              : "text-base whitespace-nowrap",
            item.keepCase ? "normal-case" : "lowercase",
            item.id === current
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground active:border-border active:text-foreground"
          )

          return onSelect ? (
            <button
              key={item.id}
              ref={item.id === current ? active : undefined}
              type="button"
              role="tab"
              aria-selected={item.id === current}
              className={className}
              onClick={() => onSelect(item.id)}
            >
              {item.icon ? (
                <span className="flex items-center gap-1.5">
                  <item.icon aria-hidden className="size-4 shrink-0" />
                  <span>{item.label}</span>
                </span>
              ) : (
                item.label
              )}
            </button>
          ) : (
            <Link
              key={item.id}
              ref={item.id === current ? active : undefined}
              href={item.href ?? ""}
              aria-current={item.id === current ? "page" : undefined}
              className={className}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
